// Vercel serverless function for sector overview
export default function handler(req, res) {
    // Enable CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }
    
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }
    
    try {
        const { industry, currency = 'EUR', country_filter = 'all' } = req.body;
        
        // Belgium & France brands database
        const sectorData = {
            automotive: {
                total_brands: 12,
                sector_totals: {
                    total_brands: 12,
                    total_ad_spend: 890000000,
                    total_ad_spend_formatted: "€890M"
                },
                categories: {
                    luxury: {
                        brand_count: 4,
                        total_spend: 380000000,
                        total_spend_formatted: "€380M",
                        brands: [
                            { name: "BMW", country: "Germany", annual_ad_spend_formatted: "€85M" },
                            { name: "Mercedes-Benz", country: "Germany", annual_ad_spend_formatted: "€95M" },
                            { name: "Audi", country: "Germany", annual_ad_spend_formatted: "€78M" },
                            { name: "Tesla", country: "USA", annual_ad_spend_formatted: "€42M" }
                        ]
                    },
                    mainstream: {
                        brand_count: 8,
                        total_spend: 510000000,
                        total_spend_formatted: "€510M",
                        brands: [
                            { name: "Volkswagen", country: "Germany", annual_ad_spend_formatted: "€85M" },
                            { name: "Renault", country: "France", annual_ad_spend_formatted: "€92M" },
                            { name: "Peugeot", country: "France", annual_ad_spend_formatted: "€67M" },
                            { name: "Toyota", country: "Japan", annual_ad_spend_formatted: "€71M" },
                            { name: "Ford", country: "USA", annual_ad_spend_formatted: "€48M" },
                            { name: "Citroën", country: "France", annual_ad_spend_formatted: "€52M" },
                            { name: "Opel", country: "Germany", annual_ad_spend_formatted: "€38M" },
                            { name: "Hyundai", country: "South Korea", annual_ad_spend_formatted: "€35M" }
                        ]
                    }
                },
                country_breakdown: {
                    Germany: { brands: 4, total_spend_formatted: "€286M" },
                    France: { brands: 3, total_spend_formatted: "€211M" },
                    Japan: { brands: 1, total_spend_formatted: "€71M" },
                    USA: { brands: 2, total_spend_formatted: "€90M" },
                    "South Korea": { brands: 1, total_spend_formatted: "€35M" }
                }
            },
            technology: {
                total_brands: 15,
                sector_totals: {
                    total_brands: 15,
                    total_ad_spend: 1250000000,
                    total_ad_spend_formatted: "€1.25B"
                },
                categories: {
                    enterprise: {
                        brand_count: 6,
                        total_spend: 680000000,
                        total_spend_formatted: "€680M",
                        brands: [
                            { name: "SAP", country: "Germany", annual_ad_spend_formatted: "€125M" },
                            { name: "Microsoft", country: "USA", annual_ad_spend_formatted: "€145M" },
                            { name: "Oracle", country: "USA", annual_ad_spend_formatted: "€89M" },
                            { name: "ASML", country: "Netherlands", annual_ad_spend_formatted: "€98M" },
                            { name: "Siemens", country: "Germany", annual_ad_spend_formatted: "€112M" },
                            { name: "Nokia", country: "Finland", annual_ad_spend_formatted: "€67M" }
                        ]
                    },
                    consumer: {
                        brand_count: 9,
                        total_spend: 570000000,
                        total_spend_formatted: "€570M",
                        brands: [
                            { name: "Apple", country: "USA", annual_ad_spend_formatted: "€89M" },
                            { name: "Samsung", country: "South Korea", annual_ad_spend_formatted: "€78M" },
                            { name: "Philips", country: "Netherlands", annual_ad_spend_formatted: "€65M" },
                            { name: "Sony", country: "Japan", annual_ad_spend_formatted: "€58M" },
                            { name: "Spotify", country: "Sweden", annual_ad_spend_formatted: "€45M" },
                            { name: "Booking.com", country: "Netherlands", annual_ad_spend_formatted: "€92M" },
                            { name: "TomTom", country: "Netherlands", annual_ad_spend_formatted: "€34M" },
                            { name: "Garmin", country: "USA", annual_ad_spend_formatted: "€41M" },
                            { name: "JBL", country: "USA", annual_ad_spend_formatted: "€38M" }
                        ]
                    }
                }
            },
            fashion: {
                total_brands: 18,
                sector_totals: {
                    total_brands: 18,
                    total_ad_spend: 980000000,
                    total_ad_spend_formatted: "€980M"
                },
                categories: {
                    luxury: {
                        brand_count: 7,
                        total_spend: 420000000,
                        total_spend_formatted: "€420M",
                        brands: [
                            { name: "Louis Vuitton", country: "France", annual_ad_spend_formatted: "€85M" },
                            { name: "Chanel", country: "France", annual_ad_spend_formatted: "€78M" },
                            { name: "Hermès", country: "France", annual_ad_spend_formatted: "€62M" },
                            { name: "Gucci", country: "Italy", annual_ad_spend_formatted: "€71M" },
                            { name: "Dior", country: "France", annual_ad_spend_formatted: "€69M" },
                            { name: "Hugo Boss", country: "Germany", annual_ad_spend_formatted: "€45M" },
                            { name: "Burberry", country: "UK", annual_ad_spend_formatted: "€38M" }
                        ]
                    },
                    mainstream: {
                        brand_count: 11,
                        total_spend: 560000000,
                        total_spend_formatted: "€560M",
                        brands: [
                            { name: "Zara", country: "Spain", annual_ad_spend_formatted: "€89M" },
                            { name: "H&M", country: "Sweden", annual_ad_spend_formatted: "€82M" },
                            { name: "Uniqlo", country: "Japan", annual_ad_spend_formatted: "€45M" },
                            { name: "Zalando", country: "Germany", annual_ad_spend_formatted: "€67M" },
                            { name: "ASOS", country: "UK", annual_ad_spend_formatted: "€52M" },
                            { name: "Adidas", country: "Germany", annual_ad_spend_formatted: "€78M" },
                            { name: "Nike", country: "USA", annual_ad_spend_formatted: "€71M" },
                            { name: "Puma", country: "Germany", annual_ad_spend_formatted: "€35M" },
                            { name: "Lacoste", country: "France", annual_ad_spend_formatted: "€28M" },
                            { name: "Tommy Hilfiger", country: "USA", annual_ad_spend_formatted: "€31M" },
                            { name: "Calvin Klein", country: "USA", annual_ad_spend_formatted: "€29M" }
                        ]
                    }
                }
            },
            finance: {
                total_brands: 14,
                sector_totals: {
                    total_brands: 14,
                    total_ad_spend: 750000000,
                    total_ad_spend_formatted: "€750M"
                },
                categories: {
                    banks: {
                        brand_count: 8,
                        total_spend: 450000000,
                        total_spend_formatted: "€450M",
                        brands: [
                            { name: "ING", country: "Netherlands", annual_ad_spend_formatted: "€68M" },
                            { name: "ABN AMRO", country: "Netherlands", annual_ad_spend_formatted: "€52M" },
                            { name: "KBC", country: "Belgium", annual_ad_spend_formatted: "€45M" },
                            { name: "BNP Paribas", country: "France", annual_ad_spend_formatted: "€89M" },
                            { name: "Société Générale", country: "France", annual_ad_spend_formatted: "€71M" },
                            { name: "Crédit Agricole", country: "France", annual_ad_spend_formatted: "€56M" },
                            { name: "Deutsche Bank", country: "Germany", annual_ad_spend_formatted: "€42M" },
                            { name: "Rabobank", country: "Netherlands", annual_ad_spend_formatted: "€38M" }
                        ]
                    },
                    insurance: {
                        brand_count: 6,
                        total_spend: 300000000,
                        total_spend_formatted: "€300M",
                        brands: [
                            { name: "AXA", country: "France", annual_ad_spend_formatted: "€78M" },
                            { name: "Allianz", country: "Germany", annual_ad_spend_formatted: "€85M" },
                            { name: "AG Insurance", country: "Belgium", annual_ad_spend_formatted: "€42M" },
                            { name: "Generali", country: "Italy", annual_ad_spend_formatted: "€45M" },
                            { name: "Zurich", country: "Switzerland", annual_ad_spend_formatted: "€35M" },
                            { name: "NN Group", country: "Netherlands", annual_ad_spend_formatted: "€28M" }
                        ]
                    }
                }
            }
        };
        
        const result = sectorData[industry] || {
            industry,
            error: `No data available for ${industry} industry`,
            available_industries: Object.keys(sectorData)
        };
        
        result.industry = industry;
        result.currency = currency;
        result.country_filter = country_filter;
        
        res.status(200).json(result);
        
    } catch (error) {
        console.error('Error in sector-overview:', error);
        res.status(500).json({ error: 'Internal server error', message: error.message });
    }
}