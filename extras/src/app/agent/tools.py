import json
import math
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data"


def load_clinics() -> list[dict]:
    with open(DATA_DIR / "clinics.json", "r", encoding="utf-8") as f:
        return json.load(f)


def load_vinmec_processes() -> list[dict]:
    with open(DATA_DIR / "vinmec_processes.json", "r", encoding="utf-8") as f:
        return json.load(f)


def search_clinics_by_city(city: str) -> list[dict]:
    """Tìm phòng khám theo thành phố (hỗ trợ alias)."""
    clinics = load_clinics()
    city_lower = city.lower()
    # Alias mapping for common city names
    aliases = {
        "sài gòn": "hồ chí minh",
        "saigon": "hồ chí minh",
        "sg": "hồ chí minh",
        "hcm": "hồ chí minh",
        "tp hcm": "hồ chí minh",
        "tp.hcm": "hồ chí minh",
        "hn": "hà nội",
        "ha noi": "hà nội",
        "hp": "hải phòng",
        "hai phong": "hải phòng",
        "đn": "đà nẵng",
        "da nang": "đà nẵng",
        "nt": "nha trang",
        "nha trang": "nha trang",
    }
    search_term = aliases.get(city_lower, city_lower)
    return [c for c in clinics if search_term in c["city"].lower() or search_term in c["address"].lower()]


def search_clinics_by_specialty(specialty: str) -> list[dict]:
    """Tìm phòng khám theo chuyên khoa."""
    clinics = load_clinics()
    specialty_lower = specialty.lower()
    return [c for c in clinics if specialty_lower in c["specialties"].lower()]


def find_nearest_clinics(lat: float, lon: float, top_n: int = 3) -> list[dict]:
    """Tìm phòng khám gần nhất dựa trên tọa độ (Haversine)."""
    clinics = load_clinics()
    for c in clinics:
        c["distance_km"] = _haversine(lat, lon, c["latitude"], c["longitude"])
    clinics.sort(key=lambda c: c["distance_km"])
    return clinics[:top_n]


def search_vinmec_process(query: str) -> list[dict]:
    """Tìm quy trình Vinmec theo keyword."""
    processes = load_vinmec_processes()
    query_lower = query.lower()
    results = []
    for p in processes:
        if (query_lower in p["title"].lower()
                or query_lower in p["category"].lower()
                or query_lower in p["content"].lower()):
            results.append(p)
    return results


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))
