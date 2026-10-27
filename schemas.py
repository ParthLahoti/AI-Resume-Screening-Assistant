from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


class RequirementImportance(str, Enum):
    MUST_HAVE = "must_have"
    NICE_TO_HAVE = "nice_to_have"


class RequirementStatus(str, Enum):
    SUPPORTED = "supported"
    PARTIAL = "partial"
    NOT_EVIDENCED = "not_evidenced"


class RequirementEvaluation(BaseModel):
    requirement: str = Field(
        description="The specific skill, experience, or credential extracted directly from the job description."
    )
    importance: RequirementImportance = Field(
        description="Priority level: 'must_have' or 'nice_to_have'."
    )
    status: RequirementStatus = Field(
        description="Evaluation status: 'supported', 'partial', or 'not_evidenced'."
    )
    evidence_quote: Optional[str] = Field(
        default=None,
        description="Verbatim short quote from the resume proving this requirement. Required unless status is 'not_evidenced'."
    )
    reasoning: str = Field(
        description="Concise, objective explanation of how the evidence supports or partially supports the requirement, or why it was not evidenced."
    )

    @model_validator(mode="after")
    def validate_evidence_quote(self) -> "RequirementEvaluation":
        if self.status in (RequirementStatus.SUPPORTED, RequirementStatus.PARTIAL):
            if not self.evidence_quote or not self.evidence_quote.strip():
                raise ValueError(
                    f"evidence_quote is required when status is '{self.status.value}'"
                )
        return self


class RelevantExperience(BaseModel):
    title: str = Field(description="Role, project, or work experience title from the resume.")
    relevance: str = Field(description="Explanation of why this experience is relevant to the JD.")
    evidence_quote: Optional[str] = Field(
        default=None,
        description="Short verbatim quote from the resume referencing this experience."
    )


class FollowUpQuestion(BaseModel):
    question: str = Field(description="Objective, technical or situational interview question.")
    targets_requirement: str = Field(description="The requirement or area this question aims to probe.")


class ScreeningReport(BaseModel):
    candidate_summary: str = Field(
        description="A neutral, factual summary of the candidate's background as documented in the resume."
    )
    requirements: List[RequirementEvaluation] = Field(
        default_factory=list,
        description="Evaluation breakdown for each requirement extracted from the JD."
    )
    relevant_experience: List[RelevantExperience] = Field(
        default_factory=list,
        description="Key roles and projects from the resume aligned with the job description."
    )
    follow_up_questions: List[FollowUpQuestion] = Field(
        default_factory=list,
        description="Targeted interview questions to verify missing or partial qualifications."
    )
    limitations: List[str] = Field(
        default_factory=list,
        description="Model-identified limitations, such as ambiguous text or missing details in the resume."
    )
