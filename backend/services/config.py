import os


def _flag(name: str, default: str = "false") -> bool:
    return (os.getenv(name, default) or "").strip().lower() in {"1", "true", "yes", "on"}


# Behavior flags
AI_IMAGE_FIRST = _flag("AI_IMAGE_FIRST", "true")
AI_DISABLE_RULES = _flag("AI_DISABLE_RULES", "false")
AI_REQUIRE = _flag("AI_REQUIRE", "false")


# Tier-based model configuration
# Free tier: Rate-limited OpenAI GPT-4o-mini
# Pro+ tiers: Unlimited GPT-4o (smarter, paid)
TIER_MODELS = {
    "FREE": {
        "llm_model": "gpt-4o-mini",           # Fast, reliable AI
        "use_local_llm": False,               # Disabled (too slow/unreliable)
        "local_llm_model": None,              # No local model
        "daily_ai_quota": 20,                 # 20 AI requests per day
        "enable_images": False,               # DALL-E disabled
        "enable_voice": False,                # Disable voice input for free users
    },
    "PRO": {
        "llm_model": "gpt-4o",                # Smarter model via OpenAI
        "use_local_llm": False,               # Use OpenAI, not local
        "local_llm_model": None,
        "enable_images": False,               # DALL-E disabled
        "enable_voice": True,                 # Enable voice input
    },
    "TEAM": {
        "llm_model": "gpt-4o",                # Smarter model via OpenAI
        "use_local_llm": False,               # Use OpenAI, not local
        "local_llm_model": None,
        "enable_images": False,               # DALL-E disabled
        "enable_voice": True,                 # Enable voice input
    },
    "ENTERPRISE": {
        "llm_model": "gpt-4o",                # Smarter model via OpenAI
        "use_local_llm": False,               # Use OpenAI, not local
        "local_llm_model": None,
        "enable_images": False,               # DALL-E disabled
        "enable_voice": True,                 # Enable voice input
    },
}


def get_tier_config(tier: str) -> dict:
    """Get configuration for a specific subscription tier"""
    return TIER_MODELS.get(tier, TIER_MODELS["FREE"])

