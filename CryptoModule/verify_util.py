import hashlib
import base64
from datetime import datetime, timezone
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

def create_canonical_message(
    file_name: str,
    file_hash: str,
    timestamp: str
) -> str:
    """
    The SINGLE canonical message format to be signed in the system.
    Format: file_name|file_hash|timestamp
    
    Removed prev_hash to simplify 2-phase commit and avoid race conditions.
    """
    return f"{file_name}|{file_hash}|{timestamp}"

def verify_signature(public_key_pem: str, message: str, signature_b64: str) -> bool:
    try:
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode('utf-8')
        )
        signature = base64.b64decode(signature_b64)
        
        public_key.verify(
            signature,
            message.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except (InvalidSignature, ValueError, Exception) as e:
        print(f"Verification Error: {e}")
        return False

def check_replay_protection(timestamp: str, window_minutes: int = 5) -> bool:
    try:
        if timestamp.endswith('Z'):
            timestamp = timestamp[:-1] + '+00:00'
            
        msg_time = datetime.fromisoformat(timestamp)

        if msg_time.tzinfo is None:
            msg_time = msg_time.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        diff = now - msg_time
        diff_minutes = diff.total_seconds() / 60.0

        return -1 <= diff_minutes < window_minutes
    except Exception as e:
        print(f"Replay Check Error: {e}")
        return False