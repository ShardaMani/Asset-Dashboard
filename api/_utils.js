const axios = require('axios');

// Helper to get headers for NocoBase API
const getHeaders = () => ({
  'Authorization': `Bearer ${process.env.API_KEY}`,
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
    const response = await axios.get(`${process.env.BASE_URL}${endpoint}`, {
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
    
    const response = await axios.get(`${process.env.BASE_URL}${endpoint}`, {
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

module.exports = {
  getHeaders,
  fetchFromAPI,
  fetchAllRecords
};