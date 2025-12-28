import hashlib
import base64
from datetime import datetime
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

def create_canonical_message(
    file_name: str,
    file_hash: str,
    prev_hash: str,
    timestamp: str
) -> str:
    """
    Sistemde imzalanacak TEK canonical mesaj formatı.
    Format: file_name|file_hash|prev_hash|timestamp
    """
    return f"{file_name}|{file_hash}|{prev_hash}|{timestamp}"

def verify_signature(public_key_pem: str, message: str, signature_b64: str) -> bool:
    """
    RSA-SHA256 (PSS Padding) ile imza doğrular.
    test_integration.py ile ve Sprint 4 standartlarıyla tam uyumludur.
    """
    try:
        # 1. Public Key'i yükle
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode('utf-8')
        )
        
        # 2. İmzayı Base64'ten çöz
        signature_bytes = base64.b64decode(signature_b64)
        
        # 3. Doğrulama yap (RSA-PSS)
        public_key.verify(
            signature_bytes,
            message.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True # Hata fırlatmazsa imza geçerlidir
    except (InvalidSignature, ValueError, Exception):
        # İmza geçersizse, key bozuksa veya base64 hatası varsa False dön
        return False

def check_replay_protection(
    timestamp: str,
    window_minutes: int = 5
) -> bool:
    """
    Replay attack önleme: Mesajın zaman damgası (timestamp)
    sunucu zamanından çok eskiyse (varsayılan 5 dk) reddeder.
    """
    try:
        # ISO formatındaki string'i datetime objesine çevir
        msg_time = datetime.fromisoformat(timestamp)
        
        # Şu anki zaman ile farkı al (UTC)
        # Not: datetime.utcnow() eski sürümler içindir, modern python'da timezone.utc önerilir
        # ama proje tutarlılığı için senin kodunu koruyoruz.
        diff_minutes = (datetime.utcnow() - msg_time).total_seconds() / 60.0
        
        # Zaman farkı 0 ile pencere aralığı (5 dk) içindeyse geçerlidir
        return 0 <= diff_minutes < window_minutes
    except Exception:
        return False