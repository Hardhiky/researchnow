"""
arXiv Paper Collection Service
Handles fetching papers from arXiv API and downloading PDFs
"""

import asyncio
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlencode

import aiohttp
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ArxivService:
    """Service for interacting with arXiv API"""

    BASE_URL = "http://export.arxiv.org/api/query"
    NAMESPACE = {"atom": "http://www.w3.org/2005/Atom"}

    def __init__(self):
        self.rate_limit = settings.ARXIV_RATE_LIMIT  # requests per second
        self.last_request_time = 0
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
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
        max_results: int = 100,
        start: int = 0,
        sort_by: str = "relevance",
        sort_order: str = "descending",
    ) -> List[Dict]:
        """
        Search arXiv papers

        Args:
            query: Search query (supports arXiv query syntax)
            max_results: Maximum number of results to return
            start: Starting index for pagination
            sort_by: Sort field ('relevance', 'lastUpdatedDate', 'submittedDate')
            sort_order: Sort order ('ascending', 'descending')

        Returns:
            List of paper dictionaries
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        params = {
            "search_query": query,
            "start": start,
            "max_results": max_results,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        }

        url = f"{self.BASE_URL}?{urlencode(params)}"

        await self._rate_limit_wait()

        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"arXiv API error: {response.status}")
                    return []

                xml_content = await response.text()
                return self._parse_arxiv_response(xml_content)

        except Exception as e:
            logger.error(f"Error fetching from arXiv: {e}")
            return []

    def _parse_arxiv_response(self, xml_content: str) -> List[Dict]:
        """
        Parse arXiv XML response into structured data

        Args:
            xml_content: XML response from arXiv API

        Returns:
            List of paper dictionaries
        """
        papers = []

        try:
            root = ET.fromstring(xml_content)

            for entry in root.findall("atom:entry", self.NAMESPACE):
                paper = self._parse_entry(entry)
                if paper:
                    papers.append(paper)

        except ET.ParseError as e:
            logger.error(f"Error parsing arXiv XML: {e}")

        return papers

    def _parse_entry(self, entry: ET.Element) -> Optional[Dict]:
        """
        Parse a single arXiv entry

        Args:
            entry: XML entry element

        Returns:
            Paper dictionary or None if parsing fails
        """
        try:
            # Extract arXiv ID from the id URL
            id_url = entry.find("atom:id", self.NAMESPACE).text
            arxiv_id = id_url.split("/abs/")[-1]

            # Extract title
            title = entry.find("atom:title", self.NAMESPACE).text
            title = " ".join(title.split())  # Clean up whitespace

            # Extract abstract
            summary = entry.find("atom:summary", self.NAMESPACE).text
            summary = " ".join(summary.split())  # Clean up whitespace

            # Extract authors
            authors = []
            for author in entry.findall("atom:author", self.NAMESPACE):
                name = author.find("atom:name", self.NAMESPACE)
                if name is not None:
                    authors.append(name.text)

            # Extract categories/subjects
            categories = []
            for category in entry.findall("atom:category", self.NAMESPACE):
                term = category.get("term")
                if term:
                    categories.append(term)

            # Extract dates
            published = entry.find("atom:published", self.NAMESPACE).text
            updated = entry.find("atom:updated", self.NAMESPACE).text

            # Convert to datetime
            published_date = datetime.fromisoformat(published.replace("Z", "+00:00"))
            updated_date = datetime.fromisoformat(updated.replace("Z", "+00:00"))

            # Extract links
            pdf_url = None
            html_url = None

            for link in entry.findall("atom:link", self.NAMESPACE):
                link_type = link.get("type")
                link_href = link.get("href")

                if link_type == "application/pdf":
                    pdf_url = link_href
                elif link_type == "text/html":
                    html_url = link_href

            # If pdf_url not found, construct it from arxiv_id
            if not pdf_url:
                pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

            # Extract DOI if present
            doi = None
            doi_elem = entry.find(
                "arxiv:doi", {"arxiv": "http://arxiv.org/schemas/atom"}
            )
            if doi_elem is not None:
                doi = doi_elem.text

            # Extract journal reference if present
            journal_ref = None
            journal_elem = entry.find(
                "arxiv:journal_ref", {"arxiv": "http://arxiv.org/schemas/atom"}
            )
            if journal_elem is not None:
                journal_ref = journal_elem.text

            # Extract comment if present
            comment = None
            comment_elem = entry.find(
                "arxiv:comment", {"arxiv": "http://arxiv.org/schemas/atom"}
            )
            if comment_elem is not None:
                comment = comment_elem.text

            # Extract primary category
            primary_category = entry.find(
                "arxiv:primary_category", {"arxiv": "http://arxiv.org/schemas/atom"}
            )
            primary_cat = (
                primary_category.get("term") if primary_category is not None else None
            )

            paper = {
                "arxiv_id": arxiv_id,
                "doi": doi,
                "title": title,
                "abstract": summary,
                "authors": authors,
                "categories": categories,
                "primary_category": primary_cat,
                "published_date": published_date,
                "updated_date": updated_date,
                "publication_year": published_date.year,
                "pdf_url": pdf_url,
                "html_url": html_url or f"https://arxiv.org/abs/{arxiv_id}",
                "journal_reference": journal_ref,
                "comment": comment,
                "is_open_access": True,
                "source": "arxiv",
                "has_full_text": True,
            }

            return paper

        except Exception as e:
            logger.error(f"Error parsing arXiv entry: {e}")
            return None

    async def get_paper_by_id(self, arxiv_id: str) -> Optional[Dict]:
        """
        Get a specific paper by arXiv ID

        Args:
            arxiv_id: arXiv identifier (e.g., '2301.12345' or '1234.5678v2')

        Returns:
            Paper dictionary or None
        """
        papers = await self.search_papers(query=f"id:{arxiv_id}", max_results=1)
        return papers[0] if papers else None

    async def get_papers_by_category(
        self, category: str, max_results: int = 100, start: int = 0
    ) -> List[Dict]:
        """
        Get papers by category

        Args:
            category: arXiv category (e.g., 'cs.AI', 'physics.optics')
            max_results: Maximum number of results
            start: Starting index for pagination

        Returns:
            List of paper dictionaries
        """
        query = f"cat:{category}"
        return await self.search_papers(
            query=query, max_results=max_results, start=start, sort_by="submittedDate"
        )

    async def get_recent_papers(
        self, category: Optional[str] = None, max_results: int = 100
    ) -> List[Dict]:
        """
        Get most recent papers, optionally filtered by category

        Args:
            category: Optional arXiv category filter
            max_results: Maximum number of results

        Returns:
            List of paper dictionaries
        """
        if category:
            query = f"cat:{category}"
        else:
            query = "all:*"

        return await self.search_papers(
            query=query,
            max_results=max_results,
            sort_by="submittedDate",
            sort_order="descending",
        )

    async def download_pdf(self, arxiv_id: str, output_path: str) -> bool:
        """
        Download PDF for a paper

        Args:
            arxiv_id: arXiv identifier
            output_path: Path to save the PDF

        Returns:
            True if successful, False otherwise
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

        await self._rate_limit_wait()

        try:
            async with self.session.get(pdf_url) as response:
                if response.status != 200:
                    logger.error(
                        f"Failed to download PDF for {arxiv_id}: {response.status}"
                    )
                    return False

                content = await response.read()

                # Write to file
                with open(output_path, "wb") as f:
                    f.write(content)

                logger.info(f"Downloaded PDF for {arxiv_id} to {output_path}")
                return True

        except Exception as e:
            logger.error(f"Error downloading PDF for {arxiv_id}: {e}")
            return False

    async def search_by_author(
        self, author_name: str, max_results: int = 100
    ) -> List[Dict]:
        """
        Search papers by author name

        Args:
            author_name: Author name to search for
            max_results: Maximum number of results

        Returns:
            List of paper dictionaries
        """
        query = f"au:{author_name}"
        return await self.search_papers(query=query, max_results=max_results)

    async def search_by_title(self, title: str, max_results: int = 100) -> List[Dict]:
        """
        Search papers by title

        Args:
            title: Title keywords to search for
            max_results: Maximum number of results

        Returns:
            List of paper dictionaries
        """
        query = f"ti:{title}"
        return await self.search_papers(query=query, max_results=max_results)

    async def advanced_search(
        self,
        all_words: Optional[str] = None,
        any_words: Optional[str] = None,
        title: Optional[str] = None,
        author: Optional[str] = None,
        abstract: Optional[str] = None,
        category: Optional[str] = None,
        max_results: int = 100,
    ) -> List[Dict]:
        """
        Advanced search with multiple criteria

        Args:
            all_words: All these words must appear
            any_words: Any of these words can appear
            title: Title keywords
            author: Author name
            abstract: Abstract keywords
            category: arXiv category
            max_results: Maximum number of results

        Returns:
            List of paper dictionaries
        """
        query_parts = []

        if all_words:
            query_parts.append(f"all:{all_words}")
        if any_words:
            query_parts.append(f"({' OR '.join(any_words.split())})")
        if title:
            query_parts.append(f"ti:{title}")
        if author:
            query_parts.append(f"au:{author}")
        if abstract:
            query_parts.append(f"abs:{abstract}")
        if category:
            query_parts.append(f"cat:{category}")

        if not query_parts:
            query_parts.append("all:*")

        query = " AND ".join(query_parts)

        return await self.search_papers(query=query, max_results=max_results)

    @staticmethod
    def extract_arxiv_id_from_url(url: str) -> Optional[str]:
        """
        Extract arXiv ID from various URL formats

        Args:
            url: arXiv URL

        Returns:
            arXiv ID or None
        """
        import re

        patterns = [
            r"arxiv\.org/abs/(\d+\.\d+(?:v\d+)?)",
            r"arxiv\.org/pdf/(\d+\.\d+(?:v\d+)?)",
            r"arxiv:(\d+\.\d+(?:v\d+)?)",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None


# Convenience functions
async def fetch_arxiv_papers(
    query: str, max_results: int = 100, start: int = 0
) -> List[Dict]:
    """
    Convenience function to fetch arXiv papers

    Args:
        query: Search query
        max_results: Maximum results to return
        start: Starting index

    Returns:
        List of paper dictionaries
    """
    async with ArxivService() as service:
        return await service.search_papers(
            query=query, max_results=max_results, start=start
        )


async def fetch_recent_arxiv_papers(
    category: Optional[str] = None, max_results: int = 100
) -> List[Dict]:
    """
    Fetch recent arXiv papers

    Args:
        category: Optional category filter
        max_results: Maximum results

    Returns:
        List of paper dictionaries
    """
    async with ArxivService() as service:
        return await service.get_recent_papers(
            category=category, max_results=max_results
        )
