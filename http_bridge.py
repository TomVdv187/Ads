#!/usr/bin/env python3
"""
HTTP Bridge Server for MCP Ad Transparency Dashboard

This server provides HTTP endpoints that bridge between the web dashboard
and the MCP server, allowing browser-based access to MCP tools.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import threading
import time
import logging
from datetime import datetime, timedelta

# Import server functions for direct access when date filtering is needed
try:
    from server import _generate_sector_overview, _get_brand_granular_details
except ImportError:
    _generate_sector_overview = None
    _get_brand_granular_details = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for browser requests

# MCP server process
mcp_process = None
mcp_tools = {
    'search_ads_by_industry': 'mcp__ads-transparency__search_ads_by_industry',
    'analyze_ad_trends': 'mcp__ads-transparency__analyze_ad_trends', 
    'get_top_advertisers': 'mcp__ads-transparency__get_top_advertisers',
    'compare_industries': 'mcp__ads-transparency__compare_industries',
    'search_google_ads_by_industry': 'mcp__ads-transparency__search_google_ads_by_industry',
    'get_all_brands_by_industry': 'mcp__ads-transparency__get_all_brands_by_industry',
    'compare_meta_vs_google_ads': 'mcp__ads-transparency__compare_meta_vs_google_ads',
    'analyze_brand_advertising_strategy': 'mcp__ads-transparency__analyze_brand_advertising_strategy',
    'get_sector_overview_eur': 'mcp__ads-transparency__get_sector_overview_eur',
    'get_brand_details_eur': 'mcp__ads-transparency__get_brand_details_eur',
    'get_country_brand_analysis_eur': 'mcp__ads-transparency__get_country_brand_analysis_eur',
    'get_subcategory_analysis_eur': 'mcp__ads-transparency__get_subcategory_analysis_eur'
}

def start_mcp_server():
    """Start the MCP server process"""
    global mcp_process
    try:
        mcp_process = subprocess.Popen(
            ['python', 'server.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info("MCP server started")
        return True
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        return False

def call_mcp_tool(tool_name, **kwargs):
    """Simulate calling an MCP tool by using the server functions directly"""
    try:
        # Import the server module to access its functions
        import server
        
        # Map tool calls to server functions
        if tool_name == 'search_ads_by_industry':
            return server.search_ads_by_industry(
                kwargs.get('industry', 'technology'),
                kwargs.get('limit', 50),
                kwargs.get('access_token')
            )
        elif tool_name == 'analyze_ad_trends':
            return server.analyze_ad_trends(
                kwargs.get('industry', 'technology'),
                kwargs.get('days_back', 7)
            )
        elif tool_name == 'get_top_advertisers':
            return server.get_top_advertisers(
                kwargs.get('industry', 'technology'),
                kwargs.get('limit', 10)
            )
        elif tool_name == 'compare_industries':
            return server.compare_industries(
                kwargs.get('industry1', 'technology'),
                kwargs.get('industry2', 'automotive'),
                kwargs.get('metric', 'ad_volume')
            )
        elif tool_name == 'search_google_ads_by_industry':
            return server.search_google_ads_by_industry(
                kwargs.get('industry', 'technology'),
                kwargs.get('limit', 50),
                kwargs.get('google_api_key')
            )
        elif tool_name == 'get_all_brands_by_industry':
            return server.get_all_brands_by_industry(
                kwargs.get('industry', 'technology'),
                kwargs.get('include_competitors', True)
            )
        elif tool_name == 'compare_meta_vs_google_ads':
            return server.compare_meta_vs_google_ads(
                kwargs.get('industry', 'technology'),
                kwargs.get('metric', 'reach')
            )
        elif tool_name == 'analyze_brand_advertising_strategy':
            return server.analyze_brand_advertising_strategy(
                kwargs.get('brand_name', 'Example Brand'),
                kwargs.get('industry', 'technology'),
                kwargs.get('platforms', ['meta', 'google'])
            )
        elif tool_name == 'get_sector_overview_eur':
            return server.get_sector_overview_eur(
                kwargs.get('industry', 'technology'),
                kwargs.get('currency', 'EUR'),
                kwargs.get('country_filter', 'all')
            )
        elif tool_name == 'get_brand_details_eur':
            return server.get_brand_details_eur(
                kwargs.get('brand_name', 'SAP'),
                kwargs.get('industry', 'technology'),
                kwargs.get('currency', 'EUR'),
                kwargs.get('country_filter', 'all')
            )
        elif tool_name == 'get_country_brand_analysis_eur':
            return server.get_country_brand_analysis_eur(
                kwargs.get('country', 'Germany'),
                kwargs.get('currency', 'EUR')
            )
        elif tool_name == 'get_subcategory_analysis_eur':
            return server.get_subcategory_analysis_eur(
                kwargs.get('industry', 'technology'),
                kwargs.get('subcategory', 'enterprise'),
                kwargs.get('currency', 'EUR'),
                kwargs.get('country_filter', 'all')
            )
        else:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})
            
    except Exception as e:
        logger.error(f"Error calling MCP tool {tool_name}: {e}")
        return json.dumps({"error": str(e)})

@app.route('/api/ads/search', methods=['POST'])
def search_ads():
    """Search for ads by industry"""
    try:
        data = request.get_json()
        industry = data.get('industry', 'technology')
        platform = data.get('platform', 'meta')
        limit = data.get('limit', 50)
        
        if platform == 'google':
            result = call_mcp_tool('search_google_ads_by_industry', 
                                 industry=industry, limit=limit)
        else:
            result = call_mcp_tool('search_ads_by_industry', 
                                 industry=industry, limit=limit)
        
        # Parse the result if it's a string
        if isinstance(result, str):
            # Extract JSON from the result string
            try:
                import re
                json_match = re.search(r'\{.*\}|\[.*\]', result, re.DOTALL)
                if json_match:
                    parsed_result = json.loads(json_match.group())
                    return jsonify(parsed_result)
                else:
                    # Return demo data if parsing fails
                    return jsonify(_generate_demo_data(industry, platform, limit))
            except:
                return jsonify(_generate_demo_data(industry, platform, limit))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in search_ads: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/ads/trends', methods=['POST'])
def analyze_trends():
    """Analyze ad trends for industry"""
    try:
        data = request.get_json()
        industry = data.get('industry', 'technology')
        days_back = data.get('days_back', 7)
        
        result = call_mcp_tool('analyze_ad_trends', 
                             industry=industry, days_back=days_back)
        
        # Parse and return result
        if isinstance(result, str):
            try:
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    return jsonify(json.loads(json_match.group()))
                else:
                    return jsonify(_generate_demo_trends(industry, days_back))
            except:
                return jsonify(_generate_demo_trends(industry, days_back))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in analyze_trends: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/ads/advertisers', methods=['POST'])
def get_advertisers():
    """Get top advertisers for industry"""
    try:
        data = request.get_json()
        industry = data.get('industry', 'technology')
        limit = data.get('limit', 10)
        
        result = call_mcp_tool('get_top_advertisers', 
                             industry=industry, limit=limit)
        
        # Parse and return result
        if isinstance(result, str):
            try:
                import re
                json_match = re.search(r'\[.*\]', result, re.DOTALL)
                if json_match:
                    return jsonify(json.loads(json_match.group()))
                else:
                    return jsonify(_generate_demo_advertisers(industry, limit))
            except:
                return jsonify(_generate_demo_advertisers(industry, limit))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_advertisers: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/ads/brands', methods=['POST'])
def get_brands():
    """Get all brands for industry"""
    try:
        data = request.get_json()
        industry = data.get('industry', 'technology')
        
        result = call_mcp_tool('get_all_brands_by_industry', 
                             industry=industry, include_competitors=True)
        
        # Parse and return result
        if isinstance(result, str):
            try:
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    return jsonify(json.loads(json_match.group()))
                else:
                    return jsonify(_generate_demo_brands(industry))
            except:
                return jsonify(_generate_demo_brands(industry))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_brands: {e}")  
        return jsonify({"error": str(e)}), 500

@app.route('/api/ads/compare-platforms', methods=['POST'])
def compare_platforms():
    """Compare Meta vs Google Ads"""
    try:
        data = request.get_json()
        industry = data.get('industry', 'technology')
        metric = data.get('metric', 'reach')
        
        result = call_mcp_tool('compare_meta_vs_google_ads', 
                             industry=industry, metric=metric)
        
        # Parse and return result
        if isinstance(result, str):
            try:
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    return jsonify(json.loads(json_match.group()))
                else:
                    return jsonify(_generate_demo_platform_comparison(industry, metric))
            except:
                return jsonify(_generate_demo_platform_comparison(industry, metric))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in compare_platforms: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/ads/brand-strategy', methods=['POST'])
def analyze_brand_strategy():
    """Analyze brand advertising strategy"""
    try:
        data = request.get_json()
        brand_name = data.get('brand_name', 'Example Brand')
        industry = data.get('industry', 'technology')
        platform = data.get('platform', 'both')
        
        platforms = ['meta', 'google'] if platform == 'both' else [platform]
        
        result = call_mcp_tool('analyze_brand_advertising_strategy',
                             brand_name=brand_name, industry=industry, platforms=platforms)
        
        # Parse and return result
        if isinstance(result, str):
            try:
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    return jsonify(json.loads(json_match.group()))
                else:
                    return jsonify(_generate_demo_brand_strategy(brand_name, industry, platforms))
            except:
                return jsonify(_generate_demo_brand_strategy(brand_name, industry, platforms))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in analyze_brand_strategy: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/ads/compare-industries', methods=['POST'])
def compare_industries_endpoint():
    """Compare two industries"""
    try:
        data = request.get_json()
        industry1 = data.get('industry1', 'technology')
        industry2 = data.get('industry2', 'automotive')
        metric = data.get('metric', 'ad_volume')
        
        result = call_mcp_tool('compare_industries',
                             industry1=industry1, industry2=industry2, metric=metric)
        
        # Parse and return result
        if isinstance(result, str):
            try:
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    return jsonify(json.loads(json_match.group()))
                else:
                    return jsonify(_generate_demo_industry_comparison(industry1, industry2, metric))
            except:
                return jsonify(_generate_demo_industry_comparison(industry1, industry2, metric))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in compare_industries: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/brands/sector-overview', methods=['POST'])
def get_sector_overview():
    """Get comprehensive sector overview with European brands in EUR"""
    try:
        data = request.get_json()
        industry = data.get('industry', 'technology')
        currency = data.get('currency', 'EUR')
        country_filter = data.get('country_filter', 'all')
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        
        # Use direct function call when date filtering is requested or server functions are available
        if (date_from and date_to and _generate_sector_overview) or _generate_sector_overview:
            result = _generate_sector_overview(industry, currency, country_filter, date_from, date_to)
            return jsonify(result)
        
        # Fallback to MCP tool call for backwards compatibility
        result = call_mcp_tool('get_sector_overview_eur', 
                             industry=industry, currency=currency, country_filter=country_filter,
                             date_from=date_from, date_to=date_to)
        
        # Parse and return result
        if isinstance(result, str):
            try:
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    return jsonify(json.loads(json_match.group()))
                else:
                    return jsonify(_generate_demo_sector_overview(industry, currency))
            except:
                return jsonify(_generate_demo_sector_overview(industry, currency))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_sector_overview: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/brands/brand-details', methods=['POST'])
def get_brand_details():
    """Get detailed brand information in EUR"""
    try:
        data = request.get_json()
        brand_name = data.get('brand_name', 'SAP')
        industry = data.get('industry', 'technology')
        currency = data.get('currency', 'EUR')
        country_filter = data.get('country_filter', 'all')
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        
        # Use direct function call when date filtering is requested or server functions are available
        if (date_from and date_to and _get_brand_granular_details) or _get_brand_granular_details:
            result = _get_brand_granular_details(brand_name, industry, currency, country_filter, date_from, date_to)
            return jsonify(result)
        
        # Fallback to MCP tool call for backwards compatibility
        result = call_mcp_tool('get_brand_details_eur',
                             brand_name=brand_name, industry=industry, currency=currency, country_filter=country_filter,
                             date_from=date_from, date_to=date_to)
        
        # Parse and return result
        if isinstance(result, str):
            try:
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    return jsonify(json.loads(json_match.group()))
                else:
                    return jsonify(_generate_demo_brand_details(brand_name, industry, currency))
            except:
                return jsonify(_generate_demo_brand_details(brand_name, industry, currency))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_brand_details: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/brands/country-analysis', methods=['POST'])
def get_country_analysis():
    """Get analysis of brands from a specific country"""
    try:
        data = request.get_json()
        country = data.get('country', 'Germany')
        currency = data.get('currency', 'EUR')
        
        result = call_mcp_tool('get_country_brand_analysis_eur',
                             country=country, currency=currency)
        
        # Parse and return result
        if isinstance(result, str):
            try:
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    return jsonify(json.loads(json_match.group()))
                else:
                    return jsonify(_generate_demo_country_analysis(country, currency))
            except:
                return jsonify(_generate_demo_country_analysis(country, currency))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_country_analysis: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/brands/subcategory-analysis', methods=['POST'])
def get_subcategory_analysis():
    """Get granular analysis of industry subcategory"""
    try:
        data = request.get_json()
        industry = data.get('industry', 'technology')
        subcategory = data.get('subcategory', 'enterprise')
        currency = data.get('currency', 'EUR')
        country_filter = data.get('country_filter', 'all')
        
        result = call_mcp_tool('get_subcategory_analysis_eur',
                             industry=industry, subcategory=subcategory, currency=currency, country_filter=country_filter)
        
        # Parse and return result
        if isinstance(result, str):
            try:
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    return jsonify(json.loads(json_match.group()))
                else:
                    return jsonify(_generate_demo_subcategory_analysis(industry, subcategory, currency))
            except:
                return jsonify(_generate_demo_subcategory_analysis(industry, subcategory, currency))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_subcategory_analysis: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def dashboard():
    """Serve the main dashboard"""
    try:
        with open('ad-transparency-dashboard.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>Dashboard Not Found</h1>
        <p>The dashboard HTML file is missing. Please ensure 'ad-transparency-dashboard.html' exists in the project directory.</p>
        <p><a href="/health">Check server health</a></p>
        """

@app.route('/test')
def network_test():
    """Serve the network access test page"""
    try:
        with open('test_network_access.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>Test Page Not Found</h1>
        <p>Network test page is missing.</p>
        <p><a href="/health">Check server health</a> | <a href="/">Back to Dashboard</a></p>
        """

@app.route('/simple')
def simple_test():
    """Serve a simple API test page"""
    try:
        with open('simple_test.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>Simple Test Not Found</h1>
        <p><a href="/health">Check server health</a></p>
        """

@app.route('/diagnostic')
def diagnostic_test():
    """Serve the platform split diagnostic page"""
    try:
        with open('diagnostic.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>Diagnostic Not Found</h1>
        <p><a href="/health">Check server health</a></p>
        """

@app.route('/working')
def working_dashboard():
    """Serve the simplified working dashboard"""
    try:
        with open('working-dashboard-simple.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>Working Dashboard Not Found</h1>
        <p><a href="/health">Check server health</a></p>
        """

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

# Demo data generators (fallback when MCP parsing fails)
def _generate_demo_data(industry, platform, limit):
    """Generate demo ad data"""
    ads = []
    for i in range(min(limit, 10)):
        if platform == 'google':
            ads.append({
                "id": f"demo_google_{industry}_{i}",
                "advertiser_name": f"Google {industry.title()} Co {i+1}",
                "ad_title": f"Best {industry} Solutions",
                "ad_description": f"Premium {industry} services",
                "display_url": f"www.{industry}{i+1}.com",
                "format": "Search",
                "impressions_min": (i+1) * 5000,
                "impressions_max": (i+1) * 25000,
                "clicks_estimate": (i+1) * 250,
                "ctr_estimate": f"{1.5 + i * 0.5}%",
                "platform": "Google Ads"
            })
        else:
            ads.append({
                "id": f"demo_meta_{industry}_{i}",
                "advertiser_name": f"Meta {industry.title()} Co {i+1}",
                "ad_creative_body": f"Amazing {industry} deals!",
                "spend_estimate": f"${(i+1) * 1000}-${(i+1) * 5000}",
                "impressions_estimate": f"{(i+1) * 10000}-{(i+1) * 50000}",
                "ad_type": "image" if i % 2 == 0 else "video",
                "platform": "Facebook"
            })
    return ads

def _generate_demo_trends(industry, days_back):
    """Generate demo trend data"""
    daily_breakdown = []
    for i in range(days_back):
        date = datetime.now() - timedelta(days=i)
        daily_breakdown.append({
            "date": date.strftime("%Y-%m-%d"),
            "ad_count": 10 + i * 2,
            "estimated_spend": f"${(10 + i * 2) * 1000}"
        })
    
    return {
        "industry": industry,
        "analysis_period": f"Last {days_back} days",
        "total_ads": sum(day["ad_count"] for day in daily_breakdown),
        "trend_direction": "increasing",
        "daily_breakdown": daily_breakdown
    }

def _generate_demo_advertisers(industry, limit):
    """Generate demo advertiser data"""
    advertisers = []
    for i in range(min(limit, 10)):
        advertisers.append({
            "rank": i + 1,
            "advertiser_name": f"{industry.title()} Leader {i+1}",
            "estimated_spend": f"${(10-i) * 50000}",
            "ad_count": (10-i) * 25,
            "avg_daily_spend": f"${(10-i) * 2000}"
        })
    return advertisers

def _generate_demo_brands(industry):
    """Generate demo brands data"""
    brands = {
        "luxury": [f"Premium {industry.title()} {i+1}" for i in range(5)],
        "mainstream": [f"Popular {industry.title()} {i+1}" for i in range(8)],
        "emerging": [f"New {industry.title()} {i+1}" for i in range(3)]
    }
    
    return {
        "industry": industry,
        "total_brands": sum(len(category) for category in brands.values()),
        "categories": brands,
        "competitive_analysis": {
            "market_leaders": brands["luxury"][:3],
            "emerging_competitors": brands["emerging"]
        }
    }

def _generate_demo_platform_comparison(industry, metric):
    """Generate demo platform comparison"""
    return {
        "industry": industry,
        "comparison_metric": metric,
        "platforms": {
            "meta": {"reach": 500000, "spend": 50000, "engagement": 3.5, "ctr": 2.1},
            "google": {"reach": 600000, "spend": 60000, "engagement": 4.2, "ctr": 2.8}
        },
        "leader": "google",
        "insights": [
            "Google Ads shows higher reach",
            "Both platforms perform well in this industry"
        ]
    }

def _generate_demo_brand_strategy(brand_name, industry, platforms):
    """Generate demo brand strategy"""
    platform_breakdown = {}
    if 'meta' in platforms:
        platform_breakdown['meta'] = {
            "primary_objective": "Brand awareness",
            "ad_formats": ["Video", "Carousel"],
            "estimated_spend": "$25000",
            "performance_score": 0.85
        }
    if 'google' in platforms:
        platform_breakdown['google'] = {
            "primary_objective": "Lead generation",
            "ad_formats": ["Search", "Display"],
            "estimated_spend": "$30000",
            "performance_score": 0.78
        }
    
    return {
        "brand": brand_name,
        "industry": industry,
        "platforms_analyzed": platforms,
        "overall_strategy": "Multi-platform brand awareness",
        "platform_breakdown": platform_breakdown,
        "recommendations": [
            "Increase video content",
            "Test new audiences",
            "Optimize for mobile"
        ]
    }

def _generate_demo_industry_comparison(industry1, industry2, metric):
    """Generate demo industry comparison"""
    return {
        "comparison_metric": metric,
        "industries": {
            industry1: {"value": 750, "trend": "increasing"},
            industry2: {"value": 680, "trend": "stable"}
        },
        "leader": industry1,
        "difference_percentage": 10.3
    }

def _generate_demo_sector_overview(industry, currency):
    """Generate demo sector overview with European brands"""
    return {
        "industry": industry,
        "currency": currency,
        "total_categories": 3,
        "sector_totals": {
            "total_brands": 15,
            "total_ad_spend": 2500000000 if currency == "EUR" else 2700000000,
            "total_ad_spend_formatted": "€2.5B" if currency == "EUR" else "$2.7B"
        },
        "categories": {
            "luxury": {
                "brand_count": 5,
                "total_spend": 1200000000,
                "total_spend_formatted": "€1.2B",
                "brands": [
                    {"name": f"Luxury {industry.title()} 1", "country": "Germany", "annual_ad_spend_formatted": "€350M"},
                    {"name": f"Luxury {industry.title()} 2", "country": "France", "annual_ad_spend_formatted": "€280M"}
                ]
            },
            "mainstream": {
                "brand_count": 8,
                "total_spend": 950000000,
                "total_spend_formatted": "€950M",
                "brands": [
                    {"name": f"Mainstream {industry.title()} 1", "country": "Germany", "annual_ad_spend_formatted": "€180M"},
                    {"name": f"Mainstream {industry.title()} 2", "country": "Spain", "annual_ad_spend_formatted": "€150M"}
                ]
            }
        },
        "country_breakdown": {
            "Germany": {"brands": 6, "total_spend_formatted": "€980M"},
            "France": {"brands": 4, "total_spend_formatted": "€720M"},
            "Spain": {"brands": 3, "total_spend_formatted": "€450M"},
            "UK": {"brands": 2, "total_spend_formatted": "€350M"}
        }
    }

def _generate_demo_brand_details(brand_name, industry, currency):
    """Generate demo detailed brand information"""
    base_spend = 480000000 if currency == "EUR" else 518400000
    symbol = "€" if currency == "EUR" else "$"
    
    return {
        "brand_name": brand_name,
        "industry": industry,
        "category": "enterprise",
        "country": "Germany",
        "headquarters": "Munich",
        "financial_data": {
            "annual_ad_spend_formatted": f"{symbol}480M",
            "currency": currency,
            "market_share_percent": 8.2,
            "estimated_monthly_spend_formatted": f"{symbol}40M",
            "estimated_daily_spend_formatted": f"{symbol}1.3M"
        },
        "competitive_position": {
            "rank_in_category": 2,
            "total_brands_in_category": 8,
            "category_leader": f"Top {industry.title()} Enterprise",
            "spend_vs_leader": 0.85
        },
        "advertising_breakdown": {
            "digital_estimated_formatted": f"{symbol}312M",
            "traditional_estimated_formatted": f"{symbol}168M",
            "meta_estimated_formatted": f"{symbol}120M",
            "google_estimated_formatted": f"{symbol}134M",
            "other_digital_estimated_formatted": f"{symbol}58M"
        }
    }

def _generate_demo_country_analysis(country, currency):
    """Generate demo country brand analysis"""
    symbol = "€" if currency == "EUR" else "$"
    
    return {
        "country": country,
        "currency": currency,
        "summary": {
            "total_brands": 25,
            "total_ad_spend_formatted": f"{symbol}3.2B",
            "total_market_share": 45.8,
            "industries_represented": 5
        },
        "top_brands": [
            {"name": f"{country} Auto Leader", "industry": "automotive", "annual_ad_spend_formatted": f"{symbol}420M"},
            {"name": f"{country} Tech Giant", "industry": "technology", "annual_ad_spend_formatted": f"{symbol}380M"},
            {"name": f"{country} Fashion House", "industry": "fashion", "annual_ad_spend_formatted": f"{symbol}320M"}
        ],
        "industry_breakdown": {
            "automotive": {"brands": 8, "total_spend_formatted": f"{symbol}1.2B"},
            "technology": {"brands": 6, "total_spend_formatted": f"{symbol}890M"},
            "fashion": {"brands": 5, "total_spend_formatted": f"{symbol}650M"},
            "finance": {"brands": 4, "total_spend_formatted": f"{symbol}380M"},
            "food": {"brands": 2, "total_spend_formatted": f"{symbol}280M"}
        }
    }

def _generate_demo_subcategory_analysis(industry, subcategory, currency):
    """Generate demo subcategory analysis"""
    symbol = "€" if currency == "EUR" else "$"
    
    return {
        "industry": industry,
        "subcategory": subcategory,
        "currency": currency,
        "summary": {
            "total_brands": 8,
            "total_ad_spend_formatted": f"{symbol}1.8B",
            "average_spend_per_brand_formatted": f"{symbol}225M",
            "countries_represented": 4
        },
        "brands": [
            {"name": f"{subcategory.title()} Leader 1", "country": "Germany", "annual_ad_spend_formatted": f"{symbol}480M", "share_of_category_spend": 26.7},
            {"name": f"{subcategory.title()} Leader 2", "country": "France", "annual_ad_spend_formatted": f"{symbol}380M", "share_of_category_spend": 21.1},
            {"name": f"{subcategory.title()} Leader 3", "country": "UK", "annual_ad_spend_formatted": f"{symbol}320M", "share_of_category_spend": 17.8}
        ],
        "country_analysis": {
            "Germany": {"brands": 3, "total_spend_formatted": f"{symbol}850M"},
            "France": {"brands": 2, "total_spend_formatted": f"{symbol}480M"},
            "UK": {"brands": 2, "total_spend_formatted": f"{symbol}380M"},
            "Netherlands": {"brands": 1, "total_spend_formatted": f"{symbol}90M"}
        },
        "market_concentration": {
            "top_3_share": 65.6,
            "top_5_share": 88.9,
            "herfindahl_index": 0.18
        }
    }

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 3000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    logger.info(f"Starting HTTP Bridge Server on port {port}...")
    
    # Start the bridge server
    app.run(host='0.0.0.0', port=port, debug=debug_mode)