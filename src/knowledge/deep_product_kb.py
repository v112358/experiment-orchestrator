"""
DEEP PRODUCT KNOWLEDGE BASE - E-Commerce Platform

This document contains detailed information about the product, its mechanics,
funnel, metrics, and known interaction patterns. Used by the AI to reason about
experiment conflicts and causal mechanisms.
"""

# ============================================================================
# PLATFORM OVERVIEW
# ============================================================================

PLATFORM = {
    "name": "TechStore - E-commerce Platform",
    "description": "Online marketplace for tech products and electronics",
    "user_types": ["browsers", "repeat_buyers", "power_users"],
    "avg_session_duration": "8.5 minutes",
    "avg_monthly_users": "500K",
}

# ============================================================================
# FUNNEL FLOW
# ============================================================================

"""
User Journey Through Platform:

1. DISCOVERY
   Entry: Homepage, Google Search, Email
   Goal: Get users to explore products
   
2. EXPLORATION
   → Homepage → Product Grid → Product Page
   Goal: Help users find relevant products
   
3. CONSIDERATION
   Product Page (reviews, specs, comparisons)
   Goal: Build confidence in purchase decision
   
4. PURCHASE
   → Add to Cart → Checkout Flow → Order Confirmation
   Goal: Reduce friction, increase conversion
   
5. POST-PURCHASE
   Email follow-ups, reviews encouragement
   Goal: Build loyalty, repeat purchases
"""

# ============================================================================
# SURFACES & THEIR ROLE
# ============================================================================

SURFACES = {
    "homepage": {
        "role": "Discovery & Entry Point",
        "funnel_stage": "Discovery",
        "key_elements": {
            "hero_banner": "Main visual + CTA, above fold",
            "product_grid": "Featured/recommended products",
            "navigation": "Category menu, search bar",
            "trust_signals": "Reviews, badges, social proof",
        },
        "primary_metrics_affected": ["pageviews", "ctr", "bounce_rate"],
        "description": "First impression. Sets tone for entire session.",
    },
    
    "product_page": {
        "role": "Consideration & Decision Making",
        "funnel_stage": "Consideration",
        "key_elements": {
            "product_images": "Gallery of product photos",
            "product_info": "Name, price, specs",
            "reviews_section": "Customer ratings and written reviews",
            "add_to_cart": "Main CTA button",
            "related_products": "Cross-sell recommendations",
        },
        "primary_metrics_affected": ["conversion_rate", "aov", "reviews_helpful"],
        "description": "Where purchase decisions happen. High-intent traffic.",
    },
    
    "checkout": {
        "role": "Transaction Completion",
        "funnel_stage": "Purchase",
        "key_elements": {
            "cart_summary": "Review items, quantities",
            "shipping_options": "Delivery method, speed/cost tradeoff",
            "payment_form": "Credit card, PayPal, etc.",
            "order_confirmation": "Success page, order details",
        },
        "primary_metrics_affected": ["conversion_rate", "cart_abandonment", "aov"],
        "description": "Final barrier to conversion. Every friction point matters.",
    },
    
    "email": {
        "role": "Re-engagement & Retention",
        "funnel_stage": "Post-Purchase",
        "key_elements": {
            "welcome_series": "Onboarding for new users",
            "promotional": "Sales, new products, discounts",
            "post_purchase": "Order confirmation, reviews request, upsell",
        },
        "primary_metrics_affected": ["open_rate", "click_rate", "repeat_purchase_rate"],
        "description": "Drives re-engagement and lifetime value.",
    },
}

# ============================================================================
# METRICS & THEIR MEANING
# ============================================================================

METRICS_DEEP = {
    "click_through_rate": {
        "definition": "Clicks / Impressions on a specific element",
        "what_it_measures": "How compelling/visible is the CTA?",
        "affected_by": ["visibility", "clarity", "urgency", "placement"],
        "affected_surfaces": ["homepage", "email"],
    },
    
    "bounce_rate": {
        "definition": "Single-page sessions / All sessions",
        "what_it_measures": "Is content relevant? Did page load? Is layout confusing?",
        "affected_by": ["page_load_time", "relevance", "layout", "value_prop_clarity"],
        "affected_surfaces": ["homepage"],
    },
    
    "conversion_rate": {
        "definition": "Completed purchases / Visitors",
        "what_it_measures": "End-to-end effectiveness. All friction points combined.",
        "affected_by": ["trust", "friction", "clarity", "urgency", "price", "product_quality"],
        "affected_surfaces": ["homepage", "product_page", "checkout", "email"],
        "note": "Most important metric. High variance due to many factors.",
    },
    
    "cart_abandonment": {
        "definition": "Abandoned carts / Carts created",
        "what_it_measures": "Is checkout too complicated? Unexpected costs? Trust issues?",
        "affected_by": ["shipping_cost_clarity", "form_complexity", "payment_options", "trust_signals"],
        "affected_surfaces": ["checkout"],
    },
    
    "average_order_value": {
        "definition": "Total revenue / Number of orders",
        "what_it_measures": "Are we upselling? Are people buying more items?",
        "affected_by": ["product_recommendations", "bundle_offers", "perceived_value"],
        "affected_surfaces": ["product_page", "checkout"],
    },
    
    "reviews_helpful": {
        "definition": "Helpful votes / Total review votes",
        "what_it_measures": "Are reviews actually helping people decide?",
        "affected_by": ["review_formatting", "review_authenticity", "sorting_algorithm"],
        "affected_surfaces": ["product_page"],
    },
    
    "email_open_rate": {
        "definition": "Opens / Sends",
        "what_it_measures": "Is subject line compelling?",
        "affected_by": ["subject_line", "send_time", "sender_reputation"],
        "affected_surfaces": ["email"],
    },
    
    "repeat_purchase_rate": {
        "definition": "Users who made 2+ purchases / All users",
        "what_it_measures": "Long-term satisfaction & loyalty",
        "affected_by": ["product_quality", "customer_service", "post_purchase_experience"],
        "affected_surfaces": ["email"],
    },
}

# ============================================================================
# SURFACE-SPECIFIC NOTES
# ============================================================================

SURFACE_NOTES = {
    "homepage": {
        "user_intent": "Exploring, not yet committed",
        "time_on_page": "15-30 seconds",
        "key_challenge": "High bounce rate - must be compelling",
        "experiment_notes": "Changes here have broad reach but small individual effects",
    },
    
    "product_page": {
        "user_intent": "Evaluating purchase decision",
        "time_on_page": "3-5 minutes",
        "key_challenge": "Lots of info to process. Don't overwhelm.",
        "experiment_notes": "Changes here have direct impact on conversion - high-leverage",
    },
    
    "checkout": {
        "user_intent": "Committed to purchase, wants to complete quickly",
        "time_on_page": "1-3 minutes",
        "key_challenge": "Every friction point is a drop-off point",
        "experiment_notes": "Any friction removal here is high-impact. Test conservatively.",
    },
    
    "email": {
        "user_intent": "Varies (browsing emails in inbox)",
        "time_on_page": "N/A",
        "key_challenge": "Getting them to click through",
        "experiment_notes": "Subject line changes have huge variance. A/B test rigorously.",
    },
}

# ============================================================================
# METRIC INTERACTION NOTES
# ============================================================================

"""
These are things we know about how metrics relate to each other.
Important for understanding if experiments on different metrics interfere.
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
