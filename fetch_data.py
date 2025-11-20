"""Fetch configured endpoints and do a simple FK relationship inference.

Place your `VENDOR_API_KEY` and `API_BASE_URL` in `.env` (see `.env.example`).

The script will:
- Fetch each endpoint (GET) and save the JSON to `api_model_gen/data/<name>.json`.
- Load the samples and run heuristics to guess foreign-key relationships:
  - look for fields named like `<collection>_id` or `<collection>Id`
  - check value overlap between candidate fields and target collection ids

Run:
  python api_model_gen/fetch_and_inspect.py

You can also pass --endpoints to override the built-in list.
"""

from __future__ import annotations

import os
import sys
import json
import argparse
import re
from typing import Any, Dict, List, Set

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

# Standard headers for all API requests
def get_headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
        "X-Role": "admin",
        "X-Locale": "en-US",
        "X-App": "Assets",
        "X-Timezone": "+05:30",
        "X-Hostname": "spaces.iitm.ac.in",
        "X-Authentication": "basic",
    }

DEFAULT_ENDPOINTS = [
    "/api/swagger:get?ns=collections%2FBuildings",
    "/api/swagger:get?ns=collections%2FInstance",
    "/api/swagger:get?ns=collections%2FVendor",
    "/api/swagger:get?ns=collections%2FSRB_Details",
    "/api/swagger:get?ns=collections%2FAsset_Specifications",
    "/api/swagger:get?ns=collections%2FRooms",
    "/api/swagger:get?ns=collections%2FAsset_Coverage_History",
    "/api/swagger:get?ns=collections%2FAsset",
    "/api/swagger:get?ns=collections%2FAsset_Movement",
    "/api/swagger:get?ns=collections%2FAttached_Documents",
    "/api/swagger:get?ns=collections%2FAsset_Condition",
    "/api/swagger:get?ns=collections%2FMaintenance_Log",
    "/api/swagger:get?ns=collections%2Fdepartments",
    "/api/swagger:get?ns=collections%2FPurchase_Order_Details",
]

# Collection data endpoints (to fetch actual records, not just OpenAPI specs)
COLLECTION_DATA_ENDPOINTS = [
    "/api/Asset:list",
    "/api/Instance:list",
    "/api/Buildings:list",
    "/api/Rooms:list",
    "/api/Vendor:list",
    "/api/SRB_Details:list",
    "/api/Purchase_Order_Details:list",
    "/api/Asset_Condition:list",
    "/api/Asset_Coverage_History:list",
    "/api/Asset_Movement:list",
    "/api/Asset_Specifications:list",
    "/api/Attached_Documents:list",
    "/api/Maintenance_Log:list",
    "/api/departments:list",
]



def safe_name_from_endpoint(ep: str) -> str:
    # extract last part after ns=collections%2F... or fallback to sanitized path
    m = re.search(r"ns=collections%25?2F([^&]+)", ep)
    if m:
        return re.sub(r"[^0-9A-Za-z_]", "_", m.group(1))
    # else fallback
    s = ep.strip("/ ")
    s = re.sub(r"[^0-9A-Za-z_]", "_", s)
    return s[:64]


def fetch_endpoint(base: str, ep: str, headers: Dict[str, str]):
    """Return a tuple (status_code, parsed_json_or_text, raw_text, url)"""
    url = base.rstrip("/") + "/" + ep.lstrip("/")
    print(f"Fetching {url}")
    try:
        r = requests.get(url, headers=headers, timeout=20)
    except Exception as e:
        return None, None, f"Request error: {e}", url
    raw = r.text
    parsed = None
    try:
        parsed = r.json()
    except Exception:
        parsed = raw
    return r.status_code, parsed, raw, url


def ensure_data_dir():
    d = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(d, exist_ok=True)
    return d


def normalize_id_field(item: Dict[str, Any]) -> str | None:
    # common id names
    for k in ("id", "_id", "Id", "ID"):
        if k in item:
            return k
    # otherwise try to find field that looks like key (endswith _id)
    for k in item.keys():
        if k.lower().endswith("_id") or k.lower().endswith("id"):
            return k
    return None


def collect_ids(items: List[Dict[str, Any]]) -> Set[Any]:
    ids = set()
    for it in items:
        if not isinstance(it, dict):
            continue
        k = normalize_id_field(it)
        if k and it.get(k) is not None:
            ids.add(stringify(it.get(k)))
    return ids


def find_fk_candidates(all_collections: Dict[str, List[Dict[str, Any]]]):
    # For each collection A, for each field f, check if f's values overlap with IDs of some collection B
    results = []
    col_ids = {name: collect_ids(items) for name, items in all_collections.items()}

    for a_name, a_items in all_collections.items():
        if not a_items or not isinstance(a_items, list):
            continue
        sample = next((it for it in a_items if isinstance(it, dict)), None)
        if not sample:
            continue
    for field in sample.keys():
            # skip obvious id field of the collection
            if field.lower() in ("id", "_id"):
                continue
            # gather values for this field
            vals = set()
            for it in a_items:
                if not isinstance(it, dict):
                    continue
                v = it.get(field)
                if v is not None:
                    vals.add(stringify(v))
            if not vals:
                continue
            # compare to each collection's ids
            for b_name, ids in col_ids.items():
                if not ids:
                    continue
                inter = vals.intersection(ids)
                if inter:
                    # Heuristic: field name matches target name or endswith _id
                    name_match = False
                    if field.lower().endswith("_id") and field.lower().startswith(b_name.lower()[:3]):
                        name_match = True
                    if b_name.lower() in field.lower() or field.lower() in b_name.lower():
                        name_match = True
                    results.append({
                        "from_collection": a_name,
                        "field": field,
                        "to_collection": b_name,
                        "matches": len(inter),
                        "sample_matches": list(inter)[:5],
                        "name_match": name_match,
                    })
    return results


def stringify(v: Any) -> str:
    """Convert a value to a stable string for set membership comparison.

    - If primitive, return str(v)
    - If dict, try to extract common id fields, else JSON dump
    - If list, JSON dump
    """
    if v is None:
        return "<null>"
    if isinstance(v, (str, int, float, bool)):
        return str(v)
    if isinstance(v, dict):
        # try common id fields
        for k in ("id", "_id", "Id", "ID", "serial_number", "asset_rfid_tag", "rfid", "serial"):
            if k in v and v[k] is not None:
                return str(v[k])
        try:
            return json.dumps(v, sort_keys=True, default=str)
        except Exception:
            return str(v)
    try:
        return json.dumps(v, sort_keys=True, default=str)
    except Exception:
        return str(v)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoints", help="Comma-separated endpoints to fetch (override defaults)")
    parser.add_argument("--fetch-data", action="store_true", help="Fetch actual collection data (not just OpenAPI specs)")
    args = parser.parse_args()

    if not API_KEY or not BASE_URL:
        print("Please ensure API_KEY and BASE_URL are set in your .env file.")
        sys.exit(1)

    if args.endpoints:
        endpoints = [e.strip() for e in args.endpoints.split(",") if e.strip()]
    else:
        if args.fetch_data:
            endpoints = COLLECTION_DATA_ENDPOINTS
            print("Fetching actual collection data records...")
        else:
            endpoints = DEFAULT_ENDPOINTS
            print("Fetching OpenAPI specs...")

    headers = get_headers()
    data_dir = ensure_data_dir()

    all_collections: Dict[str, List[Dict[str, Any]]] = {}

    for ep in endpoints:
        name = safe_name_from_endpoint(ep)
        status, content, raw_text, url = fetch_endpoint(BASE_URL, ep, headers)
        if status is None:
            print(f"Failed to fetch {ep}: {raw_text}")
            # save network error
            errpath = os.path.join(data_dir, f"errors_{safe_name_from_endpoint(ep)}.txt")
            with open(errpath, "w", encoding="utf-8") as ef:
                ef.write(raw_text)
            continue

        if status != 200:
            print(f"Failed to fetch {ep}: {status} Server Error for url: {url}")
            # save full response body for debugging
            errpath = os.path.join(data_dir, f"errors_{safe_name_from_endpoint(ep)}.txt")
            with open(errpath, "w", encoding="utf-8") as ef:
                ef.write(f"URL: {url}\nStatus: {status}\n\nResponse body:\n")
                ef.write(raw_text)
            # still attempt to use parsed if it contains useful JSON (some APIs return error object)
            if not isinstance(content, (list, dict)):
                # skip adding to collections
                print(f"Saved error response to {errpath}")
                continue
        # If server error returned a JSON error like "Cannot read properties of undefined (reading 'name')",
        # try fallback collection endpoints (common pattern) to see if direct collection API works.
        if status >= 500:
            # try to extract collection name from the endpoint
            m = re.search(r"ns=collections%25?2F([^&]+)", ep)
            if m:
                coll = m.group(1)
                # URL decode percent-encodings (simple)
                coll = coll.replace('%20', ' ').replace('%2F', '/').replace('%252F','/')
                # try direct collection endpoints
                fallbacks = [f"/api/collections/{coll}", f"/api/collections/{coll}?limit=100"]
                for fb in fallbacks:
                    print(f"Attempting fallback {fb}")
                    s2, content2, raw2, url2 = fetch_endpoint(BASE_URL, fb, headers)
                    errname = safe_name_from_endpoint(ep) + "_fallback"
                    if s2 is None:
                        # network error, save
                        ef = os.path.join(data_dir, f"errors_{errname}.txt")
                        with open(ef, 'w', encoding='utf-8') as f:
                            f.write(str(content2))
                        continue
                    if s2 != 200:
                        ef = os.path.join(data_dir, f"errors_{errname}.txt")
                        with open(ef, 'w', encoding='utf-8') as f:
                            f.write(f"URL: {url2}\nStatus: {s2}\n\nResponse body:\n")
                            f.write(raw2)
                        print(f"Fallback {fb} returned status {s2}, saved to {ef}")
                        continue
                    # success: use content2 as parsed items
                    print(f"Fallback {fb} succeeded; saving to data and using for FK inference")
                    items2 = []
                    if isinstance(content2, dict):
                        if "items" in content2 and isinstance(content2["items"], list):
                            items2 = content2["items"]
                        elif "results" in content2 and isinstance(content2["results"], list):
                            items2 = content2["results"]
                        else:
                            items2 = [content2]
                    elif isinstance(content2, list):
                        items2 = content2
                    outpath2 = os.path.join(data_dir, f"{safe_name_from_endpoint(fb)}.json")
                    with open(outpath2, "w", encoding="utf-8") as f:
                        json.dump(items2, f, indent=2, default=str)
                    all_collections[safe_name_from_endpoint(ep)] = items2
                    # break fallback loop
                    break
        

        # normalize into list of dicts if possible
        items: List[Dict[str, Any]] = []
        if isinstance(content, dict):
            # try common patterns - NocoBase API wraps in {"data": [...]}
            if "data" in content and isinstance(content["data"], list):
                items = content["data"]
            elif "items" in content and isinstance(content["items"], list):
                items = content["items"]
            elif "results" in content and isinstance(content["results"], list):
                items = content["results"]
            else:
                # if single object, wrap
                items = [content]
                items = [content]
        elif isinstance(content, list):
            items = content
        else:
            # not JSON-serializable structure we can inspect
            print(f"Endpoint {ep} returned non-JSON structure; saved to file but skipping FK inference.")
            items = []

        # save
        outpath = os.path.join(data_dir, f"{name}.json")
        with open(outpath, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, default=str)
        print(f"Saved {len(items)} items to {outpath}")
        all_collections[name] = items

    # run FK inference
    fk = find_fk_candidates(all_collections)
    if not fk:
        print("No candidate foreign-key relationships were detected by heuristics.")
        return

    print("\nCandidate foreign-key relationships:\n")
    for rel in sorted(fk, key=lambda x: (-x["matches"], x["from_collection"])):
        print(f"{rel['from_collection']}.{rel['field']}  ->  {rel['to_collection']}  (matches: {rel['matches']})  name_match={rel['name_match']}")
        print(f"  sample matches: {rel['sample_matches']}\n")


if __name__ == '__main__':
    main()
