"""
Crossref API Service
Handles fetching paper metadata from Crossref (200M+ papers, no API key required)
Crossref is the world's largest DOI registry with excellent API and no rate limits with polite pool.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import quote

import aiohttp
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CrossrefService:
    """Service for interacting with Crossref API (200M+ papers)"""

    BASE_URL = "https://api.crossref.org"

    def __init__(self):
        self.email = settings.CROSSREF_EMAIL  # For polite pool access
        self.rate_limit = settings.CROSSREF_RATE_LIMIT  # 50 req/sec for polite pool
        self.last_request_time = 0
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        headers = {
            "User-Agent": f"ResearchNow/1.0 (mailto:{self.email})",
        }
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

    async def search_papers(
        self,
        query: str,
        rows: int = 100,
        offset: int = 0,
        filter_params: Optional[Dict] = None,
        sort: str = "relevance",
        order: str = "desc",
    ) -> List[Dict]:
        """
        Search papers on Crossref

        Args:
            query: Search query
            rows: Number of results (max 1000)
            offset: Offset for pagination
            filter_params: Filters (e.g., {"from-pub-date": "2020-01-01"})
            sort: Sort field (relevance, published, indexed, etc.)
            order: Sort order (asc, desc)

        Returns:
            List of paper dictionaries
        """
        if not self.session:
            await self.__aenter__()

        params = {
            "query": query,
            "rows": min(rows, 1000),  # Max 1000 per request
            "offset": offset,
            "sort": sort,
            "order": order,
        }

        # Add filters if provided
        if filter_params:
            for key, value in filter_params.items():
                params[f"filter"] = f"{key}:{value}"

        url = f"{self.BASE_URL}/works"

        await self._rate_limit_wait()

        try:
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Crossref API error: {response.status}")
                    return []

                data = await response.json()
                items = data.get("message", {}).get("items", [])
                return [self._parse_paper(item) for item in items]

        except Exception as e:
            logger.error(f"Error fetching from Crossref: {e}")
            return []

    async def get_paper_by_doi(self, doi: str) -> Optional[Dict]:
        """
        Get paper by DOI

        Args:
            doi: DOI identifier

        Returns:
            Paper dictionary or None
        """
        if not self.session:
            await self.__aenter__()

        url = f"{self.BASE_URL}/works/{quote(doi, safe='')}"

        await self._rate_limit_wait()

        try:
            async with self.session.get(url) as response:
                if response.status == 404:
                    logger.warning(f"DOI not found: {doi}")
                    return None

                if response.status != 200:
                    logger.error(f"Crossref API error: {response.status}")
                    return None

                data = await response.json()
                return self._parse_paper(data.get("message", {}))

        except Exception as e:
            logger.error(f"Error fetching DOI {doi}: {e}")
            return None

    async def get_papers_by_citation_count(
        self,
        min_citations: int = 50,
        rows: int = 100,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
    ) -> List[Dict]:
        """
        Get highly cited papers

        Args:
            min_citations: Minimum citation count
            rows: Number of results
            year_from: Start year filter
            year_to: End year filter

        Returns:
            List of highly cited papers
        """
        filter_params = {}

        if year_from:
            filter_params["from-pub-date"] = f"{year_from}-01-01"
        if year_to:
            filter_params["until-pub-date"] = f"{year_to}-12-31"

        # Crossref doesn't have citation count filter directly, but we can sort by cited-by-count
        papers = await self.search_papers(
            query="*",  # All papers
            rows=rows * 3,  # Get more to filter
            filter_params=filter_params,
            sort="is-referenced-by-count",
            order="desc",
        )

        # Filter by citation count
        return [p for p in papers if p.get("citation_count", 0) >= min_citations][:rows]

    async def get_papers_by_field(
        self, field: str, rows: int = 100, offset: int = 0
    ) -> List[Dict]:
        """
        Get papers by subject/field

        Args:
            field: Subject area
            rows: Number of results
            offset: Pagination offset

        Returns:
            List of papers
        """
        return await self.search_papers(query=field, rows=rows, offset=offset)

    async def get_recent_papers(self, days: int = 30, rows: int = 100) -> List[Dict]:
        """
        Get recently published papers

        Args:
            days: Number of days back
            rows: Number of results

        Returns:
            List of recent papers
        """
        from datetime import datetime, timedelta

        date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        filter_params = {"from-pub-date": date_from}

        return await self.search_papers(
            query="*",
            rows=rows,
            filter_params=filter_params,
            sort="published",
            order="desc",
        )

    async def get_papers_by_funder(
        self, funder_name: str, rows: int = 100
    ) -> List[Dict]:
        """
        Get papers by funding organization

        Args:
            funder_name: Name of funding organization
            rows: Number of results

        Returns:
            List of papers
        """
        filter_params = {"funder": funder_name}

        return await self.search_papers(
            query="*", rows=rows, filter_params=filter_params
        )

    def _parse_paper(self, data: Dict) -> Dict:
        """
        Parse paper data from Crossref API

        Args:
            data: Raw API response

        Returns:
            Standardized paper dictionary
        """
        if not data:
            return {}

        # Extract DOI
        doi = data.get("DOI")

        # Extract title
        title_list = data.get("title", [])
        title = title_list[0] if title_list else None

        # Extract authors
        authors = []
        for author in data.get("author", []):
            given = author.get("given", "")
            family = author.get("family", "")
            name = f"{given} {family}".strip()
            if name:
                authors.append(name)

        # Extract abstract (if available)
        abstract = data.get("abstract")

        # Extract publication date
        pub_date = data.get("published-print") or data.get("published-online")
        publication_date = None
        publication_year = None

        if pub_date:
            date_parts = pub_date.get("date-parts", [[]])[0]
            if date_parts:
                try:
                    if len(date_parts) >= 1:
                        publication_year = date_parts[0]
                    if len(date_parts) >= 3:
                        publication_date = datetime(
                            date_parts[0], date_parts[1], date_parts[2]
                        ).strftime("%Y-%m-%d")
                    elif len(date_parts) >= 2:
                        publication_date = datetime(
                            date_parts[0], date_parts[1], 1
                        ).strftime("%Y-%m-%d")
                    elif len(date_parts) >= 1:
                        publication_date = f"{date_parts[0]}-01-01"
                except:
                    pass

        # Extract journal/venue
        container_title = data.get("container-title", [])
        journal = container_title[0] if container_title else None
        publisher = data.get("publisher")

        # Extract citation count
        citation_count = data.get("is-referenced-by-count", 0)

        # Extract reference count
        reference_count = data.get("references-count", 0)

        # Extract subjects/fields
        subjects = data.get("subject", [])

        # Extract ISSN
        issn = data.get("ISSN", [])

        # Extract volume, issue, page
        volume = data.get("volume")
        issue = data.get("issue")
        page = data.get("page")

        # Extract URLs
        url = data.get("URL")

        # Check if open access
        license_info = data.get("license", [])
        is_open_access = len(license_info) > 0

        # Extract PDF URL if available
        pdf_url = None
        for link in data.get("link", []):
            if link.get("content-type") == "application/pdf":
                pdf_url = link.get("URL")
                break

        # Extract type
        paper_type = data.get("type")

        paper = {
            "doi": doi,
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "publication_date": publication_date,
            "publication_year": publication_year,
            "journal": journal,
            "publisher": publisher,
            "volume": volume,
            "issue": issue,
            "page": page,
            "citation_count": citation_count,
            "reference_count": reference_count,
            "subjects": subjects,
            "issn": issn,
            "is_open_access": is_open_access,
            "pdf_url": pdf_url,
            "html_url": url,
            "paper_type": paper_type,
            "source": "crossref",
        }

        return paper


# Convenience functions
async def fetch_paper_by_doi(doi: str) -> Optional[Dict]:
    """
    Fetch paper by DOI from Crossref

    Args:
        doi: DOI identifier

    Returns:
        Paper dictionary or None
    """
    async with CrossrefService() as service:
        return await service.get_paper_by_doi(doi)


async def search_crossref(query: str, rows: int = 100) -> List[Dict]:
    """
    Search Crossref

    Args:
        query: Search query
        rows: Number of results

    Returns:
        List of papers
    """
    async with CrossrefService() as service:
        return await service.search_papers(query=query, rows=rows)


async def fetch_highly_cited_papers(
    min_citations: int = 50, rows: int = 100, year_from: Optional[int] = None
) -> List[Dict]:
    """
    Fetch highly cited papers from Crossref

    Args:
        min_citations: Minimum citation count
        rows: Number of results
        year_from: Filter from year

    Returns:
        List of highly cited papers
    """
    async with CrossrefService() as service:
        return await service.get_papers_by_citation_count(
            min_citations=min_citations, rows=rows, year_from=year_from
        )
