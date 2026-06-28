from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.database import get_db, init_db
from app.models import NewRequest, RequestsList, RequestData, DataCreated, UpdateStatus, ValidationError, ReqStatusEnum, ReqModelEnum, ReqSortEnum, QueryFilters
import math

app = FastAPI()

init_db()

def apply_filters(status: ReqStatusEnum | None = None, priority: ReqModelEnum | None = None, sort: ReqSortEnum | None = None, query: str | None = None, page: int = 0) -> QueryFilters:
    where_query: list[str] = []
    where_params: list[str] = []
    if (status):
        where_query.append("status = ?")
        where_params.append(status)
    if (priority):
        where_query.append("priority = ?")
        where_params.append(priority)
    if (query):
        where_query.append("(title LIKE ? OR description LIKE ?)")
        where_params.extend([f"%{query}%", f"%{query}%"])
    
    where_req = ""
    if where_query:
        where_req = "WHERE " + " AND ".join(where_query)
    
    sort_fields = {
        "createdAtAsc":  ["created_at", "ASC"],
        "createdAtDesc":  ["created_at", "DESC"],
        "priorityAsc": ["priority", "ASC"],
        "priorityDesc": ["priority", "DESC"]
    }

    order_by =  sort_fields['createdAtAsc'] if sort else ["created_at", "ASC"]
    return {
        "order_by": order_by[0],
        "order_dir": order_by[1],
        "where_req": where_req,
        "where_params": where_params
    }


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    errorData: ValidationError = {"type": "Validation errors","errors": []}
    for error in exc.errors():
        errorData['errors'].append({
            "location": " > ".join(error['loc']),
            "message": error['msg']
        })
    return JSONResponse(content=errorData, status_code=400)

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
def get_all_items(status: ReqStatusEnum | None = None, priority: ReqModelEnum | None = None, sort: ReqSortEnum | None = None, query: str | None = None, page: int = 0) -> RequestsList:
    with get_db() as db:
        filters = apply_filters(status, priority, sort, query, page)
        cursor = db.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM test {filters["where_req"]}", (filters["where_params"]))
        pages = cursor.fetchone()[0]
        offset = (page - 1) * 10
        print('🚀 ~ get_all_items ~ f"SELECT * FROM test {filters["where_req"]} ORDER BY {filters["order_by"]} {filters["order_dir"]} LIMIT ? OFFSET ?":', f"SELECT * FROM test {filters["where_req"]} ORDER BY {filters["order_by"]} {filters["order_dir"]} LIMIT ? OFFSET ?")
        cursor.execute(f"SELECT * FROM test {filters["where_req"]} ORDER BY {filters["order_by"]} {filters["order_dir"]} LIMIT ? OFFSET ?", filters["where_params"] + [10, offset])
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
    
@app.delete('/requests/{request_id}')
def delete_request(request_id: int):
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT id, status FROM test WHERE id = ?", (request_id,))
        row = cursor.fetchone()

        if row is None:
            raise HTTPException(404, detail="User not found")
        if (row["status"] == "done"):
            raise HTTPException(400, detail="Cannot delete request when it has status = done")
        cursor.execute("DELETE FROM test WHERE ?", (request_id,))
        return 'success'