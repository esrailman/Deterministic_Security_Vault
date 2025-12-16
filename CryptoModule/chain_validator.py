from typing import List, Dict

class ChainValidator:
    """
    Validates the mathematical integrity of the hash chain.
    """
    
    @staticmethod
    def validate_chain(records: List[Dict]) -> Dict:
        """
        Scans the record list for chain breaks.
        Returns: {"is_valid": bool, "broken_indices": List[int]}
        """
        broken_indices = []
        
        if len(records) < 2:
            return {"is_valid": True, "broken_indices": []}

        for i in range(1, len(records)):
            current = records[i]
            prev = records[i-1]
            
            # Does the record's claimed previous hash (prev_hash) 
            # match the actual hash of the previous record (file_hash)?
            prev_hash_claim = current.get("prev_hash")
            actual_prev_hash = prev.get("file_hash")
            
            if prev_hash_claim != actual_prev_hash:
                broken_indices.append(current.get("id"))
                
        return {
            "is_valid": len(broken_indices) == 0,
            "broken_indices": broken_indices
        }