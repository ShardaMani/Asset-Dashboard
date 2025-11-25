export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  res.status(200).json({ 
    message: 'Hello from Vercel API!', 
    timestamp: new Date().toISOString(),
    env_check: {
      has_api_key: !!process.env.API_KEY,
      has_base_url: !!process.env.BASE_URL
    }
  });
}