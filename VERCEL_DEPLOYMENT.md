# Vercel Deployment Guide

## Quick Deploy to Vercel

### 1. Prerequisites
- Vercel account (free at https://vercel.com)
- GitHub repository with the latest code

### 2. Deploy Steps

#### Option A: Direct from GitHub (Recommended)
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository: `ShardaMani/Asset-Dashboard`
4. Configure the project:
   - **Framework Preset**: Other
   - **Root Directory**: Leave blank (uses entire repo)
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Output Directory**: `frontend/dist`
   - **Install Command**: `cd frontend && npm install && cd ../api && npm install`

#### Option B: Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# In your project root
vercel

# Follow the prompts
```

### 3. Environment Variables
In Vercel Dashboard → Project → Settings → Environment Variables, add:

| Name | Value | Description |
|------|-------|-------------|
| `API_KEY` | `your_jwt_token_here` | NocoBase JWT token |
| `BASE_URL` | `https://spaces.iitm.ac.in` | NocoBase API base URL |

**Important**: Do NOT set `VITE_API_BASE` in Vercel - it should use relative paths (`/api`) automatically.

### 4. Custom Build Settings
If you need to customize the build, create this file:

**`vercel.json`** (already included):
```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "frontend/dist"
      }
    },
    {
      "src": "api/**/*.js",
      "use": "@vercel/node"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/dist/$1"
    }
  ]
}
```

### 5. API Endpoints (Serverless Functions)
Once deployed, your API will be available at:

- `https://your-app.vercel.app/api/stats/summary`
- `https://your-app.vercel.app/api/stats/srb-amount-distribution`
- `https://your-app.vercel.app/api/stats/asset-by-category`
- `https://your-app.vercel.app/api/admin/count-active-assets?building=Computer%20Center`

### 6. Troubleshooting

#### Build Fails
- Check that both `frontend/package.json` and `api/package.json` exist
- Verify environment variables are set correctly
- Check build logs in Vercel dashboard

#### API Returns 500 Errors
- Verify `API_KEY` and `BASE_URL` environment variables
- Check function logs in Vercel dashboard → Functions tab
- Test the JWT token is still valid

#### Frontend Shows "Loading..." Forever
- Check browser Network tab for API errors
- Verify API endpoints are accessible
- Check CORS settings (should be handled by serverless functions)

### 7. Local Development vs Production

| Environment | Frontend URL | Backend URL | API Calls |
|-------------|-------------|-------------|-----------|
| **Local** | http://localhost:5173 | http://localhost:3001 | Via Vite proxy `/api` → `http://localhost:3001` |
| **Vercel** | https://your-app.vercel.app | Serverless functions | Direct to `/api/*` (same domain) |
| **Custom VM** | http://VM_IP:5173 | http://VM_IP:3001 | Via `VITE_API_BASE=http://VM_IP:3001` |

### 8. Deployment URL Structure
After deployment, your app will be at: `https://asset-dashboard-[random].vercel.app`

You can customize the URL in Vercel Dashboard → Project → Settings → Domains.

## Next Steps
1. Deploy to Vercel following steps above
2. Test all API endpoints work
3. Verify dashboard loads and shows real data
4. Set up custom domain (optional)