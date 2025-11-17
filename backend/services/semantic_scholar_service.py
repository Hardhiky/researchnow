"""
Semantic Scholar API Service
Handles fetching paper metadata, abstracts, and citations from Semantic Scholar
"""

import asyncio
import logging
from typing import Dict, List, Optional
from urllib.parse import quote

import aiohttp
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SemanticScholarService:
    """Service for interacting with Semantic Scholar API"""

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    # Fields to request from API
    PAPER_FIELDS = [
        "paperId",
        "externalIds",
        "url",
        "title",
        "abstract",
        "venue",
        "year",
        "referenceCount",
        "citationCount",
        "influentialCitationCount",
        "isOpenAccess",
        "openAccessPdf",
        "fieldsOfStudy",
        "s2FieldsOfStudy",
        "publicationTypes",
        "publicationDate",
        "journal",
        "authors",
        "citations",
        "references",
        "embedding",
        "tldr",
    ]

    def __init__(self):
        self.api_key = settings.SEMANTIC_SCHOLAR_API_KEY
        self.rate_limit = settings.SEMANTIC_SCHOLAR_RATE_LIMIT
        self.last_request_time = 0
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        headers = {}
        if self.api_key:
            headers["x-api-key"] = self.api_key

        self.session = aiohttp.ClientSession(headers=headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def _rate_limit_wait(self):
        """Enforce rate limiting"""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.rate_limit

        if time_since_last < min_interval:
            await asyncio.sleep(min_interval - time_since_last)

        self.last_request_time = asyncio.get_event_loop().time()

    async def get_paper_by_id(
        self, paper_id: str, fields: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        Get paper by Semantic Scholar ID

        Args:
            paper_id: S2 paper ID, DOI, arXiv ID, etc.
            fields: List of fields to retrieve

        Returns:
            Paper dictionary or None
        """
        if not self.session:
            await self.__aenter__()

        if fields is None:
            fields = self.PAPER_FIELDS

        fields_str = ",".join(fields)
        url = f"{self.BASE_URL}/paper/{paper_id}?fields={fields_str}"

        await self._rate_limit_wait()

        try:
            async with self.session.get(url) as response:
                if response.status == 404:
                    logger.warning(f"Paper not found: {paper_id}")
                    return None

                if response.status != 200:
                    logger.error(f"S2 API error: {response.status}")
                    return None

                data = await response.json()
                return self._parse_paper(data)

        except Exception as e:
            logger.error(f"Error fetching from Semantic Scholar: {e}")
            return None

    async def search_papers(
        self,
        query: str,
        limit: int = 100,
        offset: int = 0,
        fields: Optional[List[str]] = None,
        year: Optional[str] = None,
        publication_types: Optional[List[str]] = None,
        open_access_pdf: Optional[bool] = None,
        venue: Optional[str] = None,
        fields_of_study: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Search papers on Semantic Scholar

        Args:
            query: Search query
            limit: Maximum results (max 100 per request)
            offset: Offset for pagination
            fields: Fields to retrieve
            year: Year or year range (e.g., "2020", "2020-2023")
            publication_types: Filter by publication type
            open_access_pdf: Filter by open access availability
            venue: Filter by venue
            fields_of_study: Filter by fields of study

        Returns:
            List of paper dictionaries
        """
        if not self.session:
            await self.__aenter__()

        if fields is None:
            fields = self.PAPER_FIELDS

        fields_str = ",".join(fields)
        url = f"{self.BASE_URL}/paper/search?query={quote(query)}&offset={offset}&limit={limit}&fields={fields_str}"

        # Add filters
        if year:
            url += f"&year={year}"
        if publication_types:
            url += f"&publicationTypes={','.join(publication_types)}"
        if open_access_pdf is not None:
            url += f"&openAccessPdf={'true' if open_access_pdf else 'false'}"
        if venue:
            url += f"&venue={quote(venue)}"
        if fields_of_study:
            url += f"&fieldsOfStudy={','.join(fields_of_study)}"

        await self._rate_limit_wait()

        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"S2 search error: {response.status}")
                    return []

                data = await response.json()
                papers = data.get("data", [])
                return [self._parse_paper(p) for p in papers if p]

        except Exception as e:
            logger.error(f"Error searching Semantic Scholar: {e}")
            return []

    async def get_paper_citations(
        self, paper_id: str, limit: int = 100, offset: int = 0
    ) -> List[Dict]:
        """
        Get papers that cite the given paper

        Args:
            paper_id: S2 paper ID
            limit: Maximum results
            offset: Offset for pagination

        Returns:
            List of citing paper dictionaries
        """
        if not self.session:
            await self.__aenter__()

        fields_str = ",".join(self.PAPER_FIELDS)
        url = f"{self.BASE_URL}/paper/{paper_id}/citations?limit={limit}&offset={offset}&fields={fields_str}"

        await self._rate_limit_wait()

        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"S2 citations error: {response.status}")
                    return []

                data = await response.json()
                citations = data.get("data", [])
                return [
                    self._parse_paper(c.get("citingPaper"))
                    for c in citations
                    if c.get("citingPaper")
                ]

        except Exception as e:
            logger.error(f"Error fetching citations: {e}")
            return []

    async def get_paper_references(
        self, paper_id: str, limit: int = 100, offset: int = 0
    ) -> List[Dict]:
        """
        Get papers referenced by the given paper

        Args:
            paper_id: S2 paper ID
            limit: Maximum results
            offset: Offset for pagination

        Returns:
            List of referenced paper dictionaries
        """
        if not self.session:
            await self.__aenter__()

        fields_str = ",".join(self.PAPER_FIELDS)
        url = f"{self.BASE_URL}/paper/{paper_id}/references?limit={limit}&offset={offset}&fields={fields_str}"

        await self._rate_limit_wait()

        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"S2 references error: {response.status}")
                    return []

                data = await response.json()
                references = data.get("data", [])
                return [
                    self._parse_paper(r.get("citedPaper"))
                    for r in references
                    if r.get("citedPaper")
                ]

        except Exception as e:
            logger.error(f"Error fetching references: {e}")
            return []

    async def get_author(self, author_id: str) -> Optional[Dict]:
        """
        Get author information

        Args:
            author_id: S2 author ID

        Returns:
            Author dictionary or None
        """
        if not self.session:
            await self.__aenter__()

        fields = "authorId,externalIds,name,affiliations,homepage,paperCount,citationCount,hIndex,papers"
        url = f"{self.BASE_URL}/author/{author_id}?fields={fields}"

        await self._rate_limit_wait()

        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"S2 author error: {response.status}")
                    return None

                data = await response.json()
                return self._parse_author(data)

        except Exception as e:
            logger.error(f"Error fetching author: {e}")
            return None

    async def get_author_papers(
        self, author_id: str, limit: int = 100, offset: int = 0
    ) -> List[Dict]:
        """
        Get papers by author

        Args:
            author_id: S2 author ID
            limit: Maximum results
            offset: Offset for pagination

        Returns:
            List of paper dictionaries
        """
        if not self.session:
            await self.__aenter__()

        fields_str = ",".join(self.PAPER_FIELDS)
        url = f"{self.BASE_URL}/author/{author_id}/papers?limit={limit}&offset={offset}&fields={fields_str}"

        await self._rate_limit_wait()

        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"S2 author papers error: {response.status}")
                    return []

                data = await response.json()
                papers = data.get("data", [])
                return [self._parse_paper(p) for p in papers if p]

        except Exception as e:
            logger.error(f"Error fetching author papers: {e}")
            return []

    async def get_recommendations(self, paper_id: str, limit: int = 100) -> List[Dict]:
        """
        Get recommended papers based on a paper

        Args:
            paper_id: S2 paper ID
            limit: Maximum results

        Returns:
            List of recommended paper dictionaries
        """
        if not self.session:
            await self.__aenter__()

        fields_str = ",".join(self.PAPER_FIELDS)
        url = f"{self.BASE_URL}/paper/{paper_id}/recommendations?limit={limit}&fields={fields_str}"

        await self._rate_limit_wait()

        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"S2 recommendations error: {response.status}")
                    return []

                data = await response.json()
                recommendations = data.get("recommendedPapers", [])
                return [self._parse_paper(p) for p in recommendations if p]

        except Exception as e:
            logger.error(f"Error fetching recommendations: {e}")
            return []

    def _parse_paper(self, data: Dict) -> Dict:
        """
        Parse paper data from API response

        Args:
            data: Raw API response data

        Returns:
            Standardized paper dictionary
        """
        if not data:
            return {}

        # Extract external IDs
        external_ids = data.get("externalIds", {}) or {}

        # Parse authors
        authors = []
        author_ids = []
        for author in data.get("authors", []):
            if author:
                authors.append(author.get("name"))
                if author.get("authorId"):
                    author_ids.append(author.get("authorId"))

        # Parse fields of study
        fields_of_study = []
        s2_fields = data.get("s2FieldsOfStudy", [])
        if s2_fields:
            fields_of_study = [f.get("category") for f in s2_fields if f]

        # Fallback to legacy fieldsOfStudy
        if not fields_of_study:
            fields_of_study = data.get("fieldsOfStudy", [])

        # Parse journal info
        journal_info = data.get("journal", {}) or {}

        # Parse open access PDF
        open_access_pdf = data.get("openAccessPdf", {})
        pdf_url = None
        if open_access_pdf:
            pdf_url = open_access_pdf.get("url")

        # Parse TLDR (auto-generated summary)
        tldr = data.get("tldr", {})
        tldr_text = tldr.get("text") if tldr else None

        paper = {
            "s2_paper_id": data.get("paperId"),
            "doi": external_ids.get("DOI"),
            "arxiv_id": external_ids.get("ArXiv"),
            "pubmed_id": external_ids.get("PubMed"),
            "title": data.get("title"),
            "abstract": data.get("abstract"),
            "tldr": tldr_text,
            "authors": authors,
            "author_ids": author_ids,
            "publication_date": data.get("publicationDate"),
            "publication_year": data.get("year"),
            "venue": data.get("venue"),
            "journal": journal_info.get("name"),
            "journal_volume": journal_info.get("volume"),
            "journal_pages": journal_info.get("pages"),
            "publication_types": data.get("publicationTypes", []),
            "fields_of_study": fields_of_study,
            "citation_count": data.get("citationCount", 0),
            "reference_count": data.get("referenceCount", 0),
            "influential_citation_count": data.get("influentialCitationCount", 0),
            "is_open_access": data.get("isOpenAccess", False),
            "pdf_url": pdf_url,
            "html_url": data.get("url"),
            "source": "semantic_scholar",
            "external_ids": external_ids,
            "embedding": data.get("embedding"),
        }

        return paper

    def _parse_author(self, data: Dict) -> Dict:
        """
        Parse author data from API response

        Args:
            data: Raw API response data

        Returns:
            Standardized author dictionary
        """
        if not data:
            return {}

        external_ids = data.get("externalIds", {}) or {}
        affiliations = data.get("affiliations", [])

        author = {
            "s2_author_id": data.get("authorId"),
            "name": data.get("name"),
            "orcid": external_ids.get("ORCID"),
            "affiliations": affiliations,
            "current_affiliation": affiliations[0] if affiliations else None,
            "homepage": data.get("homepage"),
            "paper_count": data.get("paperCount", 0),
            "citation_count": data.get("citationCount", 0),
            "h_index": data.get("hIndex", 0),
        }

        return author


# Convenience functions
async def fetch_paper_by_doi(doi: str) -> Optional[Dict]:
    """
    Fetch paper by DOI

    Args:
        doi: Paper DOI

    Returns:
        Paper dictionary or None
    """
    async with SemanticScholarService() as service:
        return await service.get_paper_by_id(f"DOI:{doi}")


async def fetch_paper_by_arxiv(arxiv_id: str) -> Optional[Dict]:
    """
    Fetch paper by arXiv ID

    Args:
        arxiv_id: arXiv identifier

    Returns:
        Paper dictionary or None
    """
    async with SemanticScholarService() as service:
        return await service.get_paper_by_id(f"ARXIV:{arxiv_id}")


async def search_semantic_scholar(query: str, limit: int = 100) -> List[Dict]:
    """
    Search Semantic Scholar

    Args:
        query: Search query
        limit: Maximum results

    Returns:
        List of paper dictionaries
    """
    async with SemanticScholarService() as service:
        return await service.search_papers(query=query, limit=limit)
