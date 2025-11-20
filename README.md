# Asset Management Dashboard

A full-stack dashboard for visualizing asset data from NocoBase API, showing statistics on SRB Details amounts and asset categorization.

## Features

- 📊 **SRB Amount Distribution**: View assets categorized by value ranges (>1 Crore, 10L-1Cr, 1L-10L, <1L)
- 📈 **Interactive Charts**: Bar charts and pie charts for data visualization
- 🏢 **Asset Categories**: Group and analyze assets by Asset Code
- 📱 **Responsive Design**: Built with Tailwind CSS for all screen sizes
- ⚡ **Fast & Cached**: Backend caching for improved performance

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development
- **Tailwind CSS** for styling
- **Recharts** for data visualization
- **React Query** for data fetching & caching
- **Axios** for API calls

### Backend
- **Node.js** with Express
- **NocoBase API** integration
- **node-cache** for response caching
- **CORS** enabled

## Project Structure

```
Asset Dashboard/
├── backend/
│   ├── server.js          # Express server with API routes
│   ├── package.json       # Backend dependencies
│   └── .env.example       # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Dashboard.tsx    # Main dashboard component
│   │   ├── App.tsx              # App root
│   │   ├── main.tsx             # Entry point
│   │   └── index.css            # Global styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
├── data/                  # API response JSON files
├── scripts/               # Python scripts for data analysis
└── .env                   # Environment variables (create from backend/.env.example)
```

## Setup Instructions

### Prerequisites
- Node.js 18+ installed
- NPM or Yarn package manager
- NocoBase API credentials (API key and base URL)

### 1. Clone or Setup Project

```bash
cd "C:\Users\Admin\Desktop\Sharda\Asset Dashboard"
```

### 2. Configure Environment Variables

Create a `.env` file in the **root directory** (same level as backend/ and frontend/ folders):

```env
API_KEY=your_actual_api_key_here
BASE_URL=https://spaces.iitm.ac.in
PORT=3001
```

**Important**: Use your actual API key from the NocoBase dashboard.

### 3. Install Backend Dependencies

```powershell
cd backend
npm install
```

### 4. Install Frontend Dependencies

```powershell
cd ..\frontend
npm install
```

## Running the Application

You need to run both backend and frontend servers.

### Terminal 1: Start Backend Server

```powershell
cd backend
npm run dev
```

The backend will start on **http://localhost:3001**

### Terminal 2: Start Frontend Dev Server

```powershell
cd frontend
npm run dev
```

The frontend will start on **http://localhost:5173**

### 5. Access Dashboard

Open your browser and navigate to:
```
http://localhost:5173
```

## API Endpoints

The backend exposes the following REST API endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stats/summary` | GET | Overall statistics (total assets, SRB records, etc.) |
| `/api/stats/srb-amount-distribution` | GET | Asset counts by amount ranges (>1Cr, 10L-1Cr, 1L-10L, <1L) |
| `/api/stats/asset-by-category` | GET | Assets grouped by Asset_Code |
| `/api/assets` | GET | List all assets with optional filters (?building=X&status=Y) |
| `/api/buildings` | GET | List all buildings |
| `/health` | GET | Health check endpoint |

## Dashboard Features

### Summary Cards
- Total Assets
- Active Assets
- Total SRB Records
- Total SRB Value (in Crores/Lakhs)

### Amount Distribution Section
Four color-coded cards showing:
- **Blue**: Assets > ₹1 Crore
- **Purple**: Assets ₹10 Lakhs - ₹1 Crore
- **Pink**: Assets ₹1 Lakh - ₹10 Lakhs
- **Amber**: Assets < ₹1 Lakh

### Visualizations
1. **Bar Chart**: Asset count by amount range
2. **Pie Chart**: Top 6 asset categories distribution
3. **Table**: Detailed category breakdown with counts and amounts

## Data Flow

```
NocoBase API (spaces.iitm.ac.in)
         ↓
  Express Backend (Port 3001)
  - Fetches data with proper headers
  - Caches responses (5 min TTL)
  - Processes & aggregates data
         ↓
  Vite Proxy (/api → localhost:3001)
         ↓
  React Frontend (Port 5173)
  - React Query for data fetching
  - Recharts for visualization
  - Tailwind for styling
```

## Troubleshooting

### Backend won't start
- Ensure `.env` file exists in root directory
- Check API_KEY and BASE_URL are correct
- Verify port 3001 is not in use

### Frontend shows errors
- Run `npm install` in frontend directory
- Check backend is running on port 3001
- Check browser console for specific errors

### No data showing
- Verify API key has correct permissions
- Check backend terminal for API errors
- Ensure NocoBase API is accessible

### CORS errors
- Backend has CORS enabled by default
- Check Vite proxy configuration in `vite.config.ts`

## Development

### Backend Development
```powershell
cd backend
npm run dev  # Uses nodemon for auto-reload
```

### Frontend Development
```powershell
cd frontend
npm run dev  # Vite HMR enabled
```

### Production Build
```powershell
# Build frontend
cd frontend
npm run build

# Output will be in frontend/dist/
# Serve with any static file server
```

## Cache Management

Backend caches API responses for 5 minutes to reduce load:
- Summary stats: 5 min TTL
- SRB amount distribution: 5 min TTL
- Category data: 5 min TTL

To clear cache: Restart the backend server.

## Python Scripts (Optional)

The `scripts/` folder contains Python utilities for data analysis:
- `fetch_data.py`: Fetch raw data from API
- `analyze.py`: Detect FK relationships
- `verify_fks.py`: Verify data integrity

See `QUICK_START.md` for Python script usage.

## License

Internal project for Sharda University Asset Management.

## Support

For issues or questions, contact the development team.
