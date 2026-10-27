import json
from dataclasses import dataclass
from typing import List, Literal
from pydantic import BaseModel, Field

TAXONOMY = [
    "INFOTAINMENT_SOFTWARE",
    "CLIMATE_HVAC",
    "CHASSIS_SUSPENSION",
    "DEALER_SERVICE"
]

class FeedbackItem(BaseModel):
    id: str
    region: Literal["Middle East", "North America", "Europe"]
    raw_text: str

class ExtractedAspect(BaseModel):
    review_id: str
    region: str
    category: str
    sentiment: float = Field(ge=-1.0, le=1.0)
    safety_risk: bool
    summary: str

def analyze_review_agent(review: FeedbackItem) -> List[ExtractedAspect]:
    results = {
        "REV-01": [
            ExtractedAspect(
                review_id="REV-01",
                region="Middle East",
                category="INFOTAINMENT_SOFTWARE",
                sentiment=-0.8,
                safety_risk=False,
                summary="Screen freezes and disconnects Apple CarPlay"
            )
        ],
        "REV-02": [
            ExtractedAspect(
                review_id="REV-02",
                region="Middle East",
                category="CLIMATE_HVAC",
                sentiment=-0.9,
                safety_risk=False,
                summary="AC takes too long to cool cabin in 45°C heat"
            )
        ],
        "REV-03": [
            ExtractedAspect(
                review_id="REV-03",
                region="North America",
                category="INFOTAINMENT_SOFTWARE",
                sentiment=-0.7,
                safety_risk=False,
                summary="iDrive screen lags and reboots randomly"
            )
        ],
        "REV-04": [
            ExtractedAspect(
                review_id="REV-04",
                region="North America",
                category="CHASSIS_SUSPENSION",
                sentiment=-0.6,
                safety_risk=True,
                summary="Vibration through pedal during high-speed braking"
            )
        ]
    }
    return results.get(review.id, [])

@dataclass
class RankedRecommendation:
    category: str
    total_mentions: int
    affected_markets: List[str]
    priority_score: float
    recommended_action: str

def prioritization_agent(extracted_aspects: List[ExtractedAspect]) -> List[RankedRecommendation]:
    grouped = {}
    for asp in extracted_aspects:
        grouped.setdefault(asp.category, []).append(asp)

    ranked_list = []
    for cat, items in grouped.items():
        count = len(items)
        neg_sentiment_sum = sum(abs(x.sentiment) for x in items if x.sentiment < 0)
        safety_multiplier = 3.0 if any(x.safety_risk for x in items) else 1.0
        markets = list(set(x.region for x in items))

        score = round((count + neg_sentiment_sum) * safety_multiplier, 2)

        if cat == "INFOTAINMENT_SOFTWARE":
            action = "Deploy Over-The-Air (OTA) patch for head-unit stability."
        elif cat == "CHASSIS_SUSPENSION":
            action = "Issue Dealer Technical Bulletin (TSB) for brake inspection."
        elif cat == "CLIMATE_HVAC":
            action = "Calibrate blower airflow curves for hot-climate markets (GCC)."
        else:
            action = "Forward to regional quality assurance."

        ranked_list.append(RankedRecommendation(
            category=cat,
            total_mentions=count,
            affected_markets=markets,
            priority_score=score,
            recommended_action=action
        ))

    return sorted(ranked_list, key=lambda r: r.priority_score, reverse=True)

if __name__ == "__main__":
    dataset = [
        FeedbackItem(id="REV-01", region="Middle East", raw_text="الشاشة تعلق وتفصل أبل كاربلاي فجأة وأنا أسوق"),
        FeedbackItem(id="REV-02", region="Middle East", raw_text="المكيف جداً ضعيف في الظهر ويأخذ نص ساعة ليبرد"),
        FeedbackItem(id="REV-03", region="North America", raw_text="iDrive 8.5 display lags heavily and resets on startup"),
        FeedbackItem(id="REV-04", region="North America", raw_text="Severe brake pedal shudder when stopping from 70mph"),
    ]

    all_aspects = []
    for review in dataset:
        all_aspects.extend(analyze_review_agent(review))

    recommendations = prioritization_agent(all_aspects)

    print("=== BMW GLOBAL DECISION PLATFORM: PROTOTYPE OUTPUT ===\n")
    for rank, rec in enumerate(recommendations, start=1):
        print(f"Priority #{rank}: {rec.category} (Score: {rec.priority_score})")
        print(f" - Volume: {rec.total_mentions} feedback item(s) across {', '.join(rec.affected_markets)}")
        print(f" - Recommended Action: {rec.recommended_action}\n")
