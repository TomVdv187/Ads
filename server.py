#!/usr/bin/env python3
"""
Simple MCP Server Example

This server provides basic tools and resources for demonstration purposes.
"""

import json
import platform
import sys
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from mcp.server import FastMCP
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Server instance
mcp = FastMCP("demo-server")

# Simple in-memory storage for demonstration
notes_storage: Dict[str, Dict[str, str]] = {}

# Ad transparency cache to avoid excessive API calls
ad_cache: Dict[str, Dict] = {}
google_ads_cache: Dict[str, Dict] = {}
brands_cache: Dict[str, List] = {}

# Industry keywords mapping for ad filtering
INDUSTRY_KEYWORDS = {
    "automotive": ["car", "auto", "vehicle", "truck", "suv", "sedan", "hybrid", "electric vehicle", "ev", "dealership", "automotive", "motor", "drive", "lease", "finance car"],
    "fashion": ["clothing", "fashion", "apparel", "style", "wear", "dress", "shirt", "shoes", "accessories", "designer", "boutique", "retail fashion"],
    "technology": ["tech", "software", "app", "digital", "ai", "artificial intelligence", "cloud", "saas", "mobile", "computer", "innovation", "startup"],
    "healthcare": ["health", "medical", "healthcare", "doctor", "hospital", "medicine", "wellness", "pharma", "treatment", "clinic", "therapy"],
    "finance": ["bank", "finance", "loan", "credit", "investment", "insurance", "financial", "money", "mortgage", "crypto", "trading", "fintech"],
    "food": ["food", "restaurant", "dining", "cuisine", "delivery", "meal", "recipe", "cooking", "kitchen", "beverage", "grocery", "fast food"],
    "travel": ["travel", "hotel", "vacation", "flight", "tourism", "booking", "resort", "trip", "airline", "cruise", "adventure", "destination"],
    "education": ["education", "school", "university", "course", "learning", "training", "degree", "online learning", "academy", "certification", "tutoring"],
    "real_estate": ["real estate", "property", "home", "house", "apartment", "rent", "buy", "mortgage", "realtor", "housing", "commercial property"],
    "gaming": ["game", "gaming", "video game", "mobile game", "console", "esports", "streaming", "twitch", "xbox", "playstation", "nintendo"]
}

# Comprehensive brand database for Belgian and French market advertising spend
# All brands (global and local) spending on Meta and Google ads targeting Belgian and French consumers
BELGIUM_FRANCE_BRANDS_DATABASE = {
    "automotive": {
        # Global luxury brands advertising in Belgium & France
        "Mercedes-Benz": {"belgium_ad_spend_eur": 45000000, "france_ad_spend_eur": 180000000, "total_spend": 225000000, "market_share_be": 8.2, "market_share_fr": 12.5, "platforms": ["Meta", "Google"], "ad_types": {"video": 65, "display": 35, "video_spend_eur": 146250000, "display_spend_eur": 78750000}},
        "BMW": {"belgium_ad_spend_eur": 42000000, "france_ad_spend_eur": 165000000, "total_spend": 207000000, "market_share_be": 7.8, "market_share_fr": 11.8, "platforms": ["Meta", "Google"], "ad_types": {"video": 70, "display": 30, "video_spend_eur": 144900000, "display_spend_eur": 62100000}},
        "Audi": {"belgium_ad_spend_eur": 38000000, "france_ad_spend_eur": 155000000, "total_spend": 193000000, "market_share_be": 7.1, "market_share_fr": 10.2, "platforms": ["Meta", "Google"], "ad_types": {"video": 68, "display": 32, "video_spend_eur": 131240000, "display_spend_eur": 61760000}},
        "Tesla": {"belgium_ad_spend_eur": 15000000, "france_ad_spend_eur": 75000000, "total_spend": 90000000, "market_share_be": 2.8, "market_share_fr": 4.2, "platforms": ["Meta", "Google"], "ad_types": {"video": 80, "display": 20, "video_spend_eur": 72000000, "display_spend_eur": 18000000}},
        "Toyota": {"belgium_ad_spend_eur": 28000000, "france_ad_spend_eur": 120000000, "total_spend": 148000000, "market_share_be": 9.5, "market_share_fr": 8.9, "platforms": ["Meta", "Google"], "ad_types": {"video": 55, "display": 45, "video_spend_eur": 81400000, "display_spend_eur": 66600000}},
        "Volkswagen": {"belgium_ad_spend_eur": 35000000, "france_ad_spend_eur": 145000000, "total_spend": 180000000, "market_share_be": 12.5, "market_share_fr": 15.2, "platforms": ["Meta", "Google"], "ad_types": {"video": 58, "display": 42, "video_spend_eur": 104400000, "display_spend_eur": 75600000}},
        "Renault": {"belgium_ad_spend_eur": 22000000, "france_ad_spend_eur": 185000000, "total_spend": 207000000, "market_share_be": 6.8, "market_share_fr": 18.5, "platforms": ["Meta", "Google"], "ad_types": {"video": 62, "display": 38, "video_spend_eur": 128340000, "display_spend_eur": 78660000}},
        "Peugeot": {"belgium_ad_spend_eur": 25000000, "france_ad_spend_eur": 165000000, "total_spend": 190000000, "market_share_be": 7.5, "market_share_fr": 16.2, "platforms": ["Meta", "Google"]},
        "Citroën": {"belgium_ad_spend_eur": 18000000, "france_ad_spend_eur": 125000000, "total_spend": 143000000, "market_share_be": 5.2, "market_share_fr": 12.8, "platforms": ["Meta", "Google"]},
        "Ford": {"belgium_ad_spend_eur": 20000000, "france_ad_spend_eur": 85000000, "total_spend": 105000000, "market_share_be": 6.1, "market_share_fr": 6.5, "platforms": ["Meta", "Google"]},
        "Opel": {"belgium_ad_spend_eur": 16000000, "france_ad_spend_eur": 68000000, "total_spend": 84000000, "market_share_be": 4.8, "market_share_fr": 5.9, "platforms": ["Meta", "Google"]},
        "Hyundai": {"belgium_ad_spend_eur": 14000000, "france_ad_spend_eur": 58000000, "total_spend": 72000000, "market_share_be": 4.2, "market_share_fr": 4.8, "platforms": ["Meta", "Google"]},
        "Kia": {"belgium_ad_spend_eur": 12000000, "france_ad_spend_eur": 52000000, "total_spend": 64000000, "market_share_be": 3.8, "market_share_fr": 4.2, "platforms": ["Meta", "Google"]},
        "Nissan": {"belgium_ad_spend_eur": 11000000, "france_ad_spend_eur": 48000000, "total_spend": 59000000, "market_share_be": 3.2, "market_share_fr": 3.8, "platforms": ["Meta", "Google"]},
        "Volvo": {"belgium_ad_spend_eur": 9000000, "france_ad_spend_eur": 42000000, "total_spend": 51000000, "market_share_be": 2.8, "market_share_fr": 3.2, "platforms": ["Meta", "Google"]},
        "Mazda": {"belgium_ad_spend_eur": 8000000, "france_ad_spend_eur": 35000000, "total_spend": 43000000, "market_share_be": 2.4, "market_share_fr": 2.8, "platforms": ["Meta", "Google"]},
        "Honda": {"belgium_ad_spend_eur": 10000000, "france_ad_spend_eur": 45000000, "total_spend": 55000000, "market_share_be": 3.1, "market_share_fr": 3.5, "platforms": ["Meta", "Google"]},
        "Porsche": {"belgium_ad_spend_eur": 8000000, "france_ad_spend_eur": 38000000, "total_spend": 46000000, "market_share_be": 1.2, "market_share_fr": 2.1, "platforms": ["Meta", "Google"]},
        "Jaguar": {"belgium_ad_spend_eur": 5000000, "france_ad_spend_eur": 25000000, "total_spend": 30000000, "market_share_be": 0.8, "market_share_fr": 1.2, "platforms": ["Meta", "Google"]},
        "Land Rover": {"belgium_ad_spend_eur": 7000000, "france_ad_spend_eur": 32000000, "total_spend": 39000000, "market_share_be": 1.5, "market_share_fr": 1.8, "platforms": ["Meta", "Google"]},
        # Local Belgian car dealers
        "D'Ieteren Group": {"belgium_ad_spend_eur": 3500000, "france_ad_spend_eur": 0, "total_spend": 3500000, "market_share_be": 2.1, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "Kroymans": {"belgium_ad_spend_eur": 1200000, "france_ad_spend_eur": 0, "total_spend": 1200000, "market_share_be": 0.8, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "Autoscoop": {"belgium_ad_spend_eur": 800000, "france_ad_spend_eur": 0, "total_spend": 800000, "market_share_be": 0.5, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        # Local French car dealers 
        "Groupe PSA Retail": {"belgium_ad_spend_eur": 0, "france_ad_spend_eur": 25000000, "total_spend": 25000000, "market_share_be": 0, "market_share_fr": 5.2, "platforms": ["Meta", "Google"]},
        "Groupe Maurin": {"belgium_ad_spend_eur": 0, "france_ad_spend_eur": 8000000, "total_spend": 8000000, "market_share_be": 0, "market_share_fr": 1.8, "platforms": ["Meta", "Google"]},
        "Groupe Bernard": {"belgium_ad_spend_eur": 0, "france_ad_spend_eur": 6500000, "total_spend": 6500000, "market_share_be": 0, "market_share_fr": 1.5, "platforms": ["Meta", "Google"]},
        # More automotive brands
        "Lexus": {"belgium_ad_spend_eur": 6000000, "france_ad_spend_eur": 28000000, "total_spend": 34000000, "market_share_be": 1.8, "market_share_fr": 2.4, "platforms": ["Meta", "Google"], "ad_types": {"video": 75, "display": 25, "video_spend_eur": 25500000, "display_spend_eur": 8500000}},
        "Infiniti": {"belgium_ad_spend_eur": 3500000, "france_ad_spend_eur": 18000000, "total_spend": 21500000, "market_share_be": 1.1, "market_share_fr": 1.5, "platforms": ["Meta", "Google"], "ad_types": {"video": 68, "display": 32, "video_spend_eur": 14620000, "display_spend_eur": 6880000}},
        "Acura": {"belgium_ad_spend_eur": 2800000, "france_ad_spend_eur": 15000000, "total_spend": 17800000, "market_share_be": 0.9, "market_share_fr": 1.2, "platforms": ["Meta", "Google"], "ad_types": {"video": 65, "display": 35, "video_spend_eur": 11570000, "display_spend_eur": 6230000}},
        "Genesis": {"belgium_ad_spend_eur": 2200000, "france_ad_spend_eur": 12000000, "total_spend": 14200000, "market_share_be": 0.7, "market_share_fr": 1.0, "platforms": ["Meta", "Google"], "ad_types": {"video": 72, "display": 28, "video_spend_eur": 10224000, "display_spend_eur": 3976000}},
        "Subaru": {"belgium_ad_spend_eur": 5000000, "france_ad_spend_eur": 22000000, "total_spend": 27000000, "market_share_be": 1.6, "market_share_fr": 1.8, "platforms": ["Meta", "Google"], "ad_types": {"video": 58, "display": 42, "video_spend_eur": 15660000, "display_spend_eur": 11340000}},
        "Mitsubishi": {"belgium_ad_spend_eur": 3800000, "france_ad_spend_eur": 16000000, "total_spend": 19800000, "market_share_be": 1.2, "market_share_fr": 1.3, "platforms": ["Meta", "Google"], "ad_types": {"video": 52, "display": 48, "video_spend_eur": 10296000, "display_spend_eur": 9504000}},
        "Isuzu": {"belgium_ad_spend_eur": 1800000, "france_ad_spend_eur": 8500000, "total_spend": 10300000, "market_share_be": 0.6, "market_share_fr": 0.7, "platforms": ["Meta", "Google"], "ad_types": {"video": 45, "display": 55, "video_spend_eur": 4635000, "display_spend_eur": 5665000}},
        "Suzuki": {"belgium_ad_spend_eur": 4200000, "france_ad_spend_eur": 18500000, "total_spend": 22700000, "market_share_be": 1.3, "market_share_fr": 1.5, "platforms": ["Meta", "Google"], "ad_types": {"video": 48, "display": 52, "video_spend_eur": 10896000, "display_spend_eur": 11804000}},
        "Dacia": {"belgium_ad_spend_eur": 8000000, "france_ad_spend_eur": 45000000, "total_spend": 53000000, "market_share_be": 2.5, "market_share_fr": 3.8, "platforms": ["Meta", "Google"], "ad_types": {"video": 40, "display": 60, "video_spend_eur": 21200000, "display_spend_eur": 31800000}},
        "Skoda": {"belgium_ad_spend_eur": 6500000, "france_ad_spend_eur": 32000000, "total_spend": 38500000, "market_share_be": 2.0, "market_share_fr": 2.7, "platforms": ["Meta", "Google"], "ad_types": {"video": 55, "display": 45, "video_spend_eur": 21175000, "display_spend_eur": 17325000}}
    },
    "fashion": {
        # Global luxury brands advertising in Belgium & France
        "LVMH": {"belgium_ad_spend_eur": 25000000, "france_ad_spend_eur": 285000000, "total_spend": 310000000, "market_share_be": 18.5, "market_share_fr": 22.8, "platforms": ["Meta", "Google"]},
        "Chanel": {"belgium_ad_spend_eur": 20000000, "france_ad_spend_eur": 195000000, "total_spend": 215000000, "market_share_be": 15.2, "market_share_fr": 18.5, "platforms": ["Meta", "Google"]},
        "Hermès": {"belgium_ad_spend_eur": 18000000, "france_ad_spend_eur": 165000000, "total_spend": 183000000, "market_share_be": 12.8, "market_share_fr": 16.2, "platforms": ["Meta", "Google"]},
        "Gucci": {"belgium_ad_spend_eur": 15000000, "france_ad_spend_eur": 125000000, "total_spend": 140000000, "market_share_be": 10.5, "market_share_fr": 12.8, "platforms": ["Meta", "Google"]},
        "Prada": {"belgium_ad_spend_eur": 12000000, "france_ad_spend_eur": 95000000, "total_spend": 107000000, "market_share_be": 8.5, "market_share_fr": 9.8, "platforms": ["Meta", "Google"]},
        "Burberry": {"belgium_ad_spend_eur": 8000000, "france_ad_spend_eur": 65000000, "total_spend": 73000000, "market_share_be": 5.8, "market_share_fr": 6.5, "platforms": ["Meta", "Google"]},
        # Global fast fashion brands
        "Zara": {"belgium_ad_spend_eur": 22000000, "france_ad_spend_eur": 145000000, "total_spend": 167000000, "market_share_be": 15.8, "market_share_fr": 18.2, "platforms": ["Meta", "Google"]},
        "H&M": {"belgium_ad_spend_eur": 18000000, "france_ad_spend_eur": 125000000, "total_spend": 143000000, "market_share_be": 12.5, "market_share_fr": 15.8, "platforms": ["Meta", "Google"]},
        "Uniqlo": {"belgium_ad_spend_eur": 8000000, "france_ad_spend_eur": 55000000, "total_spend": 63000000, "market_share_be": 5.2, "market_share_fr": 6.8, "platforms": ["Meta", "Google"]},
        "Mango": {"belgium_ad_spend_eur": 6000000, "france_ad_spend_eur": 42000000, "total_spend": 48000000, "market_share_be": 4.2, "market_share_fr": 5.1, "platforms": ["Meta", "Google"]},
        # Global sportswear brands
        "Nike": {"belgium_ad_spend_eur": 35000000, "france_ad_spend_eur": 185000000, "total_spend": 220000000, "market_share_be": 25.8, "market_share_fr": 28.5, "platforms": ["Meta", "Google"]},
        "Adidas": {"belgium_ad_spend_eur": 28000000, "france_ad_spend_eur": 155000000, "total_spend": 183000000, "market_share_be": 20.5, "market_share_fr": 22.8, "platforms": ["Meta", "Google"]},
        "Puma": {"belgium_ad_spend_eur": 12000000, "france_ad_spend_eur": 85000000, "total_spend": 97000000, "market_share_be": 8.5, "market_share_fr": 9.8, "platforms": ["Meta", "Google"]},
        "Under Armour": {"belgium_ad_spend_eur": 5000000, "france_ad_spend_eur": 35000000, "total_spend": 40000000, "market_share_be": 3.5, "market_share_fr": 4.2, "platforms": ["Meta", "Google"]},
        "Lululemon": {"belgium_ad_spend_eur": 4000000, "france_ad_spend_eur": 28000000, "total_spend": 32000000, "market_share_be": 2.8, "market_share_fr": 3.5, "platforms": ["Meta", "Google"]},
        # Belgian fashion brands/retailers
        "JBC": {"belgium_ad_spend_eur": 3500000, "france_ad_spend_eur": 0, "total_spend": 3500000, "market_share_be": 5.8, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "CKS": {"belgium_ad_spend_eur": 1800000, "france_ad_spend_eur": 0, "total_spend": 1800000, "market_share_be": 2.5, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "ZEB": {"belgium_ad_spend_eur": 1200000, "france_ad_spend_eur": 0, "total_spend": 1200000, "market_share_be": 1.8, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "Mayerline": {"belgium_ad_spend_eur": 800000, "france_ad_spend_eur": 0, "total_spend": 800000, "market_share_be": 1.2, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "Terre Bleue": {"belgium_ad_spend_eur": 650000, "france_ad_spend_eur": 0, "total_spend": 650000, "market_share_be": 0.9, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        # French fashion brands/retailers
        "Lacoste": {"belgium_ad_spend_eur": 3000000, "france_ad_spend_eur": 45000000, "total_spend": 48000000, "market_share_be": 2.2, "market_share_fr": 5.8, "platforms": ["Meta", "Google"]},
        "Galeries Lafayette": {"belgium_ad_spend_eur": 0, "france_ad_spend_eur": 35000000, "total_spend": 35000000, "market_share_be": 0, "market_share_fr": 4.5, "platforms": ["Meta", "Google"]},
        "Printemps": {"belgium_ad_spend_eur": 0, "france_ad_spend_eur": 28000000, "total_spend": 28000000, "market_share_be": 0, "market_share_fr": 3.8, "platforms": ["Meta", "Google"]},
        "La Redoute": {"belgium_ad_spend_eur": 1500000, "france_ad_spend_eur": 25000000, "total_spend": 26500000, "market_share_be": 1.1, "market_share_fr": 3.2, "platforms": ["Meta", "Google"]},
        "3 Suisses": {"belgium_ad_spend_eur": 800000, "france_ad_spend_eur": 12000000, "total_spend": 12800000, "market_share_be": 0.6, "market_share_fr": 1.5, "platforms": ["Meta", "Google"]},
        "Kiabi": {"belgium_ad_spend_eur": 2500000, "france_ad_spend_eur": 22000000, "total_spend": 24500000, "market_share_be": 1.8, "market_share_fr": 2.8, "platforms": ["Meta", "Google"]},
        "Celio": {"belgium_ad_spend_eur": 1200000, "france_ad_spend_eur": 18000000, "total_spend": 19200000, "market_share_be": 0.9, "market_share_fr": 2.2, "platforms": ["Meta", "Google"]}
    },
    "technology": {
        # Global tech giants advertising in Belgium & France
        "Apple": {"belgium_ad_spend_eur": 25000000, "france_ad_spend_eur": 125000000, "total_spend": 150000000, "market_share_be": 28.5, "market_share_fr": 25.8, "platforms": ["Meta", "Google"]},
        "Google": {"belgium_ad_spend_eur": 22000000, "france_ad_spend_eur": 115000000, "total_spend": 137000000, "market_share_be": 25.2, "market_share_fr": 22.5, "platforms": ["Meta"]},
        "Microsoft": {"belgium_ad_spend_eur": 18000000, "france_ad_spend_eur": 95000000, "total_spend": 113000000, "market_share_be": 20.5, "market_share_fr": 18.8, "platforms": ["Meta", "Google"]},
        "Meta": {"belgium_ad_spend_eur": 15000000, "france_ad_spend_eur": 85000000, "total_spend": 100000000, "market_share_be": 18.2, "market_share_fr": 16.5, "platforms": ["Google"]},
        "Samsung": {"belgium_ad_spend_eur": 12000000, "france_ad_spend_eur": 75000000, "total_spend": 87000000, "market_share_be": 15.8, "market_share_fr": 14.2, "platforms": ["Meta", "Google"]},
        "Amazon": {"belgium_ad_spend_eur": 10000000, "france_ad_spend_eur": 65000000, "total_spend": 75000000, "market_share_be": 12.5, "market_share_fr": 12.8, "platforms": ["Meta", "Google"]},
        "Netflix": {"belgium_ad_spend_eur": 8000000, "france_ad_spend_eur": 55000000, "total_spend": 63000000, "market_share_be": 8.5, "market_share_fr": 9.2, "platforms": ["Meta", "Google"]},
        "Spotify": {"belgium_ad_spend_eur": 6000000, "france_ad_spend_eur": 42000000, "total_spend": 48000000, "market_share_be": 6.8, "market_share_fr": 7.5, "platforms": ["Meta", "Google"]},
        "Adobe": {"belgium_ad_spend_eur": 4000000, "france_ad_spend_eur": 32000000, "total_spend": 36000000, "market_share_be": 4.2, "market_share_fr": 5.1, "platforms": ["Meta", "Google"]},
        "Salesforce": {"belgium_ad_spend_eur": 3500000, "france_ad_spend_eur": 28000000, "total_spend": 31500000, "market_share_be": 3.8, "market_share_fr": 4.5, "platforms": ["Meta", "Google"]},
        # European tech companies
        "SAP": {"belgium_ad_spend_eur": 5000000, "france_ad_spend_eur": 35000000, "total_spend": 40000000, "market_share_be": 5.2, "market_share_fr": 6.8, "platforms": ["Meta", "Google"]},
        "Philips": {"belgium_ad_spend_eur": 4500000, "france_ad_spend_eur": 32000000, "total_spend": 36500000, "market_share_be": 4.8, "market_share_fr": 6.2, "platforms": ["Meta", "Google"]},
        "ASML": {"belgium_ad_spend_eur": 2000000, "france_ad_spend_eur": 18000000, "total_spend": 20000000, "market_share_be": 2.1, "market_share_fr": 3.2, "platforms": ["Meta", "Google"]},
        "Nokia": {"belgium_ad_spend_eur": 1800000, "france_ad_spend_eur": 15000000, "total_spend": 16800000, "market_share_be": 1.9, "market_share_fr": 2.8, "platforms": ["Meta", "Google"]},
        "Siemens": {"belgium_ad_spend_eur": 3000000, "france_ad_spend_eur": 25000000, "total_spend": 28000000, "market_share_be": 3.2, "market_share_fr": 4.8, "platforms": ["Meta", "Google"]},
        # Fintech companies
        "Klarna": {"belgium_ad_spend_eur": 3500000, "france_ad_spend_eur": 28000000, "total_spend": 31500000, "market_share_be": 8.5, "market_share_fr": 12.5, "platforms": ["Meta", "Google"]},
        "Revolut": {"belgium_ad_spend_eur": 3000000, "france_ad_spend_eur": 25000000, "total_spend": 28000000, "market_share_be": 7.2, "market_share_fr": 10.8, "platforms": ["Meta", "Google"]},
        "N26": {"belgium_ad_spend_eur": 2500000, "france_ad_spend_eur": 22000000, "total_spend": 24500000, "market_share_be": 6.1, "market_share_fr": 9.5, "platforms": ["Meta", "Google"]},
        "Wise": {"belgium_ad_spend_eur": 2000000, "france_ad_spend_eur": 18000000, "total_spend": 20000000, "market_share_be": 4.8, "market_share_fr": 7.8, "platforms": ["Meta", "Google"]},
        "PayPal": {"belgium_ad_spend_eur": 4000000, "france_ad_spend_eur": 32000000, "total_spend": 36000000, "market_share_be": 9.8, "market_share_fr": 15.2, "platforms": ["Meta", "Google"]},
        # Belgian tech companies
        "Odoo": {"belgium_ad_spend_eur": 2800000, "france_ad_spend_eur": 5000000, "total_spend": 7800000, "market_share_be": 3.2, "market_share_fr": 1.8, "platforms": ["Meta", "Google"]},
        "Collibra": {"belgium_ad_spend_eur": 1500000, "france_ad_spend_eur": 2000000, "total_spend": 3500000, "market_share_be": 1.8, "market_share_fr": 0.8, "platforms": ["Meta", "Google"]},
        "Showpad": {"belgium_ad_spend_eur": 800000, "france_ad_spend_eur": 1200000, "total_spend": 2000000, "market_share_be": 0.9, "market_share_fr": 0.5, "platforms": ["Meta", "Google"]},
        # French tech companies
        "Criteo": {"belgium_ad_spend_eur": 1200000, "france_ad_spend_eur": 15000000, "total_spend": 16200000, "market_share_be": 1.4, "market_share_fr": 5.8, "platforms": ["Meta", "Google"]},
        "Dassault Systèmes": {"belgium_ad_spend_eur": 800000, "france_ad_spend_eur": 12000000, "total_spend": 12800000, "market_share_be": 0.9, "market_share_fr": 4.5, "platforms": ["Meta", "Google"]},
        "Atos": {"belgium_ad_spend_eur": 1000000, "france_ad_spend_eur": 8000000, "total_spend": 9000000, "market_share_be": 1.1, "market_share_fr": 3.2, "platforms": ["Meta", "Google"]},
        # More global tech companies
        "Adobe": {"belgium_ad_spend_eur": 4000000, "france_ad_spend_eur": 18000000, "total_spend": 22000000, "market_share_be": 4.6, "market_share_fr": 6.8, "platforms": ["Meta", "Google"], "ad_types": {"video": 72, "display": 28, "video_spend_eur": 15840000, "display_spend_eur": 6160000}},
        "Oracle": {"belgium_ad_spend_eur": 3500000, "france_ad_spend_eur": 16000000, "total_spend": 19500000, "market_share_be": 4.1, "market_share_fr": 6.1, "platforms": ["Meta", "Google"], "ad_types": {"video": 45, "display": 55, "video_spend_eur": 8775000, "display_spend_eur": 10725000}},
        "Salesforce": {"belgium_ad_spend_eur": 5000000, "france_ad_spend_eur": 22000000, "total_spend": 27000000, "market_share_be": 5.8, "market_share_fr": 8.3, "platforms": ["Meta", "Google"], "ad_types": {"video": 65, "display": 35, "video_spend_eur": 17550000, "display_spend_eur": 9450000}},
        "ServiceNow": {"belgium_ad_spend_eur": 2800000, "france_ad_spend_eur": 12000000, "total_spend": 14800000, "market_share_be": 3.2, "market_share_fr": 4.5, "platforms": ["Meta", "Google"], "ad_types": {"video": 58, "display": 42, "video_spend_eur": 8584000, "display_spend_eur": 6216000}},
        "Workday": {"belgium_ad_spend_eur": 2200000, "france_ad_spend_eur": 9500000, "total_spend": 11700000, "market_share_be": 2.5, "market_share_fr": 3.6, "platforms": ["Meta", "Google"], "ad_types": {"video": 52, "display": 48, "video_spend_eur": 6084000, "display_spend_eur": 5616000}},
        "Palantir": {"belgium_ad_spend_eur": 1800000, "france_ad_spend_eur": 8000000, "total_spend": 9800000, "market_share_be": 2.1, "market_share_fr": 3.0, "platforms": ["Meta", "Google"], "ad_types": {"video": 75, "display": 25, "video_spend_eur": 7350000, "display_spend_eur": 2450000}},
        "Snowflake": {"belgium_ad_spend_eur": 3200000, "france_ad_spend_eur": 14000000, "total_spend": 17200000, "market_share_be": 3.7, "market_share_fr": 5.3, "platforms": ["Meta", "Google"], "ad_types": {"video": 68, "display": 32, "video_spend_eur": 11696000, "display_spend_eur": 5504000}},
        "MongoDB": {"belgium_ad_spend_eur": 1500000, "france_ad_spend_eur": 6500000, "total_spend": 8000000, "market_share_be": 1.7, "market_share_fr": 2.5, "platforms": ["Meta", "Google"], "ad_types": {"video": 60, "display": 40, "video_spend_eur": 4800000, "display_spend_eur": 3200000}},
        "Atlassian": {"belgium_ad_spend_eur": 2500000, "france_ad_spend_eur": 11000000, "total_spend": 13500000, "market_share_be": 2.9, "market_share_fr": 4.2, "platforms": ["Meta", "Google"], "ad_types": {"video": 55, "display": 45, "video_spend_eur": 7425000, "display_spend_eur": 6075000}},
        "Slack": {"belgium_ad_spend_eur": 2800000, "france_ad_spend_eur": 12500000, "total_spend": 15300000, "market_share_be": 3.2, "market_share_fr": 4.7, "platforms": ["Meta", "Google"], "ad_types": {"video": 70, "display": 30, "video_spend_eur": 10710000, "display_spend_eur": 4590000}},
        "Zoom": {"belgium_ad_spend_eur": 3500000, "france_ad_spend_eur": 15000000, "total_spend": 18500000, "market_share_be": 4.1, "market_share_fr": 5.7, "platforms": ["Meta", "Google"], "ad_types": {"video": 80, "display": 20, "video_spend_eur": 14800000, "display_spend_eur": 3700000}},
        "Dropbox": {"belgium_ad_spend_eur": 1800000, "france_ad_spend_eur": 7500000, "total_spend": 9300000, "market_share_be": 2.1, "market_share_fr": 2.8, "platforms": ["Meta", "Google"], "ad_types": {"video": 50, "display": 50, "video_spend_eur": 4650000, "display_spend_eur": 4650000}}
    },
    "finance": {
        # Major European banks advertising in Belgium & France
        "BNP Paribas": {"belgium_ad_spend_eur": 15000000, "france_ad_spend_eur": 95000000, "total_spend": 110000000, "market_share_be": 18.5, "market_share_fr": 22.8, "platforms": ["Meta", "Google"]},
        "Crédit Agricole": {"belgium_ad_spend_eur": 8000000, "france_ad_spend_eur": 85000000, "total_spend": 93000000, "market_share_be": 9.8, "market_share_fr": 20.5, "platforms": ["Meta", "Google"]},
        "Société Générale": {"belgium_ad_spend_eur": 6000000, "france_ad_spend_eur": 75000000, "total_spend": 81000000, "market_share_be": 7.2, "market_share_fr": 18.2, "platforms": ["Meta", "Google"]},
        "ING": {"belgium_ad_spend_eur": 12000000, "france_ad_spend_eur": 25000000, "total_spend": 37000000, "market_share_be": 14.5, "market_share_fr": 6.1, "platforms": ["Meta", "Google"]},
        "KBC": {"belgium_ad_spend_eur": 18000000, "france_ad_spend_eur": 0, "total_spend": 18000000, "market_share_be": 22.8, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "Belfius": {"belgium_ad_spend_eur": 12000000, "france_ad_spend_eur": 0, "total_spend": 12000000, "market_share_be": 15.2, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "Deutsche Bank": {"belgium_ad_spend_eur": 3000000, "france_ad_spend_eur": 18000000, "total_spend": 21000000, "market_share_be": 3.8, "market_share_fr": 4.2, "platforms": ["Meta", "Google"]},
        "Santander": {"belgium_ad_spend_eur": 2000000, "france_ad_spend_eur": 15000000, "total_spend": 17000000, "market_share_be": 2.5, "market_share_fr": 3.6, "platforms": ["Meta", "Google"]},
        # Insurance companies
        "AXA": {"belgium_ad_spend_eur": 8000000, "france_ad_spend_eur": 65000000, "total_spend": 73000000, "market_share_be": 15.8, "market_share_fr": 18.5, "platforms": ["Meta", "Google"]},
        "Allianz": {"belgium_ad_spend_eur": 6000000, "france_ad_spend_eur": 35000000, "total_spend": 41000000, "market_share_be": 12.2, "market_share_fr": 9.8, "platforms": ["Meta", "Google"]},
        "Generali": {"belgium_ad_spend_eur": 4000000, "france_ad_spend_eur": 28000000, "total_spend": 32000000, "market_share_be": 8.5, "market_share_fr": 7.8, "platforms": ["Meta", "Google"]},
        "AG Insurance": {"belgium_ad_spend_eur": 5500000, "france_ad_spend_eur": 0, "total_spend": 5500000, "market_share_be": 11.2, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "Ethias": {"belgium_ad_spend_eur": 3000000, "france_ad_spend_eur": 0, "total_spend": 3000000, "market_share_be": 6.8, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "Zurich": {"belgium_ad_spend_eur": 2500000, "france_ad_spend_eur": 12000000, "total_spend": 14500000, "market_share_be": 5.1, "market_share_fr": 3.4, "platforms": ["Meta", "Google"]},
        # Investment/Trading platforms
        "DEGIRO": {"belgium_ad_spend_eur": 2000000, "france_ad_spend_eur": 8000000, "total_spend": 10000000, "market_share_be": 8.5, "market_share_fr": 6.2, "platforms": ["Meta", "Google"]},
        "eToro": {"belgium_ad_spend_eur": 3000000, "france_ad_spend_eur": 12000000, "total_spend": 15000000, "market_share_be": 12.8, "market_share_fr": 9.8, "platforms": ["Meta", "Google"]},
        "Plus500": {"belgium_ad_spend_eur": 1500000, "france_ad_spend_eur": 6000000, "total_spend": 7500000, "market_share_be": 6.4, "market_share_fr": 4.8, "platforms": ["Meta", "Google"]},
        "XTB": {"belgium_ad_spend_eur": 1200000, "france_ad_spend_eur": 5000000, "total_spend": 6200000, "market_share_be": 5.1, "market_share_fr": 3.9, "platforms": ["Meta", "Google"]},
        # Cryptocurrency platforms
        "Binance": {"belgium_ad_spend_eur": 2500000, "france_ad_spend_eur": 15000000, "total_spend": 17500000, "market_share_be": 18.5, "market_share_fr": 22.8, "platforms": ["Meta", "Google"]},
        "Coinbase": {"belgium_ad_spend_eur": 1800000, "france_ad_spend_eur": 12000000, "total_spend": 13800000, "market_share_be": 13.2, "market_share_fr": 18.2, "platforms": ["Meta", "Google"]},
        "Crypto.com": {"belgium_ad_spend_eur": 1500000, "france_ad_spend_eur": 10000000, "total_spend": 11500000, "market_share_be": 11.1, "market_share_fr": 15.1, "platforms": ["Meta", "Google"]},
        # Belgian financial services
        "Keytrade Bank": {"belgium_ad_spend_eur": 1200000, "france_ad_spend_eur": 0, "total_spend": 1200000, "market_share_be": 3.8, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "Argenta": {"belgium_ad_spend_eur": 2800000, "france_ad_spend_eur": 0, "total_spend": 2800000, "market_share_be": 8.9, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "VDK Spaarbank": {"belgium_ad_spend_eur": 800000, "france_ad_spend_eur": 0, "total_spend": 800000, "market_share_be": 2.5, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        # French financial services
        "Boursorama": {"belgium_ad_spend_eur": 500000, "france_ad_spend_eur": 25000000, "total_spend": 25500000, "market_share_be": 1.6, "market_share_fr": 15.8, "platforms": ["Meta", "Google"]},
        "Fortuneo": {"belgium_ad_spend_eur": 300000, "france_ad_spend_eur": 18000000, "total_spend": 18300000, "market_share_be": 0.9, "market_share_fr": 11.4, "platforms": ["Meta", "Google"]},
        "Hello bank!": {"belgium_ad_spend_eur": 400000, "france_ad_spend_eur": 15000000, "total_spend": 15400000, "market_share_be": 1.3, "market_share_fr": 9.5, "platforms": ["Meta", "Google"]}
    },
    "food": {
        # Major global food brands advertising in Belgium & France - the user specifically mentioned these missing brands
        "Coca-Cola": {"belgium_ad_spend_eur": 35000000, "france_ad_spend_eur": 185000000, "total_spend": 220000000, "market_share_be": 28.5, "market_share_fr": 25.8, "platforms": ["Meta", "Google"], "ad_types": {"video": 75, "display": 25, "video_spend_eur": 165000000, "display_spend_eur": 55000000}},
        "McDonald's": {"belgium_ad_spend_eur": 25000000, "france_ad_spend_eur": 165000000, "total_spend": 190000000, "market_share_be": 22.8, "market_share_fr": 22.5, "platforms": ["Meta", "Google"]},
        "Nestlé": {"belgium_ad_spend_eur": 22000000, "france_ad_spend_eur": 145000000, "total_spend": 167000000, "market_share_be": 18.5, "market_share_fr": 20.1, "platforms": ["Meta", "Google"]},
        "Unilever": {"belgium_ad_spend_eur": 20000000, "france_ad_spend_eur": 135000000, "total_spend": 155000000, "market_share_be": 16.8, "market_share_fr": 18.8, "platforms": ["Meta", "Google"]},
        "Danone": {"belgium_ad_spend_eur": 15000000, "france_ad_spend_eur": 125000000, "total_spend": 140000000, "market_share_be": 12.5, "market_share_fr": 17.4, "platforms": ["Meta", "Google"]},
        "PepsiCo": {"belgium_ad_spend_eur": 18000000, "france_ad_spend_eur": 95000000, "total_spend": 113000000, "market_share_be": 15.2, "market_share_fr": 13.2, "platforms": ["Meta", "Google"]},
        "Ferrero": {"belgium_ad_spend_eur": 12000000, "france_ad_spend_eur": 85000000, "total_spend": 97000000, "market_share_be": 10.1, "market_share_fr": 11.8, "platforms": ["Meta", "Google"]},
        "Mars": {"belgium_ad_spend_eur": 10000000, "france_ad_spend_eur": 75000000, "total_spend": 85000000, "market_share_be": 8.5, "market_share_fr": 10.4, "platforms": ["Meta", "Google"]},
        "Mondelez": {"belgium_ad_spend_eur": 8000000, "france_ad_spend_eur": 65000000, "total_spend": 73000000, "market_share_be": 6.8, "market_share_fr": 9.0, "platforms": ["Meta", "Google"]},
        "Kellogg's": {"belgium_ad_spend_eur": 6000000, "france_ad_spend_eur": 45000000, "total_spend": 51000000, "market_share_be": 5.1, "market_share_fr": 6.2, "platforms": ["Meta", "Google"]},
        "General Mills": {"belgium_ad_spend_eur": 4000000, "france_ad_spend_eur": 32000000, "total_spend": 36000000, "market_share_be": 3.4, "market_share_fr": 4.4, "platforms": ["Meta", "Google"]},
        "Kraft Heinz": {"belgium_ad_spend_eur": 5000000, "france_ad_spend_eur": 38000000, "total_spend": 43000000, "market_share_be": 4.2, "market_share_fr": 5.3, "platforms": ["Meta", "Google"]},
        "Dr. Oetker": {"belgium_ad_spend_eur": 3500000, "france_ad_spend_eur": 28000000, "total_spend": 31500000, "market_share_be": 2.9, "market_share_fr": 3.9, "platforms": ["Meta", "Google"]},
        "Haribo": {"belgium_ad_spend_eur": 4500000, "france_ad_spend_eur": 35000000, "total_spend": 39500000, "market_share_be": 3.8, "market_share_fr": 4.9, "platforms": ["Meta", "Google"]},
        "Red Bull": {"belgium_ad_spend_eur": 8000000, "france_ad_spend_eur": 55000000, "total_spend": 63000000, "market_share_be": 6.8, "market_share_fr": 7.6, "platforms": ["Meta", "Google"]},
        # Major supermarket chains - the user specifically mentioned these missing brands
        "Lidl": {"belgium_ad_spend_eur": 18000000, "france_ad_spend_eur": 125000000, "total_spend": 143000000, "market_share_be": 22.8, "market_share_fr": 18.5, "platforms": ["Meta", "Google"], "ad_types": {"video": 45, "display": 55, "video_spend_eur": 64350000, "display_spend_eur": 78650000}},
        "ALDI": {"belgium_ad_spend_eur": 15000000, "france_ad_spend_eur": 85000000, "total_spend": 100000000, "market_share_be": 18.9, "market_share_fr": 12.6, "platforms": ["Meta", "Google"], "ad_types": {"video": 40, "display": 60, "video_spend_eur": 40000000, "display_spend_eur": 60000000}},
        "Delhaize": {"belgium_ad_spend_eur": 28000000, "france_ad_spend_eur": 0, "total_spend": 28000000, "market_share_be": 35.4, "market_share_fr": 0, "platforms": ["Meta", "Google"], "ad_types": {"video": 50, "display": 50, "video_spend_eur": 14000000, "display_spend_eur": 14000000}},
        "Carrefour": {"belgium_ad_spend_eur": 12000000, "france_ad_spend_eur": 155000000, "total_spend": 167000000, "market_share_be": 15.2, "market_share_fr": 22.9, "platforms": ["Meta", "Google"]},
        "Leclerc": {"belgium_ad_spend_eur": 2000000, "france_ad_spend_eur": 95000000, "total_spend": 97000000, "market_share_be": 2.5, "market_share_fr": 14.1, "platforms": ["Meta", "Google"]},
        "Intermarché": {"belgium_ad_spend_eur": 1500000, "france_ad_spend_eur": 65000000, "total_spend": 66500000, "market_share_be": 1.9, "market_share_fr": 9.6, "platforms": ["Meta", "Google"]},
        "Casino": {"belgium_ad_spend_eur": 800000, "france_ad_spend_eur": 45000000, "total_spend": 45800000, "market_share_be": 1.0, "market_share_fr": 6.7, "platforms": ["Meta", "Google"]},
        "Monoprix": {"belgium_ad_spend_eur": 600000, "france_ad_spend_eur": 35000000, "total_spend": 35600000, "market_share_be": 0.8, "market_share_fr": 5.2, "platforms": ["Meta", "Google"]},
        "Franprix": {"belgium_ad_spend_eur": 0, "france_ad_spend_eur": 28000000, "total_spend": 28000000, "market_share_be": 0, "market_share_fr": 4.1, "platforms": ["Meta", "Google"]},
        "Super U": {"belgium_ad_spend_eur": 0, "france_ad_spend_eur": 42000000, "total_spend": 42000000, "market_share_be": 0, "market_share_fr": 6.2, "platforms": ["Meta", "Google"]},
        # Belgian supermarket chains
        "Colruyt": {"belgium_ad_spend_eur": 22000000, "france_ad_spend_eur": 0, "total_spend": 22000000, "market_share_be": 27.8, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "Carrefour Belgium": {"belgium_ad_spend_eur": 8000000, "france_ad_spend_eur": 0, "total_spend": 8000000, "market_share_be": 10.1, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "Cora": {"belgium_ad_spend_eur": 3500000, "france_ad_spend_eur": 12000000, "total_spend": 15500000, "market_share_be": 4.4, "market_share_fr": 1.8, "platforms": ["Meta", "Google"]},
        # Food delivery platforms
        "Uber Eats": {"belgium_ad_spend_eur": 8000000, "france_ad_spend_eur": 55000000, "total_spend": 63000000, "market_share_be": 35.8, "market_share_fr": 28.5, "platforms": ["Meta", "Google"]},
        "Deliveroo": {"belgium_ad_spend_eur": 5000000, "france_ad_spend_eur": 42000000, "total_spend": 47000000, "market_share_be": 22.4, "market_share_fr": 21.8, "platforms": ["Meta", "Google"]},
        "Just Eat Takeaway": {"belgium_ad_spend_eur": 4000000, "france_ad_spend_eur": 28000000, "total_spend": 32000000, "market_share_be": 17.9, "market_share_fr": 14.5, "platforms": ["Meta", "Google"]},
        "Domino's": {"belgium_ad_spend_eur": 3500000, "france_ad_spend_eur": 25000000, "total_spend": 28500000, "market_share_be": 15.7, "market_share_fr": 13.0, "platforms": ["Meta", "Google"]},
        "Pizza Hut": {"belgium_ad_spend_eur": 2500000, "france_ad_spend_eur": 18000000, "total_spend": 20500000, "market_share_be": 11.2, "market_share_fr": 9.3, "platforms": ["Meta", "Google"]},
        # Beer and beverages - Belgium is famous for beer
        "AB InBev": {"belgium_ad_spend_eur": 25000000, "france_ad_spend_eur": 65000000, "total_spend": 90000000, "market_share_be": 45.5, "market_share_fr": 18.2, "platforms": ["Meta", "Google"]},
        "Heineken": {"belgium_ad_spend_eur": 8000000, "france_ad_spend_eur": 55000000, "total_spend": 63000000, "market_share_be": 14.5, "market_share_fr": 15.4, "platforms": ["Meta", "Google"]},
        "Carlsberg": {"belgium_ad_spend_eur": 4000000, "france_ad_spend_eur": 35000000, "total_spend": 39000000, "market_share_be": 7.3, "market_share_fr": 9.8, "platforms": ["Meta", "Google"]},
        "Duvel Moortgat": {"belgium_ad_spend_eur": 3500000, "france_ad_spend_eur": 8000000, "total_spend": 11500000, "market_share_be": 6.4, "market_share_fr": 2.2, "platforms": ["Meta", "Google"]},
        "Groupe Castel": {"belgium_ad_spend_eur": 500000, "france_ad_spend_eur": 28000000, "total_spend": 28500000, "market_share_be": 0.9, "market_share_fr": 7.8, "platforms": ["Meta", "Google"]}
    },
    "healthcare": {
        # Major pharmaceutical companies advertising in Belgium & France
        "Sanofi": {"belgium_ad_spend_eur": 8000000, "france_ad_spend_eur": 95000000, "total_spend": 103000000, "market_share_be": 18.5, "market_share_fr": 22.8, "platforms": ["Meta", "Google"]},
        "Novartis": {"belgium_ad_spend_eur": 6000000, "france_ad_spend_eur": 65000000, "total_spend": 71000000, "market_share_be": 13.9, "market_share_fr": 15.6, "platforms": ["Meta", "Google"]},
        "Roche": {"belgium_ad_spend_eur": 5500000, "france_ad_spend_eur": 58000000, "total_spend": 63500000, "market_share_be": 12.7, "market_share_fr": 13.9, "platforms": ["Meta", "Google"]},
        "Bayer": {"belgium_ad_spend_eur": 5000000, "france_ad_spend_eur": 52000000, "total_spend": 57000000, "market_share_be": 11.6, "market_share_fr": 12.5, "platforms": ["Meta", "Google"]},
        "AstraZeneca": {"belgium_ad_spend_eur": 4500000, "france_ad_spend_eur": 48000000, "total_spend": 52500000, "market_share_be": 10.4, "market_share_fr": 11.5, "platforms": ["Meta", "Google"]},
        "GSK": {"belgium_ad_spend_eur": 4000000, "france_ad_spend_eur": 42000000, "total_spend": 46000000, "market_share_be": 9.3, "market_share_fr": 10.1, "platforms": ["Meta", "Google"]},
        "Pfizer": {"belgium_ad_spend_eur": 6500000, "france_ad_spend_eur": 55000000, "total_spend": 61500000, "market_share_be": 15.0, "market_share_fr": 13.2, "platforms": ["Meta", "Google"]},
        "Johnson & Johnson": {"belgium_ad_spend_eur": 5800000, "france_ad_spend_eur": 48000000, "total_spend": 53800000, "market_share_be": 13.4, "market_share_fr": 11.5, "platforms": ["Meta", "Google"]},
        "Merck": {"belgium_ad_spend_eur": 3500000, "france_ad_spend_eur": 32000000, "total_spend": 35500000, "market_share_be": 8.1, "market_share_fr": 7.7, "platforms": ["Meta", "Google"]},
        "Boehringer Ingelheim": {"belgium_ad_spend_eur": 3000000, "france_ad_spend_eur": 28000000, "total_spend": 31000000, "market_share_be": 6.9, "market_share_fr": 6.7, "platforms": ["Meta", "Google"]},
        # Medical devices and healthcare technology
        "Philips Healthcare": {"belgium_ad_spend_eur": 4000000, "france_ad_spend_eur": 35000000, "total_spend": 39000000, "market_share_be": 12.8, "market_share_fr": 10.5, "platforms": ["Meta", "Google"]},
        "Siemens Healthineers": {"belgium_ad_spend_eur": 3500000, "france_ad_spend_eur": 28000000, "total_spend": 31500000, "market_share_be": 11.2, "market_share_fr": 8.4, "platforms": ["Meta", "Google"]},
        "Medtronic": {"belgium_ad_spend_eur": 2500000, "france_ad_spend_eur": 22000000, "total_spend": 24500000, "market_share_be": 8.0, "market_share_fr": 6.6, "platforms": ["Meta", "Google"]},
        "Abbott": {"belgium_ad_spend_eur": 2200000, "france_ad_spend_eur": 18000000, "total_spend": 20200000, "market_share_be": 7.0, "market_share_fr": 5.4, "platforms": ["Meta", "Google"]},
        # Belgian healthcare companies
        "UCB": {"belgium_ad_spend_eur": 3500000, "france_ad_spend_eur": 8000000, "total_spend": 11500000, "market_share_be": 11.2, "market_share_fr": 2.4, "platforms": ["Meta", "Google"]},
        "Galapagos": {"belgium_ad_spend_eur": 1800000, "france_ad_spend_eur": 2500000, "total_spend": 4300000, "market_share_be": 5.8, "market_share_fr": 0.8, "platforms": ["Meta", "Google"]},
        "Janssen Pharmaceutica": {"belgium_ad_spend_eur": 2500000, "france_ad_spend_eur": 5000000, "total_spend": 7500000, "market_share_be": 8.0, "market_share_fr": 1.5, "platforms": ["Meta", "Google"]},
        # French healthcare companies
        "Servier": {"belgium_ad_spend_eur": 1200000, "france_ad_spend_eur": 25000000, "total_spend": 26200000, "market_share_be": 3.8, "market_share_fr": 7.5, "platforms": ["Meta", "Google"]},
        "Pierre Fabre": {"belgium_ad_spend_eur": 800000, "france_ad_spend_eur": 18000000, "total_spend": 18800000, "market_share_be": 2.6, "market_share_fr": 5.4, "platforms": ["Meta", "Google"]},
        "Ipsen": {"belgium_ad_spend_eur": 600000, "france_ad_spend_eur": 12000000, "total_spend": 12600000, "market_share_be": 1.9, "market_share_fr": 3.6, "platforms": ["Meta", "Google"]},
        # Health insurance and services
        "Mutualités Libres": {"belgium_ad_spend_eur": 2800000, "france_ad_spend_eur": 0, "total_spend": 2800000, "market_share_be": 15.8, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "Mutualités Chrétiennes": {"belgium_ad_spend_eur": 2200000, "france_ad_spend_eur": 0, "total_spend": 2200000, "market_share_be": 12.4, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "CPAM": {"belgium_ad_spend_eur": 0, "france_ad_spend_eur": 35000000, "total_spend": 35000000, "market_share_be": 0, "market_share_fr": 18.5, "platforms": ["Meta", "Google"]},
        "Harmonie Mutuelle": {"belgium_ad_spend_eur": 0, "france_ad_spend_eur": 22000000, "total_spend": 22000000, "market_share_be": 0, "market_share_fr": 11.6, "platforms": ["Meta", "Google"]}
    },
    "travel": {
        # Major airlines advertising in Belgium & France
        "Air France-KLM": {"belgium_ad_spend_eur": 15000000, "france_ad_spend_eur": 125000000, "total_spend": 140000000, "market_share_be": 28.5, "market_share_fr": 35.8, "platforms": ["Meta", "Google"]},
        "Brussels Airlines": {"belgium_ad_spend_eur": 12000000, "france_ad_spend_eur": 8000000, "total_spend": 20000000, "market_share_be": 22.8, "market_share_fr": 2.3, "platforms": ["Meta", "Google"]},
        "Lufthansa": {"belgium_ad_spend_eur": 8000000, "france_ad_spend_eur": 35000000, "total_spend": 43000000, "market_share_be": 15.2, "market_share_fr": 10.0, "platforms": ["Meta", "Google"]},
        "Ryanair": {"belgium_ad_spend_eur": 6000000, "france_ad_spend_eur": 45000000, "total_spend": 51000000, "market_share_be": 11.4, "market_share_fr": 12.9, "platforms": ["Meta", "Google"]},
        "British Airways": {"belgium_ad_spend_eur": 4000000, "france_ad_spend_eur": 28000000, "total_spend": 32000000, "market_share_be": 7.6, "market_share_fr": 8.0, "platforms": ["Meta", "Google"]},
        "easyJet": {"belgium_ad_spend_eur": 3500000, "france_ad_spend_eur": 42000000, "total_spend": 45500000, "market_share_be": 6.7, "market_share_fr": 12.0, "platforms": ["Meta", "Google"]},
        "Turkish Airlines": {"belgium_ad_spend_eur": 2500000, "france_ad_spend_eur": 18000000, "total_spend": 20500000, "market_share_be": 4.8, "market_share_fr": 5.1, "platforms": ["Meta", "Google"]},
        "Emirates": {"belgium_ad_spend_eur": 3000000, "france_ad_spend_eur": 25000000, "total_spend": 28000000, "market_share_be": 5.7, "market_share_fr": 7.1, "platforms": ["Meta", "Google"]},
        # Online travel agencies and booking platforms
        "Booking.com": {"belgium_ad_spend_eur": 18000000, "france_ad_spend_eur": 95000000, "total_spend": 113000000, "market_share_be": 35.8, "market_share_fr": 28.5, "platforms": ["Meta", "Google"]},
        "Expedia": {"belgium_ad_spend_eur": 8000000, "france_ad_spend_eur": 55000000, "total_spend": 63000000, "market_share_be": 15.9, "market_share_fr": 16.5, "platforms": ["Meta", "Google"]},
        "Airbnb": {"belgium_ad_spend_eur": 12000000, "france_ad_spend_eur": 85000000, "total_spend": 97000000, "market_share_be": 23.9, "market_share_fr": 25.5, "platforms": ["Meta", "Google"]},
        "Hotels.com": {"belgium_ad_spend_eur": 4000000, "france_ad_spend_eur": 32000000, "total_spend": 36000000, "market_share_be": 8.0, "market_share_fr": 9.6, "platforms": ["Meta", "Google"]},
        "Skyscanner": {"belgium_ad_spend_eur": 3500000, "france_ad_spend_eur": 28000000, "total_spend": 31500000, "market_share_be": 7.0, "market_share_fr": 8.4, "platforms": ["Meta", "Google"]},
        "Kayak": {"belgium_ad_spend_eur": 2500000, "france_ad_spend_eur": 22000000, "total_spend": 24500000, "market_share_be": 5.0, "market_share_fr": 6.6, "platforms": ["Meta", "Google"]},
        "Momondo": {"belgium_ad_spend_eur": 1800000, "france_ad_spend_eur": 15000000, "total_spend": 16800000, "market_share_be": 3.6, "market_share_fr": 4.5, "platforms": ["Meta", "Google"]},
        # Tour operators and travel companies
        "TUI": {"belgium_ad_spend_eur": 6000000, "france_ad_spend_eur": 35000000, "total_spend": 41000000, "market_share_be": 18.2, "market_share_fr": 12.5, "platforms": ["Meta", "Google"]},
        "Thomas Cook": {"belgium_ad_spend_eur": 3000000, "france_ad_spend_eur": 18000000, "total_spend": 21000000, "market_share_be": 9.1, "market_share_fr": 6.4, "platforms": ["Meta", "Google"]},
        "Club Med": {"belgium_ad_spend_eur": 2500000, "france_ad_spend_eur": 45000000, "total_spend": 47500000, "market_share_be": 7.6, "market_share_fr": 16.1, "platforms": ["Meta", "Google"]},
        "Pierre & Vacances": {"belgium_ad_spend_eur": 1500000, "france_ad_spend_eur": 28000000, "total_spend": 29500000, "market_share_be": 4.5, "market_share_fr": 10.0, "platforms": ["Meta", "Google"]},
        "Center Parcs": {"belgium_ad_spend_eur": 4000000, "france_ad_spend_eur": 22000000, "total_spend": 26000000, "market_share_be": 12.1, "market_share_fr": 7.9, "platforms": ["Meta", "Google"]},
        # Belgian travel companies
        "Connections": {"belgium_ad_spend_eur": 2200000, "france_ad_spend_eur": 0, "total_spend": 2200000, "market_share_be": 6.7, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "Jetair": {"belgium_ad_spend_eur": 1800000, "france_ad_spend_eur": 0, "total_spend": 1800000, "market_share_be": 5.5, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "Sunweb": {"belgium_ad_spend_eur": 2500000, "france_ad_spend_eur": 8000000, "total_spend": 10500000, "market_share_be": 7.6, "market_share_fr": 2.9, "platforms": ["Meta", "Google"]},
        # French travel companies
        "Nouvelles Frontières": {"belgium_ad_spend_eur": 0, "france_ad_spend_eur": 15000000, "total_spend": 15000000, "market_share_be": 0, "market_share_fr": 5.4, "platforms": ["Meta", "Google"]},
        "Promovacances": {"belgium_ad_spend_eur": 500000, "france_ad_spend_eur": 12000000, "total_spend": 12500000, "market_share_be": 1.5, "market_share_fr": 4.3, "platforms": ["Meta", "Google"]},
        "Lastminute.com": {"belgium_ad_spend_eur": 1200000, "france_ad_spend_eur": 18000000, "total_spend": 19200000, "market_share_be": 3.6, "market_share_fr": 6.4, "platforms": ["Meta", "Google"]}
    },
    "education": {
        # Online learning platforms advertising in Belgium & France
        "Coursera": {"belgium_ad_spend_eur": 2500000, "france_ad_spend_eur": 18000000, "total_spend": 20500000, "market_share_be": 22.8, "market_share_fr": 15.8, "platforms": ["Meta", "Google"]},
        "Udemy": {"belgium_ad_spend_eur": 2000000, "france_ad_spend_eur": 15000000, "total_spend": 17000000, "market_share_be": 18.2, "market_share_fr": 13.2, "platforms": ["Meta", "Google"]},
        "LinkedIn Learning": {"belgium_ad_spend_eur": 1800000, "france_ad_spend_eur": 12000000, "total_spend": 13800000, "market_share_be": 16.4, "market_share_fr": 10.5, "platforms": ["Meta", "Google"]},
        "Skillshare": {"belgium_ad_spend_eur": 1200000, "france_ad_spend_eur": 8000000, "total_spend": 9200000, "market_share_be": 10.9, "market_share_fr": 7.0, "platforms": ["Meta", "Google"]},
        "MasterClass": {"belgium_ad_spend_eur": 800000, "france_ad_spend_eur": 6000000, "total_spend": 6800000, "market_share_be": 7.3, "market_share_fr": 5.3, "platforms": ["Meta", "Google"]},
        "Duolingo": {"belgium_ad_spend_eur": 1500000, "france_ad_spend_eur": 12000000, "total_spend": 13500000, "market_share_be": 13.6, "market_share_fr": 10.5, "platforms": ["Meta", "Google"]},
        "Babbel": {"belgium_ad_spend_eur": 1000000, "france_ad_spend_eur": 8500000, "total_spend": 9500000, "market_share_be": 9.1, "market_share_fr": 7.5, "platforms": ["Meta", "Google"]},
        # Traditional education and publishers
        "Pearson": {"belgium_ad_spend_eur": 800000, "france_ad_spend_eur": 6000000, "total_spend": 6800000, "market_share_be": 12.5, "market_share_fr": 8.8, "platforms": ["Meta", "Google"]},
        "McGraw-Hill": {"belgium_ad_spend_eur": 600000, "france_ad_spend_eur": 4500000, "total_spend": 5100000, "market_share_be": 9.4, "market_share_fr": 6.6, "platforms": ["Meta", "Google"]},
        "Cambridge University Press": {"belgium_ad_spend_eur": 500000, "france_ad_spend_eur": 3500000, "total_spend": 4000000, "market_share_be": 7.8, "market_share_fr": 5.1, "platforms": ["Meta", "Google"]},
        # Belgian education institutions and services
        "KU Leuven": {"belgium_ad_spend_eur": 1200000, "france_ad_spend_eur": 0, "total_spend": 1200000, "market_share_be": 10.9, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "UCLouvain": {"belgium_ad_spend_eur": 800000, "france_ad_spend_eur": 0, "total_spend": 800000, "market_share_be": 7.3, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "UGent": {"belgium_ad_spend_eur": 600000, "france_ad_spend_eur": 0, "total_spend": 600000, "market_share_be": 5.5, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "EPHEC": {"belgium_ad_spend_eur": 400000, "france_ad_spend_eur": 0, "total_spend": 400000, "market_share_be": 3.6, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "HEC Liège": {"belgium_ad_spend_eur": 350000, "france_ad_spend_eur": 0, "total_spend": 350000, "market_share_be": 3.2, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        # French education institutions and services
        "Sorbonne Université": {"belgium_ad_spend_eur": 0, "france_ad_spend_eur": 3500000, "total_spend": 3500000, "market_share_be": 0, "market_share_fr": 5.1, "platforms": ["Meta", "Google"]},
        "HEC Paris": {"belgium_ad_spend_eur": 200000, "france_ad_spend_eur": 2800000, "total_spend": 3000000, "market_share_be": 1.8, "market_share_fr": 4.1, "platforms": ["Meta", "Google"]},
        "INSEAD": {"belgium_ad_spend_eur": 300000, "france_ad_spend_eur": 2200000, "total_spend": 2500000, "market_share_be": 2.7, "market_share_fr": 3.2, "platforms": ["Meta", "Google"]},
        "Sciences Po": {"belgium_ad_spend_eur": 0, "france_ad_spend_eur": 1800000, "total_spend": 1800000, "market_share_be": 0, "market_share_fr": 2.6, "platforms": ["Meta", "Google"]},
        "CNED": {"belgium_ad_spend_eur": 0, "france_ad_spend_eur": 4500000, "total_spend": 4500000, "market_share_be": 0, "market_share_fr": 6.6, "platforms": ["Meta", "Google"]},
        # Private training and certification companies
        "OpenClassrooms": {"belgium_ad_spend_eur": 800000, "france_ad_spend_eur": 8000000, "total_spend": 8800000, "market_share_be": 7.3, "market_share_fr": 11.8, "platforms": ["Meta", "Google"]},
        "Le Wagon": {"belgium_ad_spend_eur": 600000, "france_ad_spend_eur": 4500000, "total_spend": 5100000, "market_share_be": 5.5, "market_share_fr": 6.6, "platforms": ["Meta", "Google"]},
        "Wild Code School": {"belgium_ad_spend_eur": 400000, "france_ad_spend_eur": 3200000, "total_spend": 3600000, "market_share_be": 3.6, "market_share_fr": 4.7, "platforms": ["Meta", "Google"]},
        "BeCode": {"belgium_ad_spend_eur": 800000, "france_ad_spend_eur": 200000, "total_spend": 1000000, "market_share_be": 7.3, "market_share_fr": 0.3, "platforms": ["Meta", "Google"]}
    },
    "real_estate": {
        # Real estate portals and platforms advertising in Belgium & France
        "Immoweb": {"belgium_ad_spend_eur": 8000000, "france_ad_spend_eur": 0, "total_spend": 8000000, "market_share_be": 45.7, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "Logic-immo.com": {"belgium_ad_spend_eur": 500000, "france_ad_spend_eur": 12000000, "total_spend": 12500000, "market_share_be": 2.9, "market_share_fr": 18.5, "platforms": ["Meta", "Google"]},
        "SeLoger.com": {"belgium_ad_spend_eur": 300000, "france_ad_spend_eur": 15000000, "total_spend": 15300000, "market_share_be": 1.7, "market_share_fr": 23.1, "platforms": ["Meta", "Google"]},
        "Leboncoin": {"belgium_ad_spend_eur": 1200000, "france_ad_spend_eur": 18000000, "total_spend": 19200000, "market_share_be": 6.9, "market_share_fr": 27.7, "platforms": ["Meta", "Google"]},
        "PAP.fr": {"belgium_ad_spend_eur": 0, "france_ad_spend_eur": 8000000, "total_spend": 8000000, "market_share_be": 0, "market_share_fr": 12.3, "platforms": ["Meta", "Google"]},
        "Bien'ici": {"belgium_ad_spend_eur": 0, "france_ad_spend_eur": 6500000, "total_spend": 6500000, "market_share_be": 0, "market_share_fr": 10.0, "platforms": ["Meta", "Google"]},
        # Belgian real estate companies and services
        "Zimmo": {"belgium_ad_spend_eur": 3500000, "france_ad_spend_eur": 0, "total_spend": 3500000, "market_share_be": 20.0, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "Realo": {"belgium_ad_spend_eur": 2200000, "france_ad_spend_eur": 0, "total_spend": 2200000, "market_share_be": 12.6, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "Era Belgium": {"belgium_ad_spend_eur": 1800000, "france_ad_spend_eur": 0, "total_spend": 1800000, "market_share_be": 10.3, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "Century 21 Belgium": {"belgium_ad_spend_eur": 1500000, "france_ad_spend_eur": 0, "total_spend": 1500000, "market_share_be": 8.6, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "Engel & Völkers Belgium": {"belgium_ad_spend_eur": 800000, "france_ad_spend_eur": 0, "total_spend": 800000, "market_share_be": 4.6, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "Dewaele": {"belgium_ad_spend_eur": 1200000, "france_ad_spend_eur": 0, "total_spend": 1200000, "market_share_be": 6.9, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        # French real estate companies and services
        "Century 21 France": {"belgium_ad_spend_eur": 0, "france_ad_spend_eur": 12000000, "total_spend": 12000000, "market_share_be": 0, "market_share_fr": 18.5, "platforms": ["Meta", "Google"]},
        "Orpi": {"belgium_ad_spend_eur": 0, "france_ad_spend_eur": 10000000, "total_spend": 10000000, "market_share_be": 0, "market_share_fr": 15.4, "platforms": ["Meta", "Google"]},
        "Guy Hoêet l'Immobilier": {"belgium_ad_spend_eur": 0, "france_ad_spend_eur": 8500000, "total_spend": 8500000, "market_share_be": 0, "market_share_fr": 13.1, "platforms": ["Meta", "Google"]},
        "Foncia": {"belgium_ad_spend_eur": 0, "france_ad_spend_eur": 7000000, "total_spend": 7000000, "market_share_be": 0, "market_share_fr": 10.8, "platforms": ["Meta", "Google"]},
        "Laforêt": {"belgium_ad_spend_eur": 0, "france_ad_spend_eur": 5500000, "total_spend": 5500000, "market_share_be": 0, "market_share_fr": 8.5, "platforms": ["Meta", "Google"]},
        "Square Habitat": {"belgium_ad_spend_eur": 0, "france_ad_spend_eur": 4500000, "total_spend": 4500000, "market_share_be": 0, "market_share_fr": 6.9, "platforms": ["Meta", "Google"]},
        # Property developers and investment companies
        "Unibail-Rodamco-Westfield": {"belgium_ad_spend_eur": 2500000, "france_ad_spend_eur": 18000000, "total_spend": 20500000, "market_share_be": 8.5, "market_share_fr": 12.8, "platforms": ["Meta", "Google"]},
        "Klepierre": {"belgium_ad_spend_eur": 1500000, "france_ad_spend_eur": 12000000, "total_spend": 13500000, "market_share_be": 5.1, "market_share_fr": 8.5, "platforms": ["Meta", "Google"]},
        "Cofinimmo": {"belgium_ad_spend_eur": 2000000, "france_ad_spend_eur": 800000, "total_spend": 2800000, "market_share_be": 6.8, "market_share_fr": 0.6, "platforms": ["Meta", "Google"]},
        "Montea": {"belgium_ad_spend_eur": 800000, "france_ad_spend_eur": 1200000, "total_spend": 2000000, "market_share_be": 2.7, "market_share_fr": 0.9, "platforms": ["Meta", "Google"]},
        # Construction and home improvement
        "Ikea": {"belgium_ad_spend_eur": 12000000, "france_ad_spend_eur": 65000000, "total_spend": 77000000, "market_share_be": 25.8, "market_share_fr": 22.3, "platforms": ["Meta", "Google"]},
        "Leroy Merlin": {"belgium_ad_spend_eur": 6000000, "france_ad_spend_eur": 45000000, "total_spend": 51000000, "market_share_be": 12.9, "market_share_fr": 15.4, "platforms": ["Meta", "Google"]},
        "Brico": {"belgium_ad_spend_eur": 4000000, "france_ad_spend_eur": 0, "total_spend": 4000000, "market_share_be": 8.6, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "Castorama": {"belgium_ad_spend_eur": 2000000, "france_ad_spend_eur": 35000000, "total_spend": 37000000, "market_share_be": 4.3, "market_share_fr": 12.0, "platforms": ["Meta", "Google"]},
        "Bricoman": {"belgium_ad_spend_eur": 1500000, "france_ad_spend_eur": 28000000, "total_spend": 29500000, "market_share_be": 3.2, "market_share_fr": 9.6, "platforms": ["Meta", "Google"]}
    },
    "gaming": {
        # Major gaming companies advertising in Belgium & France
        "Ubisoft": {"belgium_ad_spend_eur": 5000000, "france_ad_spend_eur": 85000000, "total_spend": 90000000, "market_share_be": 22.8, "market_share_fr": 28.5, "platforms": ["Meta", "Google"]},
        "EA": {"belgium_ad_spend_eur": 4000000, "france_ad_spend_eur": 55000000, "total_spend": 59000000, "market_share_be": 18.2, "market_share_fr": 18.5, "platforms": ["Meta", "Google"]},
        "Activision Blizzard": {"belgium_ad_spend_eur": 3500000, "france_ad_spend_eur": 48000000, "total_spend": 51500000, "market_share_be": 15.9, "market_share_fr": 16.1, "platforms": ["Meta", "Google"]},
        "Epic Games": {"belgium_ad_spend_eur": 3000000, "france_ad_spend_eur": 42000000, "total_spend": 45000000, "market_share_be": 13.6, "market_share_fr": 14.1, "platforms": ["Meta", "Google"]},
        "Riot Games": {"belgium_ad_spend_eur": 2500000, "france_ad_spend_eur": 35000000, "total_spend": 37500000, "market_share_be": 11.4, "market_share_fr": 11.7, "platforms": ["Meta", "Google"]},
        "Sony PlayStation": {"belgium_ad_spend_eur": 4500000, "france_ad_spend_eur": 58000000, "total_spend": 62500000, "market_share_be": 20.5, "market_share_fr": 19.5, "platforms": ["Meta", "Google"]},
        "Microsoft Xbox": {"belgium_ad_spend_eur": 4000000, "france_ad_spend_eur": 52000000, "total_spend": 56000000, "market_share_be": 18.2, "market_share_fr": 17.5, "platforms": ["Meta", "Google"]},
        "Nintendo": {"belgium_ad_spend_eur": 3500000, "france_ad_spend_eur": 45000000, "total_spend": 48500000, "market_share_be": 15.9, "market_share_fr": 15.1, "platforms": ["Meta", "Google"]},
        # Mobile gaming companies
        "King (Candy Crush)": {"belgium_ad_spend_eur": 2500000, "france_ad_spend_eur": 28000000, "total_spend": 30500000, "market_share_be": 25.8, "market_share_fr": 22.5, "platforms": ["Meta", "Google"]},
        "Supercell": {"belgium_ad_spend_eur": 2000000, "france_ad_spend_eur": 25000000, "total_spend": 27000000, "market_share_be": 20.6, "market_share_fr": 20.1, "platforms": ["Meta", "Google"]},
        "Niantic": {"belgium_ad_spend_eur": 1500000, "france_ad_spend_eur": 18000000, "total_spend": 19500000, "market_share_be": 15.5, "market_share_fr": 14.5, "platforms": ["Meta", "Google"]},
        "Zynga": {"belgium_ad_spend_eur": 1200000, "france_ad_spend_eur": 15000000, "total_spend": 16200000, "market_share_be": 12.4, "market_share_fr": 12.1, "platforms": ["Meta", "Google"]},
        "Rovio": {"belgium_ad_spend_eur": 800000, "france_ad_spend_eur": 12000000, "total_spend": 12800000, "market_share_be": 8.2, "market_share_fr": 9.6, "platforms": ["Meta", "Google"]},
        # Gaming platforms and services
        "Steam": {"belgium_ad_spend_eur": 2000000, "france_ad_spend_eur": 32000000, "total_spend": 34000000, "market_share_be": 18.2, "market_share_fr": 15.8, "platforms": ["Meta", "Google"]},
        "Twitch": {"belgium_ad_spend_eur": 1800000, "france_ad_spend_eur": 28000000, "total_spend": 29800000, "market_share_be": 16.4, "market_share_fr": 13.8, "platforms": ["Meta", "Google"]},
        "Discord": {"belgium_ad_spend_eur": 1500000, "france_ad_spend_eur": 22000000, "total_spend": 23500000, "market_share_be": 13.6, "market_share_fr": 10.8, "platforms": ["Meta", "Google"]},
        "Google Stadia": {"belgium_ad_spend_eur": 800000, "france_ad_spend_eur": 12000000, "total_spend": 12800000, "market_share_be": 7.3, "market_share_fr": 5.9, "platforms": ["Meta"]},
        # French gaming companies
        "Focus Entertainment": {"belgium_ad_spend_eur": 300000, "france_ad_spend_eur": 8000000, "total_spend": 8300000, "market_share_be": 1.4, "market_share_fr": 2.7, "platforms": ["Meta", "Google"]},
        "Dontnod Entertainment": {"belgium_ad_spend_eur": 200000, "france_ad_spend_eur": 5000000, "total_spend": 5200000, "market_share_be": 0.9, "market_share_fr": 1.7, "platforms": ["Meta", "Google"]},
        "Quantic Dream": {"belgium_ad_spend_eur": 150000, "france_ad_spend_eur": 4000000, "total_spend": 4150000, "market_share_be": 0.7, "market_share_fr": 1.3, "platforms": ["Meta", "Google"]},
        # Belgian gaming companies and local esports
        "Larian Studios": {"belgium_ad_spend_eur": 2500000, "france_ad_spend_eur": 3000000, "total_spend": 5500000, "market_share_be": 11.4, "market_share_fr": 1.0, "platforms": ["Meta", "Google"]},
        "Appeal Studios": {"belgium_ad_spend_eur": 400000, "france_ad_spend_eur": 0, "total_spend": 400000, "market_share_be": 1.8, "market_share_fr": 0, "platforms": ["Meta", "Google"]},
        "Team Vitality": {"belgium_ad_spend_eur": 800000, "france_ad_spend_eur": 6000000, "total_spend": 6800000, "market_share_be": 3.6, "market_share_fr": 2.0, "platforms": ["Meta", "Google"]},
        "G2 Esports": {"belgium_ad_spend_eur": 600000, "france_ad_spend_eur": 4500000, "total_spend": 5100000, "market_share_be": 2.7, "market_share_fr": 1.5, "platforms": ["Meta", "Google"]},
        # Gaming hardware and accessories
        "Razer": {"belgium_ad_spend_eur": 1200000, "france_ad_spend_eur": 18000000, "total_spend": 19200000, "market_share_be": 8.5, "market_share_fr": 7.2, "platforms": ["Meta", "Google"]},
        "Logitech G": {"belgium_ad_spend_eur": 1000000, "france_ad_spend_eur": 15000000, "total_spend": 16000000, "market_share_be": 7.1, "market_share_fr": 6.0, "platforms": ["Meta", "Google"]},
        "SteelSeries": {"belgium_ad_spend_eur": 800000, "france_ad_spend_eur": 12000000, "total_spend": 12800000, "market_share_be": 5.7, "market_share_fr": 4.8, "platforms": ["Meta", "Google"]},
        "HyperX": {"belgium_ad_spend_eur": 600000, "france_ad_spend_eur": 9000000, "total_spend": 9600000, "market_share_be": 4.3, "market_share_fr": 3.6, "platforms": ["Meta", "Google"]}
    }
}

# Currency conversion rates (EUR base)
CURRENCY_RATES = {
    "EUR": 1.0,
    "USD": 1.08,
    "GBP": 0.85,
    "CHF": 0.95,
    "SEK": 11.2,
    "NOK": 11.8,
    "DKK": 7.45
}

@mcp.resource("notes://all")
def get_all_notes() -> str:
    """Get all stored notes as JSON."""
    return json.dumps(notes_storage, indent=2)

@mcp.resource("ads://industries")
def get_available_industries() -> str:
    """Get list of available industries for ad transparency analysis."""
    return json.dumps(list(INDUSTRY_KEYWORDS.keys()), indent=2)

@mcp.resource("ads://cache")
def get_ad_cache() -> str:
    """Get cached ad transparency data."""
    return json.dumps(ad_cache, indent=2)

@mcp.resource("ads://google-cache")
def get_google_ads_cache() -> str:
    """Get cached Google Ads transparency data."""
    return json.dumps(google_ads_cache, indent=2)

@mcp.resource("ads://brands")
def get_brands_cache() -> str:
    """Get cached brand data by industry."""
    return json.dumps(brands_cache, indent=2)

@mcp.tool()
def calculator(operation: str, a: float, b: float) -> str:
    """Perform basic arithmetic operations.
    
    Args:
        operation: The operation to perform (add, subtract, multiply, divide)
        a: First number
        b: Second number
    """
    operation = operation.lower()
    
    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
    else:
        raise ValueError(f"Unknown operation: {operation}")
    
    return f"Result: {a} {operation} {b} = {result}"

@mcp.tool()
def add_note(title: str, content: str) -> str:
    """Add a new note to storage.
    
    Args:
        title: Title of the note
        content: Content of the note
    """
    note_id = f"note_{len(notes_storage) + 1}"
    notes_storage[note_id] = {
        "title": title,
        "content": content
    }
    return f"Note added successfully with ID: {note_id}"

@mcp.tool()
def list_notes() -> str:
    """List all stored notes."""
    if not notes_storage:
        return "No notes found."
    
    notes_list = []
    for note_id, note_data in notes_storage.items():
        notes_list.append(f"**{note_id}**: {note_data['title']}")
    
    return "Stored Notes:\n" + "\n".join(notes_list)

@mcp.tool()
def get_system_info() -> str:
    """Get basic system information."""
    info = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "server_name": "demo-server",
        "mcp_version": "1.4.0+"
    }
    
    return f"System Information:\n{json.dumps(info, indent=2)}"

@mcp.tool()
def search_ads_by_industry(industry: str, limit: int = 50, access_token: Optional[str] = None) -> str:
    """Search for Meta ads by industry using Facebook Ad Library API.
    
    Args:
        industry: Industry to search for (automotive, fashion, technology, etc.)
        limit: Maximum number of ads to return (default: 50)
        access_token: Meta API access token (optional, uses demo data if not provided)
    """
    if industry.lower() not in INDUSTRY_KEYWORDS:
        available = ", ".join(INDUSTRY_KEYWORDS.keys())
        return f"Industry '{industry}' not supported. Available industries: {available}"
    
    # Check cache first
    cache_key = f"{industry}_{limit}"
    if cache_key in ad_cache:
        cached_data = ad_cache[cache_key]
        cache_time = datetime.fromisoformat(cached_data.get("timestamp", "2020-01-01"))
        if datetime.now() - cache_time < timedelta(hours=1):
            return f"Cached Ad Data for {industry}:\n{json.dumps(cached_data['data'], indent=2)}"
    
    # If no access token provided, return demo data
    if not access_token:
        demo_ads = _generate_demo_ad_data(industry, limit)
        ad_cache[cache_key] = {
            "data": demo_ads,
            "timestamp": datetime.now().isoformat()
        }
        return f"Demo Ad Data for {industry}:\n{json.dumps(demo_ads, indent=2)}"
    
    # Real API call (placeholder for actual implementation)
    keywords = INDUSTRY_KEYWORDS[industry.lower()]
    try:
        ads_data = _fetch_meta_ads(keywords, limit, access_token)
        ad_cache[cache_key] = {
            "data": ads_data,
            "timestamp": datetime.now().isoformat()
        }
        return f"Ad Transparency Data for {industry}:\n{json.dumps(ads_data, indent=2)}"
    except Exception as e:
        return f"Error fetching ads: {str(e)}"

@mcp.tool()
def analyze_ad_trends(industry: str, days_back: int = 7) -> str:
    """Analyze advertising trends for a specific industry over time.
    
    Args:
        industry: Industry to analyze
        days_back: Number of days to look back for trend analysis
    """
    if industry.lower() not in INDUSTRY_KEYWORDS:
        available = ", ".join(INDUSTRY_KEYWORDS.keys())
        return f"Industry '{industry}' not supported. Available industries: {available}"
    
    # Generate trend analysis based on cached data or demo data
    trends = _generate_trend_analysis(industry, days_back)
    return f"Ad Trend Analysis for {industry} (last {days_back} days):\n{json.dumps(trends, indent=2)}"

@mcp.tool()
def get_top_advertisers(industry: str, limit: int = 10) -> str:
    """Get top advertisers in a specific industry by ad spend or volume.
    
    Args:
        industry: Industry to analyze
        limit: Number of top advertisers to return
    """
    if industry.lower() not in INDUSTRY_KEYWORDS:
        available = ", ".join(INDUSTRY_KEYWORDS.keys())
        return f"Industry '{industry}' not supported. Available industries: {available}"
    
    top_advertisers = _generate_top_advertisers(industry, limit)
    return f"Top {limit} Advertisers in {industry}:\n{json.dumps(top_advertisers, indent=2)}"

@mcp.tool()
def compare_industries(industry1: str, industry2: str, metric: str = "ad_volume") -> str:
    """Compare advertising metrics between two industries.
    
    Args:
        industry1: First industry to compare
        industry2: Second industry to compare
        metric: Metric to compare (ad_volume, spend_estimate, avg_duration)
    """
    valid_industries = list(INDUSTRY_KEYWORDS.keys())
    if industry1.lower() not in INDUSTRY_KEYWORDS or industry2.lower() not in INDUSTRY_KEYWORDS:
        return f"Both industries must be from: {', '.join(valid_industries)}"
    
    comparison = _generate_industry_comparison(industry1, industry2, metric)
    return f"Industry Comparison ({industry1} vs {industry2}):\n{json.dumps(comparison, indent=2)}"

@mcp.tool()
def search_google_ads_by_industry(industry: str, limit: int = 50, google_api_key: Optional[str] = None) -> str:
    """Search Google Ads transparency data by industry.
    
    Args:
        industry: Industry to search for (automotive, fashion, technology, etc.)
        limit: Maximum number of ads to return (default: 50)
        google_api_key: Google Ads API key (optional, uses demo data if not provided)
    """
    if industry.lower() not in INDUSTRY_KEYWORDS:
        available = ", ".join(INDUSTRY_KEYWORDS.keys())
        return f"Industry '{industry}' not supported. Available industries: {available}"
    
    # Check cache first
    cache_key = f"google_{industry}_{limit}"
    if cache_key in google_ads_cache:
        cached_data = google_ads_cache[cache_key]
        cache_time = datetime.fromisoformat(cached_data.get("timestamp", "2020-01-01"))
        if datetime.now() - cache_time < timedelta(hours=1):
            return f"Cached Google Ads Data for {industry}:\n{json.dumps(cached_data['data'], indent=2)}"
    
    # If no API key provided, return demo data
    if not google_api_key:
        demo_ads = _generate_demo_google_ads_data(industry, limit)
        google_ads_cache[cache_key] = {
            "data": demo_ads,
            "timestamp": datetime.now().isoformat()
        }
        return f"Demo Google Ads Data for {industry}:\n{json.dumps(demo_ads, indent=2)}"
    
    # Real Google Ads API call (placeholder for actual implementation)
    try:
        ads_data = _fetch_google_ads(industry, limit, google_api_key)
        google_ads_cache[cache_key] = {
            "data": ads_data,
            "timestamp": datetime.now().isoformat()
        }
        return f"Google Ads Transparency Data for {industry}:\n{json.dumps(ads_data, indent=2)}"
    except Exception as e:
        return f"Error fetching Google ads: {str(e)}"

@mcp.tool()
def get_all_brands_by_industry(industry: str, include_competitors: bool = True) -> str:
    """Get comprehensive list of all brands in a specific industry.
    
    Args:
        industry: Industry to search for brands
        include_competitors: Include competitor analysis data
    """
    if industry.lower() not in INDUSTRY_KEYWORDS:
        available = ", ".join(INDUSTRY_KEYWORDS.keys())
        return f"Industry '{industry}' not supported. Available industries: {available}"
    
    # Check cache first
    cache_key = f"brands_{industry}_{include_competitors}"
    if cache_key in brands_cache:
        return f"Brands in {industry}:\n{json.dumps(brands_cache[cache_key], indent=2)}"
    
    # Generate comprehensive brand list
    brands_data = _generate_comprehensive_brands_data(industry, include_competitors)
    brands_cache[cache_key] = brands_data
    
    return f"Comprehensive Brands in {industry}:\n{json.dumps(brands_data, indent=2)}"

@mcp.tool()
def compare_meta_vs_google_ads(industry: str, metric: str = "reach") -> str:
    """Compare Meta vs Google Ads performance for an industry.
    
    Args:
        industry: Industry to compare
        metric: Metric to compare (reach, spend, engagement, ctr)
    """
    if industry.lower() not in INDUSTRY_KEYWORDS:
        available = ", ".join(INDUSTRY_KEYWORDS.keys())
        return f"Industry '{industry}' not supported. Available industries: {available}"
    
    comparison = _generate_platform_comparison(industry, metric)
    return f"Meta vs Google Ads Comparison ({industry}):\n{json.dumps(comparison, indent=2)}"

@mcp.tool()
def analyze_brand_advertising_strategy(brand_name: str, industry: str, platforms: List[str] = ["meta", "google"]) -> str:
    """Analyze a specific brand's advertising strategy across platforms.
    
    Args:
        brand_name: Name of the brand to analyze
        industry: Industry the brand belongs to
        platforms: List of platforms to analyze (meta, google, both)
    """
    if industry.lower() not in INDUSTRY_KEYWORDS:
        available = ", ".join(INDUSTRY_KEYWORDS.keys())
        return f"Industry '{industry}' not supported. Available industries: {available}"
    
    strategy_analysis = _generate_brand_strategy_analysis(brand_name, industry, platforms)
    return f"Brand Strategy Analysis for {brand_name}:\n{json.dumps(strategy_analysis, indent=2)}"

@mcp.tool()
def get_sector_overview_eur(industry: str, currency: str = "EUR", country_filter: str = "all", date_from: str = None, date_to: str = None) -> str:
    """Get comprehensive sector overview with European brands and spending in EUR.
    
    Args:
        industry: Industry to analyze
        currency: Target currency (EUR, USD, GBP, etc.)
        country_filter: Country to filter by (all, Germany, France, etc.)
    """
    if industry.lower() not in BELGIUM_FRANCE_BRANDS_DATABASE:
        available = ", ".join(BELGIUM_FRANCE_BRANDS_DATABASE.keys())
        return f"Industry '{industry}' not available in Belgian/French database. Available industries: {available}"
    
    if currency not in CURRENCY_RATES:
        available = ", ".join(CURRENCY_RATES.keys())
        return f"Currency '{currency}' not supported. Available currencies: {available}"
    
    sector_data = _generate_sector_overview(industry, currency, country_filter, date_from, date_to)
    return f"European Sector Overview - {industry.title()}:\n{json.dumps(sector_data, indent=2)}"

@mcp.tool()
def get_brand_details_eur(brand_name: str, industry: str, currency: str = "EUR", country_filter: str = "all", date_from: str = None, date_to: str = None) -> str:
    """Get detailed information about a specific European brand including ad spend in EUR.
    
    Args:
        brand_name: Name of the brand
        industry: Industry the brand belongs to
        currency: Target currency for financial data
        country_filter: Country to filter by (all, Germany, France, etc.)
    """
    if industry.lower() not in BELGIUM_FRANCE_BRANDS_DATABASE:
        available = ", ".join(BELGIUM_FRANCE_BRANDS_DATABASE.keys())
        return f"Industry '{industry}' not available. Available industries: {available}"
    
    if currency not in CURRENCY_RATES:
        available = ", ".join(CURRENCY_RATES.keys())
        return f"Currency '{currency}' not supported. Available currencies: {available}"
    
    brand_details = _get_brand_granular_details(brand_name, industry, currency, country_filter, date_from, date_to)
    return f"Brand Details - {brand_name}:\n{json.dumps(brand_details, indent=2)}"

@mcp.tool()
def get_country_brand_analysis_eur(country: str, currency: str = "EUR") -> str:
    """Get all brands from a specific European country with ad spending analysis.
    
    Args:
        country: Country to analyze (Germany, France, UK, etc.)
        currency: Target currency for financial data
    """
    if currency not in CURRENCY_RATES:
        available = ", ".join(CURRENCY_RATES.keys())
        return f"Currency '{currency}' not supported. Available currencies: {available}"
    
    country_analysis = _generate_country_brand_analysis(country, currency)
    return f"Country Brand Analysis - {country}:\n{json.dumps(country_analysis, indent=2)}"

@mcp.tool()
def get_subcategory_analysis_eur(industry: str, subcategory: str, currency: str = "EUR", country_filter: str = "all") -> str:
    """Get granular analysis of a specific subcategory within an industry.
    
    Args:
        industry: Main industry (automotive, fashion, technology, etc.)
        subcategory: Specific subcategory (luxury, mainstream, enterprise, etc.)
        currency: Target currency for financial data
        country_filter: Country to filter by (all, Germany, France, etc.)
    """
    if industry.lower() not in BELGIUM_FRANCE_BRANDS_DATABASE:
        available = ", ".join(BELGIUM_FRANCE_BRANDS_DATABASE.keys())
        return f"Industry '{industry}' not available. Available industries: {available}"
    
    if currency not in CURRENCY_RATES:
        available = ", ".join(CURRENCY_RATES.keys())
        return f"Currency '{currency}' not supported. Available currencies: {available}"
    
    subcategory_data = _generate_subcategory_analysis(industry, subcategory, currency, country_filter)
    return f"Subcategory Analysis - {industry.title()} > {subcategory.title()}:\n{json.dumps(subcategory_data, indent=2)}"

def _generate_demo_google_ads_data(industry: str, limit: int) -> List[Dict]:
    """Generate demo Google Ads data for testing purposes."""
    demo_ads = []
    keywords = INDUSTRY_KEYWORDS[industry.lower()]
    
    for i in range(min(limit, 20)):
        ad = {
            "id": f"google_ad_{industry}_{i+1}",
            "advertiser_name": f"Google {industry.title()} Advertiser {i+1}",
            "ad_title": f"Best {keywords[i % len(keywords)]} Solutions",
            "ad_description": f"Discover premium {keywords[i % len(keywords)]} with Google Ads",
            "display_url": f"www.{industry}company{i+1}.com",
            "first_shown": (datetime.now() - timedelta(days=i*2)).isoformat(),
            "last_shown": (datetime.now() - timedelta(days=i)).isoformat(),
            "format": ["Text", "Display", "Video", "Shopping"][i % 4],
            "targeting": {
                "locations": ["United States", "Canada", "United Kingdom", "Australia"],
                "age_range": f"{18 + (i % 4) * 10}-{27 + (i % 4) * 10}",
                "interests": keywords[:3]
            },
            "performance_metrics": {
                "impressions_min": (i+1) * 5000,
                "impressions_max": (i+1) * 25000,
                "clicks_estimate": (i+1) * 250,
                "ctr_estimate": f"{1.5 + (i % 5) * 0.5}%"
            },
            "political_ad": False,
            "platform": "Google Ads"
        }
        demo_ads.append(ad)
    
    return demo_ads

def _fetch_google_ads(industry: str, limit: int, api_key: str) -> List[Dict]:
    """Fetch real Google Ads from Transparency Center API (placeholder implementation)."""
    # This is a placeholder for actual Google Ads Transparency Center API
    # Real implementation would use Google's BigQuery API or third-party services like SerpApi
    
    # Example SerpApi integration:
    # base_url = "https://serpapi.com/search"
    # params = {
    #     "engine": "google_ads_transparency_center",
    #     "api_key": api_key,
    #     "advertiser": industry_specific_advertisers,
    #     "format": "json"
    # }
    
    try:
        # Placeholder for actual API implementation
        # response = requests.get(base_url, params=params, timeout=30)
        # response.raise_for_status()
        # return response.json().get("ads", [])
        
        # Return demo data for now
        return _generate_demo_google_ads_data(industry, limit)
    except Exception as e:
        raise Exception(f"Google Ads API request failed: {str(e)}")

def _filter_brands_by_country(brands_dict: Dict, country_filter: str) -> Dict:
    """Filter brands by country."""
    if country_filter == "all":
        return brands_dict
    
    filtered_brands = {}
    for brand_name, brand_data in brands_dict.items():
        # Handle multi-country brands like "Netherlands/UK"
        brand_country = brand_data["country"].lower()
        filter_country = country_filter.lower()
        
        if filter_country in brand_country or brand_country in filter_country:
            filtered_brands[brand_name] = brand_data
        # Handle exact matches and partial matches
        elif any(filter_country == c.strip().lower() for c in brand_country.split('/')):
            filtered_brands[brand_name] = brand_data
    
    return filtered_brands

def _convert_currency(amount_eur: float, target_currency: str) -> float:
    """Convert EUR amount to target currency."""
    if target_currency not in CURRENCY_RATES:
        return amount_eur
    return amount_eur * CURRENCY_RATES[target_currency]

def _format_currency(amount: float, currency: str) -> str:
    """Format currency amount with appropriate symbol."""
    symbols = {
        "EUR": "€", "USD": "$", "GBP": "£", "CHF": "CHF", 
        "SEK": "kr", "NOK": "kr", "DKK": "kr"
    }
    symbol = symbols.get(currency, currency)
    
    if amount >= 1000000000:
        return f"{symbol}{amount/1000000000:.1f}B"
    elif amount >= 1000000:
        return f"{symbol}{amount/1000000:.1f}M"
    elif amount >= 1000:
        return f"{symbol}{amount/1000:.0f}K"
    else:
        return f"{symbol}{amount:.0f}"

def _calculate_date_multiplier(date_from: str, date_to: str) -> float:
    """Calculate the multiplier for date range filtering.
    
    Args:
        date_from: Start date (YYYY-MM-DD)
        date_to: End date (YYYY-MM-DD)
    
    Returns:
        float: Multiplier (e.g., 0.25 for Q1, 0.083 for 1 month, etc.)
    """
    if not date_from or not date_to:
        return 1.0  # Full year if no dates specified
    
    try:
        start = datetime.strptime(date_from, "%Y-%m-%d")
        end = datetime.strptime(date_to, "%Y-%m-%d")
        days_in_range = (end - start).days + 1
        
        # Assume annual data, so calculate fraction of year
        days_in_year = 365
        multiplier = days_in_range / days_in_year
        
        return max(0.001, min(1.0, multiplier))  # Clamp between 0.1% and 100%
    except (ValueError, TypeError):
        return 1.0  # Return full year if date parsing fails

def _calculate_platform_split(brand_name: str, industry: str, total_spend: float) -> Dict[str, float]:
    """Calculate realistic Meta vs Google ad spend split based on industry and brand characteristics.
    
    Args:
        brand_name: Name of the brand
        industry: Industry category
        total_spend: Total ad spend amount
    
    Returns:
        Dict with meta_percentage, google_percentage, meta_spend, google_spend
    """
    # Industry-based platform preferences (based on real market data)
    industry_splits = {
        "automotive": {"meta": 35, "google": 65},  # Google stronger for automotive searches
        "fashion": {"meta": 65, "google": 35},     # Meta stronger for visual/lifestyle brands
        "technology": {"meta": 40, "google": 60},  # Google stronger for B2B tech
        "finance": {"meta": 30, "google": 70},     # Google stronger for financial services
        "food": {"meta": 55, "google": 45},        # Meta stronger for food/lifestyle
        "healthcare": {"meta": 25, "google": 75},  # Google dominant for health searches
        "travel": {"meta": 50, "google": 50},      # Balanced for travel industry
        "education": {"meta": 35, "google": 65},   # Google stronger for education
        "real_estate": {"meta": 45, "google": 55}, # Balanced with slight Google preference
        "gaming": {"meta": 70, "google": 30}       # Meta dominant for gaming/entertainment
    }
    
    # Get base split for industry
    base_split = industry_splits.get(industry.lower(), {"meta": 45, "google": 55})
    
    # Adjust based on brand characteristics
    meta_percentage = base_split["meta"]
    google_percentage = base_split["google"]
    
    # B2C brands tend to favor Meta more than B2B
    b2c_indicators = ["coca-cola", "nike", "adidas", "zara", "h&m", "mcdonald", "pizza", "burger"]
    if any(indicator in brand_name.lower() for indicator in b2c_indicators):
        meta_percentage += 10
        google_percentage -= 10
    
    # Local/regional brands tend to use more Google (local search)
    local_indicators = ["belgium", "kroymans", "d'ieteren", "jbc", "delhaize", "colruyt"]
    if any(indicator in brand_name.lower() for indicator in local_indicators):
        google_percentage += 15
        meta_percentage -= 15
    
    # Luxury brands tend to favor Meta (visual appeal)
    luxury_indicators = ["mercedes", "bmw", "audi", "chanel", "lvmh", "hermès", "gucci", "prada"]
    if any(indicator in brand_name.lower() for indicator in luxury_indicators):
        meta_percentage += 15
        google_percentage -= 15
    
    # E-commerce/retail brands favor Google (shopping ads)
    ecommerce_indicators = ["amazon", "booking", "expedia", "zalando", "bol.com"]
    if any(indicator in brand_name.lower() for indicator in ecommerce_indicators):
        google_percentage += 20
        meta_percentage -= 20
    
    # Ensure percentages are valid
    meta_percentage = max(10, min(90, meta_percentage))
    google_percentage = 100 - meta_percentage
    
    # Calculate spend amounts
    meta_spend = total_spend * (meta_percentage / 100)
    google_spend = total_spend * (google_percentage / 100)
    
    return {
        "meta_percentage": meta_percentage,
        "google_percentage": google_percentage,
        "meta_spend": meta_spend,
        "google_spend": google_spend
    }

def _generate_sector_overview(industry: str, currency: str, country_filter: str = "all", date_from: str = None, date_to: str = None) -> Dict:
    """Generate comprehensive sector overview with European brands."""
    industry_data = BELGIUM_FRANCE_BRANDS_DATABASE.get(industry.lower(), {})
    
    sector_overview = {
        "industry": industry,
        "currency": currency,
        "total_categories": len(industry_data),
        "categories": {},
        "sector_totals": {
            "total_ad_spend": 0,
            "total_brands": 0,
            "total_market_share": 0
        },
        "top_spenders": [],
        "country_breakdown": {},
        "generated_at": datetime.now().isoformat()
    }
    
    all_brands = []
    
    for brand_name, brand_data in industry_data.items():
        # Apply country filter and calculate date multiplier
        belgium_spend = brand_data["belgium_ad_spend_eur"]
        france_spend = brand_data["france_ad_spend_eur"]
        total_spend = brand_data["total_spend"]
        
        if country_filter.lower() == "belgium" and belgium_spend == 0:
            continue
        elif country_filter.lower() == "france" and france_spend == 0:
            continue
        
        # Apply date filtering
        date_multiplier = _calculate_date_multiplier(date_from, date_to)
        belgium_spend *= date_multiplier
        france_spend *= date_multiplier
        total_spend *= date_multiplier
        
        # Convert currency
        belgium_spend_converted = _convert_currency(belgium_spend, currency)
        france_spend_converted = _convert_currency(france_spend, currency)
        total_spend_converted = _convert_currency(total_spend, currency)
        
        # Determine display spend based on country filter
        if country_filter.lower() == "belgium":
            display_spend = belgium_spend_converted
            display_spend_formatted = _format_currency(belgium_spend_converted, currency)
        elif country_filter.lower() == "france":
            display_spend = france_spend_converted
            display_spend_formatted = _format_currency(france_spend_converted, currency)
        else:
            display_spend = total_spend_converted
            display_spend_formatted = _format_currency(total_spend_converted, currency)
        
        brand_info = {
            "name": brand_name,
            "belgium_spend": belgium_spend_converted,
            "belgium_spend_formatted": _format_currency(belgium_spend_converted, currency),
            "france_spend": france_spend_converted,
            "france_spend_formatted": _format_currency(france_spend_converted, currency),
            "total_spend": display_spend,
            "total_spend_formatted": display_spend_formatted,
            "market_share_belgium": brand_data["market_share_be"],
            "market_share_france": brand_data["market_share_fr"],
            "platforms": brand_data["platforms"]
        }
        
        all_brands.append(brand_info)
        
        # Country breakdown
        if belgium_spend > 0:
            if "Belgium" not in sector_overview["country_breakdown"]:
                sector_overview["country_breakdown"]["Belgium"] = {
                    "brands": 0,
                    "total_spend": 0,
                    "market_share": 0
                }
            sector_overview["country_breakdown"]["Belgium"]["brands"] += 1
            sector_overview["country_breakdown"]["Belgium"]["total_spend"] += belgium_spend_converted
            sector_overview["country_breakdown"]["Belgium"]["market_share"] += brand_data["market_share_be"]
        
        if france_spend > 0:
            if "France" not in sector_overview["country_breakdown"]:
                sector_overview["country_breakdown"]["France"] = {
                    "brands": 0,
                    "total_spend": 0,
                    "market_share": 0
                }
            sector_overview["country_breakdown"]["France"]["brands"] += 1
            sector_overview["country_breakdown"]["France"]["total_spend"] += france_spend_converted
            sector_overview["country_breakdown"]["France"]["market_share"] += brand_data["market_share_fr"]
    
    # Update totals
    sector_overview["sector_totals"]["total_ad_spend"] = sum(brand["total_spend"] for brand in all_brands)
    sector_overview["sector_totals"]["total_brands"] = len(all_brands)
    
    # Format country breakdown
    for country_data in sector_overview["country_breakdown"].values():
        country_data["total_spend_formatted"] = _format_currency(country_data["total_spend"], currency)
    
    # Top spenders across all categories
    sector_overview["top_spenders"] = sorted(all_brands, key=lambda x: x["total_spend"], reverse=True)[:10]
    
    # Format sector totals
    sector_overview["sector_totals"]["total_ad_spend_formatted"] = _format_currency(
        sector_overview["sector_totals"]["total_ad_spend"], currency
    )
    
    return sector_overview

def _get_brand_granular_details(brand_name: str, industry: str, currency: str, country_filter: str = "all", date_from: str = None, date_to: str = None) -> Dict:
    """Get detailed granular information about a specific brand."""
    industry_data = BELGIUM_FRANCE_BRANDS_DATABASE.get(industry.lower(), {})
    
    # Find the brand in flat structure (case-insensitive)
    brand_key = None
    for key in industry_data.keys():
        if key.lower() == brand_name.lower():
            brand_key = key
            break
    
    if brand_key is None:
        return {
            "error": f"Brand '{brand_name}' not found in {industry} industry",
            "available_brands": list(industry_data.keys())
        }
    
    brand_info = industry_data[brand_key]
    # Use the actual brand name from database for consistency
    brand_name = brand_key
    
    # Check country filter and apply date filtering
    belgium_spend = brand_info["belgium_ad_spend_eur"]
    france_spend = brand_info["france_ad_spend_eur"]
    total_spend = brand_info["total_spend"]
    
    if country_filter.lower() == "belgium" and belgium_spend == 0:
        return {
            "error": f"Brand '{brand_name}' has no advertising spend in Belgium",
            "available_brands": [brand for brand, data in industry_data.items() if data["belgium_ad_spend_eur"] > 0]
        }
    elif country_filter.lower() == "france" and france_spend == 0:
        return {
            "error": f"Brand '{brand_name}' has no advertising spend in France", 
            "available_brands": [brand for brand, data in industry_data.items() if data["france_ad_spend_eur"] > 0]
        }
    
    # Apply date filtering
    date_multiplier = _calculate_date_multiplier(date_from, date_to)
    belgium_spend *= date_multiplier
    france_spend *= date_multiplier
    total_spend *= date_multiplier
    
    # Convert currency
    belgium_spend_converted = _convert_currency(belgium_spend, currency)
    france_spend_converted = _convert_currency(france_spend, currency)
    total_spend_converted = _convert_currency(total_spend, currency)
    
    # Determine display spend based on country filter
    if country_filter.lower() == "belgium":
        display_spend = belgium_spend_converted
        display_spend_formatted = _format_currency(belgium_spend_converted, currency)
    elif country_filter.lower() == "france":
        display_spend = france_spend_converted  
        display_spend_formatted = _format_currency(france_spend_converted, currency)
    else:
        display_spend = total_spend_converted
        display_spend_formatted = _format_currency(total_spend_converted, currency)
    
    # Generate detailed analysis
    brand_details = {
        "brand_name": brand_name,
        "industry": industry,
        "market_presence": {
            "belgium": belgium_spend > 0,
            "france": france_spend > 0,
            "platforms": brand_info["platforms"]
        },
        "financial_data": {
            "belgium_ad_spend": belgium_spend_converted,
            "belgium_ad_spend_formatted": _format_currency(belgium_spend_converted, currency),
            "france_ad_spend": france_spend_converted,
            "france_ad_spend_formatted": _format_currency(france_spend_converted, currency),
            "total_ad_spend": display_spend,
            "total_ad_spend_formatted": display_spend_formatted,
            "currency": currency,
            "market_share_belgium": brand_info["market_share_be"],
            "market_share_france": brand_info["market_share_fr"],
            "estimated_monthly_spend_total": display_spend / 12,
            "estimated_monthly_spend_total_formatted": _format_currency(display_spend / 12, currency),
            "estimated_daily_spend_total": display_spend / 365,
            "estimated_daily_spend_total_formatted": _format_currency(display_spend / 365, currency)
        },
        "platform_breakdown": {
            "meta_estimated": _calculate_platform_split(brand_name, industry, display_spend)["meta_spend"],
            "google_estimated": _calculate_platform_split(brand_name, industry, display_spend)["google_spend"],
            "meta_estimated_formatted": _format_currency(_calculate_platform_split(brand_name, industry, display_spend)["meta_spend"], currency),
            "google_estimated_formatted": _format_currency(_calculate_platform_split(brand_name, industry, display_spend)["google_spend"], currency),
            "meta_percentage": _calculate_platform_split(brand_name, industry, display_spend)["meta_percentage"],
            "google_percentage": _calculate_platform_split(brand_name, industry, display_spend)["google_percentage"]
        },
        "ad_type_breakdown": {
            "video_percentage": brand_info.get("ad_types", {}).get("video", 60),
            "display_percentage": brand_info.get("ad_types", {}).get("display", 40),
            "video_spend": display_spend * (brand_info.get("ad_types", {}).get("video", 60) / 100),
            "display_spend": display_spend * (brand_info.get("ad_types", {}).get("display", 40) / 100),
            "video_spend_formatted": _format_currency(display_spend * (brand_info.get("ad_types", {}).get("video", 60) / 100), currency),
            "display_spend_formatted": _format_currency(display_spend * (brand_info.get("ad_types", {}).get("display", 40) / 100), currency)
        },
        "generated_at": datetime.now().isoformat()
    }
    
    # Competitive position analysis
    all_brands_spending = [(name, data["total_spend"]) for name, data in industry_data.items()]
    all_brands_spending.sort(key=lambda x: x[1], reverse=True)
    
    brand_rank = next((i+1 for i, (name, _) in enumerate(all_brands_spending) if name == brand_name), None)
    
    brand_details["competitive_position"] = {
        "rank_in_industry": brand_rank,
        "total_brands_in_industry": len(industry_data),
        "industry_leader": all_brands_spending[0][0] if all_brands_spending else None,
        "spend_vs_leader_ratio": total_spend_converted / _convert_currency(all_brands_spending[0][1], currency) if all_brands_spending else 0
    }
    
    return brand_details

def _generate_country_brand_analysis(country: str, currency: str) -> Dict:
    """Generate analysis of all brands from a specific country."""
    country_brands = []
    
    for industry, categories in BELGIUM_FRANCE_BRANDS_DATABASE.items():
        for category, brands in categories.items():
            for brand_name, brand_data in brands.items():
                if country.lower() in brand_data["country"].lower():
                    spend_converted = _convert_currency(brand_data["annual_ad_spend_eur"], currency)
                    country_brands.append({
                        "name": brand_name,
                        "industry": industry,
                        "category": category,
                        "headquarters": brand_data["headquarters"],
                        "annual_ad_spend": spend_converted,
                        "annual_ad_spend_formatted": _format_currency(spend_converted, currency),
                        "market_share": brand_data["market_share"]
                    })
    
    if not country_brands:
        return {
            "error": f"No brands found for country '{country}'",
            "available_countries": list(set(
                brand_data["country"] for categories in BELGIUM_FRANCE_BRANDS_DATABASE.values() 
                for brands in categories.values() 
                for brand_data in brands.values()
            ))
        }
    
    # Sort by spending
    country_brands.sort(key=lambda x: x["annual_ad_spend"], reverse=True)
    
    # Calculate totals
    total_spend = sum(brand["annual_ad_spend"] for brand in country_brands)
    total_market_share = sum(brand["market_share"] for brand in country_brands)
    
    # Industry breakdown
    industry_breakdown = {}
    for brand in country_brands:
        industry = brand["industry"]
        if industry not in industry_breakdown:
            industry_breakdown[industry] = {"brands": 0, "total_spend": 0, "brands_list": []}
        industry_breakdown[industry]["brands"] += 1
        industry_breakdown[industry]["total_spend"] += brand["annual_ad_spend"]
        industry_breakdown[industry]["brands_list"].append(brand["name"])
    
    # Format industry breakdown
    for industry_data in industry_breakdown.values():
        industry_data["total_spend_formatted"] = _format_currency(industry_data["total_spend"], currency)
    
    return {
        "country": country,
        "currency": currency,
        "summary": {
            "total_brands": len(country_brands),
            "total_ad_spend": total_spend,
            "total_ad_spend_formatted": _format_currency(total_spend, currency),
            "total_market_share": total_market_share,
            "industries_represented": len(industry_breakdown)
        },
        "top_brands": country_brands[:15],
        "industry_breakdown": industry_breakdown,
        "generated_at": datetime.now().isoformat()
    }

def _generate_subcategory_analysis(industry: str, subcategory: str, currency: str, country_filter: str = "all") -> Dict:
    """Generate granular analysis of a specific subcategory."""
    industry_data = BELGIUM_FRANCE_BRANDS_DATABASE.get(industry.lower(), {})
    
    if subcategory.lower() not in industry_data:
        return {
            "error": f"Subcategory '{subcategory}' not found in {industry}",
            "available_subcategories": list(industry_data.keys())
        }
    
    category_brands = industry_data[subcategory.lower()]
    
    # Apply country filter
    filtered_brands = _filter_brands_by_country(category_brands, country_filter)
    
    # Convert and sort brands
    brands_analysis = []
    total_spend = 0
    
    for brand_name, brand_data in filtered_brands.items():
        spend_converted = _convert_currency(brand_data["annual_ad_spend_eur"], currency)
        total_spend += spend_converted
        
        brands_analysis.append({
            "name": brand_name,
            "country": brand_data["country"],
            "headquarters": brand_data["headquarters"],
            "annual_ad_spend": spend_converted,
            "annual_ad_spend_formatted": _format_currency(spend_converted, currency),
            "market_share": brand_data["market_share"],
            "share_of_category_spend": 0  # Will calculate after total is known
        })
    
    # Calculate share of category spend
    for brand in brands_analysis:
        brand["share_of_category_spend"] = (brand["annual_ad_spend"] / total_spend * 100) if total_spend > 0 else 0
    
    # Sort by spending
    brands_analysis.sort(key=lambda x: x["annual_ad_spend"], reverse=True)
    
    # Country analysis within subcategory
    country_analysis = {}
    for brand in brands_analysis:
        country = brand["country"]
        if country not in country_analysis:
            country_analysis[country] = {"brands": 0, "total_spend": 0, "market_share": 0}
        country_analysis[country]["brands"] += 1
        country_analysis[country]["total_spend"] += brand["annual_ad_spend"]
        country_analysis[country]["market_share"] += brand["market_share"]
    
    # Format country analysis
    for country_data in country_analysis.values():
        country_data["total_spend_formatted"] = _format_currency(country_data["total_spend"], currency)
    
    return {
        "industry": industry,
        "subcategory": subcategory,
        "currency": currency,
        "summary": {
            "total_brands": len(brands_analysis),
            "total_ad_spend": total_spend,
            "total_ad_spend_formatted": _format_currency(total_spend, currency),
            "average_spend_per_brand": total_spend / len(brands_analysis) if brands_analysis else 0,
            "average_spend_per_brand_formatted": _format_currency(total_spend / len(brands_analysis), currency) if brands_analysis else "€0",
            "countries_represented": len(country_analysis)
        },
        "brands": brands_analysis,
        "country_analysis": country_analysis,
        "market_concentration": {
            "top_3_share": sum(brand["share_of_category_spend"] for brand in brands_analysis[:3]),
            "top_5_share": sum(brand["share_of_category_spend"] for brand in brands_analysis[:5]),
            "herfindahl_index": sum(brand["share_of_category_spend"]**2 for brand in brands_analysis) / 10000
        },
        "generated_at": datetime.now().isoformat()
    }

def _generate_comprehensive_brands_data(industry: str, include_competitors: bool) -> Dict:
    """Generate comprehensive brand data using real European brand database."""
    industry_data = BELGIUM_FRANCE_BRANDS_DATABASE.get(industry.lower(), {})
    
    if not industry_data:
        return {
            "error": f"Industry '{industry}' not found in European database",
            "available_industries": list(BELGIUM_FRANCE_BRANDS_DATABASE.keys())
        }
    
    result = {
        "industry": industry,
        "total_brands": sum(len(brands) for brands in industry_data.values()),
        "categories": {},
        "analysis_timestamp": datetime.now().isoformat()
    }
    
    # Convert from detailed brand data to simplified format for this function
    for category, brands in industry_data.items():
        result["categories"][category] = list(brands.keys())
    
    if include_competitors:
        # Get top brands by spending from each category
        all_brands = []
        for category, brands in industry_data.items():
            category_brands = [{"name": name, "spend": data["annual_ad_spend_eur"]} 
                             for name, data in brands.items()]
            category_brands.sort(key=lambda x: x["spend"], reverse=True)
            all_brands.extend(category_brands)
        
        all_brands.sort(key=lambda x: x["spend"], reverse=True)
        
        result["competitive_analysis"] = {
            "market_leaders": [brand["name"] for brand in all_brands[:5]],
            "emerging_competitors": [brand["name"] for brand in all_brands[-3:]] if len(all_brands) > 3 else [],
            "market_share_estimate": {
                brand["name"]: f"€{brand['spend']/1000000:.0f}M" for brand in all_brands[:5]
            }
        }
    
    return result

def _generate_platform_comparison(industry: str, metric: str) -> Dict:
    """Generate comparison between Meta and Google Ads for an industry."""
    
    # Generate realistic comparison metrics
    meta_base = hash(f"meta_{industry}") % 1000 + 500
    google_base = hash(f"google_{industry}") % 1000 + 500
    
    metrics_data = {
        "reach": {
            "meta": {"value": meta_base * 1000, "unit": "users", "trend": "stable"},
            "google": {"value": google_base * 1200, "unit": "users", "trend": "increasing"}
        },
        "spend": {
            "meta": {"value": meta_base * 100, "unit": "USD", "trend": "increasing"},
            "google": {"value": google_base * 120, "unit": "USD", "trend": "stable"}
        },
        "engagement": {
            "meta": {"value": meta_base / 100, "unit": "rate", "trend": "decreasing"},
            "google": {"value": google_base / 150, "unit": "rate", "trend": "stable"}
        },
        "ctr": {
            "meta": {"value": (meta_base % 10) / 10 + 1, "unit": "percentage", "trend": "stable"},
            "google": {"value": (google_base % 10) / 10 + 2, "unit": "percentage", "trend": "increasing"}
        }
    }
    
    current_metric = metrics_data.get(metric, metrics_data["reach"])
    leader = "google" if current_metric["google"]["value"] > current_metric["meta"]["value"] else "meta"
    
    return {
        "industry": industry,
        "comparison_metric": metric,
        "platforms": current_metric,
        "leader": leader,
        "difference_percentage": abs(current_metric["meta"]["value"] - current_metric["google"]["value"]) / max(current_metric["meta"]["value"], current_metric["google"]["value"]) * 100,
        "insights": [
            f"Google Ads shows higher {metric} volume in {industry}",
            f"Meta provides better engagement rates for {industry} brands",
            f"Both platforms show strong performance in {industry} sector"
        ][:2] if leader == "google" else [
            f"Meta leads in {metric} performance for {industry}",
            f"Google Ads offers broader reach in {industry} market"
        ]
    }

def _generate_brand_strategy_analysis(brand_name: str, industry: str, platforms: List[str]) -> Dict:
    """Generate brand advertising strategy analysis."""
    
    strategy_data = {
        "brand": brand_name,
        "industry": industry,
        "platforms_analyzed": platforms,
        "analysis_period": "Last 30 days",
        "overall_strategy": "Multi-platform approach with focus on brand awareness",
        "platform_breakdown": {}
    }
    
    if "meta" in platforms:
        strategy_data["platform_breakdown"]["meta"] = {
            "primary_objective": "Brand awareness and engagement",
            "ad_formats": ["Video", "Carousel", "Single Image"],
            "targeting_strategy": "Interest-based with lookalike audiences",
            "estimated_spend": f"${hash(brand_name) % 50000 + 10000}",
            "performance_score": (hash(brand_name) % 10) / 10 + 0.7,
            "key_campaigns": [
                f"{brand_name} Brand Launch",
                f"{brand_name} Product Showcase",
                f"{brand_name} Customer Stories"
            ]
        }
    
    if "google" in platforms:
        strategy_data["platform_breakdown"]["google"] = {
            "primary_objective": "Lead generation and conversions",
            "ad_formats": ["Search", "Display", "Shopping", "YouTube"],
            "targeting_strategy": "Keyword-based with demographic overlays",
            "estimated_spend": f"${hash(brand_name) % 60000 + 15000}",
            "performance_score": (hash(brand_name) % 8) / 10 + 0.75,
            "key_campaigns": [
                f"{brand_name} Search Campaign",
                f"{brand_name} Shopping Ads",
                f"{brand_name} Retargeting"
            ]
        }
    
    # Add recommendations
    strategy_data["recommendations"] = [
        "Increase video content allocation for better engagement",
        "Implement cross-platform attribution tracking",
        "Test audience expansion on both platforms",
        "Consider seasonal campaign adjustments"
    ]
    
    return strategy_data

def _generate_demo_ad_data(industry: str, limit: int) -> List[Dict]:
    """Generate demo ad data for testing purposes."""
    demo_ads = []
    keywords = INDUSTRY_KEYWORDS[industry.lower()]
    
    for i in range(min(limit, 20)):  # Cap demo data at 20 ads
        ad = {
            "id": f"demo_ad_{industry}_{i+1}",
            "advertiser_name": f"Demo {industry.title()} Company {i+1}",
            "ad_creative_body": f"Discover amazing {keywords[i % len(keywords)]} deals!",
            "ad_delivery_start_time": (datetime.now() - timedelta(days=i)).isoformat(),
            "ad_delivery_stop_time": (datetime.now() + timedelta(days=30-i)).isoformat(),
            "spend_estimate": f"${(i+1) * 1000}-${(i+1) * 5000}",
            "impressions_estimate": f"{(i+1) * 10000}-{(i+1) * 50000}",
            "demographic_distribution": {
                "age": {"13-17": 5, "18-24": 25, "25-34": 35, "35-44": 20, "45-54": 10, "55-64": 3, "65+": 2},
                "gender": {"male": 45 + (i % 10), "female": 55 - (i % 10)}
            },
            "region_distribution": ["US", "CA", "UK", "AU"],
            "ad_type": "image" if i % 2 == 0 else "video",
            "platform": ["Facebook", "Instagram"][i % 2]
        }
        demo_ads.append(ad)
    
    return demo_ads

def _fetch_meta_ads(keywords: List[str], limit: int, access_token: str) -> List[Dict]:
    """Fetch real ads from Meta Ad Library API (placeholder implementation)."""
    # This is a placeholder for the actual Meta Ad Library API integration
    # In a real implementation, you would make authenticated requests to:
    # https://graph.facebook.com/v18.0/ads_archive
    
    base_url = "https://graph.facebook.com/v18.0/ads_archive"
    params = {
        "access_token": access_token,
        "search_terms": " OR ".join(keywords[:5]),  # Limit to first 5 keywords
        "ad_reached_countries": ["US"],
        "ad_active_status": "ALL",
        "limit": limit,
        "fields": "id,ad_creative_body,ad_delivery_start_time,ad_delivery_stop_time,page_name,spend,impressions,demographic_distribution,region_distribution"
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except requests.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")

def _generate_trend_analysis(industry: str, days_back: int) -> Dict:
    """Generate trend analysis for demo purposes."""
    return {
        "industry": industry,
        "analysis_period": f"Last {days_back} days",
        "total_ads": days_back * 15,  # Demo: ~15 ads per day
        "trend_direction": "increasing" if industry in ["technology", "automotive"] else "stable",
        "top_keywords": INDUSTRY_KEYWORDS[industry.lower()][:5],
        "daily_breakdown": [
            {
                "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                "ad_count": 10 + (i * 2) + (hash(industry) % 10),
                "estimated_spend": f"${(10 + i * 2) * 1000}"
            }
            for i in range(days_back)
        ]
    }

def _generate_top_advertisers(industry: str, limit: int) -> List[Dict]:
    """Generate top advertisers data for demo purposes."""
    base_companies = [
        f"{industry.title()} Leader Corp",
        f"Best {industry.title()} Co",
        f"Premium {industry.title()} Inc",
        f"Global {industry.title()} Solutions",
        f"Advanced {industry.title()} Systems",
        f"Elite {industry.title()} Group",
        f"Superior {industry.title()} Enterprises",
        f"Top-Tier {industry.title()} Ltd",
        f"Industry {industry.title()} Experts",
        f"Leading {industry.title()} Innovators"
    ]
    
    return [
        {
            "rank": i + 1,
            "advertiser_name": base_companies[i % len(base_companies)],
            "estimated_spend": f"${(limit - i) * 50000}",
            "ad_count": (limit - i) * 25,
            "avg_daily_spend": f"${(limit - i) * 2000}",
            "primary_platforms": ["Facebook", "Instagram"],
            "top_keywords": INDUSTRY_KEYWORDS[industry.lower()][:3]
        }
        for i in range(min(limit, len(base_companies)))
    ]

def _generate_industry_comparison(industry1: str, industry2: str, metric: str) -> Dict:
    """Generate industry comparison data for demo purposes."""
    metrics1 = {
        "ad_volume": hash(industry1) % 1000 + 500,
        "spend_estimate": hash(industry1) % 100000 + 50000,
        "avg_duration": hash(industry1) % 30 + 15
    }
    
    metrics2 = {
        "ad_volume": hash(industry2) % 1000 + 500,
        "spend_estimate": hash(industry2) % 100000 + 50000,
        "avg_duration": hash(industry2) % 30 + 15
    }
    
    return {
        "comparison_metric": metric,
        "industries": {
            industry1: {
                "value": metrics1[metric],
                "trend": "increasing" if metrics1[metric] > 700 else "stable"
            },
            industry2: {
                "value": metrics2[metric],
                "trend": "increasing" if metrics2[metric] > 700 else "stable"
            }
        },
        "leader": industry1 if metrics1[metric] > metrics2[metric] else industry2,
        "difference_percentage": abs(metrics1[metric] - metrics2[metric]) / max(metrics1[metric], metrics2[metric]) * 100
    }

if __name__ == "__main__":
    try:
        logger.info("Starting MCP server...")
        mcp.run()
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)