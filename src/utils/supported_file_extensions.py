import asyncio
import logging
from pathlib import Path

from fpdf import FPDF  # pip install fpdf

# ---------------------- Extension Sets ---------------------- #
text_file_extensions = [".txt", ".md", ".csv", ".json"]
word_file_extensions = [".docx", ".doc"]
excel_file_extensions = [".xlsx", ".xls"]
presentation_file_extensions = [".pptx", ".ppt"]

SUPPORTED_FILE_EXTENSIONS = [
    ".pdf",
    *text_file_extensions,
    *word_file_extensions,
    *excel_file_extensions,
    *presentation_file_extensions,
]

# ---------------------- Logging Setup ---------------------- #
logger = logging.getLogger("file2pdf")
logger.setLevel(logging.INFO)


# ---------------------- Main Entry ---------------------- #
async def convert_supported_file_extension_to_pdf(file_path: Path) -> Path:
    """
    Convert a supported file to PDF and return the resulting PDF path.
    If already a PDF, return the original path.
    """
    ext = file_path.suffix.lower()
    logger.info(f"Converting {file_path} (type: {ext}) to PDF")
    if ext == ".pdf":
        return file_path
    if ext in text_file_extensions:
        return await convert_text_to_pdf(file_path)
    if ext in word_file_extensions:
        return await convert_office_to_pdf(file_path)
    if ext in excel_file_extensions:
        return await convert_office_to_pdf(file_path)
    if ext in presentation_file_extensions:
        return await convert_office_to_pdf(file_path)
    raise ValueError(f"Unsupported file type for conversion: {ext}")


# ---------------------- Text/Markdown/CSV/JSON to PDF ---------------------- #
async def convert_text_to_pdf(file_path: Path) -> Path:
    """
    Convert a plain text, markdown, CSV, or JSON file to PDF.
    """
    pdf_path = file_path.with_suffix(".pdf")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Failed to read {file_path}: {e}")
        raise

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # For huge files, consider paging:
    for line in content.splitlines():
        pdf.cell(0, 10, txt=line, ln=True)
    try:
        pdf.output(str(pdf_path))
    except Exception as e:
        logger.error(f"Failed to write PDF to {pdf_path}: {e}")
        raise
    logger.info(f"Converted {file_path} to {pdf_path}")
    return pdf_path


# ---------------------- Office File to PDF (using LibreOffice) ---------------------- #
async def convert_office_to_pdf(file_path: Path, timeout: int = 60) -> Path:
    """
    Convert an office file (Word, Excel, PowerPoint) to PDF using LibreOffice CLI.
    """
    pdf_dir = file_path.parent
    out_name = file_path.with_suffix(".pdf").name
    cmd = [
        "libreoffice",
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        str(pdf_dir),
        str(file_path),
    ]
    logger.info(f"Running: {' '.join(cmd)}")
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        logger.error(f"Timeout during conversion of {file_path}")
        raise RuntimeError("LibreOffice conversion timed out")
    if proc.returncode != 0:
        logger.error(f"LibreOffice failed: {stderr.decode().strip()}")
        raise RuntimeError(
            f"LibreOffice failed (exit {proc.returncode}): {stderr.decode().strip()}"
        )
    result_path = pdf_dir / out_name
    if not result_path.exists():
        logger.error(f"Expected output not found: {result_path}")
        raise FileNotFoundError(f"Output PDF not found: {result_path}")
    logger.info(f"Converted {file_path} to {result_path}")
    return result_path


# ---------------------- Example Usage ---------------------- #
# import asyncio
# asyncio.run(convert_supported_file_extension_to_pdf(Path("yourfile.docx")))
