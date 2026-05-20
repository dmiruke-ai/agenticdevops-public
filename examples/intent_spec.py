"""
IntentSpec — Core data model for the AgenticDevops intent engine.

This module is published as an illustrative extract.
Full source: github.com/dmiruke-ai/AgenticDevops (private).

The IntentSpec is the canonical intermediate representation between what a
user says in natural language and what the generators produce. Every field
has a confidence band; actions that can't be undone (terraform apply, delete)
require `confirmed` or `stated` confidence on all load-bearing items.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class ConfidenceBand(str, Enum):
    """
    Confidence levels for intent items.
    Lower confidence items cannot trigger irreversible actions.
    """
    SPECULATIVE = "speculative"  # LLM inferred with no user signal
    INFERRED = "inferred"        # Reasonable inference from context
    CONFIRMED = "confirmed"      # User explicitly affirmed
    STATED = "stated"            # User said it verbatim


class IntentCategory(str, Enum):
    """Three-layer intent taxonomy."""
    TASK = "task"              # What to build (compute, networking, CI/CD)
    META = "meta"              # Why and how (cost optimisation, security)
    CONSTRAINT = "constraint"  # Hard requirements (region, compliance, budget)


class SpecItem(BaseModel):
    """
    A single piece of extracted user intent with confidence tracking.
    """
    id: UUID = Field(default_factory=uuid4)
    key: str = Field(..., description="Parameter name, e.g. 'compute_platform', 'region'")
    value: Any = Field(..., description="Parameter value")
    confidence: ConfidenceBand
    category: IntentCategory
    evidence: str = Field(..., description="Quote or context that supports this extraction")
    turn: int = Field(..., description="Conversation turn when extracted / last updated")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    depends_on: list[UUID] = Field(default_factory=list)

    model_config = ConfigDict(
        json_encoders={UUID: str, datetime: lambda v: v.isoformat()}
    )


class OpenQuestion(BaseModel):
    """A question the system needs answered before it can proceed."""
    id: UUID = Field(default_factory=uuid4)
    question_text: str
    blocks_action: str
    priority: str  # high | medium | low
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Conflict(BaseModel):
    """Detected contradiction between two intent items."""
    id: UUID = Field(default_factory=uuid4)
    item_a: UUID
    item_b: UUID
    conflict_type: str
    description: str
    resolution_options: list[str] = Field(default_factory=list)
    auto_resolvable: bool = False
    auto_resolution: Optional[str] = None


class IntentSpec(BaseModel):
    """
    Canonical intent specification — the single source of truth for user intent.

    All agents read from and write to this. Confidence transitions are enforced
    via the IntentTransitionEngine (not shown here). The spec is versioned so
    every mutation is auditable.
    """
    session_id: str
    version: int = 1
    items: dict[UUID, SpecItem] = Field(default_factory=dict)
    open_questions: list[OpenQuestion] = Field(default_factory=list)
    conflicts: list[Conflict] = Field(default_factory=list)
    fixes: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        json_encoders={UUID: str, datetime: lambda v: v.isoformat()}
    )

    def get_item_by_key(self, key: str) -> Optional[SpecItem]:
        for item in self.items.values():
            if item.key == key:
                return item
        return None

    def get_items_by_category(self, category: IntentCategory) -> list[SpecItem]:
        return [item for item in self.items.values() if item.category == category]

    def get_items_by_confidence(self, confidence: ConfidenceBand) -> list[SpecItem]:
        return [item for item in self.items.values() if item.confidence == confidence]


# ---------------------------------------------------------------------------
# Transition rules — the complete confidence state machine
# ---------------------------------------------------------------------------

VALID_TRANSITIONS: dict[tuple[str, str], str] = {
    ("speculative", "inferred"):  "context_implies",
    ("speculative", "confirmed"): "explicit_affirmation",
    ("inferred",    "confirmed"): "explicit_affirmation",
    ("inferred",    "speculative"): "contradicting_signal",
    ("confirmed",   "inferred"):  "user_revision",
    ("stated",      "confirmed"): "always_valid",
}

# Actions that require confirmed or stated confidence on all load-bearing items.
IRREVERSIBLE_ACTIONS = {
    "generate_terraform",
    "create_pipeline",
    "terraform_apply",
    "delete_resource",
    "modify_iam",
}
