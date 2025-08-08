// Vercel serverless function for health check
export default function handler(req, res) {
    // Enable CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }
    
    try {
        const healthData = {
            status: "healthy",
            timestamp: new Date().toISOString(),
            service: "Ads Transparency Dashboard API",
            version: "1.0.0",
            endpoints: {
                "sector-overview": "/api/brands/sector-overview",
                "brand-details": "/api/brands/brand-details", 
                "subcategory-analysis": "/api/brands/subcategory-analysis",
                "real-campaigns": "/api/real-campaigns"
            },
            environment: "production",
            region: process.env.VERCEL_REGION || "unknown"
        };
        
        res.status(200).json(healthData);
        
    } catch (error) {
        console.error('Health check error:', error);
        res.status(500).json({ 
            status: "unhealthy", 
            timestamp: new Date().toISOString(),
            error: error.message 
        });
    }
}