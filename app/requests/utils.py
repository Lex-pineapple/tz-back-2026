from app.requests.schemas import QueryFilters, ReqModelEnum, ReqSortEnum, ReqStatusEnum


def apply_filters(
    status: ReqStatusEnum | None = None,
    priority: ReqModelEnum | None = None,
    sort: ReqSortEnum | None = None,
    query: str | None = None,
    page: int = 0,
) -> QueryFilters:
    where_query: list[str] = []
    where_params: list[str] = []
    if status:
        where_query.append("status = ?")
        where_params.append(status)
    if priority:
        where_query.append("priority = ?")
        where_params.append(priority)
    if query:
        where_query.append("(title LIKE ? OR description LIKE ?)")
        where_params.extend([f"%{query}%", f"%{query}%"])

    where_req = ""
    if where_query:
        where_req = "WHERE " + " AND ".join(where_query)

    sort_fields = {
        "createdAtAsc": ["created_at", "ASC"],
        "createdAtDesc": ["created_at", "DESC"],
        "priorityAsc": ["priority", "ASC"],
        "priorityDesc": ["priority", "DESC"],
    }

    order_by = sort_fields["createdAtAsc"] if sort else ["created_at", "ASC"]
    return {
        "order_by": order_by[0],
        "order_dir": order_by[1],
        "where_req": where_req,
        "where_params": where_params,
    }
