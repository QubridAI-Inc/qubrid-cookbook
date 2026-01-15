from typing import Dict, Any, List

def calculate_schedule_readiness(extraction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes extracted JSON for medical completeness required for scheduling.
    
    Returns:
        Dict containing:
            "is_ready": bool
            "missing_fields": List of dicts {medicine, field}
            "low_confidence_fields": List of dicts {medicine, field}
    """
    medicines = extraction.get("medicines", [])
    missing = []
    low_conf = []
    
    # Required fields for a safe schedule
    REQUIRED_FIELDS = ["dosage", "frequency", "duration_days"]
    CONFIDENCE_THRESHOLD = 0.8
    
    for med in medicines:
        med_name = med.get("name", "Unknown Medicine")
        
        # Check for missing fields
        for field in REQUIRED_FIELDS:
            val = med.get(field)
            if val is None or val == "" or val == "N/A" or val == "null":
                missing.append({"medicine": med_name, "field": field})
            
        # Check for low confidence
        # Note: If a med has a total confidence, we use that as a proxy for all fields
        # unless field-level confidence is added in the future.
        m_conf = med.get("confidence", 1.0)
        if m_conf < CONFIDENCE_THRESHOLD:
            # Only add to low_conf if not already in missing
            already_missing = [m["field"] for m in missing if m["medicine"] == med_name]
            for field in REQUIRED_FIELDS:
                if field not in already_missing:
                    low_conf.append({"medicine": med_name, "field": field})

    return {
        "is_ready": len(missing) == 0 and len(low_conf) == 0,
        "missing": missing,
        "low_confidence": low_conf
    }
