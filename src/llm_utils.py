"""
LLM Utility Helpers — shared across all dynamic pipeline stages.

Provides a retry-aware Groq LLM call with round-robin API key rotation
that automatically reduces context on 413/rate-limit errors,
plus a consistent JSON parsing helper.
"""

import json
import os
import re
import time
import yaml
from typing import Optional, Dict, Any, List

# Global throttle: minimum seconds between LLM calls to avoid rate limits
_LLM_MIN_INTERVAL = 2.0
_last_llm_call_time = 0.0

# Round-robin key pool
_api_keys: List[str] = []
_current_key_index = 0
_exhausted_keys: set = set()  # Keys that hit rate limits
_keys_loaded = False

# Circuit breaker: only trips when ALL keys are exhausted
_circuit_open = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


def _load_api_keys() -> List[str]:
    """Load all Groq API keys from environment or .env file.
    
    Supports:
      - GROQ_API_KEY_1, GROQ_API_KEY_2, ... (numbered keys)
      - GROQ_API_KEY (single key fallback)
    """
    global _keys_loaded
    if _keys_loaded:
        return _api_keys

    keys = []

    # First, try loading .env file into environment
    try:
        from pathlib import Path
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split("=", 1)
                        v = v.strip("'").strip('"')
                        os.environ[k.strip()] = v
    except Exception:
        pass

    # Collect numbered keys: GROQ_API_KEY_1, GROQ_API_KEY_2, ...
    for i in range(1, 20):
        key = os.environ.get(f'GROQ_API_KEY_{i}', '').strip()
        if key:
            keys.append(key)

    # Fallback to single GROQ_API_KEY if no numbered keys found
    if not keys:
        single = os.environ.get('GROQ_API_KEY', '').strip()
        if single:
            keys.append(single)

    _api_keys.clear()
    _api_keys.extend(keys)
    _keys_loaded = True

    if len(keys) > 1:
        print(f"   [OK] Loaded {len(keys)} Groq API keys for round-robin rotation")
    return _api_keys


def _get_next_key() -> Optional[str]:
    """Get the next available API key via round-robin, skipping exhausted ones."""
    global _current_key_index, _circuit_open

    keys = _load_api_keys()
    if not keys:
        return None

    # Try each key once starting from current index
    for _ in range(len(keys)):
        key = keys[_current_key_index % len(keys)]
        _current_key_index = (_current_key_index + 1) % len(keys)
        if key not in _exhausted_keys:
            return key

    # All keys exhausted
    _circuit_open = True
    print(f"   [WARN] Circuit breaker OPEN -- all {len(keys)} API keys exhausted. Skipping LLM calls.")
    return None


def _mark_key_exhausted(key: str):
    """Mark an API key as rate-limited."""
    _exhausted_keys.add(key)
    remaining = len(_api_keys) - len(_exhausted_keys)
    if remaining > 0:
        print(f"   [WARN] Key ...{key[-6:]} rate-limited. Rotating to next key ({remaining} remaining)")


def _load_llm_config(config_path: str = 'config/config.yaml') -> Dict:
    """Load LLM config from YAML."""
    with open(config_path, 'r') as f:
        cfg = yaml.safe_load(f)
    return cfg.get('knowledge_bank', {})


def call_llm_with_retry(
    system_prompt: str,
    user_prompt: str,
    config_path: str = 'config/config.yaml',
    max_retries: int = 5,
    temperature: float = 0.4,
) -> Optional[str]:
    """Call Groq LLM with round-robin key rotation and automatic retry.

    On rate-limit errors, rotates to the next API key. On context-too-long
    errors, halves the prompt and retries. Circuit breaker trips only when
    ALL keys are exhausted.

    Returns the raw text response or None on failure.
    """
    if not GROQ_AVAILABLE:
        print("   [WARN] Groq SDK not available -- skipping LLM call")
        return None

    global _circuit_open, _last_llm_call_time
    if _circuit_open:
        return None

    keys = _load_api_keys()
    if not keys:
        print("   [WARN] No GROQ_API_KEY set -- skipping LLM call")
        return None

    kb_cfg = _load_llm_config(config_path)
    model = kb_cfg.get('llm_model', 'llama-3.3-70b-versatile')

    current_user_prompt = user_prompt

    for attempt in range(1, max_retries + 1):
        api_key = _get_next_key()
        if api_key is None:
            return None  # All keys exhausted, circuit open

        try:
            # Throttle: wait if needed to respect rate limits
            elapsed = time.time() - _last_llm_call_time
            if elapsed < _LLM_MIN_INTERVAL:
                time.sleep(_LLM_MIN_INTERVAL - elapsed)
            _last_llm_call_time = time.time()

            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": current_user_prompt},
                ],
                temperature=temperature,
                max_tokens=4096,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            err_str = str(e).lower()
            is_rate_limit = '429' in err_str or 'rate_limit' in err_str
            is_context_too_long = any(kw in err_str for kw in [
                '413', 'token', 'context_length', 'too long', 'request too large',
            ])

            if is_rate_limit:
                _mark_key_exhausted(api_key)
                # Don't count as an attempt — just rotate key and retry immediately
                continue

            if is_context_too_long and attempt < max_retries:
                half = len(current_user_prompt) // 2
                current_user_prompt = current_user_prompt[:half]
                print(f"   [WARN] LLM context too large -- reducing prompt to {half} chars (attempt {attempt + 1}/{max_retries})")
            elif attempt >= max_retries:
                print(f"   [WARN] LLM call failed: {str(e)[:120]}")
                return None

    return None


def parse_json_response(text: str) -> Optional[Any]:
    """Extract and parse JSON from an LLM response that may contain markdown fences."""
    if not text:
        return None
    # Strip markdown code fences
    cleaned = re.sub(r'```(?:json)?\s*', '', text)
    cleaned = cleaned.strip()
    # Try parsing directly
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    # Try extracting first JSON object/array
    for pattern in [r'\{[\s\S]*\}', r'\[[\s\S]*\]']:
        match = re.search(pattern, text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                continue
    return None
