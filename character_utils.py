from pathlib import Path

CHARACTER_IMAGE_MAP = {
    "sarai": "sarai.png",
    "tech_cofounder": "tech_cofounder.png",
    "advisor": "advisor.png",
    "marketing_cofounder": "marketing_cofounder.png",
    "vc": "vc.png",
    "coach": "coach.png",
    "therapist_1": "therapist_analytical.png",
    "therapist_2": "therapist_empathic.png",
    "therapist_3": "therapist_skeptical.png",
}

CHARACTER_AVATARS = {
    "sarai": "🧠",
    "tech_cofounder": "👨‍💻",
    "advisor": "🎯",
    "marketing_cofounder": "📈",
    "vc": "💰",
    "coach": "🏆",
    "therapist_1": "👥",
    "therapist_2": "👥",
    "therapist_3": "👥",
}

ASSET_ROOT = Path("Documents") / "assets" / "characters"


def get_character_image_path(character_name: str) -> str:
    """Return a relative path to the character portrait."""
    normalized = character_name.lower()
    filename = CHARACTER_IMAGE_MAP.get(normalized, "sarai.png")
    return str(ASSET_ROOT / filename)


def normalize_character_key(character_name: str) -> str:
    """Normalize a character identifier for registry lookups."""
    if character_name.startswith("therapist_"):
        return "therapist_customers"
    return character_name.lower().replace(" ", "_")


def get_character_avatar(character_name: str) -> str:
    """Return an emoji avatar for a character."""
    return CHARACTER_AVATARS.get(character_name.lower(), "🤖")

