# Quick Start Guide - Asset Dashboard

## What We Have

✅ **API Connection Working**
- Base URL: `https://spaces.iitm.ac.in`
- All required headers configured
- 14 collections available
- OpenAPI specs + actual data fetched

✅ **FK Relationships Mapped**
- 6 relationships verified (100% match)
- 2 relationships partially working (orphaned FKs)
- Full relationship diagram in `FK_RELATIONSHIPS.md`

✅ **Sample Data Available**
- 9 Assets
- 12 Instances
- 2 Buildings
- 20 Rooms
- 20 Vendors
- 20 SRB Details
- See `data/` folder for JSON files

## Files in This Project

| File | Purpose |
|------|---------|
| `analyze.py` | Analyze OpenAPI specs, detect FK relationships |
| `fetch_data.py` | Fetch collection data with proper headers |
| `verify_fks.py` | Verify FK integrity in actual data |
| `FK_RELATIONSHIPS.md` | Full FK documentation |
| `ANALYSIS_SUMMARY.md` | Complete analysis results |
| `data/` | All fetched JSON data |
| `.env` | API credentials (API_KEY, BASE_URL) |
| `requirements.txt` | Python dependencies |

## Quick Commands

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Analyze schemas
python analyze.py

# Fetch all data
python fetch_data.py --fetch-data

# Verify relationships
python verify_fks.py
```

## Next: Build the Dashboard

### Recommended Stack:
- **Frontend**: React + TypeScript + Vite
- **UI**: Tailwind CSS + shadcn/ui
- **Charts**: Recharts or Chart.js
- **Data**: React Query (TanStack Query)
- **Backend Proxy**: Node.js + Express (or Python FastAPI)

### Why Backend Proxy?
- Keep API key secure (never in frontend)
- Add caching layer
- Handle rate limits
- Clean up API responses
- Aggregate stats endpoints

### Dashboard Pages to Build:

1. **Overview** - Stats tiles, charts (assets by building, category, status)
2. **Asset List** - Searchable table with filters
3. **Asset Detail** - Full asset info + related records
4. **Location View** - Buildings → Rooms → Assets
5. **Reports** - Coverage expiring, verification due

### Endpoints to Create (Backend):

```
GET /api/stats/summary
GET /api/assets?page=1&search=&building=&status=
GET /api/assets/:id
GET /api/buildings
GET /api/buildings/:id/rooms
```

## Environment Variables Needed

```env
# .env file
API_KEY=your_api_key_here
BASE_URL=https://spaces.iitm.ac.in
```

## Key FK Relationships (for Dashboard Joins)

```
Asset
  → Buildings (Building_Id)
  → Rooms (Room_Id)
  → SRB_Details (SRB_Id)
  
Instance
  → Asset (Asset_Id)
  
Rooms
  → Buildings (Building_id)
  
Asset_Condition
  → Asset (asset_id)
  
Asset_Coverage_History
  → Asset (Asset_Id)
```

## Sample API Response Structure

**NocoBase API wraps responses in `{"data": [...]}`**

Example:
```json
{
  "data": [
    {
      "id": 11,
      "Asset_Name": "Server",
      "Building_Id": 1,
      "Room_Id": 4,
      "is_active": "Yes"
    }
  ]
}
```

Your backend should extract `.data` and pass clean arrays/objects to frontend.

## Issues to Note

1. **Vendor_Id** field is string type, not integer FK
2. Some **Room_Id** and **SRB_Id** values are orphaned (target records not in sample)
3. Empty collections: **Asset_Movement**, **Attached_Documents**, **Maintenance_Log**

---

**Ready to scaffold the dashboard? Tell me and I'll create the React + Express starter!**
