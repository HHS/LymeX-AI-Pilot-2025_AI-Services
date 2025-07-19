from pathlib import Path
from src.modules.product_profile.analyze import load_questionnaire_text
from src.modules.product_profile.schema import ProductProfileSchema
from src.services.openai.extract_files_data import extract_files_data


async def run() -> None:
    documents = [Path("/Users/macbookpro/Downloads/K203292.pdf")]
    system_instruction = (
        "You are an FDA expert. Use the uploaded PDF files to extract a complete "
        "product profile. Return **only** valid JSON that matches the "
        "ProductProfile schema exactly (no explanations or bullet points). "
        "Required fields now include trade name, model number, generic name, "
        "FDA product code, CFR regulation number, storage conditions, shelf-life, "
        "sterility status, warnings, limitations, contraindications, and a "
        "step-by-step instructions-for-use list. Use the literal string "
        "'not available' for any field you cannot confidently extract."
    )

    questionnaire_text = load_questionnaire_text()
    user_question = (
        "Please extract a complete product profile using all uploaded FDA PDF "
        "document and return a JSON object matching the ProductProfile schema. "
        "Only include fields present in schema. In particular:\n"
        "• Determine the FDA regulatory pathway ('510(k)', 'De Novo', or 'Premarket Approval (PMA)').\n"
        "• Capture **trade name, model number, and generic name**.\n"
        "• Capture **FDA product code** and **21 CFR regulation number**.\n"
        "• Capture storage conditions, shelf-life, and sterility status if present.\n"
        "• List any warnings, limitations, or contraindications that appear in labeling.\n"
        "• Any software present, single-use or reprocessed single use device "
        "are there any animal-derived materials in the product \n"
        "• Provide a **step-by-step instructions-for-use** list.\n"
        "If an answer is not found, return the field value as 'not available'.\n\n"
        f"{questionnaire_text}"
    )
    result = await extract_files_data(
        file_paths=documents,
        system_instruction=system_instruction,
        user_question=user_question,
        model_class=ProductProfileSchema,
    )
    print("Extraction completed.")
    print("Result:", result)
