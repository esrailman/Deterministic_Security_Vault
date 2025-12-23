"""
TODO:
- verify_signature(public_key: str, message: str, signature: str) -> bool
- optional: generate_keypair()
- optional: canonical_message_format (backend ile ortak format)
- optional: replay protection / timestamp binding

Backend integration notes:
- Backend /register içinde:
  - message = f"{file_name}|{file_hash}|{prev_hash}|{timestamp}"
  - signature doğrulaması verify_signature(...) ile yapılacak
"""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
import base64

def verify_signature(public_key_pem: str, message: str, signature_b64: str) -> bool:
    """
    Verilen mesajın imzasını doğrular.
    
    Args:
        public_key_pem (str): PEM formatında public key string'i.
        message (str): İmzalanmış orijinal mesaj.
        signature_b64 (str): Base64 encode edilmiş imza string'i.
        
    Returns:
        bool: İmza geçerliyse True, değilse False.
    """
    try:
        if not public_key_pem or not signature_b64:
            return False

        # Public Key'i yükle
        public_key = serialization.load_pem_public_key(public_key_pem.encode('utf-8'))
        
        # İmzayı decode et (Base64 -> bytes)
        signature = base64.b64decode(signature_b64)
        
        # Mesajı encode et
        message_bytes = message.encode('utf-8')
        
        # Doğrulama işlemi (PSS padding ve SHA256)
        public_key.verify(
            signature,
            message_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except (InvalidSignature, ValueError, Exception):
        # Hata detaylarını gizle ve sadece başarısız olduğunu dön
        return False