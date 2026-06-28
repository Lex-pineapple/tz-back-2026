import math

from fastapi import APIRouter
from fastapi import HTTPException
from app.requests.schemas import NewRequest, RequestsList, RequestData, DataCreated, UpdateStatus, ReqStatusEnum, ReqModelEnum, ReqSortEnum
from app.core.database import get_db
from app.requests.utils import apply_filters

router = APIRouter(
  prefix="/requests",
  tags=["requests"],
  responses={404: {"description": "Not Found"}}
)

@router.post("/")
async def create_request(item: NewRequest) -> DataCreated:
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("INSERT INTO test (title, description, status, priority) VALUES (?, ?, ?, ?)", (item.title, item.description, "new", item.priority))
        db.commit()
        item_id = cursor.lastrowid
    if not item_id:
        raise HTTPException(404, detail="Error")
    return DataCreated(id=item_id, message="Request created")

@router.get('/')
async def get_all_items(status: ReqStatusEnum | None = None, priority: ReqModelEnum | None = None, sort: ReqSortEnum | None = None, query: str | None = None, page: int = 0) -> RequestsList:
    with get_db() as db:
        filters = apply_filters(status, priority, sort, query, page)
        cursor = db.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM test {filters["where_req"]}", (filters["where_params"]))
        pages = cursor.fetchone()[0]
        offset = (page - 1) * 10
        cursor.execute(f"SELECT * FROM test {filters["where_req"]} ORDER BY {filters["order_by"]} {filters["order_dir"]} LIMIT ? OFFSET ?", filters["where_params"] + [10, offset])
        rows = cursor.fetchall()
    if not rows:
        return {"pages": 0, "items": []}
    return {
        "pages": math.ceil(pages / 10),
        "items": [RequestData(**dict(row)) for row in rows]
    }
    
@router.patch('/{request_id}')
async def update_item(request_id: int, body: UpdateStatus):
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
    
@router.delete('/{request_id}')
async def delete_request(request_id: int):
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