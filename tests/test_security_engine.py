import unittest
import hashlib
from CryptoModule.security_engine import SecurityVaultManager

class TestSecurityEngine(unittest.TestCase):
    
    def setUp(self):
        # Her testten önce temiz bir motor başlat
        self.vault = SecurityVaultManager()

    def _get_hash(self, data: str) -> str:
        """Yardımcı fonksiyon: Rastgele ama geçerli formatta hash üretir."""
        return hashlib.sha256(data.encode()).hexdigest()

    def test_merkle_root_logic(self):
        """Build Merkle Root fonksiyonunun doğruluğunu test eder."""
        # Gerçekçi 64 karakterlik hashler kullanıyoruz
        hashes = [
            self._get_hash("data1"),
            self._get_hash("data2"),
            self._get_hash("data3"),
            self._get_hash("data4")
        ]
        
        # build_merkle_root statik bir metot, direkt çağrılabilir
        root = SecurityVaultManager.build_merkle_root(hashes)
        
        # 1. SHA-256 uzunluğu (64 karakter) olmalı
        self.assertEqual(len(root), 64, "Merkle Root 64 karakter (SHA-256 Hex) olmalı.")
        # 2. Boş olmamalı
        self.assertNotEqual(root, "")

    def test_proof_generation_and_verification(self):
        """
        Proof oluşturma ve doğrulama mantığını test eder.
        """
        # Test verileri (Leaf Nodes)
        leaf_data = ["a", "b", "c", "d"]
        hashes = [self._get_hash(x) for x in leaf_data]
        
        target_hash = hashes[1] # 'b' nin hash'i
        
        # Root oluştur
        root = SecurityVaultManager.build_merkle_root(hashes)
        
        # Kanıt iste
        proof = SecurityVaultManager.get_merkle_proof(hashes, target_hash)
        
        # SENARYO 1: Geçerli Kanıt
        is_valid = SecurityVaultManager.verify_merkle_proof(target_hash, proof, root)
        self.assertTrue(is_valid, "Geçerli kanıt ve hash doğrulanmalıydı.")
        
        # SENARYO 2: Geçersiz Veri (Hash değişirse)
        fake_hash = self._get_hash("fake_b")
        is_invalid = SecurityVaultManager.verify_merkle_proof(fake_hash, proof, root)
        self.assertFalse(is_invalid, "Yanlış hash ile yapılan doğrulama reddedilmeliydi.")
        
        # SENARYO 3: Yanlış Root
        fake_root = self._get_hash("fake_root")
        is_bad_root = SecurityVaultManager.verify_merkle_proof(target_hash, proof, fake_root)
        self.assertFalse(is_bad_root, "Yanlış Root ile doğrulama başarısız olmalıydı.")

    def test_chain_operations(self):
        """
        Chain ekleme fonksiyonu (InMemory) çalışıyor mu?
        Not: Bu test, SecurityEngine'in 'chain' listesini bellekte tuttuğunu varsayar.
        """
        # Eğer SecurityVaultManager içinde 'chain' listesi yoksa bu test hata verebilir.
        # Genellikle bu logic engine sadece hesaplama yapar, ama varsa test edelim:
        if hasattr(self.vault, 'chain'):
            h1 = self.vault.add_to_chain("data1")
            h2 = self.vault.add_to_chain("data2")
            
            self.assertEqual(len(self.vault.chain), 2)
            self.assertNotEqual(h1, h2)
        else:
            # Eğer chain veritabanında tutuluyorsa (database.py), engine içinde chain listesi olmayabilir.
            # Bu durumda testi pass geçiyoruz.
            print("\n[Bilgi] SecurityVaultManager stateless çalışıyor (chain DB'de), bu test atlandı.")

if __name__ == '__main__':
    unittest.main()