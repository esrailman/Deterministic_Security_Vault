import hashlib
import os
import json
from datetime import datetime
from typing import List, Optional
from CryptoModule.hash_util import Hasher

class SecurityVaultManager:
    def __init__(self):
        self.chain = []

    
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
