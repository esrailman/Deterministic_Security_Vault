import hashlib
import base64
from datetime import datetime
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from datetime import timezone
def create_canonical_message(
    file_name: str,
    file_hash: str,
    prev_hash: str,
    timestamp: str
) -> str:
    """
    The SINGLE canonical message format to be signed in the system.
    Format: file_name|file_hash|prev_hash|timestamp
    """
    return f"{file_name}|{file_hash}|{prev_hash}|{timestamp}"

def verify_signature(public_key_pem: str, message: str, signature_b64: str) -> bool:
    """
    Verifies signature using RSA-SHA256 (PSS Padding).
    Fully compatible with test_integration.py and Sprint 4 standards.
    """
    try:
        # 1. Load Public Key
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode('utf-8')
        )
        
        # 2. Decode Signature from Base64
        signature_bytes = base64.b64decode(signature_b64)
        
        # 3. Perform Verification (RSA-PSS)
        public_key.verify(
            signature_bytes,
            message.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True # Signature is valid if no error is raised
    except (InvalidSignature, ValueError, Exception):
        # Return False if signature is invalid, key is corrupt, or base64 error
        return False

def check_replay_protection(timestamp: str, window_minutes: int = 5) -> bool:
    try:
        msg_time = datetime.fromisoformat(timestamp)

        now = datetime.now(timezone.utc)
        diff_minutes = (now - msg_time).total_seconds() / 60.0

        return 0 <= diff_minutes < window_minutes
    except Exception:
        return False