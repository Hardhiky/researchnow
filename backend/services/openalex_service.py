"""
OpenAlex API Service
Handles fetching paper metadata, abstracts, and topics from OpenAlex
OpenAlex is a free, open catalog of scholarly papers with excellent API and high limits.
- 100,000 requests per day per email
- 10 requests per second
- 200M+ works with abstracts
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


class OpenAlexService:
    """Service for interacting with OpenAlex API (200M+ papers with abstracts)"""

    BASE_URL = "https://api.openalex.org"

    def __init__(self):
        self.email = settings.CROSSREF_EMAIL  # Required for polite pool
        self.rate_limit = 10  # 10 requests per second
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
        per_page: int = 100,
        page: int = 1,
        filter_params: Optional[Dict] = None,
        sort: str = "relevance_score:desc",
    ) -> List[Dict]:
        """
        Search papers on OpenAlex

        Args:
            query: Search query
            per_page: Results per page (max 200)
            page: Page number
            filter_params: Filters (e.g., {"cited_by_count": ">50"})
            sort: Sort parameter

        Returns:
            List of paper dictionaries
        """
        if not self.session:
            await self.__aenter__()

        params = {
            "per-page": min(per_page, 200),
            "page": page,
            "mailto": self.email,
        }

        # Only add search parameter if query is not wildcard
        if query and query != "*":
            params["search"] = query

        # Add filters
        if filter_params:
            filter_str = ",".join([f"{k}:{v}" for k, v in filter_params.items()])
            params["filter"] = filter_str
            logger.info(f"OpenAlex filters: {filter_str}")

        # Add sort
        if sort:
            params["sort"] = sort

        url = f"{self.BASE_URL}/works"

        await self._rate_limit_wait()

        try:
            logger.info(f"OpenAlex request URL: {url}")
            logger.info(f"OpenAlex request params: {params}")
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(
                        f"OpenAlex API error: {response.status} - {error_text[:200]}"
                    )
                    return []

                data = await response.json()
                logger.info(f"OpenAlex response meta: {data.get('meta', {})}")
                results = data.get("results", [])
                logger.info(f"OpenAlex returned {len(results)} raw results")

                parsed_papers = []
                for item in results:
                    parsed = self._parse_paper(item)
                    if parsed:  # Only add if parsing succeeded
                        parsed_papers.append(parsed)
                    else:
                        logger.warning(f"Failed to parse a paper result")

                logger.info(f"Successfully parsed {len(parsed_papers)} papers")
                return parsed_papers

        except Exception as e:
            logger.error(f"Error fetching from OpenAlex: {e}")
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

        url = f"{self.BASE_URL}/works/doi:{quote(doi, safe='')}"
        params = {"mailto": self.email}

        await self._rate_limit_wait()

        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 404:
                    logger.warning(f"DOI not found in OpenAlex: {doi}")
                    return None

                if response.status != 200:
                    logger.error(f"OpenAlex API error: {response.status}")
                    return None

                data = await response.json()
                return self._parse_paper(data)

        except Exception as e:
            logger.error(f"Error fetching DOI {doi} from OpenAlex: {e}")
            return None

    async def get_highly_cited_papers(
        self,
        min_citations: int = 50,
        per_page: int = 100,
        year_from: Optional[int] = None,
        concept: Optional[str] = None,
    ) -> List[Dict]:
        """
        Get highly cited papers

        Args:
            min_citations: Minimum citation count
            per_page: Results per page
            year_from: Filter from year
            concept: Filter by concept/topic

        Returns:
            List of highly cited papers
        """
        filter_params = {"cited_by_count": f">{min_citations}"}

        if year_from:
            filter_params["publication_year"] = f">{year_from}"

        if concept:
            # Don't use concept filter as it's too restrictive
            pass

        logger.info(
            f"Fetching highly cited papers with min_citations={min_citations}, year_from={year_from}"
        )
        results = await self.search_papers(
            query="*",
            per_page=per_page,
            filter_params=filter_params,
            sort="cited_by_count:desc",
        )
        logger.info(f"Found {len(results)} highly cited papers")
        return results

    async def get_papers_by_topic(
        self, topic: str, per_page: int = 100, min_citations: int = 0
    ) -> List[Dict]:
        """
        Get papers by topic/concept

        Args:
            topic: Topic or concept name
            per_page: Results per page
            min_citations: Minimum citation count filter

        Returns:
            List of papers
        """
        filter_params = {"concepts.display_name": topic}

        if min_citations > 0:
            filter_params["cited_by_count"] = f">{min_citations}"

        return await self.search_papers(
            query="*", per_page=per_page, filter_params=filter_params
        )

    async def get_recent_papers(
        self, days: int = 30, per_page: int = 100, min_citations: int = 0
    ) -> List[Dict]:
        """
        Get recently published papers

        Args:
            days: Number of days back
            per_page: Results per page
            min_citations: Minimum citation count

        Returns:
            List of recent papers
        """
        from datetime import datetime, timedelta

        date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        filter_params = {"from_publication_date": date_from}

        if min_citations > 0:
            filter_params["cited_by_count"] = f">{min_citations}"

        return await self.search_papers(
            query="*",
            per_page=per_page,
            filter_params=filter_params,
            sort="publication_date:desc",
        )

    async def get_papers_by_institution(
        self, institution: str, per_page: int = 100
    ) -> List[Dict]:
        """
        Get papers by institution

        Args:
            institution: Institution name
            per_page: Results per page

        Returns:
            List of papers
        """
        filter_params = {"institutions.display_name": institution}

        return await self.search_papers(
            query="*", per_page=per_page, filter_params=filter_params
        )

    async def enrich_with_abstract(self, doi: str) -> Optional[Dict]:
        """
        Get abstract for a paper by DOI

        Args:
            doi: DOI identifier

        Returns:
            Paper with abstract or None
        """
        paper = await self.get_paper_by_doi(doi)
        if paper and paper.get("abstract"):
            return paper
        return None

    def _parse_paper(self, data: Dict) -> Dict:
        """
        Parse paper data from OpenAlex API

        Args:
            data: Raw API response

        Returns:
            Standardized paper dictionary
        """
        if not data:
            return {}

        try:
            # Extract IDs
            openalex_id = data.get("id", "").replace("https://openalex.org/", "")
            doi = (
                data.get("doi", "").replace("https://doi.org/", "")
                if data.get("doi")
                else None
            )

            # Extract title
            title = data.get("title")

            if not title:
                logger.warning(f"Paper missing title, skipping: {openalex_id}")
                return {}

            # Extract abstract (inverted index format)
            abstract = None
            abstract_inverted = data.get("abstract_inverted_index")
            if abstract_inverted:
                try:
                    # Reconstruct abstract from inverted index
                    words = [""] * 10000  # Pre-allocate
                    max_pos = 0
                    for word, positions in abstract_inverted.items():
                        for pos in positions:
                            if pos < len(words):
                                words[pos] = word
                                max_pos = max(max_pos, pos)
                    abstract = " ".join(words[: max_pos + 1]).strip()
                except Exception as e:
                    logger.warning(f"Failed to parse abstract for {title[:50]}: {e}")
                    abstract = None

            # Extract authors
            authors = []
            try:
                for authorship in data.get("authorships", []):
                    author_data = authorship.get("author", {})
                    display_name = author_data.get("display_name")
                    if display_name:
                        authors.append(display_name)
            except Exception as e:
                logger.warning(f"Failed to parse authors: {e}")

            # Extract publication date
            pub_date = data.get("publication_date")
            publication_year = data.get("publication_year")

            # Extract venue/journal
            primary_location = data.get("primary_location", {}) or {}
            source = primary_location.get("source", {}) or {}
            journal = source.get("display_name")
            publisher = None
            is_open_access = primary_location.get("is_oa", False)

            # Extract PDF URL
            pdf_url = None
            best_oa_location = data.get("best_oa_location")
            if best_oa_location:
                pdf_url = best_oa_location.get("pdf_url")

            # Extract citation count
            citation_count = data.get("cited_by_count", 0)

            # Extract referenced works count
            referenced_works = data.get("referenced_works", [])
            reference_count = len(referenced_works) if referenced_works else 0

            # Extract topics/concepts
            topics = []
            try:
                concepts = data.get("concepts", [])
                for concept in concepts[:10]:  # Top 10 concepts
                    display_name = concept.get("display_name")
                    score = concept.get("score", 0)
                    if (
                        display_name and score > 0.3
                    ):  # Only concepts with >30% relevance
                        topics.append(display_name)
            except Exception as e:
                logger.warning(f"Failed to parse concepts: {e}")

            # Extract fields
            field = None
            domain = None
            try:
                primary_topic = data.get("primary_topic", {})
                if primary_topic:
                    field = (
                        primary_topic.get("field", {}).get("display_name")
                        if primary_topic.get("field")
                        else None
                    )
                    domain = (
                        primary_topic.get("domain", {}).get("display_name")
                        if primary_topic.get("domain")
                        else None
                    )
            except Exception as e:
                logger.warning(f"Failed to parse fields: {e}")

            # Extract language
            language = data.get("language")

            # Extract type
            paper_type = data.get("type")

            # Extract URLs
            landing_page_url = primary_location.get("landing_page_url")

            paper = {
                "openalex_id": openalex_id,
                "doi": doi,
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "publication_date": pub_date,
                "publication_year": publication_year,
                "journal": journal,
                "publisher": publisher,
                "citation_count": citation_count,
                "reference_count": reference_count,
                "topics": topics,
                "field": field,
                "domain": domain,
                "language": language,
                "is_open_access": is_open_access,
                "pdf_url": pdf_url,
                "html_url": landing_page_url,
                "paper_type": paper_type,
                "source": "openalex",
            }

            logger.debug(f"Successfully parsed paper: {title[:50]}...")
            return paper

        except Exception as e:
            logger.error(f"Failed to parse paper data: {e}", exc_info=True)
            return {}


# Convenience functions
async def fetch_paper_by_doi_openalex(doi: str) -> Optional[Dict]:
    """
    Fetch paper by DOI from OpenAlex

    Args:
        doi: DOI identifier

    Returns:
        Paper dictionary with abstract or None
    """
    async with OpenAlexService() as service:
        return await service.get_paper_by_doi(doi)


async def search_openalex(query: str, per_page: int = 100) -> List[Dict]:
    """
    Search OpenAlex

    Args:
        query: Search query
        per_page: Results per page

    Returns:
        List of papers with abstracts
    """
    async with OpenAlexService() as service:
        return await service.search_papers(query=query, per_page=per_page)


async def fetch_highly_cited_openalex(
    min_citations: int = 50, per_page: int = 100, year_from: Optional[int] = None
) -> List[Dict]:
    """
    Fetch highly cited papers from OpenAlex

    Args:
        min_citations: Minimum citation count
        per_page: Results per page
        year_from: Filter from year

    Returns:
        List of highly cited papers with abstracts
    """
    async with OpenAlexService() as service:
        return await service.get_highly_cited_papers(
            min_citations=min_citations, per_page=per_page, year_from=year_from
        )


async def enrich_paper_with_abstract(doi: str) -> Optional[Dict]:
    """
    Enrich a paper with abstract from OpenAlex

    Args:
        doi: DOI of paper

    Returns:
        Paper with abstract or None
    """
    async with OpenAlexService() as service:
        return await service.enrich_with_abstract(doi)
