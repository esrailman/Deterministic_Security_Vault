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

    def _prepare(self, file_name: str, file_hash: str) -> dict:
        """
        /register/prepare çağrısı yapıp canonical_message + timestamp döndürür.
        """
        # NOTE: Yeni mimaride register'dan önce prepare zorunlu olduğu için eklendi.
        resp = self.client.post("/register/prepare", json={
            "file_name": file_name,
            "file_hash": file_hash
        })
        self.assertEqual(resp.status_code, 200, f"Prepare failed: {resp.text}")  # NOTE
        return resp.json()

    def test_dynamic_merkle_root(self):
        """
        Dinamik Merkle Root + Hash Chain bağlantısını test eder.

        NOT: Bu test kripto doğrulamasını (RSA doğrulama + replay protection)
        gerçek anahtarlarla yapmak yerine mock'lar.
        Çünkü bu testin amacı kripto değil, zincir/merkle davranışını doğrulamak.
        """

        # NOTE: Yeni mimaride verify_signature ZORUNLU olduğu için mock'lanıyor.
        # NOTE: Yeni mimaride replay protection (check_replay_protection) da devrede olduğu için mock'lanıyor.
        with unittest.mock.patch("backend.main.verify_signature", return_value=True), \
             unittest.mock.patch("backend.main.check_replay_protection", return_value=True):

            # 1) Dosya Kaydı (Genesis)
            file1_name = "dosya1.txt"
            file1_hash = "aaaa1111"

            prep1 = self._prepare(file1_name, file1_hash)  # NOTE: prepare adımı eklendi

            payload1 = {
                "file_name": file1_name,
                "file_hash": file1_hash,
                "public_key": "mock_public_key",
                "signature": "mock_signature",
                "timestamp": prep1["timestamp"]  # NOTE: Yeni mimaride timestamp zorunlu
            }

            response1 = self.client.post("/register", json=payload1)

            if response1.status_code != 200:
                print(f"\n[HATA DETAYI] Status: {response1.status_code}, Body: {response1.text}")

            self.assertEqual(response1.status_code, 200)

            # Merkle Root Kontrolü (DB'den)
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT merkle_root FROM records WHERE file_hash=?", (file1_hash,))
            row1 = cur.fetchone()
            self.assertIsNotNone(row1, "Record 1 DB insert failed")  # NOTE: ekstra güvenlik kontrolü
            db_root1 = row1[0]

            print(f"\n[Test] Kayıt 1 Merkle Root: {db_root1}")
            self.assertNotEqual(
                db_root1,
                "root",
                "HATA: Merkle Root hala statik 'root' olarak atanıyor!"
            )

            # 2) Dosya Kaydı (Zincire Ekleme)
            file2_name = "dosya2.txt"
            file2_hash = "bbbb2222"

            prep2 = self._prepare(file2_name, file2_hash)  # NOTE: prepare adımı eklendi

            payload2 = {
                "file_name": file2_name,
                "file_hash": file2_hash,
                "public_key": "mock_public_key",
                "signature": "mock_signature",
                "timestamp": prep2["timestamp"]  # NOTE: timestamp zorunlu
            }

            response2 = self.client.post("/register", json=payload2)
            self.assertEqual(response2.status_code, 200, f"Register 2 failed: {response2.text}")  # NOTE

            cur.execute("SELECT merkle_root, prev_hash FROM records WHERE file_hash=?", (file2_hash,))
            row2 = cur.fetchone()
            self.assertIsNotNone(row2, "Record 2 DB insert failed")  # NOTE: ekstra kontrol
            db_root2, prev_hash2 = row2[0], row2[1]
            conn.close()

            print(f"[Test] Kayıt 2 Merkle Root: {db_root2}")

            # KONTROLLER
            self.assertNotEqual(
                db_root1,
                db_root2,
                "HATA: Yeni kayıt eklendiğinde Merkle Root değişmedi!"
            )

            # NOTE: prev_hash tasarımında 'prev_hash' bir önceki kaydın file_hash'ine eşit olmalı
            self.assertEqual(
                prev_hash2,
                file1_hash,
                "HATA: Zincir kopuk! prev_hash önceki kaydın file_hash'ine eşit değil."
            )


if __name__ == "__main__":
    unittest.main()
