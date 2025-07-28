from pathlib import Path
from hashlib import sha1


ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
BASE = len(ALPHABET)


def hash_data(data: bytes) -> str:
    sha_digest = sha1(data).digest()
    num = int.from_bytes(sha_digest, byteorder="big")
    encoded = ""
    while num > 0:
        num, rem = divmod(num, BASE)
        encoded = ALPHABET[rem] + encoded
    return encoded


def hash_document_paths(document_paths: list[Path]) -> str:
    hashes = []
    for path in document_paths:
        with open(path, "rb") as f:
            content = f.read()
        hashes.append(hash_data(content))
    hashes.sort()
    combined_hash = "".join(hashes)
    return hash_data(combined_hash.encode("utf-8"))


if __name__ == "__main__":
    document_paths = [
        "/Users/macbookpro/Documents/demo_system_document/K233367.pdf",
        "/Users/macbookpro/Documents/demo_system_document/K220016.pdf",
        "/Users/macbookpro/Documents/demo_system_document/K203292.pdf",
    ]
    document_paths = [Path(path) for path in document_paths]
    document_hash = hash_document_paths(document_paths)
    print(f"Document hash: {document_hash}")
