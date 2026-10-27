import os
from dataclasses import dataclass
from typing import List, Literal
from openai import OpenAI
from pydantic import BaseModel, Field

# =====================================================================
# 1. Schemas & Volkswagen Group Taxonomy
# =====================================================================

TAXONOMY = [
    "INFOTAINMENT_MIB_SOFTWARE",
    "CLIMATE_HVAC",
    "CHASSIS_SUSPENSION",
    "POWERTRAIN_MEB_BATTERY",
    "DEALER_SERVICE"
]

class FeedbackItem(BaseModel):
    id: str
    region: Literal["Middle East", "North America", "Europe"]
    raw_text: str

class ExtractedAspect(BaseModel):
    category: Literal[
        "INFOTAINMENT_MIB_SOFTWARE",
        "CLIMATE_HVAC",
        "CHASSIS_SUSPENSION",
        "POWERTRAIN_MEB_BATTERY",
        "DEALER_SERVICE"
    ] = Field(description="Must match Volkswagen global component taxonomy.")
    sentiment: float = Field(
        ge=-1.0, 
        le=1.0, 
        description="-1.0 (severe failure/defect) to +1.0 (delight/praise)."
    )
    safety_risk: bool = Field(
        description="True if involves braking, steering, battery thermal, or ADAS/airbag faults."
    )
    summary: str = Field(description="Brief English summary of the issue.")

class LLMExtractionResponse(BaseModel):
    aspects: List[ExtractedAspect]

# =====================================================================
# 2. Volkswagen Quality AI Agent Call
# =====================================================================

client = OpenAI()

SYSTEM_PROMPT = f"""
You are an expert Automotive Quality AI Engineer at Volkswagen Group.
Your task is to analyze incoming customer feedback across all markets in any language 
(including Modern Standard Arabic, regional Arabic dialects, German, and English).

For each issue or theme found in the review:
1. Map the component to Volkswagen's official taxonomy: {TAXONOMY}.
2. Assign a sentiment score from -1.0 to +1.0.
3. Determine if the issue presents an immediate or potential vehicle safety risk.
4. Provide a concise English summary.

If the customer mentions multiple separate issues, extract each as a distinct aspect.
"""

def analyze_review_with_llm(review: FeedbackItem) -> List[ExtractedAspect]:
    """
    Calls OpenAI using Structured Outputs to parse multilingual customer text into VW taxonomy.
    """
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Market Region: {review.region}\nRaw Customer Feedback: {review.raw_text}"}
            ],
            response_format=LLMExtractionResponse,
            temperature=0.0
        )
        return completion.choices[0].message.parsed.aspects
    except Exception as e:
        print(f"Error calling LLM for {review.id}: {e}")
        return []

# =====================================================================
# 3. Prioritization & Action Routing
# =====================================================================

@dataclass
class RankedRecommendation:
    category: str
    total_mentions: int
    affected_markets: List[str]
    priority_score: float
    recommended_action: str

def prioritization_agent(
    feedback_aspect_pairs: List[tuple[FeedbackItem, ExtractedAspect]]
) -> List[RankedRecommendation]:
    grouped = {}
    for review, aspect in feedback_aspect_pairs:
        grouped.setdefault(aspect.category, []).append((review, aspect))

    ranked_list = []
    for cat, items in grouped.items():
        count = len(items)
        neg_sentiment_sum = sum(abs(asp.sentiment) for _, asp in items if asp.sentiment < 0)
        safety_multiplier = 3.0 if any(asp.safety_risk for _, asp in items) else 1.0
        markets = list(set(rev.region for rev, _ in items))

        # Scoring Formula: (Volume + Severity) * Safety Multiplier
        score = round((count + neg_sentiment_sum) * safety_multiplier, 2)

        # Operational decision routing tailored to Volkswagen operations
        if cat == "INFOTAINMENT_MIB_SOFTWARE":
            action = "Deploy Over-The-Air (OTA) update for MIB / ID.Software digital cockpit stability."
        elif cat == "CHASSIS_SUSPENSION":
            action = "Issue Dealer Technical Bulletin (TSB) for mechanical/braking inspection."
        elif cat == "CLIMATE_HVAC":
            action = "Recalibrate Climatronic thermal curves for hot-climate export regions (e.g. GCC)."
        else:
            action = "Forward diagnostic report to regional VW Quality Assurance."

        ranked_list.append(RankedRecommendation(
            category=cat,
            total_mentions=count,
            affected_markets=markets,
            priority_score=score,
            recommended_action=action
        ))

    return sorted(ranked_list, key=lambda r: r.priority_score, reverse=True)

# =====================================================================
# 4. Pipeline Execution
# =====================================================================

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY environment variable to run live calls.")
        exit(1)

    # Real-world test examples including Arabic dialects and VW-specific terms
    dataset = [
        FeedbackItem(
            id="REV-01", 
            region="Middle East", 
            raw_text="شاشة الميديا بتعلق كتير والوايرلس كاربلاي بيفصل كل شوية وأنا سايق على الطريق"
        ),
        FeedbackItem(
            id="REV-02", 
            region="Middle East", 
            raw_text="تكييف الكليماترونيك ضعيف جدا في الصيف ودرجة الحرارة برا 45، العربية بتاخد نص ساعة عشان تبرد"
        ),
        FeedbackItem(
            id="REV-03", 
            region="North America", 
            raw_text="The MIB3 infotainment screen went completely black and restarted during highway navigation."
        ),
        FeedbackItem(
            id="REV-04", 
            region="North America", 
            raw_text="Violent brake pedal vibration and pulsing when slowing down from freeway speeds."
        ),
    ]

    print("Running live LLM extraction across multilingual dataset...\n")
    processed_aspects = []
    
    for review in dataset:
        aspects = analyze_review_with_llm(review)
        for asp in aspects:
            print(f"[{review.id} | {review.region}] -> Category: {asp.category} | Sentiment: {asp.sentiment} | Safety Risk: {asp.safety_risk}")
            print(f"   Summary: {asp.summary}\n")
            processed_aspects.append((review, asp))

    recommendations = prioritization_agent(processed_aspects)

    print("=" * 65)
    print("=== VOLKSWAGEN GROUP DECISION PLATFORM: EXECUTIVE REPORT ===")
    print("=" * 65 + "\n")
    for rank, rec in enumerate(recommendations, start=1):
        print(f"Priority #{rank}: {rec.category} (Score: {rec.priority_score})")
        print(f" - Volume: {rec.total_mentions} review(s) across {', '.join(rec.affected_markets)}")
        print(f" - Recommended Action: {rec.recommended_action}\n")
