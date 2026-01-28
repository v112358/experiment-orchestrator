"""
INTERACTION PATTERNS & LEARNED KNOWLEDGE

This file tracks:
1. Known interaction patterns between experiment types
2. Learnings from past experiments
3. Confidence scores for different combinations

This gets updated as the system learns from real experiments.
"""

# ============================================================================
# KNOWN INTERACTION PATTERNS
# ============================================================================

"""
These are patterns we expect about which experiment types interact with each other.
As experiments accumulate, we add empirical observations here.
"""

INTERACTION_PATTERNS = {
    "low_risk_combinations": [
        {
            "exp_type_1": "Button/CTA modification",
            "exp_type_2": "Product description change",
            "reason": "One affects friction (button placement/clarity), other affects clarity (description). Different user decision points.",
            "interaction_risk": 0.1,
            "confidence": "high",
        },
        {
            "exp_type_1": "Search/discovery improvement",
            "exp_type_2": "Checkout simplification",
            "reason": "Affect different funnel stages (discovery vs. purchase). Orthogonal.",
            "interaction_risk": 0.15,
            "confidence": "high",
        },
        {
            "exp_type_1": "Product reviews display",
            "exp_type_2": "Trust badges addition",
            "reason": "Both build confidence but through different trust signals.",
            "interaction_risk": 0.2,
            "confidence": "medium",
        },
    ],
    
    "medium_risk_combinations": [
        {
            "exp_type_1": "Limited time offer message",
            "exp_type_2": "Product copy rewrite",
            "reason": "Both compete for user attention. Urgency message can drown out product benefits.",
            "interaction_risk": 0.4,
            "confidence": "medium",
            "mitigation": "Consider sequential testing or user segmentation",
        },
        {
            "exp_type_1": "One-click checkout",
            "exp_type_2": "Upsell bundle recommendations",
            "reason": "Skipping steps might bypass upsell opportunities.",
            "interaction_risk": 0.35,
            "confidence": "medium",
            "mitigation": "Ensure upsells are part of the streamlined flow",
        },
    ],
    
    "high_risk_combinations": [
        {
            "exp_type_1": "Form field reduction",
            "exp_type_2": "Checkout page redesign",
            "reason": "Same element modified by two experiments = results confounded.",
            "interaction_risk": 0.85,
            "confidence": "high",
            "mitigation": "MUST run sequentially",
        },
        {
            "exp_type_1": "Countdown timer",
            "exp_type_2": "'Only X left' inventory message",
            "reason": "Both create urgency. Can't tell which one worked.",
            "interaction_risk": 0.9,
            "confidence": "high",
            "mitigation": "MUST run sequentially or as variants in same test",
        },
        {
            "exp_type_1": "Product description improvement",
            "exp_type_2": "Product specs layout redesign",
            "reason": "Both improve clarity on same element. Results unclear.",
            "interaction_risk": 0.8,
            "confidence": "high",
            "mitigation": "MUST run sequentially",
        },
    ],
}

# ============================================================================
# METRIC RELATIONSHIP NOTES
# ============================================================================

"""
Understanding how metrics relate helps identify hidden conflicts.
If two experiments both claim to improve the same metric through different paths,
that's usually fine. But if they're measuring the same metric, be careful.
"""

METRIC_RELATIONSHIPS = {
    "conversion_rate_and_cart_abandonment": {
        "relationship": "Inverse (mostly)",
        "note": "If cart abandonment goes down, conversion typically goes up",
        "confounding_risk": "Medium - could measure same thing from different angles",
    },
    
    "conversion_rate_and_aov": {
        "relationship": "Often uncorrelated or negatively correlated",
        "note": "Increasing conversion doesn't mean higher spending per order",
        "confounding_risk": "Low - can optimize both independently",
    },
    
    "click_through_rate_and_conversion_rate": {
        "relationship": "Positive correlation (usually)",
        "note": "If CTR goes up on checkout, conversion likely increases",
        "confounding_risk": "Medium - related but not identical",
    },
    
    "bounce_rate_and_conversion_rate": {
        "relationship": "Negative correlation",
        "note": "Lower bounce = more people go deeper = more conversions",
        "confounding_risk": "Low - measure different things",
    },
}

# ============================================================================
# LEARNED PATTERNS (Updated as experiments run)
# ============================================================================

LEARNED_PATTERNS = {
    "experiment_count": 6,  # Total experiments run so far
    "patterns": {
        "homepage_experiments": {
            "count": 4,
            "observation": "Homepage experiments often interfere with each other on CTR metric",
            "confidence": "medium",
        },
        "friction_vs_clarity": {
            "count": 0,
            "observation": "Not yet observed in real experiments",
            "confidence": "low",
        },
    },
    "recommendations": {
        "phase": "cold_start",
        "message": "Early in experimentation. Recommendations are conservative. As more experiments run, patterns will become clearer.",
    },
}

# ============================================================================
# FUTURE LEARNINGS
# ============================================================================

"""
As the system runs more experiments and collects results, we can add:

- Empirical interaction effect sizes
- Metric correlation patterns specific to this company
- Time-of-month effects
- Seasonal patterns
- Experiment success rates by type
"""
