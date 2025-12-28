import hashlib
import os

class Hasher:
    """
    Class performing deterministic SHA-256 hashing operations.
    Cornerstone of the 'Security Vault' structure within the project scope.
    """
    
    @staticmethod
    def get_hash(data: str) -> str:
        """Returns the SHA-256 digest of text data."""
        if not isinstance(data, str):
            raise TypeError("Data must be in string format.")
        
        # Encode and hash data
        encoded_data = data.encode('utf-8')
        return hashlib.sha256(encoded_data).hexdigest()

    @staticmethod
    def get_file_hash(file_path: str) -> str:
        """Returns the SHA-256 digest of the specified file."""
        sha256_hash = hashlib.sha256()
        
        if not os.path.exists(file_path):
            return "File Not Found"

        try:
            with open(file_path, "rb") as f:
                # Read file in chunks (memory friendly for large files)
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            return f"Error: {str(e)}"