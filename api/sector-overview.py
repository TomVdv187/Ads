from flask import request, jsonify

  def handler(request):
      if request.method == 'OPTIONS':
          return ('', 204, {
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Methods': 'POST, OPTIONS',
              'Access-Control-Allow-Headers': 'Content-Type',
          })

      try:
          data = request.get_json()
          industry = data.get('industry', 'automotive')

          result = {
              "industry": industry,
              "currency": "EUR",
              "sector_totals": {
                  "total_ad_spend_formatted": "€2.5B",
                  "total_brands": 36
              },
              "top_spenders": [
                  {"name": "Mercedes-Benz", "total_spend_formatted": "€225.0M"},
                  {"name": "BMW", "total_spend_formatted": "€207.0M"},
                  {"name": "Audi", "total_spend_formatted": "€189.0M"},
                  {"name": "Toyota", "total_spend_formatted": "€165.0M"},
                  {"name": "Tesla", "total_spend_formatted": "€143.0M"}
              ]
          }

          return jsonify(result)
      except Exception as e:
          return jsonify({"error": str(e)}), 500

  4. Click "Commit new file"

  Step 3: Update vercel.json

  1. Find your existing vercel.json file and edit it
  2. Replace the content with:

  {
    "version": 2,
    "builds": [
      {
        "src": "api/*.py",
        "use": "@vercel/python"
      }
    ],
    "routes": [
      {
        "src": "/api/brands/brand-details",
        "dest": "/api/brand-details.py"
      },
      {
        "src": "/api/brands/sector-overview",
        "dest": "/api/sector-overview.py"
      },
      {
        "src": "/(.*)",
        "dest": "/ad-transparency-dashboard.html"
      }
    ]
  }
