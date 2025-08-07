from flask import Flask, request, jsonify
  from flask_cors import CORS
  import json

  app = Flask(__name__)
  CORS(app)

  # Simplified brand data for Vercel
  BRAND_DATA = {
      "bmw": {"meta_pct": 50, "total": "€207.0M", "belgium": "€42.0M", "france": "€165.0M"},
      "nike": {"meta_pct": 75, "total": "€220.0M", "belgium": "€55.0M", "france": "€165.0M"},
      "sap": {"meta_pct": 40, "total": "€40.0M", "belgium": "€8.0M", "france": "€32.0M"},
      "coca-cola": {"meta_pct": 65, "total": "€220.0M", "belgium": "€66.0M", "france": "€154.0M"}
  }

  def handler(request):
      if request.method == 'OPTIONS':
          return ('', 204, {
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Methods': 'POST, OPTIONS',
              'Access-Control-Allow-Headers': 'Content-Type',
          })

      try:
          data = request.get_json()
          brand_name = data.get('brand_name', 'BMW').lower()
          industry = data.get('industry', 'automotive')

          # Get brand data or use default
          brand_info = BRAND_DATA.get(brand_name, BRAND_DATA["bmw"])

          # Calculate platform split
          total_amount = float(brand_info["total"].replace('€', '').replace('M', '')) * 1000000
          meta_amount = total_amount * (brand_info["meta_pct"] / 100)
          google_amount = total_amount - meta_amount

          result = {
              "brand_name": brand_name.title(),
              "industry": industry,
              "financial_data": {
                  "total_ad_spend_formatted": brand_info["total"],
                  "belgium_ad_spend_formatted": brand_info["belgium"],
                  "france_ad_spend_formatted": brand_info["france"]
              },
              "platform_breakdown": {
                  "meta_estimated_formatted": f"€{meta_amount/1000000:.1f}M",
                  "meta_percentage": brand_info["meta_pct"],
                  "google_estimated_formatted": f"€{google_amount/1000000:.1f}M",
                  "google_percentage": 100 - brand_info["meta_pct"]
              },
              "ad_type_breakdown": {
                  "video_percentage": 60,
                  "video_spend_formatted": f"€{(meta_amount + google_amount) * 0.6/1000000:.1f}M",
                  "display_percentage": 40,
                  "display_spend_formatted": f"€{(meta_amount + google_amount) * 0.4/1000000:.1f}M"
              },
              "competitive_position": {
                  "rank_in_industry": 2,
                  "total_brands_in_industry": 36,
                  "industry_leader": "Mercedes-Benz"
              }
          }

          return jsonify(result)
      except Exception as e:
          return jsonify({"error": str(e)}), 500
