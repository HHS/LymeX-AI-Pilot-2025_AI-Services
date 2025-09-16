import tempfile
from pathlib import Path

import httpx
from src.utils.prompt import model_to_schema
from .model import ClaimBuilder


async def _download_to_tmp(url: str, suffix: str = ".pdf") -> Path:
    """Download *url* to a NamedTemporaryFile and return its Path."""
    async with httpx.AsyncClient() as http:
        resp = await http.get(url)
        resp.raise_for_status()

    tmp_fd, tmp_name = tempfile.mkstemp(suffix=suffix)
    Path(tmp_name).write_bytes(resp.content)
    return Path(tmp_name)


def _build_system_prompt(model_cls: type[ClaimBuilder]) -> str:
    """Generate an instruction block containing the JSON schema."""
    schema = model_to_schema(model_cls)
    return f"""
You are an expert at extracting structured information from regulatory and product documentation for medical devices.

Your task:
- Read and analyze all uploaded PDF documents.
- Extract all relevant information and return a JSON object that exactly matches the following ClaimBuilder schema.
- Only include fields present in the schema, matching their types and structure.

# ClaimBuilder JSON Schema

{schema}

# Output
Return only the final JSON object matching the schema above, ready for deserialization into the ClaimBuilder model.

Strictly output valid JSON.
""".strip()


def _norm(s: str) -> str:
    return s.strip().lower()
