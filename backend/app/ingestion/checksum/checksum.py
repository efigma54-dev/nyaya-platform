
import hashlib
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def compute_file_sha256(file_path: Path) -> str:
    sha256_hash = hashlib.sha256()
    with file_path.open("rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def compute_content_sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def generate_file_metadata(file_path: Path, source_url: str = None, publication_date: str = None, version: str = None, document_type: str = "act", parser_version: str = "1.0.0") -> Dict[str, Any]:
    stat = file_path.stat()
    return {
        "filename": file_path.name,
        "file_size": stat.st_size,
        "sha256": compute_file_sha256(file_path),
        "source_url": source_url,
        "publication_date": publication_date,
        "official_version": version,
        "retrieval_timestamp": datetime.now().isoformat(),
        "download_timestamp": datetime.now().isoformat(),  # Alias for retrieval_timestamp
        "document_type": document_type,
        "parser_version": parser_version
    }
