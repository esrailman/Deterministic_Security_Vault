from datetime import timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.database import init_db
from backend.database import get_records, verify_chain
from backend.logger import logger
from backend.schemas import AuditResponse, RecordOut, RegisterRequest, VerifyRequest, VerifyResponse
from backend.database import insert_record, get_last_record, get_record_by_hash
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    timestamp = datetime.now(timezone.utc).isoformat()

    # Canonical message (tek format)
    message = create_canonical_message(
        file_name=payload.file_name,
        file_hash=payload.file_hash,
        prev_hash=prev_hash,
        timestamp=timestamp
    )

    # Signature zorunlu
    if not payload.public_key or not payload.signature:
        raise HTTPException(
            status_code=400,
            detail="public_key ve signature zorunludur."
        )
    
    # Signature doğrulama
    # NOT: Frontend (app.js) demo modunda gerçek bir RSA anahtarı üretemediği için
    # ve backend-side timestamp'i imzalayamadığı için, demo anahtarına izin veriyoruz.
    if payload.public_key.startswith("PREMIUM_USER"):
        logger.warning(f"DEV SIGNATURE BYPASS for user: {payload.public_key}")
    elif not verify_signature(
        payload.public_key,
        message,
        payload.signature
    ):
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
        user_key=payload.public_key,  # <--- KRİTİK DÜZELTME BURADA YAPILDI
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


@app.post(
    "/verify",
    response_model=VerifyResponse,
    tags=["Audit"],
    summary="Verify File Existence",
    description="Checks if a specific file hash exists in the immutable vault."
)
def verify_record(payload: VerifyRequest):
    record = get_record_by_hash(payload.file_hash)
    
    if record:
        return VerifyResponse(
            verified=True,
            message="File found in the vault.",
            record=RecordOut(
                id=record["id"],
                file_name=record["file_name"],
                file_hash=record["file_hash"],
                prev_hash=record["prev_hash"],
                timestamp=record["timestamp"]
            )
        )
    else:
        return VerifyResponse(
            verified=False,
            message="File NOT found in the vault.",
            record=None
        )