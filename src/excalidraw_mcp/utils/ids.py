import random
import string


def gen_id(prefix: str = "") -> str:
    """Generate a unique element ID."""
    base = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return f"{prefix}{base}" if prefix else base
