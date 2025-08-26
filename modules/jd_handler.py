import json
from typing import List, Dict

_jd_cache = None

def load_predefined_jds(json_path: str = "data/predefined_jds.json") -> Dict[str, str]:
    global _jd_cache
    if _jd_cache is not None:
        return _jd_cache
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            _jd_cache = json.load(f)
        return _jd_cache
    except Exception as e:
        print(f"Error loading predefined JDs: {e}")
        return {}

def get_job_roles(json_path: str = "data/predefined_jds.json") -> List[str]:
    jd_dict = load_predefined_jds(json_path)
    # Preserve deterministic order for UI elements
    return list(jd_dict.keys())

def get_description_for_role(role: str, json_path: str = "data/predefined_jds.json") -> str:
    jd_dict = load_predefined_jds(json_path)
    return jd_dict.get(role, "")
