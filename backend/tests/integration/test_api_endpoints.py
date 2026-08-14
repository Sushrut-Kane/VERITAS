import uuid

import pytest

from app.db.models.attribute import Attribute, Classification, PolicyDecision
from app.db.models.document import DocType, Document, DocumentStatus
from app.db.models.product import Product
from app.db.session import AsyncSessionLocal


async def _auth_header(client) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login", json={"username": "demo", "password": "veritas"}
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_login_rejects_bad_credentials(client):
    response = await client.post(
        "/api/v1/auth/login", json={"username": "demo", "password": "wrong"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_requires_token(client):
    response = await client.post("/api/v1/products", json={"sku": "X-1"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_product_crud_flow(client):
    headers = await _auth_header(client)

    created = await client.post(
        "/api/v1/products", json={"sku": "ACME-1", "name": "Widget"}, headers=headers
    )
    assert created.status_code == 201
    product_id = created.json()["id"]

    listed = await client.get("/api/v1/products")
    assert listed.status_code == 200
    assert any(p["sku"] == "ACME-1" for p in listed.json())

    fetched = await client.get(f"/api/v1/products/{product_id}")
    assert fetched.status_code == 200

    missing = await client.get(f"/api/v1/products/{uuid.uuid4()}")
    assert missing.status_code == 404


@pytest.mark.asyncio
async def test_document_upload_queues_pipeline(client, monkeypatch):
    async def _noop(document_id):  # don't run the real pipeline in this test
        return None

    monkeypatch.setattr("app.api.v1.documents.run_pipeline", _noop)
    headers = await _auth_header(client)

    response = await client.post(
        "/api/v1/documents",
        data={"product_sku": "UPLOAD-1", "doc_type": "pdf_spec"},
        files={"file": ("spec.txt", b"Weight: 10 kg", "text/plain")},
        headers=headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "queued"
    assert body["filename"] == "spec.txt"


@pytest.mark.asyncio
async def test_catalog_and_review_reflect_persisted_attributes(client):
    headers = await _auth_header(client)

    async with AsyncSessionLocal() as session:
        product = Product(sku="CAT-1", name="Pump")
        session.add(product)
        await session.flush()
        document = Document(
            product_id=product.id,
            filename="a.pdf",
            doc_type=DocType.pdf_spec,
            storage_path="/tmp/a.pdf",
            status=DocumentStatus.done,
        )
        session.add(document)
        await session.flush()
        published = Attribute(
            product_id=product.id,
            attr_key="weight",
            attr_value="10",
            unit="kg",
            source_document_id=document.id,
            source_span="Weight: 10 kg",
            classification=Classification.verified,
            classification_confidence=0.95,
            policy_decision=PolicyDecision.publish,
        )
        review = Attribute(
            product_id=product.id,
            attr_key="voltage_rating",
            attr_value="230",
            unit="V",
            source_document_id=document.id,
            source_span="230 V",
            classification=Classification.verified,
            classification_confidence=0.95,
            policy_decision=PolicyDecision.human_review,
        )
        session.add_all([published, review])
        await session.commit()
        published_id = published.id
        document_id = document.id

    catalog = await client.get("/api/v1/catalog")
    assert catalog.status_code == 200
    skus = {entry["sku"] for entry in catalog.json()}
    assert "CAT-1" in skus

    queue = await client.get("/api/v1/review/queue", headers=headers)
    assert queue.status_code == 200
    assert any(item["attr_key"] == "voltage_rating" for item in queue.json())

    attribute = await client.get(f"/api/v1/attributes/{published_id}")
    assert attribute.status_code == 200
    assert attribute.json()["attr_key"] == "weight"

    status = await client.get(f"/api/v1/pipeline-status/{document_id}")
    assert status.status_code == 200
    assert status.json()["attributes_total"] == 2


@pytest.mark.asyncio
async def test_review_decision_publishes_attribute(client):
    headers = await _auth_header(client)

    async with AsyncSessionLocal() as session:
        product = Product(sku="REV-1")
        session.add(product)
        await session.flush()
        document = Document(
            product_id=product.id,
            filename="a.pdf",
            doc_type=DocType.pdf_spec,
            storage_path="/tmp/a.pdf",
            status=DocumentStatus.done,
        )
        session.add(document)
        await session.flush()
        attribute = Attribute(
            product_id=product.id,
            attr_key="max_operating_temp",
            attr_value="80",
            unit="degC",
            source_document_id=document.id,
            source_span="80 C",
            classification=Classification.verified,
            classification_confidence=0.95,
            policy_decision=PolicyDecision.human_review,
        )
        session.add(attribute)
        await session.commit()
        attribute_id = attribute.id

    response = await client.post(
        f"/api/v1/review/{attribute_id}/decision",
        json={"decision": "publish", "note": "looks good"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["policy_decision"] == "publish"
