import hashlib
import os

class Hasher:
    """
    Deterministik SHA-256 hashleme işlemlerini yapan sınıf.
    Proje kapsamındaki 'Security Vault' yapısının temel taşıdır.
    """
    
    @staticmethod
    def get_hash(data: str) -> str:
        """Metin verisinin SHA-256 özetini döner."""
        if not isinstance(data, str):
            raise TypeError("Veri string formatında olmalıdır.")
        
        # Veriyi encode et ve hashle
        encoded_data = data.encode('utf-8')
        return hashlib.sha256(encoded_data).hexdigest()

    @staticmethod
    def get_file_hash(file_path: str) -> str:
        """Belirtilen dosyanın SHA-256 özetini döner."""
        sha256_hash = hashlib.sha256()
        
        if not os.path.exists(file_path):
            return "Dosya Bulunamadı"

        try:
            with open(file_path, "rb") as f:
                # Dosyayı parça parça oku (Büyük dosyalar için bellek dostu)
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            return f"Hata: {str(e)}"