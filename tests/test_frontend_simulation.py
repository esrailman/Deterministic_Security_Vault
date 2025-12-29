import requests
import hashlib
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

# Backend URL
BASE_URL = "http://127.0.0.1:8000"

def simulate_frontend_logic():
    print("--- FRONTEND SİMÜLASYONU BAŞLIYOR ---")
    
    # 1. Frontend'de bir dosya varmış gibi davranalım
    file_content = b"Merhaba Dunya, bu frontend testi."
    file_name = "frontend_test.txt"
    
    # 2. HASH HESAPLAMA (Frontend'in yapacağı iş)
    # JS tarafında bu işi crypto.subtle kütüphanesi yapar.
    file_hash = hashlib.sha256(file_content).hexdigest()
    print(f"[Frontend] Dosya Hashlendi: {file_hash}")

    # 3. ANAHTAR OLUŞTURMA (Kullanıcının tarayıcısında oluşan anahtar)
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    # ---------------------------------------------------------
    # KRİTİK BÖLGE: İMZA OLUŞTURMA
    # Backend ne bekliyor? -> file_name|file_hash|prev_hash|timestamp
    # Frontend neyi biliyor? -> file_name, file_hash.
    # Frontend prev_hash ve timestamp'i BİLEMEZ (çünkü backend üretiyor).
    # ---------------------------------------------------------
    
    # SENARYO A: Frontend sadece bildiği veriyi imzalarsa (HATA BEKLENİR)
    print("\n[Senaryo A] Frontend sadece kendi bildiği veriyi imzalıyor...")
    naive_message = f"{file_name}|{file_hash}" # Eksik format
    signature = private_key.sign(
        naive_message.encode('utf-8'),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    sig_b64 = base64.b64encode(signature).decode('utf-8')
    
    payload = {
        "file_name": file_name,
        "file_hash": file_hash,
        "public_key": public_key_pem,
        "signature": sig_b64
    }
    
    response = requests.post(f"{BASE_URL}/register", json=payload)
    
    if response.status_code == 401 or response.status_code == 422:
        print("✅ BEKLENEN SONUÇ: Backend reddetti. (Çünkü Backend timestamp de bekliyor)")
        print(f"   Sunucu Yanıtı: {response.json()}")
    elif response.status_code == 200:
        print("❌ HATA: Backend bunu kabul etmemeliydi! Güvenlik açığı var.")
    else:
        print(f"⚠️ Beklenmedik durum: {response.status_code}")

    # ---------------------------------------------------------
    
    # SENARYO B: Frontend Backend ile konuşup verileri alırsa (İDEAL SENARYO)
    # Not: Şu anki API tasarımında /get-params gibi bir endpoint yok.
    # Bu test, Frontend ekibine "Bize bir endpoint lazım" demek için kanıttır.
    
    print("\n--- SİMÜLASYON BİTTİ ---")

if __name__ == "__main__":
    simulate_frontend_logic()