# Asset Dashboard - Data Analysis Summary

## ✅ Completed Tasks

### 1. API Discovery & Schema Analysis
- ✓ Successfully connected to NocoBase API at `https://spaces.iitm.ac.in`
- ✓ Fetched OpenAPI specifications for all 14 collections
- ✓ Fetched actual collection data from all endpoints
- ✓ Verified FK relationships in live data

### 2. Foreign Key Relationships Detected

#### ✓ Verified Working Relationships (100% match rate):
1. **Asset.Building_Id → Buildings** (8 values, 2 unique buildings)
2. **Rooms.Building_id → Buildings** (20 values, all to Building ID 1)
3. **Instance.Asset_Id → Asset** (12 values, 3 unique assets)
4. **Asset_Condition.asset_id → Asset** (5 values, 5 assets)
5. **Asset_Coverage_History.Asset_Id → Asset** (5 values, 5 assets)
6. **Asset_Specifications.Asset_Id → Asset** (3 values, 1 asset)

#### ⚠ Partial Matches (50-67% match rate - orphaned FKs exist):
1. **Asset.Room_Id → Rooms** (50.0% match - some rooms not in Rooms table yet)
2. **Asset.SRB_Id → SRB_Details** (66.7% match - some SRBs not fetched in sample)

#### ✗ Issues Found (0% match - data type mismatch):
1. **SRB_Details.Vendor_Id → Vendor** (0% - Vendor_Id is string, Vendor.id is int)
2. **Purchase_Order_Details.Vendor_Id → Vendor** (0% - same issue)

**Note**: The Vendor_Id mismatch suggests the schema uses a custom `Vendor_Id` string field instead of the integer `id` field as FK. Need to check Vendor schema for proper FK field.

### 3. Data Statistics

| Collection | Records | Unique IDs | Notes |
|-----------|---------|------------|-------|
| Asset | 9 | 9 | Main entity |
| Instance | 12 | 12 | Asset instances |
| Buildings | 2 | 2 | CC & EU buildings |
| Rooms | 20 | 20 | Rooms in buildings |
| Vendor | 20 | 20 | Vendor master |
| SRB_Details | 20 | 20 | Store requisitions |
| Purchase_Order_Details | 20 | 20 | Purchase orders |
| Asset_Condition | 5 | 5 | Condition tracking |
| Asset_Coverage_History | 5 | 5 | Warranty/AMC |
| Asset_Specifications | 3 | 3 | Tech specs |
| Asset_Movement | 0 | 0 | No data yet |
| Attached_Documents | 0 | 0 | No data yet |
| Maintenance_Log | 0 | 0 | No data yet |
| departments | 0 | 0 | No data yet |

### 4. API Endpoints (Working)

#### Collection Data (Records):
```
GET /api/Asset:list
GET /api/Instance:list
GET /api/Buildings:list
GET /api/Rooms:list
GET /api/Vendor:list
GET /api/SRB_Details:list
GET /api/Purchase_Order_Details:list
GET /api/Asset_Condition:list
GET /api/Asset_Coverage_History:list
GET /api/Asset_Movement:list
GET /api/Asset_Specifications:list
GET /api/Attached_Documents:list
GET /api/Maintenance_Log:list
GET /api/departments:list
```

#### OpenAPI Specs:
```
GET /api/swagger:get?ns=collections%2F<CollectionName>
```

### 5. Required Headers (Confirmed Working)
```json
{
  "Authorization": "Bearer <API_KEY>",
  "Accept": "application/json",
  "X-Role": "admin",
  "X-Locale": "en-US",
  "X-App": "Assets",
  "X-Timezone": "+05:30",
  "X-Hostname": "spaces.iitm.ac.in",
  "X-Authentication": "basic"
}
```

## Data Model (Core Entities)

```
Building (2 records)
  ├── id (PK)
  └── Building_Name

Rooms (20 records)
  ├── id (PK)
  ├── Building_id (FK → Buildings.id) ✓
  └── Room_Number

Asset (9 records)
  ├── id (PK)
  ├── Asset_Name
  ├── Building_Id (FK → Buildings.id) ✓
  ├── Room_Id (FK → Rooms.id) ⚠
  ├── SRB_Id (FK → SRB_Details.id) ⚠
  ├── PO_Id (FK → Purchase_Order_Details.id)
  ├── end_user_id (FK → users.id)
  ├── Asset_RFID_Tag
  ├── Serial_Number
  ├── Model_Number
  ├── Operational_Purpose
  ├── is_active
  └── Is_registered

Instance (12 records)
  ├── id (PK)
  ├── Asset_Id (FK → Asset.id) ✓
  ├── Asset_RFID_Tag
  ├── Serial_Number
  └── Asset_health

Asset_Condition (5 records)
  ├── id (PK)
  └── asset_id (FK → Asset.id) ✓

Asset_Coverage_History (5 records)
  ├── id (PK)
  ├── Asset_Id (FK → Asset.id) ✓
  ├── Type_of_coverage
  ├── start_date
  └── end_date

Asset_Specifications (3 records)
  ├── id (PK)
  └── Asset_Id (FK → Asset.id) ✓

SRB_Details (20 records)
  ├── id (PK)
  ├── SRB_Number
  ├── SRB_Date
  ├── Vendor_Id (FK → Vendor.?) ✗
  ├── Po_Id
  └── Amount

Vendor (20 records)
  ├── id (PK)
  ├── Vendor_Id (custom string ID?)
  ├── Vendor_name
  └── Vendor_Contact

Purchase_Order_Details (20 records)
  ├── id (PK)
  ├── PODate
  ├── Vendor_Id (FK → Vendor.?) ✗
  └── PurchaseTotal
```

## Tools Created

1. **analyze.py** - Detects FK relationships from OpenAPI specs (both field names and API paths)
2. **fetch_data.py** - Fetches collection data with proper headers
3. **verify_fks.py** - Verifies FK relationships in actual data
4. **FK_RELATIONSHIPS.md** - Documentation of all detected relationships

## Next Steps for Dashboard

### Immediate Actions:
1. ✅ **Data contract defined** - We know the schema and endpoints
2. ⏭️ **Choose stack** - Recommend: React + TypeScript + Vite + Tailwind + React Query
3. ⏭️ **Create backend proxy** - Node/Express or Python/FastAPI to:
   - Store API key securely
   - Add caching layer
   - Expose clean REST endpoints to frontend
   - Handle pagination
   - Aggregate stats

### Dashboard Features to Build:

#### 1. Overview/Stats Page:
- Total assets count
- Assets by Building (pie/bar chart)
- Assets by Operational Purpose
- Active vs Inactive assets
- Recently added assets

#### 2. Asset List Page:
- Searchable/filterable table
- Columns: ID, Name, Building, Room, Status, Category
- Click → Asset detail

#### 3. Asset Detail Page:
- All asset fields
- Related Instance records
- Condition history
- Coverage (Warranty/AMC) timeline
- Specifications
- SRB & PO details
- Documents (when available)

#### 4. Location View:
- Building → Rooms → Assets hierarchy
- Map view (if geo coordinates available)

#### 5. Reports:
- Assets by category
- Coverage expiring soon
- Verification due

### API Endpoints to Create (Backend Proxy):

```typescript
// Stats
GET /api/stats/summary
GET /api/stats/by-building
GET /api/stats/by-category
GET /api/stats/coverage-expiring?days=90

// Assets
GET /api/assets?page=1&pageSize=50&search=&building=&status=
GET /api/assets/:id
GET /api/assets/:id/instances
GET /api/assets/:id/condition-history
GET /api/assets/:id/coverage
GET /api/assets/:id/specifications
GET /api/assets/:id/srb-details

// Locations
GET /api/buildings
GET /api/buildings/:id/rooms
GET /api/buildings/:id/assets
GET /api/rooms/:id/assets
```

## Sample Data for Testing

Asset #1:
```json
{
  "id": 11,
  "Asset_Name": "Server/Workstation : Intel Xeon dual processor...",
  "Building_Id": null,
  "Room_Id": 4,
  "SRB_Id": 3,
  "is_active": "Yes",
  "Operational_Purpose": ["Research"]
}
```

Buildings:
```json
[
  {"id": 1, "Building_Name": "Computer Center"},
  {"id": 2, "Building_Name": "Engineering Unit"}
]
```

## Issues to Resolve

1. **Vendor_Id mismatch**: Need to clarify if Vendor uses custom string ID or integer id
2. **Orphaned FKs**: Some Room_Id and SRB_Id values don't match (API may not return full dataset with default pagination)
3. **Empty collections**: Asset_Movement, Attached_Documents, Maintenance_Log have no records yet

## Commands Reference

```powershell
# Analyze OpenAPI schemas and detect FKs
python analyze.py

# Fetch all collection data
python fetch_data.py --fetch-data

# Fetch specific endpoint
python fetch_data.py --fetch-data --endpoints "/api/Asset:list?pageSize=10"

# Verify FK relationships in fetched data
python verify_fks.py
```

---

**Status**: ✅ Data analysis complete. Ready to build dashboard!
