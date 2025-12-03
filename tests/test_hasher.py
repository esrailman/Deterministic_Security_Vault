import unittest
import os
import hashlib
from CryptoModule.hash_util import Hasher

class TestHasher(unittest.TestCase):
    
    def test_basic_string_hash(self):
        """Basit metin hashleme testi"""
        data = "gazi universitesi"
        # Beklenen değeri standart kütüphane ile hesaplayıp karşılaştırıyoruz
        expected_hash = hashlib.sha256(data.encode()).hexdigest()
        self.assertEqual(Hasher.get_hash(data), expected_hash)

    def test_deterministic_behavior(self):
        """Aynı girdinin her zaman aynı çıktıyı verdiğini (deterministik) test eder"""
        data = "guvenli kodlama"
        hash1 = Hasher.get_hash(data)
        hash2 = Hasher.get_hash(data)
        self.assertEqual(hash1, hash2)

    def test_file_hashing(self):
        """Dosya hashleme testi"""
        # Geçici bir test dosyası oluştur
        filename = "test_file_temp.txt"
        with open(filename, "w") as f:
            f.write("test content")
        
        try:
            file_hash = Hasher.get_file_hash(filename)
            # Hash boş gelmemeli ve hata mesajı olmamalı
            self.assertNotEqual(file_hash, "Dosya Bulunamadı")
            self.assertTrue(len(file_hash) == 64) # SHA-256 her zaman 64 karakterdir
        finally:
            # Test bitince dosyayı temizle
            if os.path.exists(filename):
                os.remove(filename)

if __name__ == '__main__':
    unittest.main()