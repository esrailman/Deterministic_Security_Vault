from fastapi import FastAPI
from backend.database import init_db
from backend.database import get_records, verify_chain
from backend.logger import logger
from backend.schemas import AuditResponse, RecordOut, RegisterRequest
from backend.database import insert_record, get_last_record
# from CryptoModule.verify_util import verify_signature  # Sprint-4 TODO

app = FastAPI()

# Veritabanı başlatma
init_db()

@app.post("/register", response_model=RecordOut)
def register_record(payload: RegisterRequest):

    last_record = get_last_record()
    prev_hash = last_record["file_hash"] if last_record else "GENESIS"

    insert_record(
        file_name=payload.file_name,
        file_hash=payload.file_hash,
        prev_hash=prev_hash,
        user_key=payload.user_key or "unknown",
        merkle_root="root"
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

@app.get("/audit", response_model=AuditResponse)
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
