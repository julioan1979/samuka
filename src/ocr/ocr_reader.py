"""OCR reader module for CashCheck.

Uses pytesseract + OpenCV to extract numeric totals from images of
card machine reports and POS receipts.
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import cv2
import numpy as np
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

# Regex to find Brazilian-style currency values, e.g.  R$ 1.234,56  or  1234,56  or  1234.56
_CURRENCY_RE = re.compile(
    r"(?:R\$\s*)?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})|\d+[.,]\d{2})"
)


def _preprocess_image(image: np.ndarray) -> np.ndarray:
    """Convert to grayscale, denoise, and apply adaptive thresholding."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    return thresh


def _parse_currency(value_str: str) -> float:
    """
    Parse a currency string into a float.

    Handles both comma-as-decimal (1.234,56) and dot-as-decimal (1234.56) formats.
    """
    cleaned = value_str.strip()
    # If both dot and comma present, the last one is the decimal separator
    if "," in cleaned and "." in cleaned:
        # Brazilian format: 1.234,56
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        # Could be 1234,56 (decimal comma) or 1,234 (thousands)
        parts = cleaned.split(",")
        if len(parts) == 2 and len(parts[1]) == 2:
            cleaned = cleaned.replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    return float(cleaned)


def extract_text_from_image(image_path: Union[str, Path]) -> str:
    """Run pytesseract OCR on an image file and return raw text."""
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    img_bgr = cv2.imread(str(image_path))
    if img_bgr is None:
        # Fallback to PIL for formats OpenCV may not support
        pil_img = Image.open(image_path).convert("RGB")
        img_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    processed = _preprocess_image(img_bgr)
    text = pytesseract.image_to_string(processed, lang="por+eng")
    logger.debug("OCR raw text (%d chars) for %s", len(text), image_path.name)
    return text


def extract_values_from_text(text: str) -> List[float]:
    """Return a list of all numeric currency values found in text."""
    matches = _CURRENCY_RE.findall(text)
    values = []
    for m in matches:
        try:
            values.append(_parse_currency(m))
        except ValueError:
            logger.warning("Could not parse currency value: %r", m)
    return values


def extract_total_from_image(image_path: Union[str, Path]) -> Dict[str, Any]:
    """
    High-level function: runs OCR and returns structured results.

    Returns a dict with:
        - raw_text: full OCR output
        - values: all numeric values found
        - suggested_total: the largest value (heuristic for the grand total)
    """
    raw_text = extract_text_from_image(image_path)
    values = extract_values_from_text(raw_text)
    suggested_total: Optional[float] = max(values) if values else None

    result = {
        "raw_text": raw_text,
        "values": values,
        "suggested_total": suggested_total,
    }
    logger.info(
        "OCR result for %s: %d values found, suggested_total=%s",
        Path(image_path).name,
        len(values),
        suggested_total,
    )
    return result
