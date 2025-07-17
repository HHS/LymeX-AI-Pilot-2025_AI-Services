import json
from enum import Enum
from pathlib import Path
import httpx
from fastapi import HTTPException
from loguru import logger
from src.infrastructure.openai import get_openai_client

from src.modules.competitive_analysis.model import CompetitiveAnalysis
from src.modules.product_profile.schema import ProductProfileDocumentResponse


class RegulatoryPathway(str, Enum):
    K510 = "510(k)"
    PMA = "PMA"
    DE_NOVO = "De Novo"


async def create_competitive_analysis(
    product_profile_docs: list[ProductProfileDocumentResponse],
    competitor_document_paths: list[Path],
) -> CompetitiveAnalysis:
    if not product_profile_docs or not competitor_document_paths:
        logger.error("No product profile documents or competitor documents provided.")
        raise HTTPException(
            status_code=400,
            detail="Product profile documents and competitor documents are required.",
        )
    logger.info("Creating competitive analysis.")
    logger.info(
        f"Product profile docs: {' ,'.join([doc.file_name for doc in product_profile_docs])}"
    )
    logger.info(
        f"Competitor docs: {', '.join([path.name for path in competitor_document_paths])}"
    )
    client = get_openai_client()
    product_profile_uploaded_ids: list[str] = []
    competitor_uploaded_ids: list[str] = []

    # — your original upload loop for product profiles —
    for doc in product_profile_docs:
        path = Path(f"/tmp/product_profile/{doc.file_name}")
        path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Downloading product profile document from {doc.url} to {path}")
        resp = httpx.get(doc.url)
        resp.raise_for_status()
        path.write_bytes(resp.content)

        with path.open("rb") as f:
            fo = client.files.create(file=f, purpose="assistants")
        logger.info(
            f"Uploaded product profile document {doc.file_name} to OpenAI, file_id={fo.id}"
        )
        product_profile_uploaded_ids.append(fo.id)

    # — your original download & upload for competitor doc —
    for competitor_document_path in competitor_document_paths:
        with competitor_document_path.open("rb") as f:
            cfo = client.files.create(file=f, purpose="assistants")
        logger.info(
            f"Uploaded competitor document {competitor_document_path.name} to OpenAI, file_id={cfo.id}"
        )
        competitor_uploaded_ids.append(cfo.id)

    product_profile_file_names = [
        doc.file_name for doc in product_profile_docs if doc.file_name
    ]
    competitor_file_name = competitor_document_path.name

    func_spec = {
        "name": "create_competitive_analysis",
        "description": "Produce a JSON object matching the CompetitiveAnalysis schema",
        "parameters": CompetitiveAnalysis.model_json_schema(),
    }

    # instructions = (
    #     "You are an expert in competitive analysis for medical diagnostic devices. "
    #     "Your task is to extract and present ALL available details from the provided product and competitor documents for each field of the CompetitiveAnalysisDetail model. "
    #     "For each field, include every relevant detail: all text, lists, tables, or numerical data present in the documents. "
    #     "If a document contains a list, a table, or a long descriptive section for a field, include the entire content for that field (as multi-line text if needed). "
    #     "Do not summarize or condense information for individual fields. Use multi-line formatting and bullet points to preserve the structure from the source. "
    #     "For example, if the 'antigens' field lists several proteins, include the full bullet list. If the 'performance' field has a table or multi-part results, format the full results as text. "
    #     "Include all relevant descriptions, specifications, and values found—do not leave out any part of the source content for each field. "
    #     "If a field cannot be determined from the provided documents, set its value to 'Not Available'. "
    #     "Do not use null values or leave any field blank. "
    #     "Return your response as a CompetitiveAnalysis object containing: "
    #     "'your_product': CompetitiveAnalysisDetail, "
    #     "'competitor': CompetitiveAnalysisDetail. "
    #     "Do not add any extra summary or commentary outside the required fields."
    #     "Ignore two fields: 'is_ai_generated' and 'use_system_data'."
    #     "Field 'product_name' is the name of the competitor document, not the product profile."
    #     "confidence_score should be from 0 to 1, where 1 is very confident and 0 is not confident at all."
    # )

    # instructions = (
    #     "You are an expert in competitive analysis for medical diagnostic devices. "
    #     "Your task is to extract and present ALL available details from the provided product and competitor documents for each field of the CompetitiveAnalysisDetail model. "
    #     "For each field, include every relevant detail: all text, lists, tables, or numerical data present in the documents. "
    #     "If a document contains a list, a table, or a long descriptive section for a field, include the entire content for that field (as multi-line text if needed). "
    #     "Do not summarize or condense information for individual fields. Use multi-line formatting and bullet points to preserve the structure from the source. "
    #     "For example, if the 'antigens' field lists several proteins, include the full bullet list. If the 'performance' field has a table or multi-part results, format the full results as text. "
    #     "Include all relevant descriptions, specifications, and values found—do not leave out any part of the source content for each field. "
    #     "If a field cannot be determined from the provided documents, set its value to 'Not Available'. "
    #     "Do not use null values or leave any field blank. "
    #     "Return your response as a CompetitiveAnalysis object containing: "
    #     "'your_product': CompetitiveAnalysisDetail, "
    #     "'competitor': CompetitiveAnalysisDetail. "
    #     "Do not add any extra summary or commentary outside the required fields."
    #     "Ignore two fields: 'is_ai_generated' and 'use_system_data'."
    #     "Field 'product_name' is the name of the product."
    #     "confidence_score should be from 0 to 1, where 1 is very confident and 0 is not confident at all."
    #     "Field 'product_name' in CompetitiveAnalysisDetailis is the name of the product or the name of the device."
    # )

    instructions = (
        "You are an expert in competitive analysis for medical diagnostic devices. "
        "Your task is to extract and present ALL available details from the provided product  documents for each field of the CompetitiveAnalysisDetail model. "
        "For each field, include every relevant detail: all text, lists, tables, or numerical data present in the documents. "
        "If a document contains a list, a table, or a long descriptive section for a field, include the entire content for that field (as multi-line text if needed). "
        "Do not summarize or condense information for individual fields. Use multi-line formatting and bullet points to preserve the structure from the source. "
        "For example, if the 'antigens' field lists several proteins, include the full bullet list. If the 'performance' field has a table or multi-part results, format the full results as text. "
        "Include all relevant descriptions, specifications, and values found—do not leave out any part of the source content for each field. "
        "If a field cannot be determined from the provided documents, set its value to 'Not Available'. "
        "Do not use null values or leave any field blank. "
        "Return your response as a CompetitiveAnalysisDetail object containing: "
        "CompetitiveAnalysisDetail"
        "Do not add any extra summary or commentary outside the required fields."
        "Ignore two fields: 'is_ai_generated' and 'use_system_data'."
        "Field 'product_name' in CompetitiveAnalysisDetailis is the name of the product or the name of the device."
    )

    logger.info("Calling OpenAI chat completion for competitive analysis")
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": instructions},
            {
                "role": "user",
                "content": json.dumps({
                    "product_profiles": [
                        {"file_name": name, "file_id": fid}
                        for name, fid in zip(
                            product_profile_file_names, product_profile_uploaded_ids
                        )
                    ],
                }),
            },
        ],
        functions=[func_spec],
        function_call={"name": "create_competitive_analysis"},
        temperature=0,
    )

    # — parse the returned JSON into your model —
    args_json = completion.choices[0].message.function_call.arguments
    logger.info(f"Received competitive analysis response from OpenAI: {args_json}")

    logger.info("Calling OpenAI chat completion for competitive analysis")
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": instructions},
            {
                "role": "user",
                "content": json.dumps({
                    "product_profiles": [
                        {"file_name": name.name, "file_id": fid}
                        for name, fid in zip(
                            competitor_document_paths, competitor_uploaded_ids
                        )
                    ],
                }),
            },
        ],
        functions=[func_spec],
        function_call={"name": "create_competitive_analysis"},
        temperature=0,
    )

    # — parse the returned JSON into your model —
    args_json = completion.choices[0].message.function_call.arguments
    logger.info(f"Received competitive analysis response from OpenAI: {args_json}")





    analysis = CompetitiveAnalysis.model_validate_json(args_json)
    
    if analysis.confidence_score > 1:
        analysis.confidence_score = analysis.confidence_score / 100.0


    logger.info(
        f"Competitive analysis parsed successfully for competitor {competitor_file_name}"
    )
    return analysis
