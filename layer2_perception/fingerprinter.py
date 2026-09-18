import hashlib
import json
from typing import List
from common.models import UIElement

def compute_structural_fingerprint(elements: List[UIElement]) -> str:
    """
    Computes a canonical SHA-256 fingerprint hash representing the structural
    skeleton of a screen.
    
    INVARIANCE GUARANTEE:
    - Independent of dynamic runtime text (e.g. changing product titles, prices, counters, user names).
    - Dependent on hierarchy depth, view classes, resource-id layout patterns, and interactive capabilities.
    - Two different instances of the same screen with dynamic feed items produce the exact same fingerprint.
    """
    if not elements:
        return "scr_empty_00000000"

    structural_tokens = []
    for el in elements:
        # Normalize resource ID to remove package name prefix if present
        clean_res_id = el.resource_id.split("/")[-1] if el.resource_id and "/" in el.resource_id else (el.resource_id or "")
        
        # Token contains only structural and semantic capabilities, NEVER dynamic text
        token = (
            el.depth,
            el.class_name,
            clean_res_id,
            1 if el.clickable else 0,
            1 if el.editable else 0,
            1 if el.scrollable else 0,
            # Approximate relative vertical location (top/middle/bottom bucket) to preserve layout shape
            min(10, max(0, el.bounds.top // 240))
        )
        structural_tokens.append(token)

    # Serialize canonical JSON and hash
    serialized = json.dumps(structural_tokens, sort_keys=True)
    hash_digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]
    return f"scr_{hash_digest}"
