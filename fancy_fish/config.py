import os
from typing import Optional

try:
    # If the user has python-dotenv installed in local development, allow .env files
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    # dotenv is optional; continue if it's not available
    pass


def _required_env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(
            f"Missing required environment variable {name}. "
            "In GitHub Codespaces, add it under Settings → Codespaces → Secrets (Repository secrets), "
            "or set it locally (e.g. in your shell or a .env file for development)."
        )
    return val


# Default secret/env var names — change these if you used different names in Codespaces
GROQ_API_KEY: str = _required_env("GROQ_API_KEY")
OPENAI_API_KEY: str = _required_env("OPENAI_API_KEY")
GEMINI_API_KEY: str = _required_env("GEMINI_API_KEY")


def get_optional(key: str) -> Optional[str]:
    """Return an optional secret without raising.

    Use this if a secret is optional in your environment.
    """
    return os.getenv(key)
