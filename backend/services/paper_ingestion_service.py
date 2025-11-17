"""
Paper Ingestion Service
Background service for continuously ingesting papers from multiple sources
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from database.models import Paper, SourceSync, SourceType
from services.arxiv_service import ArxivService
from services.cache_service import get_cache_service
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger(__name__)


class PaperIngestionService:
    """Service for ingesting papers from multiple sources into database"""

    def __init__(self, database_url: str):
        """
        Initialize ingestion service

        Args:
            database_url: Database connection URL
        """
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.cache = get_cache_service()
        self.sources = {
            "arxiv": self._ingest_arxiv,
            # Future: Add more sources
            # "pubmed": self._ingest_pubmed,
            # "semantic_scholar": self._ingest_semantic_scholar,
        }

    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()

    async def ingest_from_source(
        self, source: str, max_papers: int = 1000, category: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Ingest papers from a specific source

        Args:
            source: Source name (arxiv, pubmed, etc.)
            max_papers: Maximum papers to ingest in this batch
            category: Optional category filter

        Returns:
            Statistics about ingestion (added, updated, skipped)
        """
        if source not in self.sources:
            raise ValueError(f"Unknown source: {source}")

        logger.info(f"Starting ingestion from {source}, max_papers={max_papers}")

        try:
            stats = await self.sources[source](max_papers, category)
            self._update_source_sync(source, stats)
            return stats
        except Exception as e:
            logger.error(f"Error ingesting from {source}: {e}", exc_info=True)
            return {"added": 0, "updated": 0, "skipped": 0, "errors": 1}

    async def _ingest_arxiv(
        self, max_papers: int, category: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Ingest papers from arXiv

        Args:
            max_papers: Maximum papers to fetch
            category: arXiv category filter

        Returns:
            Ingestion statistics
        """
        stats = {"added": 0, "updated": 0, "skipped": 0, "errors": 0}

        async with ArxivService() as arxiv:
            if category:
                papers = await arxiv.get_recent_papers(
                    category=category, max_results=max_papers
                )
            else:
                # Fetch from multiple popular categories
                papers = []
                categories = ["cs.AI", "cs.LG", "cs.CV", "cs.CL", "physics.comp-ph"]
                per_category = max_papers // len(categories)

                for cat in categories:
                    cat_papers = await arxiv.get_recent_papers(
                        category=cat, max_results=per_category
                    )
                    papers.extend(cat_papers)

        session = self.get_session()
        try:
            for paper_data in papers:
                try:
                    # Check if paper already exists
                    arxiv_id = paper_data.get("arxiv_id")
                    existing = session.query(Paper).filter_by(arxiv_id=arxiv_id).first()

                    if existing:
                        # Update if needed
                        if self._should_update_paper(existing, paper_data):
                            self._update_paper(session, existing, paper_data)
                            stats["updated"] += 1
                        else:
                            stats["skipped"] += 1
                    else:
                        # Add new paper
                        self._add_paper(session, paper_data, SourceType.ARXIV)
                        stats["added"] += 1

                    # Commit every 100 papers
                    if (stats["added"] + stats["updated"]) % 100 == 0:
                        session.commit()

                except Exception as e:
                    logger.error(f"Error processing paper {arxiv_id}: {e}")
                    stats["errors"] += 1
                    session.rollback()

            # Final commit
            session.commit()
            logger.info(
                f"arXiv ingestion complete: {stats['added']} added, "
                f"{stats['updated']} updated, {stats['skipped']} skipped, "
                f"{stats['errors']} errors"
            )

        except Exception as e:
            logger.error(f"Error in arXiv ingestion: {e}", exc_info=True)
            session.rollback()
            raise
        finally:
            session.close()

        return stats

    def _add_paper(self, session: Session, paper_data: dict, source: SourceType):
        """Add new paper to database"""
        paper = Paper(
            arxiv_id=paper_data.get("arxiv_id"),
            doi=paper_data.get("doi"),
            title=paper_data.get("title"),
            abstract=paper_data.get("abstract"),
            authors=paper_data.get("authors", []),
            publication_date=paper_data.get("published_date"),
            publication_year=paper_data.get("publication_year"),
            journal=paper_data.get("journal_reference"),
            fields_of_study=paper_data.get("categories", []),
            is_open_access=paper_data.get("is_open_access", True),
            pdf_url=paper_data.get("pdf_url"),
            html_url=paper_data.get("html_url"),
            has_full_text=paper_data.get("has_full_text", False),
            primary_source=source.value,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(paper)

    def _update_paper(self, session: Session, paper: Paper, paper_data: dict):
        """Update existing paper"""
        # Update fields that may have changed
        if paper_data.get("abstract") and not paper.abstract:
            paper.abstract = paper_data["abstract"]

        if paper_data.get("doi") and not paper.doi:
            paper.doi = paper_data["doi"]

        if paper_data.get("pdf_url") and not paper.pdf_url:
            paper.pdf_url = paper_data["pdf_url"]

        # Update metadata
        paper.updated_at = datetime.utcnow()

    def _should_update_paper(self, paper: Paper, paper_data: dict) -> bool:
        """Check if paper should be updated"""
        # Update if missing critical data
        if not paper.abstract and paper_data.get("abstract"):
            return True
        if not paper.doi and paper_data.get("doi"):
            return True
        if not paper.pdf_url and paper_data.get("pdf_url"):
            return True

        # Update if older than 30 days
        if paper.updated_at and (datetime.utcnow() - paper.updated_at).days > 30:
            return True

        return False

    def _update_source_sync(self, source: str, stats: dict):
        """Update source sync tracking"""
        session = self.get_session()
        try:
            sync = session.query(SourceSync).filter_by(source_name=source).first()

            if not sync:
                sync = SourceSync(
                    source_name=source,
                    last_sync=datetime.utcnow(),
                    papers_synced=stats["added"],
                    status="success",
                )
                session.add(sync)
            else:
                sync.last_sync = datetime.utcnow()
                sync.papers_synced += stats["added"]
                sync.status = "success" if stats["errors"] == 0 else "partial"

            session.commit()
        except Exception as e:
            logger.error(f"Error updating source sync: {e}")
            session.rollback()
        finally:
            session.close()

    async def sync_all_sources(self, max_papers_per_source: int = 500):
        """
        Sync papers from all configured sources

        Args:
            max_papers_per_source: Max papers to fetch per source
        """
        logger.info("Starting sync for all sources")
        total_stats = {"added": 0, "updated": 0, "skipped": 0, "errors": 0}

        for source in self.sources.keys():
            try:
                stats = await self.ingest_from_source(source, max_papers_per_source)
                for key in total_stats:
                    total_stats[key] += stats.get(key, 0)
            except Exception as e:
                logger.error(f"Error syncing source {source}: {e}")
                total_stats["errors"] += 1

        logger.info(
            f"Sync complete - Added: {total_stats['added']}, "
            f"Updated: {total_stats['updated']}, "
            f"Skipped: {total_stats['skipped']}, "
            f"Errors: {total_stats['errors']}"
        )

        return total_stats

    async def continuous_sync(
        self, interval_hours: int = 6, papers_per_batch: int = 500
    ):
        """
        Run continuous background sync

        Args:
            interval_hours: Hours between sync runs
            papers_per_batch: Papers to fetch per batch
        """
        logger.info(
            f"Starting continuous sync (every {interval_hours} hours, "
            f"{papers_per_batch} papers per batch)"
        )

        while True:
            try:
                await self.sync_all_sources(papers_per_batch)
                logger.info(f"Sleeping for {interval_hours} hours until next sync")
                await asyncio.sleep(interval_hours * 3600)
            except Exception as e:
                logger.error(f"Error in continuous sync: {e}", exc_info=True)
                # Sleep for 1 hour on error before retrying
                await asyncio.sleep(3600)

    def get_ingestion_stats(self) -> Dict[str, any]:
        """Get statistics about ingested papers"""
        session = self.get_session()
        try:
            total_papers = session.query(Paper).count()

            # Papers by source
            by_source = {}
            for source in SourceType:
                count = (
                    session.query(Paper).filter_by(primary_source=source.value).count()
                )
                by_source[source.value] = count

            # Recent papers (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_papers = (
                session.query(Paper).filter(Paper.created_at >= yesterday).count()
            )

            # Last sync info
            syncs = session.query(SourceSync).all()
            last_syncs = {sync.source_name: sync.last_sync for sync in syncs}

            return {
                "total_papers": total_papers,
                "by_source": by_source,
                "recent_papers_24h": recent_papers,
                "last_syncs": last_syncs,
            }
        finally:
            session.close()


# Convenience function
async def run_ingestion(database_url: str, max_papers: int = 1000):
    """Run one-time paper ingestion"""
    service = PaperIngestionService(database_url)
    return await service.sync_all_sources(max_papers)
