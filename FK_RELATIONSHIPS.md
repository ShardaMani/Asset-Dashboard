# Asset Management API - Foreign Key Relationships

## Overview
This document summarizes the foreign key relationships detected from the OpenAPI specifications. Relationships marked with ✓ are confirmed by API relationship endpoints.

## Core Entities and Relationships

### Asset (Main Entity)
**Direct Foreign Keys:**
- ✓ `end_user_id` → End_User (confirmed by API)
- ✓ `SRB_Id` → SRB (confirmed by API)
- `PO_Id` → Purchase Order (not directly confirmed)
- ✓ `Room_Id` → Room (confirmed by API)
- ✓ `Building_Id` → Building (confirmed by API)

**Has Many (Relationships via API paths):**
- ✓ Asset_Condition (one-to-many)
- ✓ Maintenance_Log (one-to-many)
- ✓ Instance (one-to-many)
- ✓ Attached_Documents (one-to-many)
- ✓ Asset_Specifications (one-to-many)
- ✓ Asset_Coverage_History (one-to-many)
- ✓ Asset_Movement (one-to-many)
- ✓ Purchase_Order (relationship)

### Instance (Asset Instance)
**Foreign Keys:**
- ✓ `Asset_RFID_Tag` → Asset (confirmed by API)
- ✓ `Asset_Id` → Asset (confirmed by API)

### Buildings
**Has Many:**
- ✓ Asset (one-to-many)
- ✓ Rooms (one-to-many)

### Rooms
**Foreign Keys:**
- ✓ `Building_id` → Building (confirmed by API)

**Has Many:**
- ✓ Asset (one-to-many)

### Vendor
**Has Many:**
- ✓ SRBDetails (one-to-many)
- ✓ Purchase_Order_Details (one-to-many)

### SRB_Details
**Foreign Keys:**
- ✓ `Vendor_Id` → Vendor (confirmed by API)
- `Po_Id` → Purchase Order
- ✓ `Asset_Instance_Id` → Asset (confirmed by API)

**Has Many:**
- ✓ Purchase_Order_Number (relationship)

### Purchase_Order_Details
**Foreign Keys:**
- ✓ `Vendor_Id` → Vendor (confirmed by API)

**Has Many:**
- ✓ SRBDetails (one-to-many)
- ✓ Asset (one-to-many)

### Asset_Condition
**Foreign Keys:**
- ✓ `asset_id` → Asset (confirmed by API)

### Asset_Coverage_History
**Foreign Keys:**
- ✓ `Asset_Id` → Asset (confirmed by API)

### Asset_Movement
**Foreign Keys:**
- ✓ `Asset_Id` → Asset (confirmed by API)
- `assigned_user_id` → User (not confirmed)

### Asset_Specifications
**Foreign Keys:**
- ✓ `Asset_Id` → Asset (confirmed by API)

### Attached_Documents
**Foreign Keys:**
- ✓ `Asset_Id` → Asset (confirmed by API)

### Maintenance_Log
**Foreign Keys:**
- ✓ `Asset_Id` → Asset (confirmed by API)

### Departments
**Relationships:**
- ✓ owners
- ✓ roles
- ✓ children
- ✓ parent
- ✓ members

## Data Model Summary

```
Building
  └── Rooms (has many)
       └── Asset (has many)
            ├── Instance (has many)
            ├── Asset_Condition (has many)
            ├── Asset_Coverage_History (has many)
            ├── Asset_Movement (has many)
            ├── Asset_Specifications (has many)
            ├── Attached_Documents (has many)
            ├── Maintenance_Log (has many)
            ├── End_User (belongs to)
            └── SRB_Details (belongs to)
                 ├── Vendor (belongs to)
                 └── Purchase_Order (belongs to)
                      └── Vendor (belongs to)
```

## API Endpoints for Data Fetching

To fetch actual collection data (not OpenAPI specs), use these endpoints:

```
/api/Asset:list
/api/Instance:list
/api/Buildings:list
/api/Rooms:list
/api/Vendor:list
/api/SRB_Details:list
/api/Purchase_Order_Details:list
/api/Asset_Condition:list
/api/Asset_Coverage_History:list
/api/Asset_Movement:list
/api/Asset_Specifications:list
/api/Attached_Documents:list
/api/Maintenance_Log:list
/api/departments:list
```

## Usage

### Fetch OpenAPI Specifications (default)
```powershell
python inspect.py
```

### Fetch Actual Collection Data
```powershell
python inspect.py --fetch-data
```

### Analyze Schemas and FK Relationships
```powershell
python analyze.py
```

## Notes
- Fields ending with `Id`, `_id`, or `_Id` are FK candidates
- API paths like `/Asset/{id}/End_User:get` confirm FK relationships
- `createdById` and `updatedById` are audit fields referencing users
