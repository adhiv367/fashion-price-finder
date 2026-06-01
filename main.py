from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from scraper import search_google_shopping
from database import init_db, save_search, get_history

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

class SearchRequest(BaseModel):
    query: str

@app.get("/")
def home():
    return FileResponse("index.html")

@app.post("/search")
def search(req: SearchRequest):
    print(f"Search received: {req.query}")
    results = search_google_shopping(req.query)
    if not results:
        return {
            "query": req.query,
            "total_found": 0,
            "cheapest": None,
            "savings": 0,
            "results": [],
            "message": "No results found"
        }
    cheapest = results[0]
    highest  = results[-1]
    savings  = highest["price"] - cheapest["price"]
    if results:
        save_search(req.query, results)
    return {
        "query":       req.query,
        "total_found": len(results),
        "cheapest":    cheapest,
        "highest":     highest,
        "savings":     savings,
        "results":     results,
        "message":     "success"
    }

@app.get("/history")
def history():
    return {"history": get_history()}

@app.get("/ping")
def ping():
    return {"status": "Server is running!"}