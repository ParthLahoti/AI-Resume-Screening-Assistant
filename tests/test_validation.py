import pytest
from pydantic import ValidationError
from schemas import (
    RequirementEvaluation,
    RequirementImportance,
    RequirementStatus,
    RelevantExperience,
    FollowUpQuestion,
    ScreeningReport,
)


def test_valid_screening_report():
    data = {
        "candidate_summary": "Experienced backend developer with 4 years in Python.",
        "requirements": [
            {
                "requirement": "Python 3",
                "importance": "must_have",
                "status": "supported",
                "evidence_quote": "4 years of Python development",
                "reasoning": "Explicitly confirmed in resume.",
            },
            {
                "requirement": "GraphQL",
                "importance": "nice_to_have",
                "status": "not_evidenced",
                "evidence_quote": None,
                "reasoning": "No mention of GraphQL in the provided text.",
            },
        ],
        "relevant_experience": [
            {
                "title": "Backend Engineer at Acme Corp",
                "relevance": "Built microservices aligning with backend requirement.",
                "evidence_quote": "Built high-throughput microservices using Python",
            }
        ],
        "follow_up_questions": [
            {
                "question": "Can you discuss your experience with API design patterns?",
                "targets_requirement": "API Architecture",
            }
        ],
        "limitations": [
            "Resume does not specify cloud deployment details.",
        ],
    }
    report = ScreeningReport.model_validate(data)
    assert report.candidate_summary == "Experienced backend developer with 4 years in Python."
    assert len(report.requirements) == 2
    assert report.requirements[0].status == RequirementStatus.SUPPORTED
    assert report.requirements[1].evidence_quote is None


def test_missing_quote_on_supported_status():
    with pytest.raises(ValidationError) as exc_info:
        RequirementEvaluation(
            requirement="Python",
            importance=RequirementImportance.MUST_HAVE,
            status=RequirementStatus.SUPPORTED,
            evidence_quote=None,
            reasoning="Claims to know python.",
        )
    assert "evidence_quote is required" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info2:
        RequirementEvaluation(
            requirement="Python",
            importance=RequirementImportance.MUST_HAVE,
            status=RequirementStatus.SUPPORTED,
            evidence_quote="   ",
            reasoning="Claims to know python.",
        )
    assert "evidence_quote is required" in str(exc_info2.value)


def test_missing_quote_on_partial_status():
    with pytest.raises(ValidationError) as exc_info:
        RequirementEvaluation(
            requirement="C++",
            importance=RequirementImportance.MUST_HAVE,
            status=RequirementStatus.PARTIAL,
            evidence_quote=None,
            reasoning="Has some C experience.",
        )
    assert "evidence_quote is required" in str(exc_info.value)


def test_bad_enum_value():
    with pytest.raises(ValidationError):
        RequirementEvaluation(
            requirement="Java",
            importance="urgent",
            status=RequirementStatus.SUPPORTED,
            evidence_quote="Java developer",
            reasoning="Valid reason",
        )

    with pytest.raises(ValidationError):
        RequirementEvaluation(
            requirement="Java",
            importance=RequirementImportance.MUST_HAVE,
            status="unknown_status",
            evidence_quote="Java developer",
            reasoning="Valid reason",
        )
