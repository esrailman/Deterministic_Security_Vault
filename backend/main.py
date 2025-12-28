from fastapi import FastAPI, HTTPException
from backend.database import init_db
from backend.database import get_records, verify_chain
from backend.logger import logger
from backend.schemas import AuditResponse, RecordOut, RegisterRequest
from backend.database import insert_record, get_last_record
from datetime import datetime
from fastapi import HTTPException
from CryptoModule.verify_util import (create_canonical_message,verify_signature,)
from CryptoModule.security_engine import SecurityVaultManager


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

    # Önceki hash (hash-chain)
    last_record = get_last_record()
    prev_hash = last_record["file_hash"] if last_record else "GENESIS"

    # Timestamp TEK KAYNAK: backend
    timestamp = datetime.utcnow().isoformat()

    # Canonical message (tek format)
    message = create_canonical_message(
        file_name=payload.file_name,
        file_hash=payload.file_hash,
        prev_hash=prev_hash,
        timestamp=timestamp
    )

    # Signature zorunlu
    if not payload.user_key or not payload.signature:
        raise HTTPException(
            status_code=400,
            detail="user_key ve signature zorunludur."
        )

    # Signature doğrulama
    if not verify_signature(payload.user_key, message, payload.signature):
        raise HTTPException(
            status_code=401,
            detail="Geçersiz signature."
        )

    # Gerçek Merkle root
    vault = SecurityVaultManager()
    merkle_root = vault.build_merkle_root(
        [payload.file_hash, prev_hash]
    )

    # DB insert (timestamp ile)
    insert_record(
        file_name=payload.file_name,
        file_hash=payload.file_hash,
        prev_hash=prev_hash,
        user_key=payload.user_key,
        merkle_root=merkle_root,
        timestamp=timestamp
    )

    logger.info(f"New record registered: {payload.file_name}")

    # Response
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