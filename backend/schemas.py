from pydantic import BaseModel, Field
from typing import List, Optional

class RecordOut(BaseModel):
    id: int
    file_name: str
    file_hash: str
    prev_hash: str
    timestamp: str

class AuditResponse(BaseModel):
    chain_valid: bool
    broken_record_ids: List[int] = Field(default_factory=list)
    records: List[RecordOut] = Field(default_factory=list)


class RegisterRequest(BaseModel):
    file_name: str
    file_hash: str
    user_key: Optional[str] = None
    signature: Optional[str] = None  
