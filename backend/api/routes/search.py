from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/")
async def search_papers(q: str = Query(..., description="Search query")):
    return {"results": [], "total": 0, "query": q}
