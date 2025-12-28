import unittest
import base64
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

# MerkleTree importuna gerek kalmadı, her şey SecurityVaultManager içinde
from CryptoModule.security_engine import SecurityVaultManager
from CryptoModule.chain_validator import ChainValidator
from CryptoModule.verify_util import verify_signature
from CryptoModule.hash_util import Hasher

class TestSystemIntegrity(unittest.TestCase):
    
    def setUp(self):
        # 1. Zincir Testi İçin Mock Veriler
        self.mock_records = [
            {"id": 1, "file_hash": "abc111", "prev_hash": "GENESIS"},
            {"id": 2, "file_hash": "def222", "prev_hash": "abc111"},
            {"id": 3, "file_hash": "ghi333", "prev_hash": "def222"}
        ]

        # 2. İmza Testi İçin Geçici RSA Anahtar Çifti Oluştur
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self.public_key = self.private_key.public_key()
        
        self.public_key_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

    def test_chain_validation(self):
        """Zincir bütünlüğünü doğrular"""
        result = ChainValidator.validate_chain(self.mock_records)
        self.assertTrue(result["is_valid"])

    def test_tamper_detection(self):
        """Zincir bozulduğunda algılandığını test eder"""
        bad_records = self.mock_records.copy()
        bad_records[1] = {"id": 2, "file_hash": "def222", "prev_hash": "HACKED"}
        
        result = ChainValidator.validate_chain(bad_records)
        self.assertFalse(result["is_valid"])
        self.assertIn(2, result["broken_indices"])

    def test_merkle_root(self):
        """Merkle Root hesaplamasını test eder"""
        hashes = ["hash1", "hash2", "hash3", "hash4"]
        
        # --- DÜZELTME
        # calculate_merkle_root YERİNE build_merkle_root KULLANIYORUZ
        root = SecurityVaultManager.build_merkle_root(hashes)
        
        self.assertTrue(len(root) > 0)

    def test_merkle_proof_integrity(self):
        """Merkle Proof'un veri manipülasyonunu yakaladığını test eder."""
        hashes = ["h1", "h2", "h3", "h4"]
        
        # --- DÜZELTME
        # calculate_merkle_root YERİNE build_merkle_root
        root = SecurityVaultManager.build_merkle_root(hashes)
        
        # Kanıt oluşturma (get_merkle_proof SecurityVaultManager içinde)
        proof = SecurityVaultManager.get_merkle_proof(hashes, "h2")
        
        # Doğru veriyle doğrulama
        self.assertTrue(SecurityVaultManager.verify_merkle_proof("h2", proof, root))
        
        # Manipüle edilmiş veriyle doğrulama
        self.assertFalse(SecurityVaultManager.verify_merkle_proof("h2_manipulated", proof, root))

    def test_digital_signature(self):
        """CryptoModule/verify_util.py içindeki imza doğrulama fonksiyonunu test eder."""
        message = "Test Mesajı"
        
        # 1. Mesajı private key ile imzala
        signature = self.private_key.sign(
            message.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # 2. İmzayı Base64 string formatına çevir
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        # Durum A: Doğru İmza
        valid = verify_signature(self.public_key_pem, message, signature_b64)
        self.assertTrue(valid, "Geçerli imza doğrulanmalıydı.")
        
        # Durum B: Değiştirilmiş Mesaj
        invalid_msg = verify_signature(self.public_key_pem, "Hacked Mesaj", signature_b64)
        self.assertFalse(invalid_msg, "Mesaj değiştiğinde imza geçersiz olmalıydı.")
        
        # Durum C: Sahte İmza
        fake_sig_b64 = base64.b64encode(b'fake_signature_bytes').decode('utf-8')
        invalid_sig = verify_signature(self.public_key_pem, message, fake_sig_b64)
        self.assertFalse(invalid_sig, "Sahte imza kabul edilmemeliydi.")

if __name__ == '__main__':
    unittest.main()