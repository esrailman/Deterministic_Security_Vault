import hashlib
import os
import json
from datetime import datetime
from typing import List, Optional

class Hasher:
    @staticmethod
    def get_hash(data: str) -> str:
        if not isinstance(data, str):
            raise TypeError("Veri string formatında olmalıdır.")
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    @staticmethod
    def get_file_hash(file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        if not os.path.exists(file_path): return "Dosya Bulunamadı"
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e: return f"Hata: {str(e)}"

class SecurityVaultManager:
    def __init__(self):
        self.chain = []

    @staticmethod
    def verify_signature(public_key: str, message: str, signature: str) -> bool:
        if not public_key or not signature: return False
        expected_sig = hashlib.sha256((public_key + message).encode()).hexdigest()
        return expected_sig == signature

    @staticmethod
    def create_canonical_message(file_name: str, file_hash: str, prev_hash: str) -> str:
        timestamp = datetime.utcnow().isoformat()
        return f"{file_name}|{file_hash}|{prev_hash}|{timestamp}"

    @staticmethod
    def check_replay_protection(timestamp: str, window_minutes: int = 5) -> bool:
        try:
            msg_time = datetime.fromisoformat(timestamp)
            diff = (datetime.utcnow() - msg_time).total_seconds() / 60
            return 0 <= diff < window_minutes
        except: return False

    @staticmethod
    def build_merkle_root(hash_list: List[str]) -> str:
        if not hash_list: return ""
        if len(hash_list) == 1: return hash_list[0]
        
        new_hashes = []
        for i in range(0, len(hash_list), 2):
            left = hash_list[i]
            right = hash_list[i+1] if i+1 < len(hash_list) else left
            combined = hashlib.sha256((left + right).encode()).hexdigest()
            new_hashes.append(combined)
        
        return SecurityVaultManager.build_merkle_root(new_hashes)

    def add_to_chain(self, data: str):
        prev_hash = self.chain[-1] if self.chain else "0" * 64
        current_hash = Hasher.get_hash(data + prev_hash)
        self.chain.append(current_hash)
        return current_hash

if __name__ == "__main__":
    vault = SecurityVaultManager()
    
    msg = vault.create_canonical_message("belge.pdf", "hash123", "000...")
    
    is_valid = vault.verify_signature("pub_key_ahmet", msg, 
                                     hashlib.sha256(("pub_key_ahmet" + msg).encode()).hexdigest())
    print(f"İmza Doğrulama: {is_valid}")
    
    h1 = vault.add_to_chain("Dosya 1 İçeriği")
    h2 = vault.add_to_chain("Dosya 2 İçeriği")
    root = vault.build_merkle_root([h1, h2])
    print(f"Kasa Merkle Root: {root}")