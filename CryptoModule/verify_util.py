"""
TODO:
- verify_signature(public_key: str, message: str, signature: str) -> bool
- optional: generate_keypair()
- optional: canonical_message_format (backend ile ortak format)
- optional: replay protection / timestamp binding

Backend integration notes:
- Backend /register içinde:
  - message = f"{file_name}|{file_hash}|{prev_hash}|{timestamp}"
  - signature doğrulaması verify_signature(...) ile yapılacak
"""