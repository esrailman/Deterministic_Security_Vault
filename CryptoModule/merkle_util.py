from typing import List
from .hash_util import Hasher

class MerkleTree:
    """
    Implements the Merkle Tree structure to prove the integrity 
    of records using a single 'Root Hash'.
    """

    @staticmethod
    def calculate_merkle_root(hashes: List[str]) -> str:
        """Calculates the Merkle Root of the given list of hashes."""
        if not hashes:
            return ""
        
        temp_hashes = hashes.copy()
        
        # Hash in pairs until one element remains
        while len(temp_hashes) > 1:
            new_level = []
            for i in range(0, len(temp_hashes), 2):
                left = temp_hashes[i]
                # If no right element exists (odd count), duplicate the left
                right = temp_hashes[i+1] if i+1 < len(temp_hashes) else left
                
                # Concatenate and hash both
                combined = left + right
                new_hash = Hasher.get_hash(combined)
                new_level.append(new_hash)
            temp_hashes = new_level
            
        return temp_hashes[0]

    @staticmethod
    def validate_merkle_root(hashes: List[str], expected_root: str) -> bool:
        """Checks if the calculated root matches the expected root."""
        calculated = MerkleTree.calculate_merkle_root(hashes)
        return calculated == expected_root

    @staticmethod
    def get_merkle_proof(hashes: List[str], target_hash: str) -> List[dict]:
        """
        Belirtilen bir hash değeri için Merkle Proof (kanıt yolu) oluşturur.
        (Düzeltilmiş Versiyon)
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
                # Sağ eleman yoksa solu kopyala (Duble)
                right = temp_hashes[i+1] if i+1 < len(temp_hashes) else left
                
                # Target bu çiftin içinde mi? (Sol: i, Sağ: i+1)
                if i == idx or i == idx - 1: # idx == i veya idx == i+1
                    if i == idx:
                        # Hedef SOLDA ise -> Kardeş SAĞDAKİDİR
                        sibling = right
                        position = "right"
                    else:
                        # Hedef SAĞDA ise -> Kardeş SOLDAKİDİR
                        sibling = left
                        position = "left"
                        
                    proof.append({
                        "position": position,
                        "hash": sibling
                    })
                
                # Bir üst seviyeye çık
                combined = left + right
                new_hash = Hasher.get_hash(combined)
                new_level.append(new_hash)
            
            temp_hashes = new_level
            idx //= 2 # İndeks bir üst seviyede yarıya düşer (integer division)
            
        return proof

    @staticmethod
    def verify_merkle_proof(target_hash: str, proof: List[dict], root: str) -> bool:
        """
        Verilen kanıt dizisini (proof) kullanarak hedef hash'in
        gerçekten o kök (root) hash'e ait olup olmadığını doğrular.
        """
        current_hash = target_hash
        
        for node in proof:
            sibling = node["hash"]
            if node["position"] == "right":
                # Kardeş sağdaysa: current + sibling
                current_hash = Hasher.get_hash(current_hash + sibling)
            else:
                # Kardeş soldaysa: sibling + current
                current_hash = Hasher.get_hash(sibling + current_hash)
        
        return current_hash == root