"""
Product Knowledge Base - Generic E-commerce

Defines the product structure: surfaces, screens, and metrics.
This helps the agent understand what experiments might interfere.
"""

class Surface:
    """A major area of the product (e.g., Homepage, Checkout)"""
    
    def __init__(self, name, description, screens, key_metrics):
        self.name = name
        self.description = description
        self.screens = screens  # List of screen IDs in this surface
        self.key_metrics = key_metrics  # Metrics affected by this surface


class Screen:
    """A specific page or component (e.g., Hero Section, Payment Form)"""
    
    def __init__(self, id, name, surface_id, description):
        self.id = id
        self.name = name
        self.surface_id = surface_id  # Which surface this belongs to
        self.description = description


class Metric:
    """A measurable outcome (e.g., Conversion Rate, AOV)"""
    
    def __init__(self, name, definition, surfaces_impacted):
        self.name = name
        self.definition = definition
        self.surfaces_impacted = surfaces_impacted  # Which surfaces affect this metric


# ============================================================================
# GENERIC E-COMMERCE PRODUCT STRUCTURE
# ============================================================================

SURFACES = {
    "homepage": Surface(
        name="Homepage",
        description="Main landing page users see first",
        screens=["hero_section", "product_grid", "navigation"],
        key_metrics=["click_through_rate", "bounce_rate", "pageviews"]
    ),
    "product_page": Surface(
        name="Product Page",
        description="Individual product detail page",
        screens=["product_info", "reviews_section", "add_to_cart_button"],
        key_metrics=["conversion_rate", "aov", "reviews_helpful"]
    ),
    "checkout": Surface(
        name="Checkout Flow",
        description="Multi-step purchase process",
        screens=["cart_summary", "shipping_options", "payment_form", "confirmation"],
        key_metrics=["conversion_rate", "cart_abandonment", "aov"]
    ),
    "email": Surface(
        name="Email",
        description="Email campaigns and notifications",
        screens=["welcome_series", "promotional", "post_purchase"],
        key_metrics=["open_rate", "click_rate", "conversion_rate"]
    ),
}

SCREENS = {
    # Homepage screens
    "hero_section": Screen("hero_section", "Hero Section", "homepage", 
                          "Main banner with headline and CTA"),
    "product_grid": Screen("product_grid", "Product Grid", "homepage",
                          "Listing of products with images and prices"),
    "navigation": Screen("navigation", "Navigation", "homepage",
                        "Top nav menu and search"),
    
    # Product page screens
    "product_info": Screen("product_info", "Product Info", "product_page",
                          "Description, images, price, specifications"),
    "reviews_section": Screen("reviews_section", "Reviews", "product_page",
                             "Customer reviews and ratings"),
    "add_to_cart_button": Screen("add_to_cart_button", "Add to Cart Button", "product_page",
                                "Button to add item to shopping cart"),
    
    # Checkout screens
    "cart_summary": Screen("cart_summary", "Cart Summary", "checkout",
                          "Review items and quantities"),
    "shipping_options": Screen("shipping_options", "Shipping Options", "checkout",
                              "Choose shipping method"),
    "payment_form": Screen("payment_form", "Payment Form", "checkout",
                          "Enter payment information"),
    "confirmation": Screen("confirmation", "Confirmation", "checkout",
                          "Order confirmation page"),
    
    # Email screens
    "welcome_series": Screen("welcome_series", "Welcome Series", "email",
                            "Automated emails for new subscribers"),
    "promotional": Screen("promotional", "Promotional", "email",
                         "Marketing campaigns"),
    "post_purchase": Screen("post_purchase", "Post-Purchase", "email",
                           "Follow-up and upsell emails"),
}

METRICS = {
    "click_through_rate": Metric(
        "Click-Through Rate",
        "Clicks / Impressions",
        ["homepage", "email"]
    ),
    "conversion_rate": Metric(
        "Conversion Rate",
        "Purchases / Sessions",
        ["homepage", "product_page", "checkout", "email"]
    ),
    "aov": Metric(
        "Average Order Value",
        "Total Revenue / Orders",
        ["product_page", "checkout"]
    ),
    "cart_abandonment": Metric(
        "Cart Abandonment Rate",
        "Abandoned Carts / Carts Created",
        ["checkout"]
    ),
    "bounce_rate": Metric(
        "Bounce Rate",
        "Single-Page Sessions / Sessions",
        ["homepage"]
    ),
    "pageviews": Metric(
        "Pageviews",
        "Total page views",
        ["homepage"]
    ),
    "open_rate": Metric(
        "Email Open Rate",
        "Opens / Sends",
        ["email"]
    ),
    "email_click_rate": Metric(
        "Email Click Rate",
        "Clicks / Opens",
        ["email"]
    ),
    "reviews_helpful": Metric(
        "Reviews Helpfulness",
        "Helpful votes / Total votes",
        ["product_page"]
    ),
}


def get_surface(surface_id):
    """Get a surface by ID"""
    return SURFACES.get(surface_id)


def get_screen(screen_id):
    """Get a screen by ID"""
    return SCREENS.get(screen_id)


def get_metric(metric_name):
    """Get a metric by name"""
    return METRICS.get(metric_name)


def get_all_surfaces():
    """Return all surfaces as readable text for LLM"""
    result = []
    for surface_id, surface in SURFACES.items():
        result.append(f"- {surface.name} ({surface_id}): {surface.description}")
        result.append(f"  Screens: {', '.join(surface.screens)}")
        result.append(f"  Key metrics: {', '.join(surface.key_metrics)}")
    return "\n".join(result)


def get_all_metrics():
    """Return all metrics as readable text for LLM"""
    result = []
    for metric_name, metric in METRICS.items():
        result.append(f"- {metric.name}: {metric.definition}")
        result.append(f"  Impacted by: {', '.join(metric.surfaces_impacted)}")
    return "\n".join(result)
