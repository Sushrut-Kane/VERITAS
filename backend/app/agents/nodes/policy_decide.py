"""policy_decide node: deterministic routing via the policy rule table."""
from app.core.logging import get_logger
from app.policy.rules import decide_policy
from app.schemas.pipeline_state import PipelineState, PolicyOutcome

logger = get_logger(__name__)


async def policy_decide(state: PipelineState) -> dict:
    decisions: dict[str, PolicyOutcome] = {}
    for attr_key, result in state.classifications.items():
        decisions[attr_key] = decide_policy(  # type: ignore[assignment]
            attr_key, result.classification, result.confidence
        )
    logger.info("policy_decide_done", decisions=decisions)
    return {"policy_decisions": decisions, "status": "policy_decided"}
