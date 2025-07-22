import asyncio
from pathlib import Path
from loguru import logger
from fpdf import FPDF  # pip install fpdf
from openpyxl import load_workbook

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


def autofit_excel_columns(path):
    wb = load_workbook(path)
    for ws in wb.worksheets:
        for col in ws.columns:
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                try:
                    cell_length = len(str(cell.value))
                    if cell_length > max_length:
                        max_length = cell_length
                except:
                    pass
            ws.column_dimensions[col_letter].width = max_length + 2  # Add some padding
    wb.save(path)


# ---------------------- Main Entry ---------------------- #
async def convert_supported_file_extension_to_pdf(file_path: Path) -> Path:
    """
    Convert a supported file to PDF and return the resulting PDF path.
    If already a PDF, return the original path.
    """
    ext = file_path.suffix.lower()

    if ext == ".pdf":
        return file_path

    logger.info(f"Converting {file_path} (type: {ext}) to PDF")

    pdf_path = file_path.with_suffix(".pdf")
    # Create empty PDF with value is 1 as a lock and make other processes wait and get result
    # not to convert the same file multiple times
    lock_value = "1"
    if pdf_path.exists():
        logger.info(f"PDF already exists: {pdf_path}")
        retries = 10  # Wait for 10 seconds for the file to be ready
        for _ in range(retries):
            # Check if the file is no longer a lock file by verifying its size is greater than 1 byte
            if pdf_path.stat().st_size > len(lock_value):
                logger.info(f"PDF file {pdf_path} is ready.")
                return pdf_path
            logger.info(
                f"Waiting for PDF file {pdf_path} to be ready...  Retrying {_ + 1} times..."
            )
            await asyncio.sleep(1)
        logger.error(
            f"PDF file {pdf_path} still not ready after {retries} seconds, aborting conversion."
        )
    else:
        pdf_path.write_text(lock_value)

    if ext in text_file_extensions:
        await convert_text_to_pdf(file_path, pdf_path)
        return pdf_path
    if ext in word_file_extensions:
        await convert_office_to_pdf(file_path, pdf_path)
        return pdf_path
    if ext in excel_file_extensions:
        autofit_excel_columns(file_path)
        await convert_office_to_pdf(file_path, pdf_path)
        return pdf_path
    if ext in presentation_file_extensions:
        await convert_office_to_pdf(file_path, pdf_path)
        return pdf_path
    raise ValueError(f"Unsupported file type for conversion: {ext}")


# ---------------------- Text/Markdown/CSV/JSON to PDF ---------------------- #
async def convert_text_to_pdf(file_path: Path, pdf_path: Path) -> None:
    """
    Convert a plain text, markdown, CSV, or JSON file to PDF.
    """
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


# ---------------------- Office File to PDF (using LibreOffice) ---------------------- #
async def convert_office_to_pdf(
    file_path: Path,
    pdf_path: Path,
    timeout: int = 60,
) -> None:
    """
    Convert an office file (Word, Excel, PowerPoint) to PDF using LibreOffice CLI.
    """
    pdf_dir = file_path.parent
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
    if not pdf_path.exists():
        logger.error(f"Expected output not found: {pdf_path}")
        raise FileNotFoundError(f"Output PDF not found: {pdf_path}")
    logger.info(f"Converted {file_path} to {pdf_path}")


# ---------------------- Example Usage ---------------------- #
# import asyncio
# asyncio.run(convert_supported_file_extension_to_pdf(Path("yourfile.docx")))
