from typing import Any
from fastapi import APIRouter
from core.processor.migros import MigrosExtractor
from core.processor.detective import generate_analysis

router = APIRouter(prefix="/barcode", tags=["barcode"])


@router.get("/{code}")
async def process_barcode(code: str) -> dict[str, Any] | None:
    """Get information about a product by barcode.

    Parameters
    ----------
    code: str
        Value of barcode.

    Returns
    -------
    Optional[dict[str, Any]]
        A dictionary containing information about the product if found, or None otherwise.
    """
    extractor = MigrosExtractor()
    product_id = extractor.get_product_id(code)
    if product_id:
        product_info = extractor.get_product_info(product_id)
        if product_info:
            new_dict = dict(product_info)
            new_dict.pop("img")
            analysis = generate_analysis(new_dict)
            product_info["detective"] = analysis
        return product_info
    else:
        return None
