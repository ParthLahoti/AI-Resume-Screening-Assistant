from typing import List, Dict, Any
from schemas import RequirementEvaluation, RequirementImportance, RequirementStatus

STATUS_POINTS: Dict[RequirementStatus, float] = {
    RequirementStatus.SUPPORTED: 1.0,
    RequirementStatus.PARTIAL: 0.5,
    RequirementStatus.NOT_EVIDENCED: 0.0,
}

IMPORTANCE_WEIGHTS: Dict[RequirementImportance, float] = {
    RequirementImportance.MUST_HAVE: 2.0,
    RequirementImportance.NICE_TO_HAVE: 1.0,
}


def calculate_coverage_score(requirements: List[RequirementEvaluation]) -> Dict[str, Any]:
    if not requirements:
        return {
            "coverage_percent": 0.0,
            "total_earned_points": 0.0,
            "total_possible_points": 0.0,
            "formula_str": "coverage = (sum(weight * points) / sum(weight)) * 100",
            "calculation_steps": "No requirements identified to evaluate.",
            "breakdown": []
        }

    total_earned = 0.0
    total_possible = 0.0
    breakdown = []

    for req in requirements:
        weight = IMPORTANCE_WEIGHTS.get(req.importance, 1.0)
        points = STATUS_POINTS.get(req.status, 0.0)
        earned = weight * points
        possible = weight

        total_earned += earned
        total_possible += possible

        breakdown.append({
            "requirement": req.requirement,
            "importance": req.importance.value,
            "status": req.status.value,
            "weight": weight,
            "points": points,
            "weighted_score": earned,
            "max_score": possible,
        })

    if total_possible == 0.0:
        coverage_percent = 0.0
    else:
        coverage_percent = round((total_earned / total_possible) * 100.0, 1)

    calculation_steps = (
        f"Earned Points: {total_earned:.1f} / Total Possible: {total_possible:.1f} = "
        f"({total_earned:.1f} / {total_possible:.1f}) * 100 = {coverage_percent:.1f}%"
    )

    return {
        "coverage_percent": coverage_percent,
        "total_earned_points": round(total_earned, 2),
        "total_possible_points": round(total_possible, 2),
        "formula_str": "Coverage % = (Total Weighted Earned Points / Total Possible Weight) * 100",
        "calculation_steps": calculation_steps,
        "breakdown": breakdown,
    }
