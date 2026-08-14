// Neo4j schema — run idempotently on startup (see app/graph/client.py:apply_schema).
CREATE CONSTRAINT product_sku IF NOT EXISTS FOR (p:Product) REQUIRE p.sku IS UNIQUE;
CREATE CONSTRAINT source_id IF NOT EXISTS FOR (s:Source) REQUIRE s.doc_id IS UNIQUE;
CREATE CONSTRAINT claim_id IF NOT EXISTS FOR (c:Claim) REQUIRE c.id IS UNIQUE;
CREATE INDEX attribute_key IF NOT EXISTS FOR (a:Attribute) ON (a.key);
