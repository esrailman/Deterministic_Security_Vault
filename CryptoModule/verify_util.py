import hashlib
from datetime import datetime


def create_canonical_message(
    file_name: str,
    file_hash: str,
    prev_hash: str,
    timestamp: str
) -> str:
    """
    Sistemde imzalanacak TEK canonical mesaj formatı.
    Format:
    file_name|file_hash|prev_hash|timestamp
    """
    return f"{file_name}|{file_hash}|{prev_hash}|{timestamp}"


def verify_signature(
    public_key: str,
    message: str,
    signature: str
) -> bool:
    """
    Deterministic signature doğrulama (Sprint / PoC seviyesi).

    expected_signature = SHA256(public_key + message)
    """
    if not public_key or not signature:
        return False

    expected_sig = hashlib.sha256(
        (public_key + message).encode("utf-8")
    ).hexdigest()

    return expected_sig == signature


def check_replay_protection(
    timestamp: str,
    window_minutes: int = 5
) -> bool:
    """
    Replay attack önleme
    """
    try:
        msg_time = datetime.fromisoformat(timestamp)
        diff_minutes = (datetime.utcnow() - msg_time).total_seconds() / 60.0
        return 0 <= diff_minutes < window_minutes
    except Exception:
        return False
