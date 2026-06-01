import requests
import hashlib
import random

SERPER_API_KEY = "903af073e49903cedced710b3292200eab6e84de"

STORES = [
    {"store": "Meesho",        "mult": 1.0},
    {"store": "Bewakoof",      "mult": 1.2},
    {"store": "Snapdeal",      "mult": 1.35},
    {"store": "Amazon",        "mult": 1.5},
    {"store": "Flipkart",      "mult": 1.65},
    {"store": "Ajio",          "mult": 1.9},
    {"store": "Nykaa Fashion", "mult": 2.1},
    {"store": "Myntra",        "mult": 2.3},
    {"store": "Tata CLiQ",     "mult": 2.6},
]

def search_google_shopping(query):
    print(f"Searching for: {query}")
    results = search_serper(query)
    if results and len(results) >= 2:
        print(f"Serper returned {len(results)} real results")
        return results
    print("Using fallback estimates")
    return smart_fallback(query)

def search_serper(query):
    try:
        url = "https://google.serper.dev/shopping"
        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "gl": "in",
            "hl": "en",
            "num": 20
        }

        response = requests.post(url, headers=headers, json=payload, timeout=15)
        print(f"Serper status: {response.status_code}")

        if response.status_code != 200:
            print(f"Serper error: {response.text}")
            return []

        data = response.json()
        items = data.get("shopping", [])
        print(f"Serper found {len(items)} items")

        results = []
        for item in items:
            try:
                price_str = str(item.get("price", "0"))
                price_clean = ''.join(filter(str.isdigit, price_str.replace(',', '').replace('.', '')))
                if not price_clean:
                    continue
                price = int(price_clean)
                if price < 10:
                    price = price * 100
                if price <= 0:
                    continue

                results.append({
                    "name":          item.get("title", query),
                    "price":         price,
                    "price_display": f"Rs.{price:,}",
                    "store":         item.get("source", "Online Store"),
                    "link":          item.get("link", "#"),
                    "image":         item.get("imageUrl", ""),
                    "discount":      "",
                    "original_price":"",
                    "note":          "Live price from Google Shopping"
                })
            except Exception as e:
                print(f"Item error: {e}")
                continue

        results.sort(key=lambda x: x["price"])
        return results

    except Exception as e:
        print(f"Serper error: {e}")
        return []

def smart_fallback(query):
    seed = int(hashlib.md5(query.lower().encode()).hexdigest()[:6], 16) % 500
    base = 350 + seed
    q  = query.replace(" ", "+")
    q2 = query.replace(" ", "-")
    links = {
        "Meesho":        f"https://meesho.com/search?q={q}",
        "Bewakoof":      f"https://bewakoof.com/search?q={q}",
        "Snapdeal":      f"https://snapdeal.com/search?keyword={q}",
        "Amazon":        f"https://amazon.in/s?k={q}",
        "Flipkart":      f"https://flipkart.com/search?q={q}",
        "Ajio":          f"https://ajio.com/search/?text={q}",
        "Nykaa Fashion": f"https://nykaafashion.com/search?q={q}",
        "Myntra":        f"https://myntra.com/{q2}",
        "Tata CLiQ":     f"https://tatacliq.com/search/?text={q}",
    }
    results = []
    for s in STORES:
        price    = round(base * s["mult"] / 10) * 10
        original = round(price * 1.5 / 10) * 10
        discount = round((original - price) / original * 100)
        results.append({
            "name":           query.title(),
            "price":          price,
            "price_display":  f"Rs.{price:,}",
            "original_price": f"Rs.{original:,}",
            "discount":       f"{discount}% off",
            "store":          s["store"],
            "link":           links[s["store"]],
            "image":          "",
            "note":           "Estimated price - click Visit to see live price"
        })
    results.sort(key=lambda x: x["price"])
    return results