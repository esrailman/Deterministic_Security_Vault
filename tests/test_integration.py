import unittest
import json
import base64
import hashlib
import os
import sqlite3
from datetime import datetime, timezone
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from fastapi.testclient import TestClient

# Proje Modülleri
from backend.main import app
from backend.database import init_db, DB_PATH, get_records
from CryptoModule.security_engine import SecurityVaultManager
from CryptoModule.chain_validator import ChainValidator

class TestSystemIntegration(unittest.TestCase):
    
    def setUp(self):
        # 1. Veritabanı Temizliği (Her testten önce SIFIRLAMA)
        if os.path.exists(DB_PATH):
            try:
                os.remove(DB_PATH)
            except PermissionError:
                pass
        init_db()
        
        # 2. Test İstemcisi
        self.client = TestClient(app)

        # 3. Gerçek RSA Anahtarı Üret
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self.public_key = self.private_key.public_key()
        self.public_key_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        # NOT: self.mock_records ARTIK YOK. Tamamen veritabanı kullanacağız.

    # --- YARDIMCI FONKSİYON ---
    def sign_data_canonical(self, file_name, file_hash, timestamp):
        """Canonical Message Formatı ile imzalar."""
        message = f"{file_name}|{file_hash}|{timestamp}"
        signature = self.private_key.sign(
            message.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')

    def register_file_helper(self, fname, fhash):
        """Yardımcı fonksiyon: Dosyayı API üzerinden GERÇEK DB'ye kaydeder."""
        ts = datetime.now(timezone.utc).isoformat()
        sig = self.sign_data_canonical(fname, fhash, ts)
        
        response = self.client.post("/register", json={
            "file_name": fname,
            "file_hash": fhash,
            "public_key": self.public_key_pem,
            "signature": sig,
            "timestamp": ts
        })
        return response

    # --- TESTLER (HEPSİ DATABASE ÜZERİNDEN) ---

    def test_chain_validation_on_real_db(self):
        """
        Mock veri YERİNE, veritabanına kayıt ekleyip ChainValidator'ı gerçek verilerle test eder.
        """
        # 1. Gerçek Kayıtlar Oluştur
        self.register_file_helper("doc1.txt", "hash_aaaa")
        self.register_file_helper("doc2.txt", "hash_bbbb")
        self.register_file_helper("doc3.txt", "hash_cccc")

        # 2. Veritabanından verileri çek (Mock değil, SQL sorgusuyla gelir)
        real_records = get_records()
        
        # 3. Validator'ı çalıştır
        result = ChainValidator.validate_chain(real_records)
        
        self.assertTrue(result["is_valid"], "Gerçek veritabanı zinciri geçerli olmalı.")
        self.assertEqual(len(real_records), 3)

    def test_tamper_detection_real_db(self):
        """
        Veritabanına SQL ile saldırı yapıldığında ChainValidator'ın bunu yakalaması.
        """
        # 1. Veri Hazırla (En az 2 kayıt)
        self.register_file_helper("doc1.txt", "hash_1111")
        self.register_file_helper("doc2.txt", "hash_2222")

        # 2. SALDIRI: Doğrudan SQL ile veriyi boz
        conn = sqlite3.connect(DB_PATH)
        conn.execute("UPDATE records SET file_hash = 'HACKED' WHERE id = 1")
        conn.commit()
        conn.close()

        # 3. Veriyi çek ve Kontrol et
        # Not: API (/audit) yerine doğrudan modülü test ediyoruz burada
        corrupted_records = get_records()
        result = ChainValidator.validate_chain(corrupted_records)

        self.assertFalse(result["is_valid"], "Bozulmuş DB zinciri geçersiz olmalı.")
        self.assertIn(2, result["broken_indices"], "Kırılma noktası 2. kayıt olmalı.")

    def test_merkle_logic_with_real_hashes(self):
        """
        Merkle Root hesaplamasını rastgele stringler yerine DB hashleri ile test eder.
        """
        self.register_file_helper("f1", "h1")
        self.register_file_helper("f2", "h2")
        
        # DB'den hashleri çek
        conn = sqlite3.connect(DB_PATH)
        hashes = [row[0] for row in conn.execute("SELECT file_hash FROM records").fetchall()]
        conn.close()
        
        # Root hesapla
        root = SecurityVaultManager.build_merkle_root(hashes)
        
        self.assertTrue(len(root) > 0)
        self.assertIn("h1", hashes) # Hashlerin doğru kaydedildiğini teyit et

    def test_full_registration_flow(self):
        """Normal API Akışı"""
        res = self.register_file_helper("test.pdf", "hash_test")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["file_hash"], "hash_test")

    def test_sequential_registration_flow(self):
        """Ardışık Kayıt ve Dinamik Root Testi"""
        # Kayıt 1
        self.register_file_helper("A.txt", "hash_A")
        
        conn = sqlite3.connect(DB_PATH)
        root1 = conn.execute("SELECT merkle_root FROM records WHERE file_hash='hash_A'").fetchone()[0]
        
        # Kayıt 2
        self.register_file_helper("B.txt", "hash_B")
        
        row2 = conn.execute("SELECT merkle_root, prev_hash FROM records WHERE file_hash='hash_B'").fetchone()
        root2, prev_hash2 = row2[0], row2[1]
        conn.close()

        # Kontroller
        self.assertNotEqual(root1, root2, "Merkle Root değişmeli")
        self.assertEqual(prev_hash2, "hash_A", "Zincir doğru bağlanmalı")

    def tearDown(self):
        if os.path.exists(DB_PATH):
            try:
                os.remove(DB_PATH)
            except PermissionError:
                pass

if __name__ == '__main__':
    unittest.main()