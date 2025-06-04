import requests

url = "https://keyvalue.hamropatro.com/kv/get/market_segment_gold::1690855810198"
res = requests.get(url)

# Print raw text so we can inspect it exactly
print("RAW RESPONSE TEXT:\n")
print(res.text)
