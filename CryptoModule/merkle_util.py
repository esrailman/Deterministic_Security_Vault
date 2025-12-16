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