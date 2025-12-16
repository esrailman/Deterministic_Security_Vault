import unittest
from CryptoModule.merkle_util import MerkleTree
from CryptoModule.chain_validator import ChainValidator

class TestSystemIntegrity(unittest.TestCase):
    
    def setUp(self):
        # Mock database records for testing
        self.mock_records = [
            {"id": 1, "file_hash": "abc111", "prev_hash": "GENESIS"},
            {"id": 2, "file_hash": "def222", "prev_hash": "abc111"},
            {"id": 3, "file_hash": "ghi333", "prev_hash": "def222"}
        ]

    def test_chain_validation(self):
        """Test for a valid chain"""
        result = ChainValidator.validate_chain(self.mock_records)
        self.assertTrue(result["is_valid"])

    def test_tamper_detection(self):
        """Test for chain tampering (hacking attempt)"""
        bad_records = self.mock_records.copy()
        # Modifying the middle record to break the chain
        bad_records[1] = {"id": 2, "file_hash": "def222", "prev_hash": "HACKED"}
        
        result = ChainValidator.validate_chain(bad_records)
        self.assertFalse(result["is_valid"])
        self.assertIn(2, result["broken_indices"])

    def test_merkle_root(self):
        """Test for Merkle Root calculation"""
        hashes = ["hash1", "hash2", "hash3", "hash4"]
        root = MerkleTree.calculate_merkle_root(hashes)
        self.assertTrue(len(root) > 0)

if __name__ == '__main__':
    unittest.main()