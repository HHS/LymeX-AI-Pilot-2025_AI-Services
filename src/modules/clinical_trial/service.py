from typing import List
from beanie import PydanticObjectId
from .client import search_trials
from .normalize import to_internal
from .model import ClinicalTrial

async def refresh_trials(product_id: str, condition: str, sponsors: List[str]) -> int:
    """
    Fetch trials for (condition × sponsors), upsert by (product_id, nct_id),
    and return total rows inserted/updated.
    """
    total = 0
    for sponsor in sponsors:
        studies = await search_trials(condition=condition, sponsor=sponsor)
        for s in studies:
            doc = to_internal(s, product_id=product_id)
            nct_id = doc.get("nct_id")
            if not nct_id:
                continue
            existing = await ClinicalTrial.find_one({"product_id": str(product_id), "nct_id": nct_id})
            if existing:
                for k, v in doc.items():
                    setattr(existing, k, v)
                await existing.save()
            else:
                await ClinicalTrial(**doc).insert()
            total += 1
    return total
