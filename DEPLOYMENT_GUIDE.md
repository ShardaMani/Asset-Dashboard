# Asset Dashboard - Vercel Deployment Guide

## 📋 Pre-Deployment Checklist
- ✅ Project cleaned and optimized
- ✅ Serverless API functions ready
- ✅ Frontend build configuration updated
- ✅ Environment variables documented

## 🚀 Step-by-Step Vercel UI Deployment

### Step 1: Prepare Your GitHub Repository
1. **Commit all changes** to your GitHub repository:
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

### Step 2: Deploy via Vercel Dashboard

#### 2.1 Access Vercel Dashboard
1. Go to [vercel.com](https://vercel.com)
2. Sign in with your GitHub account
3. Click **"New Project"**

#### 2.2 Import Your Repository
1. Find your repository: **"ShardaMani/Asset-Dashboard"**
2. Click **"Import"**

#### 2.3 Configure Project Settings
- **Project Name**: `asset-dashboard`
- **Framework Preset**: `Other`
- **Root Directory**: `.` (leave empty/default)
- **Build Command**: `npm run build` (should auto-detect)
- **Output Directory**: `frontend/dist`
- **Install Command**: `npm install` (should auto-detect)

#### 2.4 Add Environment Variables
Before deploying, click **"Environment Variables"** and add:

| Variable Name | Value | Environment |
|---------------|-------|-------------|
| `API_KEY` | `your_jwt_token_here` | Production |
| `BASE_URL` | `https://spaces.iitm.ac.in` | Production |

**Important**: Get your JWT token from your `.env` file or NocoBase admin panel.

#### 2.5 Deploy
1. Click **"Deploy"**
2. Wait for build to complete (2-3 minutes)
3. Your app will be available at: `https://your-project-name.vercel.app`

### Step 3: Post-Deployment Testing

#### 3.1 Test Frontend
Visit your deployment URL - you should see the dashboard loading screen.

#### 3.2 Test API Endpoints
Test these endpoints (replace with your actual URL):
- `https://your-app.vercel.app/api/stats/summary`
- `https://your-app.vercel.app/api/stats/srb-amount-distribution`
- `https://your-app.vercel.app/api/stats/asset-by-category`
- `https://your-app.vercel.app/api/admin/count-active-assets?building=Computer%20Center`

### Step 4: Troubleshooting

#### If deployment fails:
1. Check **Build Logs** in Vercel dashboard
2. Verify all environment variables are set
3. Ensure your JWT token is valid

#### If API returns errors:
1. Check **Function Logs** in Vercel dashboard
2. Verify environment variables: `API_KEY` and `BASE_URL`
3. Test API endpoints individually

#### If dashboard shows "Loading...":
1. Check browser Network tab for API errors
2. Verify CORS settings (should be handled automatically)
3. Check that environment variables are properly set

### Step 5: Custom Domain (Optional)
1. Go to **Project Settings** → **Domains**
2. Add your custom domain
3. Follow Vercel's DNS configuration instructions

## 🔧 Project Structure
```
Asset Dashboard/
├── api/                    # Serverless API functions
│   ├── admin/             # Admin endpoints
│   ├── stats/             # Statistics endpoints
│   └── _utils.js          # Shared utilities
├── frontend/              # React application
│   ├── src/               # Source code
│   ├── public/            # Static assets
│   └── package.json       # Frontend dependencies
├── vercel.json            # Vercel configuration
└── package.json           # Root build scripts
```

## 🎯 Expected Result
After successful deployment:
- **Frontend**: Modern React dashboard with charts and statistics
- **API**: RESTful endpoints connected to NocoBase
- **Data**: Real-time asset management data from your system
- **Performance**: Fast global CDN with serverless scaling

## 📞 Support
If you encounter issues:
1. Check Vercel's build/function logs
2. Verify environment variables
3. Test API endpoints manually
4. Ensure JWT token is not expired