import streamlit as st
import os
import re

# ── Provider slug mapping ────────────────────────────────────────────────────
def _provider_slug(provider: str) -> str:
    """Maps provider display name to internal slug."""
    p = provider.lower()
    if "openai" in p or "chatgpt" in p:
        return "openai"
    if "deepseek" in p:
        return "deepseek"
    if "gemini" in p or "google" in p:
        return "gemini"
    return "openai"


# ── Environment variable names per provider ──────────────────────────────────
_ENV_VARS = {
    "openai":   ["OPENAI_API_KEY"],
    "deepseek": ["DEEPSEEK_API_KEY"],
    "gemini":   ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
}

# ── Session state key per provider ───────────────────────────────────────────
_SESSION_KEYS = {
    "openai":   "openai_api_key",
    "deepseek": "deepseek_api_key",
    "gemini":   "gemini_api_key",
}

# ── Known placeholder patterns (treated as "no key") ─────────────────────────
_PLACEHOLDER_PATTERNS = re.compile(
    r"^(your_|sk-your|sk-xxx|changeme|placeholder|example|insert|<|>|api[_-]?key[_-]?here)",
    re.IGNORECASE,
)

# ── Key format validators per provider ───────────────────────────────────────
_KEY_VALIDATORS = {
    # OpenAI: starts with sk-  (legacy) or sk-proj- (new project keys)
    "openai":   re.compile(r"^sk-"),
    # DeepSeek: starts with sk-
    "deepseek": re.compile(r"^sk-"),
    # Google / Gemini: starts with AIza  OR  bearer tokens (long hex strings)
    "gemini":   re.compile(r"^AIza|^[A-Za-z0-9_\-]{32,}"),
}


def _is_valid_key(slug: str, key: str) -> bool:
    """
    Returns True only if:
      1. The key is not empty / whitespace
      2. The key does not match a known placeholder pattern
      3. The key has a minimum reasonable length (at least 8 characters)
    """
    key = key.strip()
    if not key:
        return False
    if _PLACEHOLDER_PATTERNS.search(key):
        return False
    return len(key) >= 8


def check_provider_api_key(provider: str) -> bool:
    """Returns True if a *real* (non-placeholder, format-valid) API key exists."""
    slug = _provider_slug(provider)

    # 1. Check session-state key pasted via Settings UI
    sess_key = _SESSION_KEYS.get(slug, "")
    if sess_key and _is_valid_key(slug, st.session_state.get(sess_key, "")):
        return True

    # 2. Check environment variables
    for env_var in _ENV_VARS.get(slug, []):
        val = os.getenv(env_var, "")
        if _is_valid_key(slug, val):
            return True

    return False


def get_provider_api_key(provider: str) -> str:
    """Returns the validated API key (session state takes priority over env)."""
    slug = _provider_slug(provider)

    sess_key = _SESSION_KEYS.get(slug, "")
    if sess_key:
        val = st.session_state.get(sess_key, "").strip()
        if _is_valid_key(slug, val):
            return val

    for env_var in _ENV_VARS.get(slug, []):
        val = os.getenv(env_var, "").strip()
        if _is_valid_key(slug, val):
            return val

    return ""


def get_key_source(provider: str) -> str:
    """Returns a human-readable label for where the active key came from."""
    slug = _provider_slug(provider)

    sess_key = _SESSION_KEYS.get(slug, "")
    if sess_key and _is_valid_key(slug, st.session_state.get(sess_key, "")):
        return "UI Session (Settings page)"

    for env_var in _ENV_VARS.get(slug, []):
        val = os.getenv(env_var, "").strip()
        if _is_valid_key(slug, val):
            return f"Environment Variable ({env_var})"

    return "Not configured"


# ── Backwards-compat aliases ─────────────────────────────────────────────────
def check_openai_api_key():
    return check_provider_api_key("openai")


def get_openai_api_key():
    return get_provider_api_key("openai")


def clear_chat_history():
    """Clear chat messages in the session state."""
    st.session_state.messages = [{"role": "assistant", "content": "How can I help you today?"}]