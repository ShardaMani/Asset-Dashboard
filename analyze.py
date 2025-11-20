"""Analyze OpenAPI JSON files in data/ and infer FK relationships between schemas.

Reads all JSON files in ../data, extracts components.schemas, then for each schema
finds properties that look like foreign keys (contain 'id' or end with '_Id'/'Id').
It then tries to match those property names to other schema names by normalization.

Run:
  python api_model_gen/analyze_fks.py
"""

from __future__ import annotations

import json
import os
import re
from typing import Dict, List, Set

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


def load_schemas_from_file(path: str) -> tuple[Dict[str, Dict], Dict[str, List[str]]]:
    """Load schemas and also extract relationship paths from OpenAPI paths.
    
    Returns: (schemas_dict, relationships_dict)
    where relationships_dict maps schema_name -> [list of related entity names from paths]
    """
    with open(path, 'r', encoding='utf-8') as f:
        j = json.load(f)
    # many files are a list whose first element contains OpenAPI doc
    if isinstance(j, list) and j:
        doc = j[0]
    elif isinstance(j, dict):
        doc = j
    else:
        return {}, {}
    
    comps = doc.get('components', {})
    schemas = comps.get('schemas', {})
    
    # Extract relationship endpoints from paths
    # Example: /Asset/{collectionIndex}/End_User:get indicates Asset -> End_User relationship
    paths = doc.get('paths', {})
    relationships: Dict[str, Set[str]] = {}
    
    for path_str, path_def in paths.items():
        # Pattern: /<Schema>/{collectionIndex}/<RelatedEntity>:get
        m = re.match(r'^/([^/]+)/\{[^}]+\}/([^:/]+):', path_str)
        if m:
            source = m.group(1)
            target = m.group(2)
            if source not in relationships:
                relationships[source] = set()
            relationships[source].add(target)
    
    # Convert sets to lists
    rel_dict = {k: list(v) for k, v in relationships.items()}
    
    return schemas or {}, rel_dict


def normalize(name: str) -> str:
    return re.sub(r'[^0-9a-z]', '', name.lower())


def collect_all_schemas() -> tuple[Dict[str, Dict], Dict[str, Set[str]]]:
    """Returns (all_schemas, all_relationships)
    
    all_relationships maps schema_name -> set of related entity names from API paths
    """
    all_schemas: Dict[str, Dict] = {}
    all_relationships: Dict[str, Set[str]] = {}
    
    if not os.path.isdir(DATA_DIR):
        print('data directory not found:', DATA_DIR)
        return all_schemas, all_relationships
    
    for fname in os.listdir(DATA_DIR):
        if not fname.endswith('.json'):
            continue
        path = os.path.join(DATA_DIR, fname)
        try:
            schemas, rels = load_schemas_from_file(path)
        except Exception as e:
            print('failed to load', path, e)
            continue
        
        for sname, sdef in schemas.items():
            # avoid overwriting; keep first seen
            if sname not in all_schemas:
                all_schemas[sname] = sdef
        
        for sname, rel_list in rels.items():
            if sname not in all_relationships:
                all_relationships[sname] = set()
            all_relationships[sname].update(rel_list)
    
    return all_schemas, all_relationships


def find_candidate_fks(schemas: Dict[str, Dict], api_relationships: Dict[str, Set[str]]) -> List[Dict[str, str]]:
    """Find FK candidates from both field names and API relationship paths."""
    results = []
    # prepare normalized name map
    norm_to_schema = {normalize(k): k for k in schemas.keys()}

    for sname, sdef in schemas.items():
        props = sdef.get('properties', {}) or {}
        
        # Track which fields we've identified as FKs
        identified_fks = set()
        
        for prop, pdef in props.items():
            if 'id' in prop.lower():
                # candidate FK from naming convention
                prop_norm = normalize(prop)
                matched = None
                
                # Try exact match to schema name
                for candidate_norm, cand in norm_to_schema.items():
                    if candidate_norm in prop_norm or prop_norm in candidate_norm:
                        matched = cand
                        break
                
                # Additional heuristics for common patterns
                if not matched:
                    # Try removing _id or Id suffix and matching
                    clean = re.sub(r'(_id|_Id|Id)$', '', prop, flags=re.IGNORECASE)
                    clean_norm = normalize(clean)
                    if clean_norm in norm_to_schema:
                        matched = norm_to_schema[clean_norm]
                    else:
                        # Try plurals/singulars
                        if clean.endswith('s'):
                            singular = clean[:-1]
                            if normalize(singular) in norm_to_schema:
                                matched = norm_to_schema[normalize(singular)]
                        else:
                            plural = clean + 's'
                            if normalize(plural) in norm_to_schema:
                                matched = norm_to_schema[normalize(plural)]
                
                # Check API paths for confirmation
                confirmed_by_api = False
                if sname in api_relationships:
                    related = api_relationships[sname]
                    # See if any related entity matches this field
                    for rel in related:
                        if normalize(rel) in prop_norm or prop_norm in normalize(rel):
                            matched = rel
                            confirmed_by_api = True
                            break
                
                results.append({
                    'from': sname,
                    'field': prop,
                    'to_guess': matched,
                    'type': pdef.get('type'),
                    'confirmed_by_api': confirmed_by_api,
                    'source': 'api_path' if confirmed_by_api else 'field_name'
                })
                identified_fks.add(prop)
        
        # Add relationships from API paths that don't have obvious _id fields
        if sname in api_relationships:
            for related in api_relationships[sname]:
                # Check if we already captured this via field naming
                found = False
                for fk in results:
                    if fk['from'] == sname and fk['to_guess'] == related:
                        found = True
                        break
                
                if not found:
                    # This is a relationship only visible from API paths
                    results.append({
                        'from': sname,
                        'field': f'<relation to {related}>',
                        'to_guess': related,
                        'type': 'relation',
                        'confirmed_by_api': True,
                        'source': 'api_path_only'
                    })
    
    return results


def main():
    schemas, api_relationships = collect_all_schemas()
    if not schemas:
        print('No schemas found to analyze.')
        return
    
    print(f'Found {len(schemas)} schemas.')
    if api_relationships:
        print(f'Found API relationship paths for {len(api_relationships)} schemas.\n')
    
    print('Listing candidate foreign keys and relationships...\n')
    fks = find_candidate_fks(schemas, api_relationships)
    if not fks:
        print('No candidate FK fields or relationships found.')
        return
    
    # group by from
    by_from = {}
    for f in fks:
        by_from.setdefault(f['from'], []).append(f)

    for src, items in sorted(by_from.items()):
        print(f'Schema: {src}')
        for it in items:
            confirmed = '✓' if it.get('confirmed_by_api') else ' '
            source = it.get('source', 'field_name')
            if source == 'api_path_only':
                print(f"  {confirmed} relationship: {it['to_guess']:30}  (detected from API paths only)")
            else:
                print(f"  {confirmed} field: {it['field']:30}  type: {it.get('type', 'N/A'):8}  -> {it['to_guess']}  (source: {source})")
        print()


if __name__ == '__main__':
    main()
