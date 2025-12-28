##################### Deterministic Security Vault (DSV) #######################
This project is a cryptographically secured vault designed to guarantee File Integrity and Data Immutability. It utilizes SHA-256, Merkle Trees, Hash Chains, and RSA Digital Signatures to mathematically prove that stored data has not been tampered with or altered.

####################### Features (Sprint Scope) #######################
The project implements four core security layers:

SHA-256 Hashing (Sprint 1): Generates a unique deterministic digital fingerprint for every file.

Merkle Tree & Proof (Sprint 2 & 4): Aggregates all records under a single "Root Hash". Using get_merkle_proof, the system can mathematically prove any file's inclusion in the tree.

Hash Chain (Sprint 3): Each record contains the hash of the previous record (prev_hash). This creates a linked data structure (Blockchain-like), making it impossible to delete or alter intermediate records without breaking the chain.

RSA Digital Signature & Authentication (Sprint 4): Operations are signed using the client's Private Key. The server verifies the identity and integrity using the Public Key (Non-repudiation).

####################### Installation #######################
Install the required Python libraries:

Bash

pip install requirements.txt
Usage
To start the backend server, run the following command in the project root directory:

Bash

python -m uvicorn backend.main:app --reload
The server will start at: http://127.0.0.1:8000

####################### API Documentation #######################
For detailed interactive documentation (Swagger UI), visit: http://127.0.0.1:8000/docs

Core Endpoints
1. Register File (POST /register)
Securely registers a file's hash into the vault.

Requirements: public_key and signature (RSA-PSS) are mandatory.

Sample Request (JSON):

JSON

{
  "file_name": "secure_document.pdf",
  "file_hash": "a1b2c3d4...", 
  "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhki...",
  "signature": "Base64_Encoded_Signature..."
}
2. Audit Chain (GET /audit)
Performs a complete audit of the hash chain to detect any tampering or broken links in the database. Returns the IDs of broken records if manipulation is detected.

####################### Testing #######################
The project includes a comprehensive test suite covering the cryptographic engine, chain structure, and API flow.

To run all tests:

Bash

python -m unittest discover tests
Test Scope:

test_security_engine.py: Validates Merkle Root calculation and Proof generation.

test_integration.py: Tests RSA Signatures, Chain validation, and Tamper simulation.

test_api_flow.py: Verifies database operations and dynamic Merkle Root updates.

test_swagger.py: Ensures API documentation standards.

####################### Project Structure #######################
Deterministic_Security_Vault/
├── backend/
│   ├── main.py            # API Gateway & Endpoints
│   ├── database.py        # SQLite Database Operations
│   ├── schemas.py         # Pydantic Data Models
│   └── logger.py          # Audit Logging
├── frontend/              # Client-side Application (UI)
│   ├── src/               
│   └── public/
├── CryptoModule/
│   ├── security_engine.py # Merkle Tree, Proof & Chain Engine
│   ├── verify_util.py     # RSA Signature Verification & Replay Protection
│   ├── hash_util.py       # SHA-256 Core
│   └── chain_validator.py # Standalone Chain Validator (Logic)
├── tests/                 # Unit and Integration Tests
└── vault.db               # SQLite Database (Auto-generated)