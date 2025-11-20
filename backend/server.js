const express = require('express');
const cors = require('cors');
const axios = require('axios');
const NodeCache = require('node-cache');
require('dotenv').config({ path: '../.env' });

const app = express();
const cache = new NodeCache({ stdTTL: 300 }); // 5 minute cache

const PORT = process.env.PORT || 3001;
const API_KEY = process.env.API_KEY;
const BASE_URL = process.env.BASE_URL;

// Middleware
app.use(cors());
app.use(express.json());

// Helper to get headers
const getHeaders = () => ({
  'Authorization': `Bearer ${API_KEY}`,
  'Accept': 'application/json',
  'X-Role': 'admin',
  'X-Locale': 'en-US',
  'X-App': 'Assets',
  'X-Timezone': '+05:30',
  'X-Hostname': 'spaces.iitm.ac.in',
  'X-Authentication': 'basic',
});

// Helper to fetch from NocoBase API
const fetchFromAPI = async (endpoint) => {
  try {
    const response = await axios.get(`${BASE_URL}${endpoint}`, {
      headers: getHeaders(),
      timeout: 15000,
    });
    // NocoBase wraps data in {data: [...]}
    const result = response.data.data || response.data;
    console.log(`Fetched ${endpoint}: ${Array.isArray(result) ? result.length : 'N/A'} records`);
    return result;
  } catch (error) {
    console.error(`Error fetching ${endpoint}:`, error.message);
    throw error;
  }
};

// Helper to fetch ALL records with pagination
const fetchAllRecords = async (collection) => {
  let allRecords = [];
  let page = 1;
  const pageSize = 200; // NocoBase might have limits
  
  while (true) {
    const endpoint = `/api/${collection}:list?page=${page}&pageSize=${pageSize}`;
    console.log(`Fetching page ${page} for ${collection}...`);
    
    const response = await axios.get(`${BASE_URL}${endpoint}`, {
      headers: getHeaders(),
      timeout: 15000,
    });
    
    const records = response.data.data || response.data;
    const meta = response.data.meta;
    
    if (Array.isArray(records) && records.length > 0) {
      allRecords = allRecords.concat(records);
      console.log(`  Got ${records.length} records, total so far: ${allRecords.length}`);
      
      // Check if there are more pages
      if (meta && meta.count && allRecords.length >= meta.count) {
        break;
      }
      if (records.length < pageSize) {
        break; // Last page
      }
      page++;
    } else {
      break;
    }
  }
  
  console.log(`✓ Total ${collection} records fetched: ${allRecords.length}`);
  return allRecords;
};

// === STATS ENDPOINTS ===

// GET /api/stats/srb-amount-distribution
// Returns asset counts by amount ranges
app.get('/api/stats/srb-amount-distribution', async (req, res) => {
  try {
    const cacheKey = 'stats:srb-amount';
    const cached = cache.get(cacheKey);
    if (cached) return res.json(cached);

    const srbDetails = await fetchAllRecords('SRB_Details');
    
    // Parse amounts and categorize
    const ranges = {
      above1Cr: { count: 0, total: 0, items: [] },      // >= 1 crore (10,000,000)
      between10LTo1Cr: { count: 0, total: 0, items: [] }, // 10L to <1Cr
      between1LTo10L: { count: 0, total: 0, items: [] },  // 1L to <10L
      below1L: { count: 0, total: 0, items: [] },         // < 1L
      noAmount: { count: 0, total: 0, items: [] },
    };

    srbDetails.forEach(srb => {
      // Amount is already a number in the API response
      const amount = parseFloat(srb.Amount) || 0;
      
      const item = {
        id: srb.id,
        srb_number: srb.SRB_Number || 'Unknown',
        amount: amount,
        asset_code: (srb.Asset_Code === 'NULL' || !srb.Asset_Code) ? 'Unknown' : srb.Asset_Code,
        item_description: (srb.Item_Description === 'NULL' || !srb.Item_Description) ? 'Unknown' : srb.Item_Description,
      };

      if (amount === 0) {
        ranges.noAmount.count++;
        ranges.noAmount.items.push(item);
      } else if (amount >= 10000000) { // >= 1 Cr
        ranges.above1Cr.count++;
        ranges.above1Cr.total += amount;
        ranges.above1Cr.items.push(item);
      } else if (amount >= 1000000) { // 10L to 1Cr
        ranges.between10LTo1Cr.count++;
        ranges.between10LTo1Cr.total += amount;
        ranges.between10LTo1Cr.items.push(item);
      } else if (amount >= 100000) { // 1L to 10L
        ranges.between1LTo10L.count++;
        ranges.between1LTo10L.total += amount;
        ranges.between1LTo10L.items.push(item);
      } else { // < 1L
        ranges.below1L.count++;
        ranges.below1L.total += amount;
        ranges.below1L.items.push(item);
      }
    });

    const result = {
      ranges,
      totalRecords: srbDetails.length,
      totalAmount: Object.values(ranges).reduce((sum, r) => sum + r.total, 0),
    };

    cache.set(cacheKey, result);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// GET /api/stats/asset-by-category
// Returns asset counts grouped by Asset_Code
app.get('/api/stats/asset-by-category', async (req, res) => {
  try {
    const cacheKey = 'stats:asset-category';
    const cached = cache.get(cacheKey);
    if (cached) return res.json(cached);

    const srbDetails = await fetchAllRecords('SRB_Details');
    
    // Group by Asset_Code
    const categoryMap = {};
    
    srbDetails.forEach(srb => {
      const code = (srb.Asset_Code === 'NULL' || !srb.Asset_Code) ? 'Unknown' : srb.Asset_Code;
      if (!categoryMap[code]) {
        categoryMap[code] = { category: code, count: 0, totalAmount: 0, items: [] };
      }
      // Amount is already a number
      const amount = parseFloat(srb.Amount) || 0;
      categoryMap[code].count++;
      categoryMap[code].totalAmount += amount;
      categoryMap[code].items.push({
        id: srb.id,
        srb_number: srb.SRB_Number || 'Unknown',
        amount: amount,
        description: (srb.Item_Description === 'NULL' || !srb.Item_Description) ? 'Unknown' : srb.Item_Description,
      });
    });

    const categories = Object.values(categoryMap).sort((a, b) => b.count - a.count);

    const result = {
      categories,
      totalCategories: categories.length,
      totalRecords: srbDetails.length,
    };

    cache.set(cacheKey, result);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// GET /api/stats/summary
// Overall summary stats
app.get('/api/stats/summary', async (req, res) => {
  try {
    const cacheKey = 'stats:summary';
    const cached = cache.get(cacheKey);
    if (cached) return res.json(cached);

    const [assets, srbDetails, buildings, instances] = await Promise.all([
      fetchAllRecords('Asset'),
      fetchAllRecords('SRB_Details'),
      fetchFromAPI('/api/Buildings:list'),
      fetchAllRecords('Instance'),
    ]);

    const totalSRBAmount = srbDetails.reduce((sum, srb) => {
      // Amount is already a number
      const amount = parseFloat(srb.Amount) || 0;
      return sum + amount;
    }, 0);

    const activeAssets = assets.filter(a => a.is_active === 'Yes').length;

    const result = {
      totalAssets: assets.length,
      activeAssets,
      inactiveAssets: assets.length - activeAssets,
      totalInstances: instances.length,
      totalBuildings: buildings.length,
      totalSRBRecords: srbDetails.length,
      totalSRBAmount,
      avgSRBAmount: srbDetails.length > 0 ? totalSRBAmount / srbDetails.length : 0,
    };

    cache.set(cacheKey, result);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// GET /api/assets
// List all assets with optional filters
app.get('/api/assets', async (req, res) => {
  try {
    const { pageSize = 50, building, status } = req.query;
    const cacheKey = `assets:list:${pageSize}:${building || 'all'}:${status || 'all'}`;
    const cached = cache.get(cacheKey);
    if (cached) return res.json(cached);

    let assets = await fetchFromAPI(`/api/Asset:list?pageSize=${pageSize}`);
    
    // Apply filters
    if (building) {
      assets = assets.filter(a => a.Building_Id == building);
    }
    if (status) {
      assets = assets.filter(a => a.is_active === status);
    }

    cache.set(cacheKey, assets);
    res.json(assets);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// GET /api/buildings
app.get('/api/buildings', async (req, res) => {
  try {
    const cacheKey = 'buildings:list';
    const cached = cache.get(cacheKey);
    if (cached) return res.json(cached);

    const buildings = await fetchFromAPI('/api/Buildings:list');
    cache.set(cacheKey, buildings);
    res.json(buildings);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Start server
app.listen(PORT, () => {
  console.log(`✅ Backend server running on http://localhost:${PORT}`);
  console.log(`📊 API endpoints:`);
  console.log(`   GET /api/stats/summary`);
  console.log(`   GET /api/stats/srb-amount-distribution`);
  console.log(`   GET /api/stats/asset-by-category`);
  console.log(`   GET /api/assets`);
  console.log(`   GET /api/buildings`);
});
