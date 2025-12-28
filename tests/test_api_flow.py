import unittest
import os
import sqlite3
import unittest.mock
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import DB_PATH, init_db

# Veritabanını test için temizle
def clear_db():
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM records")
        conn.commit()
        conn.close()

class TestAPIFlow(unittest.TestCase):
    def setUp(self):
        # Her testten önce temiz bir başlangıç yap
        self.client = TestClient(app)
        init_db()
        clear_db()

    def test_dynamic_merkle_root(self):
        """
        Main.py'de yapılan değişikliğin (Dinamik Merkle Root) çalışıp çalışmadığını test eder.
        NOT: Backend'deki 'verify_signature' fonksiyonunu bypass ediyoruz (mock).
        """
        
        # 'backend.main.verify_signature' fonksiyonunu geçici olarak 
        # her zaman 'True' dönecek şekilde ayarlıyoruz.
        with unittest.mock.patch('backend.main.verify_signature', return_value=True):
            
            # 1. Dosya Kaydı (Genesis)
            payload1 = {
                "file_name": "dosya1.txt",
                "file_hash": "aaaa1111", 
                "public_key": "mock_public_key", # DÜZELTME: user_key -> public_key
                "signature": "mock_signature"
            }
            response1 = self.client.post("/register", json=payload1)
            
            # Hata varsa görelim
            if response1.status_code != 200:
                print(f"\n[HATA DETAYI] Status: {response1.status_code}, Body: {response1.text}")
                
            self.assertEqual(response1.status_code, 200)
            
            # Merkle Root Kontrolü (DB'den)
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT merkle_root FROM records WHERE file_hash=?", ("aaaa1111",))
            db_root1 = cur.fetchone()[0]
            
            print(f"\n[Test] Kayıt 1 Merkle Root: {db_root1}")
            self.assertNotEqual(db_root1, "root", "HATA: Merkle Root hala statik 'root' olarak atanıyor!")

            # 2. Dosya Kaydı (Zincire Ekleme)
            payload2 = {
                "file_name": "dosya2.txt",
                "file_hash": "bbbb2222",
                "public_key": "mock_public_key", # DÜZELTME: user_key -> public_key
                "signature": "mock_signature"
            }
            response2 = self.client.post("/register", json=payload2)
            self.assertEqual(response2.status_code, 200)
            
            cur.execute("SELECT merkle_root, prev_hash FROM records WHERE file_hash=?", ("bbbb2222",))
            row2 = cur.fetchone()
            db_root2 = row2[0]
            prev_hash2 = row2[1]
            conn.close()

            print(f"[Test] Kayıt 2 Merkle Root: {db_root2}")

            # KONTROLLER 
            self.assertNotEqual(db_root1, db_root2, "HATA: Yeni kayıt eklendiğinde Merkle Root değişmedi!")
            self.assertEqual(prev_hash2, "aaaa1111", "HATA: Zincir kopuk!")

if __name__ == '__main__':
    unittest.main()