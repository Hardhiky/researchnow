from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_sources():
    return {
        "sources": [
            {"id": "arxiv", "name": "arXiv", "status": "active"},
            {"id": "pubmed", "name": "PubMed", "status": "active"},
            {"id": "semantic_scholar", "name": "Semantic Scholar", "status": "active"},
        ]
    }
