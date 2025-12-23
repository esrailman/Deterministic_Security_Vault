from fastapi import FastAPI, HTTPException
from backend.database import init_db
from backend.database import get_records, verify_chain
from backend.logger import logger
from backend.schemas import AuditResponse, RecordOut, RegisterRequest
from backend.database import insert_record, get_last_record

# --- EKLENEN IMPORTLAR ---
from CryptoModule.merkle_util import MerkleTree  # MerkleTree sınıfını kullanabilmek için şart!
from CryptoModule.verify_util import verify_signature  # İmza doğrulaması için

app = FastAPI(
    title="Deterministic Security Vault API",
    description="Deterministic security API providing file integrity via Merkle Tree and Hash Chain.",
    version="1.0.0",
    openapi_tags=[
        {"name": "Register", "description": "File registration and hashing operations"},
        {"name": "Audit", "description": "Chain validation and audit logs"},
    ]
)

# Veritabanı başlatma
init_db()

@app.post(
    "/register", 
    response_model=RecordOut,
    tags=["Register"],
    summary="Register a New File",
    description="Calculates the hash of the uploaded file, verifies the digital signature, updates the Merkle Tree, and stores the record immutably."
)
def register_record(payload: RegisterRequest):
    # 1. İmza Doğrulama
    if payload.signature and payload.user_key:
        is_valid = verify_signature(payload.user_key, payload.file_hash, payload.signature)
        if not is_valid:
            logger.warning(f"Invalid signature attempt for file: {payload.file_name}")
            raise HTTPException(status_code=400, detail="Invalid Digital Signature! Integrity check failed.")

    # 2. Geçmiş kayıtları getir ve Merkle Root hesapla (DÜZELTME BURADA)
    all_records = get_records()  # Veritabanındaki tüm kayıtları çek
    
    # Mevcut hash listesini oluştur
    current_hashes = [r["file_hash"] for r in all_records]
    current_hashes.append(payload.file_hash)  # Yeni hash'i ekle
    
    # Tüm geçmiş + yeni kayıt ile Root hesapla
    calculated_root = MerkleTree.calculate_merkle_root(current_hashes)

    # Önceki hash (Zincir için)
    last_record = all_records[-1] if all_records else None
    prev_hash = last_record["file_hash"] if last_record else "GENESIS"

    # Kayıt ekle
    insert_record(
        file_name=payload.file_name,
        file_hash=payload.file_hash,
        prev_hash=prev_hash,
        user_key=payload.user_key or "unknown",
        merkle_root=calculated_root 
    )

    logger.info(f"New record registered: {payload.file_name}")

    # Son eklenen kaydı dönmek için tekrar sorgula
    r = get_last_record()
    return RecordOut(
        id=r["id"],
        file_name=r["file_name"],
        file_hash=r["file_hash"],
        prev_hash=r["prev_hash"],
        timestamp=r["timestamp"]
    )

    logger.info(f"New record registered: {payload.file_name}")

    r = get_last_record()
    return RecordOut(
        id=r["id"],
        file_name=r["file_name"],
        file_hash=r["file_hash"],
        prev_hash=r["prev_hash"],
        timestamp=r["timestamp"]
    )

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get(
    "/audit", 
    response_model=AuditResponse, 
    tags=["Audit"],
    summary="Validate Chain Integrity",
    description="Performs a complete audit of the hash chain to detect any tampering or broken links in the database."
)
def audit():
    records = get_records()
    chain_valid, broken = verify_chain()

    logger.info("Audit endpoint called")

    if not chain_valid:
        logger.warning(f"Hash chain broken at records: {broken}")

    return AuditResponse(
        chain_valid=chain_valid,
        broken_record_ids=broken,
        records=[
            RecordOut(
                id=r["id"],
                file_name=r["file_name"],
                file_hash=r["file_hash"],
                prev_hash=r["prev_hash"],
                timestamp=r["timestamp"]
            )
            for r in records
        ]
    )