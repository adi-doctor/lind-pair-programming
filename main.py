from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Item API")

# In-memory data store
items_db = {
    1: {"id": 1, "name": "Wireless Mouse", "price": 29.99},
    2: {"id": 2, "name": "Mechanical Keyboard", "price": 89.99},
}

# Request schema for validation
class ItemCreate(BaseModel):
    name: str
    price: float

# GET: Fetch all items
@app.get("/items")
def list_items():
    return list(items_db.values())

# GET: Fetch a single item by ID
@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]

# POST: Create a new item
@app.post("/items", status_code=201)
def create_item(item: ItemCreate):
    new_id = max(items_db.keys(), default=0) + 1
    new_item = {"id": new_id, **item.model_dump()}
    items_db[new_id] = new_item
    return new_item