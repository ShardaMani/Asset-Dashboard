"""Verify FK relationships in actual fetched data.

This script reads the actual collection data (from :list endpoints)
and checks if FK values match actual IDs in target collections.
"""

import json
import os
from collections import defaultdict

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


def load_collection(filename):
    """Load a collection JSON file."""
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_ids(collection):
    """Extract all ID values from a collection."""
    return {item.get('id') for item in collection if isinstance(item, dict) and item.get('id') is not None}


def main():
    # Load all collections
    collections = {
        'Asset': load_collection('api_Asset_list.json'),
        'Instance': load_collection('api_Instance_list.json'),
        'Buildings': load_collection('api_Buildings_list.json'),
        'Rooms': load_collection('api_Rooms_list.json'),
        'Vendor': load_collection('api_Vendor_list.json'),
        'SRB_Details': load_collection('api_SRB_Details_list.json'),
        'Purchase_Order_Details': load_collection('api_Purchase_Order_Details_list.json'),
        'Asset_Condition': load_collection('api_Asset_Condition_list.json'),
        'Asset_Coverage_History': load_collection('api_Asset_Coverage_History_list.json'),
        'Asset_Specifications': load_collection('api_Asset_Specifications_list.json'),
    }
    
    # Extract IDs
    all_ids = {name: extract_ids(coll) for name, coll in collections.items()}
    
    print("Collection Sizes:")
    for name, coll in collections.items():
        print(f"  {name}: {len(coll)} records, {len(all_ids[name])} unique IDs")
    print()
    
    # Define FK relationships to verify (based on OpenAPI analysis)
    fk_checks = [
        ('Asset', 'Building_Id', 'Buildings'),
        ('Asset', 'Room_Id', 'Rooms'),
        ('Asset', 'SRB_Id', 'SRB_Details'),
        ('Rooms', 'Building_id', 'Buildings'),
        ('Instance', 'Asset_Id', 'Asset'),
        ('Asset_Condition', 'asset_id', 'Asset'),
        ('Asset_Coverage_History', 'Asset_Id', 'Asset'),
        ('Asset_Specifications', 'Asset_Id', 'Asset'),
        ('SRB_Details', 'Vendor_Id', 'Vendor'),
        ('Purchase_Order_Details', 'Vendor_Id', 'Vendor'),
    ]
    
    print("FK Relationship Verification:\n")
    
    for source_name, fk_field, target_name in fk_checks:
        source_coll = collections.get(source_name, [])
        target_ids = all_ids.get(target_name, set())
        
        if not source_coll:
            print(f"⚠ {source_name}.{fk_field} → {target_name}: No source data")
            continue
        
        if not target_ids:
            print(f"⚠ {source_name}.{fk_field} → {target_name}: No target IDs")
            continue
        
        # Extract FK values
        fk_values = []
        null_count = 0
        for item in source_coll:
            if not isinstance(item, dict):
                continue
            val = item.get(fk_field)
            if val is None:
                null_count += 1
            else:
                fk_values.append(val)
        
        if not fk_values:
            print(f"⚠ {source_name}.{fk_field} → {target_name}: All values are NULL ({null_count} records)")
            continue
        
        # Check matches
        fk_set = set(fk_values)
        
        # Handle string vs int comparison (Vendor_Id is string)
        if fk_field == 'Vendor_Id':
            # Convert target IDs to strings for comparison
            target_ids_str = {str(x) for x in target_ids}
            matches = fk_set.intersection(target_ids_str)
            orphans = fk_set - target_ids_str
        else:
            matches = fk_set.intersection(target_ids)
            orphans = fk_set - target_ids
        
        match_pct = (len(matches) / len(fk_set) * 100) if fk_set else 0
        
        if match_pct == 100:
            status = "✓"
        elif match_pct >= 50:
            status = "⚠"
        else:
            status = "✗"
        
        print(f"{status} {source_name}.{fk_field} → {target_name}:")
        print(f"    {len(fk_values)} FK values, {null_count} NULLs")
        print(f"    {len(matches)}/{len(fk_set)} unique values match target IDs ({match_pct:.1f}%)")
        
        if orphans:
            print(f"    ⚠ Orphaned FK values (no matching target): {list(orphans)[:5]}")
        
        # Sample matches
        if matches:
            sample = list(matches)[:3]
            print(f"    Sample matching IDs: {sample}")
        print()
    
    # Show sample records for manual inspection
    print("\n=== Sample Asset Records ===")
    for i, asset in enumerate(collections['Asset'][:3]):
        print(f"\nAsset #{i+1}:")
        print(f"  id: {asset.get('id')}")
        print(f"  Asset_Name: {asset.get('Asset_Name')}")
        print(f"  Building_Id: {asset.get('Building_Id')} (Buildings has IDs: {sorted(all_ids['Buildings'])})")
        print(f"  Room_Id: {asset.get('Room_Id')}")
        print(f"  SRB_Id: {asset.get('SRB_Id')}")


if __name__ == '__main__':
    main()
