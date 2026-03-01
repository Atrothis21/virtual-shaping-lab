from typing import Any, Dict

from experiment.config import ExperimentConfig


class PlanService:
    """Application-layer facade for payload -> resolved plan operations."""

    @staticmethod
    def resolve(payload: Dict[str, Any]) -> Dict[str, Any]:
        plan = ExperimentConfig.plan_from_payload(payload)
        return {
            "plan": plan.to_dict(),
            "stable_hash": plan.stable_hash(),
        }

