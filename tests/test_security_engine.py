import unittest
from CryptoModule.security_engine import SecurityVaultManager

class TestSecurityEngine(unittest.TestCase):
    
    def setUp(self):
        self.vault = SecurityVaultManager()

    def test_merkle_root_logic(self):
        """Build Merkle Root fonksiyonunun doğruluğunu test eder."""
        hashes = ["hash1", "hash2", "hash3", "hash4"]
        # build_merkle_root statik bir metot, direkt çağrılabilir
        root = SecurityVaultManager.build_merkle_root(hashes)
        self.assertTrue(len(root) == 64) # SHA-256 uzunluğu
        self.assertNotEqual(root, "")

    def test_proof_generation_and_verification(self):
        """
        YENİ EKLENEN ÖZELLİK: 
        Proof oluşturma ve doğrulama (Merkle Util'den gelenler) çalışıyor mu?
        """
        hashes = ["a", "b", "c", "d"]
        root = SecurityVaultManager.build_merkle_root(hashes)
        
        # 'b' için kanıt iste
        proof = SecurityVaultManager.get_merkle_proof(hashes, "b")
        
        # Kanıtın doğru olduğunu doğrula
        is_valid = SecurityVaultManager.verify_merkle_proof("b", proof, root)
        self.assertTrue(is_valid, "Geçerli kanıt doğrulanmalıydı.")
        
        # Hatalı veri ile dene
        is_invalid = SecurityVaultManager.verify_merkle_proof("x", proof, root)
        self.assertFalse(is_invalid, "Geçersiz veri reddedilmeliydi.")

    def test_chain_operations(self):
        """Chain ekleme fonksiyonu çalışıyor mu?"""
        h1 = self.vault.add_to_chain("data1")
        h2 = self.vault.add_to_chain("data2")
        
        self.assertEqual(len(self.vault.chain), 2)
        self.assertNotEqual(h1, h2)

if __name__ == '__main__':
    unittest.main()