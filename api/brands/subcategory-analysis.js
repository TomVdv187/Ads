// Vercel serverless function for subcategory analysis
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
        const { industry, subcategory = 'luxury', currency = 'EUR', country_filter = 'all' } = req.body;
        
        // Subcategory analysis data for Belgium & France markets
        const subcategoryData = {
            automotive: {
                luxury: {
                    industry: "automotive",
                    subcategory: "luxury",
                    currency: "EUR",
                    summary: {
                        total_brands: 4,
                        total_ad_spend_formatted: "€380M",
                        average_spend_per_brand_formatted: "€95M",
                        countries_represented: 3
                    },
                    brands: [
                        { name: "Mercedes-Benz", country: "Germany", annual_ad_spend_formatted: "€95M", share_of_category_spend: 25.0 },
                        { name: "BMW", country: "Germany", annual_ad_spend_formatted: "€85M", share_of_category_spend: 22.4 },
                        { name: "Audi", country: "Germany", annual_ad_spend_formatted: "€78M", share_of_category_spend: 20.5 },
                        { name: "Tesla", country: "USA", annual_ad_spend_formatted: "€42M", share_of_category_spend: 11.1 }
                    ],
                    country_analysis: {
                        Germany: { brands: 3, total_spend_formatted: "€258M" },
                        USA: { brands: 1, total_spend_formatted: "€42M" }
                    },
                    market_concentration: {
                        top_3_share: 67.9,
                        top_5_share: 100.0,
                        herfindahl_index: 0.22
                    }
                },
                mainstream: {
                    industry: "automotive",
                    subcategory: "mainstream",
                    currency: "EUR",
                    summary: {
                        total_brands: 8,
                        total_ad_spend_formatted: "€510M",
                        average_spend_per_brand_formatted: "€64M",
                        countries_represented: 5
                    },
                    brands: [
                        { name: "Renault", country: "France", annual_ad_spend_formatted: "€92M", share_of_category_spend: 18.0 },
                        { name: "Volkswagen", country: "Germany", annual_ad_spend_formatted: "€85M", share_of_category_spend: 16.7 },
                        { name: "Toyota", country: "Japan", annual_ad_spend_formatted: "€71M", share_of_category_spend: 13.9 },
                        { name: "Peugeot", country: "France", annual_ad_spend_formatted: "€67M", share_of_category_spend: 13.1 },
                        { name: "Citroën", country: "France", annual_ad_spend_formatted: "€52M", share_of_category_spend: 10.2 },
                        { name: "Ford", country: "USA", annual_ad_spend_formatted: "€48M", share_of_category_spend: 9.4 },
                        { name: "Opel", country: "Germany", annual_ad_spend_formatted: "€38M", share_of_category_spend: 7.5 },
                        { name: "Hyundai", country: "South Korea", annual_ad_spend_formatted: "€35M", share_of_category_spend: 6.9 }
                    ]
                }
            },
            technology: {
                enterprise: {
                    industry: "technology",
                    subcategory: "enterprise",
                    currency: "EUR",
                    summary: {
                        total_brands: 6,
                        total_ad_spend_formatted: "€680M",
                        average_spend_per_brand_formatted: "€113M",
                        countries_represented: 4
                    },
                    brands: [
                        { name: "Microsoft", country: "USA", annual_ad_spend_formatted: "€145M", share_of_category_spend: 21.3 },
                        { name: "SAP", country: "Germany", annual_ad_spend_formatted: "€125M", share_of_category_spend: 18.4 },
                        { name: "Siemens", country: "Germany", annual_ad_spend_formatted: "€112M", share_of_category_spend: 16.5 },
                        { name: "ASML", country: "Netherlands", annual_ad_spend_formatted: "€98M", share_of_category_spend: 14.4 },
                        { name: "Oracle", country: "USA", annual_ad_spend_formatted: "€89M", share_of_category_spend: 13.1 },
                        { name: "Nokia", country: "Finland", annual_ad_spend_formatted: "€67M", share_of_category_spend: 9.9 }
                    ]
                },
                consumer: {
                    industry: "technology",
                    subcategory: "consumer", 
                    currency: "EUR",
                    summary: {
                        total_brands: 9,
                        total_ad_spend_formatted: "€570M",
                        average_spend_per_brand_formatted: "€63M",
                        countries_represented: 6
                    },
                    brands: [
                        { name: "Booking.com", country: "Netherlands", annual_ad_spend_formatted: "€92M", share_of_category_spend: 16.1 },
                        { name: "Apple", country: "USA", annual_ad_spend_formatted: "€89M", share_of_category_spend: 15.6 },
                        { name: "Samsung", country: "South Korea", annual_ad_spend_formatted: "€78M", share_of_category_spend: 13.7 },
                        { name: "Philips", country: "Netherlands", annual_ad_spend_formatted: "€65M", share_of_category_spend: 11.4 },
                        { name: "Sony", country: "Japan", annual_ad_spend_formatted: "€58M", share_of_category_spend: 10.2 },
                        { name: "Spotify", country: "Sweden", annual_ad_spend_formatted: "€45M", share_of_category_spend: 7.9 },
                        { name: "Garmin", country: "USA", annual_ad_spend_formatted: "€41M", share_of_category_spend: 7.2 },
                        { name: "JBL", country: "USA", annual_ad_spend_formatted: "€38M", share_of_category_spend: 6.7 },
                        { name: "TomTom", country: "Netherlands", annual_ad_spend_formatted: "€34M", share_of_category_spend: 6.0 }
                    ]
                }
            },
            fashion: {
                luxury: {
                    industry: "fashion",
                    subcategory: "luxury",
                    currency: "EUR", 
                    summary: {
                        total_brands: 7,
                        total_ad_spend_formatted: "€420M",
                        average_spend_per_brand_formatted: "€60M",
                        countries_represented: 4
                    },
                    brands: [
                        { name: "Louis Vuitton", country: "France", annual_ad_spend_formatted: "€85M", share_of_category_spend: 20.2 },
                        { name: "Chanel", country: "France", annual_ad_spend_formatted: "€78M", share_of_category_spend: 18.6 },
                        { name: "Gucci", country: "Italy", annual_ad_spend_formatted: "€71M", share_of_category_spend: 16.9 },
                        { name: "Dior", country: "France", annual_ad_spend_formatted: "€69M", share_of_category_spend: 16.4 },
                        { name: "Hermès", country: "France", annual_ad_spend_formatted: "€62M", share_of_category_spend: 14.8 },
                        { name: "Hugo Boss", country: "Germany", annual_ad_spend_formatted: "€45M", share_of_category_spend: 10.7 },
                        { name: "Burberry", country: "UK", annual_ad_spend_formatted: "€38M", share_of_category_spend: 9.0 }
                    ]
                }
            },
            finance: {
                banks: {
                    industry: "finance",
                    subcategory: "banks",
                    currency: "EUR",
                    summary: {
                        total_brands: 8,
                        total_ad_spend_formatted: "€450M",
                        average_spend_per_brand_formatted: "€56M",
                        countries_represented: 4
                    },
                    brands: [
                        { name: "BNP Paribas", country: "France", annual_ad_spend_formatted: "€89M", share_of_category_spend: 19.8 },
                        { name: "Société Générale", country: "France", annual_ad_spend_formatted: "€71M", share_of_category_spend: 15.8 },
                        { name: "ING", country: "Netherlands", annual_ad_spend_formatted: "€68M", share_of_category_spend: 15.1 },
                        { name: "Crédit Agricole", country: "France", annual_ad_spend_formatted: "€56M", share_of_category_spend: 12.4 },
                        { name: "ABN AMRO", country: "Netherlands", annual_ad_spend_formatted: "€52M", share_of_category_spend: 11.6 },
                        { name: "KBC", country: "Belgium", annual_ad_spend_formatted: "€45M", share_of_category_spend: 10.0 },
                        { name: "Deutsche Bank", country: "Germany", annual_ad_spend_formatted: "€42M", share_of_category_spend: 9.3 },
                        { name: "Rabobank", country: "Netherlands", annual_ad_spend_formatted: "€38M", share_of_category_spend: 8.4 }
                    ]
                }
            }
        };
        
        const industryData = subcategoryData[industry];
        if (!industryData) {
            return res.status(404).json({ 
                error: `Industry "${industry}" not found`,
                available_industries: Object.keys(subcategoryData)
            });
        }
        
        const result = industryData[subcategory];
        if (!result) {
            return res.status(404).json({ 
                error: `Subcategory "${subcategory}" not found in ${industry}`,
                available_subcategories: Object.keys(industryData)
            });
        }
        
        // Add metadata
        result.country_filter = country_filter;
        
        res.status(200).json(result);
        
    } catch (error) {
        console.error('Error in subcategory-analysis:', error);
        res.status(500).json({ error: 'Internal server error', message: error.message });
    }
}