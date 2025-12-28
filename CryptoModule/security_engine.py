import hashlib
import os
import json
from datetime import datetime
from typing import List, Optional, Dict  # Dict eklendi
from CryptoModule.hash_util import Hasher

class SecurityVaultManager:
    def __init__(self):
        self.chain = []

    # --- EXISTING FUNCTIONS (UNCHANGED) ---
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

    #
    
    @staticmethod
    def get_merkle_proof(hashes: List[str], target_hash: str) -> List[Dict]:
        """
        Generates a Merkle Proof (proof path) for a specified hash value.
        """
        if target_hash not in hashes:
            return []

        proof = []
        try:
            idx = hashes.index(target_hash)
        except ValueError:
            return []

        temp_hashes = hashes.copy()

        while len(temp_hashes) > 1:
            new_level = []
            for i in range(0, len(temp_hashes), 2):
                left = temp_hashes[i]
                right = temp_hashes[i+1] if i+1 < len(temp_hashes) else left
                
                # Is the target one of these two?
                if i == idx or i == idx - 1:
                    if i == idx: # Target Left -> Sibling Right
                        proof.append({"position": "right", "hash": right})
                    else:        # Target Right -> Sibling Left
                        proof.append({"position": "left", "hash": left})
                
                # Concatenation (Ensures consistency using Hasher class)
                combined = left + right
                new_hash = Hasher.get_hash(combined)
                new_level.append(new_hash)
            
            temp_hashes = new_level
            idx //= 2 
            
        return proof

    @staticmethod
    def verify_merkle_proof(target_hash: str, proof: List[Dict], root: str) -> bool:
        """
        Verifies if the Root can be reached by following the proof path.
        """
        current_hash = target_hash
        
        for node in proof:
            sibling = node["hash"]
            if node["position"] == "right":
                current_hash = Hasher.get_hash(current_hash + sibling)
            else:
                current_hash = Hasher.get_hash(sibling + current_hash)
        
        return current_hash == root