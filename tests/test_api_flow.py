import unittest
import os
import sqlite3
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
        """
        # 1. Dosya Kaydı (Genesis)
        payload1 = {
            "file_name": "dosya1.txt",
            "file_hash": "aaaa1111", # Basit mock hash
            "user_key": "test_user"
        }
        response1 = self.client.post("/register", json=payload1)
        self.assertEqual(response1.status_code, 200)
        
        # --- DÜZELTME BURADA ---
        # API response içinden 'merkle_root' aramayı kaldırdık çünkü şemada yok.
        # Bunun yerine doğrudan veritabanına bakıyoruz:
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
            "user_key": "test_user"
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
        # 1. Root değişmiş olmalı (Çünkü artık listede 2 hash var: aaaa... ve bbbb...)
        self.assertNotEqual(db_root1, db_root2, "HATA: Yeni kayıt eklendiğinde Merkle Root değişmedi! (Dynamic calculation çalışmıyor)")
        
        # 2. Zincir bağı (prev_hash) doğru mu?
        self.assertEqual(prev_hash2, "aaaa1111", "HATA: Zincir kopuk! İkinci kaydın prev_hash'i ilk dosyanın hash'i olmalı.")

if __name__ == '__main__':
    unittest.main()