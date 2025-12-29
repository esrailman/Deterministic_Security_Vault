import unittest
import os
import sqlite3
import base64
import hashlib
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import DB_PATH, init_db
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

# Veritabanını test için temizle
def clear_db():
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except PermissionError:
            pass # Windows bazen dosyayı tutabilir

class TestAPIFlow(unittest.TestCase):
    def setUp(self):
        # Her testten önce temiz bir başlangıç yap
        self.client = TestClient(app)
        clear_db()
        init_db()
        
        # ---------------------------------------------------------
        # KRİTİK: Test için GERÇEK bir RSA anahtar çifti üretiyoruz.
        # Mock kullanmıyoruz, gerçek imza atacağız.
        # ---------------------------------------------------------
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key_pem = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

    def create_signed_payload(self, file_name, file_hash):
        """
        Yardımcı Fonksiyon: 
        Frontend'in yaptığı işi taklit eder.
        Canonical Message oluşturur ve RSA ile imzalar.
        """
        # 1. Timestamp İstemci Tarafında Üretiliyor
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # 2. Canonical Message (Standardımız: file_name|file_hash|timestamp)
        # prev_hash imzaya dahil EDİLMİYOR.
        message = f"{file_name}|{file_hash}|{timestamp}"
        
        # 3. Gerçek İmza Atma (RSA-PSS)
        signature = self.private_key.sign(
            message.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        sig_b64 = base64.b64encode(signature).decode('utf-8')
        
        # 4. Hazır Payload Döndür
        return {
            "file_name": file_name,
            "file_hash": file_hash,
            "public_key": self.public_key_pem,
            "signature": sig_b64,
            "timestamp": timestamp  # Zorunlu alan
        }

    def test_dynamic_merkle_root(self):
        """
        Dinamik Merkle Root ve Hash Chain test eder.
        Bunu yaparken MOCK KULLANMAZ, gerçek imza ile register olur.
        """
        
        # ------------------------------------------------
        # 1. Dosya Kaydı (Genesis)
        # ------------------------------------------------
        payload1 = self.create_signed_payload("dosya1.txt", "aaaa1111")
        response1 = self.client.post("/register", json=payload1)
        
        # Hata varsa detayını görelim
        if response1.status_code != 200:
            print(f"\n[HATA DETAYI 1] {response1.text}")
            
        self.assertEqual(response1.status_code, 200)
        
        # Merkle Root Kontrolü (DB'den)
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT merkle_root FROM records WHERE file_hash=?", ("aaaa1111",))
        db_root1 = cur.fetchone()[0]
        
        print(f"\n[Test] Kayıt 1 Merkle Root: {db_root1}")
        self.assertNotEqual(db_root1, "root", "HATA: Merkle Root statik kalmış!")

        # ------------------------------------------------
        # 2. Dosya Kaydı (Zincire Ekleme)
        # ------------------------------------------------
        payload2 = self.create_signed_payload("dosya2.txt", "bbbb2222")
        response2 = self.client.post("/register", json=payload2)
        
        if response2.status_code != 200:
            print(f"\n[HATA DETAYI 2] {response2.text}")

        self.assertEqual(response2.status_code, 200)
        
        cur.execute("SELECT merkle_root, prev_hash FROM records WHERE file_hash=?", ("bbbb2222",))
        row2 = cur.fetchone()
        db_root2 = row2[0]
        prev_hash2 = row2[1]
        conn.close()

        print(f"[Test] Kayıt 2 Merkle Root: {db_root2}")

        # ------------------------------------------------
        # KONTROLLER
        # ------------------------------------------------
        # 1. Root değişti mi?
        self.assertNotEqual(db_root1, db_root2, "HATA: Merkle Root dinamik değil!")
        
        # 2. Zincir bağlı mı? (Kayit 2'nin prev_hash'i, Kayit 1'in file_hash'i olmalı)
        self.assertEqual(prev_hash2, "aaaa1111", "HATA: Zincir kopuk!")

if __name__ == '__main__':
    unittest.main()