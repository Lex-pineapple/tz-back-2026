from fastapi import FastAPI, HTTPException
from app.database import get_db, init_db
from app.models import NewRequest, RequestsList, RequestData, DataCreated, UpdateStatus
import math

app = FastAPI()

init_db()

@app.get('/')
def test_route():
    return {"data": "test"}

@app.post('/requests')
def create_request(item: NewRequest) -> DataCreated:
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("INSERT INTO test (title, description, status, priority) VALUES (?, ?, ?, ?)", (item.title, item.description, "new", item.priority))
        db.commit()
        item_id = cursor.lastrowid
    if not item_id:
        raise HTTPException(404, detail="Error")
    return DataCreated(id=item_id, message="Request created")

@app.get('/requests')
def get_all_items() -> RequestsList:
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM test")
        pages = cursor.fetchone()[0]
        cursor.execute("SELECT * FROM test")
        rows = cursor.fetchall()
    if not rows:
        return {"pages": 0, "items": []}
    return {
        "pages": math.ceil(pages / 10),
        "items": [RequestData(**dict(row)) for row in rows]
    }
    
@app.patch('/requests/{request_id}')
def update_item(request_id: int, body: UpdateStatus):
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT id, status FROM test WHERE id = ?", (request_id,))
        row = cursor.fetchone()

        if row is None:
            raise HTTPException(404, detail="User not found")
        if (row["status"] == "done"):
            raise HTTPException(400, detail="Cannot update status when it is done")
        
        cursor.execute("UPDATE test SET status = ? WHERE id = ?", (body.status, request_id))
        db.commit()
        cursor.execute("SELECT id, status FROM test WHERE id = ?", (request_id,))
        updated = dict(cursor.fetchone())

        return updated