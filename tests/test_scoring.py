import pytest
from schemas import (
    RequirementEvaluation,
    RequirementImportance,
    RequirementStatus,
)
from scoring import calculate_coverage_score


def test_empty_requirements():
    result = calculate_coverage_score([])
    assert result["coverage_percent"] == 0.0
    assert result["total_earned_points"] == 0.0
    assert result["total_possible_points"] == 0.0
    assert result["breakdown"] == []


def test_all_supported():
    reqs = [
        RequirementEvaluation(
            requirement="Python programming",
            importance=RequirementImportance.MUST_HAVE,
            status=RequirementStatus.SUPPORTED,
            evidence_quote="5 years of Python experience",
            reasoning="Candidate explicitly lists 5 years of Python.",
        ),
        RequirementEvaluation(
            requirement="Docker experience",
            importance=RequirementImportance.NICE_TO_HAVE,
            status=RequirementStatus.SUPPORTED,
            evidence_quote="Built Docker containers for microservices",
            reasoning="Candidate has hands-on Docker experience.",
        ),
    ]
    result = calculate_coverage_score(reqs)
    assert result["coverage_percent"] == 100.0
    assert result["total_earned_points"] == 3.0
    assert result["total_possible_points"] == 3.0


def test_all_missing():
    reqs = [
        RequirementEvaluation(
            requirement="Kubernetes",
            importance=RequirementImportance.MUST_HAVE,
            status=RequirementStatus.NOT_EVIDENCED,
            reasoning="Not mentioned in resume.",
        ),
        RequirementEvaluation(
            requirement="Go",
            importance=RequirementImportance.NICE_TO_HAVE,
            status=RequirementStatus.NOT_EVIDENCED,
            reasoning="Not mentioned in resume.",
        ),
    ]
    result = calculate_coverage_score(reqs)
    assert result["coverage_percent"] == 0.0
    assert result["total_earned_points"] == 0.0
    assert result["total_possible_points"] == 3.0


def test_mixed_worked_example():
    reqs = [
        RequirementEvaluation(
            requirement="FastAPI",
            importance=RequirementImportance.MUST_HAVE,
            status=RequirementStatus.SUPPORTED,
            evidence_quote="Designed REST APIs using FastAPI",
            reasoning="Direct match.",
        ),
        RequirementEvaluation(
            requirement="PostgreSQL",
            importance=RequirementImportance.MUST_HAVE,
            status=RequirementStatus.PARTIAL,
            evidence_quote="Basic SQL queries in MySQL",
            reasoning="Has SQL experience with MySQL but not explicitly PostgreSQL.",
        ),
        RequirementEvaluation(
            requirement="AWS Cloud",
            importance=RequirementImportance.MUST_HAVE,
            status=RequirementStatus.NOT_EVIDENCED,
            reasoning="No mention of AWS in resume text.",
        ),
        RequirementEvaluation(
            requirement="Git CI/CD",
            importance=RequirementImportance.NICE_TO_HAVE,
            status=RequirementStatus.SUPPORTED,
            evidence_quote="Automated CI with GitHub Actions",
            reasoning="Direct match for Git CI/CD.",
        ),
        RequirementEvaluation(
            requirement="Redis",
            importance=RequirementImportance.NICE_TO_HAVE,
            status=RequirementStatus.NOT_EVIDENCED,
            reasoning="No mention of Redis.",
        ),
    ]

    result = calculate_coverage_score(reqs)
    assert result["coverage_percent"] == 50.0
    assert result["total_earned_points"] == 4.0
    assert result["total_possible_points"] == 8.0
    assert len(result["breakdown"]) == 5
