"""
Database Models for ResearchNow
SQLAlchemy ORM models for papers, summaries, authors, citations, etc.
"""

import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class SourceType(str, enum.Enum):
    """Enum for paper sources"""

    ARXIV = "arxiv"
    PUBMED = "pubmed"
    CORE = "core"
    DOAJ = "doaj"
    S2ORC = "s2orc"
    SEMANTIC_SCHOLAR = "semantic_scholar"
    CROSSREF = "crossref"
    OPENALEX = "openalex"
    MANUAL = "manual"


class PaperType(str, enum.Enum):
    """Enum for paper types"""

    FULL_TEXT = "full_text"
    ABSTRACT_ONLY = "abstract_only"
    METADATA_ONLY = "metadata_only"


class SummaryStatus(str, enum.Enum):
    """Enum for summary generation status"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"


class Paper(Base):
    """Main paper/article model"""

    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)

    # Identifiers
    doi = Column(String(255), unique=True, index=True, nullable=True)
    arxiv_id = Column(String(100), unique=True, index=True, nullable=True)
    pubmed_id = Column(String(100), unique=True, index=True, nullable=True)
    s2_paper_id = Column(
        String(100), unique=True, index=True, nullable=True
    )  # Semantic Scholar
    openalex_id = Column(String(100), unique=True, index=True, nullable=True)

    # Basic Information
    title = Column(Text, nullable=False, index=True)
    abstract = Column(Text, nullable=True)
    paper_type = Column(Enum(PaperType), default=PaperType.METADATA_ONLY)

    # Publication Details
    publication_date = Column(DateTime, nullable=True, index=True)
    publication_year = Column(Integer, nullable=True, index=True)
    journal = Column(String(500), nullable=True)
    conference = Column(String(500), nullable=True)
    volume = Column(String(50), nullable=True)
    issue = Column(String(50), nullable=True)
    pages = Column(String(50), nullable=True)
    publisher = Column(String(255), nullable=True)

    # URLs and Access
    pdf_url = Column(Text, nullable=True)
    html_url = Column(Text, nullable=True)
    landing_page_url = Column(Text, nullable=True)
    is_open_access = Column(Boolean, default=False, index=True)

    # Content Storage
    full_text_path = Column(Text, nullable=True)  # Path to stored full text
    pdf_path = Column(Text, nullable=True)  # Path to stored PDF
    has_full_text = Column(Boolean, default=False, index=True)

    # Categorization
    fields_of_study = Column(ARRAY(String), nullable=True)
    subjects = Column(ARRAY(String), nullable=True)
    keywords = Column(ARRAY(String), nullable=True)
    language = Column(String(10), default="en")

    # Metrics
    citation_count = Column(Integer, default=0, index=True)
    reference_count = Column(Integer, default=0)
    influential_citation_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)

    # Source Tracking
    primary_source = Column(Enum(SourceType), nullable=False)
    source_metadata = Column(JSONB, default={})  # Additional source-specific data

    # Search Optimization
    search_vector = Column(TSVECTOR)  # Full-text search vector
    embedding_id = Column(String(100), nullable=True)  # Reference to vector DB

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    last_synced_at = Column(DateTime, nullable=True)

    # Relationships
    authors = relationship("Author", secondary="paper_authors", back_populates="papers")
    summaries = relationship(
        "Summary", back_populates="paper", cascade="all, delete-orphan"
    )
    citations_out = relationship(
        "Citation",
        foreign_keys="Citation.citing_paper_id",
        back_populates="citing_paper",
    )
    citations_in = relationship(
        "Citation", foreign_keys="Citation.cited_paper_id", back_populates="cited_paper"
    )
    full_text = relationship(
        "FullText", back_populates="paper", uselist=False, cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_paper_search", "search_vector", postgresql_using="gin"),
        Index("idx_paper_fields", "fields_of_study", postgresql_using="gin"),
        Index("idx_paper_keywords", "keywords", postgresql_using="gin"),
        Index("idx_paper_date_citations", "publication_date", "citation_count"),
    )


class Author(Base):
    """Author model"""

    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)

    # Identifiers
    orcid = Column(String(19), unique=True, index=True, nullable=True)
    s2_author_id = Column(String(100), unique=True, index=True, nullable=True)
    openalex_id = Column(String(100), unique=True, index=True, nullable=True)

    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    given_name = Column(String(255), nullable=True)
    family_name = Column(String(255), nullable=True)

    # Affiliations
    current_affiliation = Column(String(500), nullable=True)
    affiliations = Column(JSONB, default=[])  # List of affiliations over time

    # Metrics
    paper_count = Column(Integer, default=0)
    citation_count = Column(Integer, default=0)
    h_index = Column(Integer, default=0)

    # Contact
    email = Column(String(255), nullable=True)
    homepage = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    papers = relationship("Paper", secondary="paper_authors", back_populates="authors")


class PaperAuthor(Base):
    """Association table for papers and authors with author position"""

    __tablename__ = "paper_authors"

    paper_id = Column(
        Integer, ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True
    )
    author_id = Column(
        Integer, ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True
    )
    author_position = Column(Integer, nullable=False)  # 1 for first author, etc.
    is_corresponding = Column(Boolean, default=False)
    affiliation_at_publication = Column(String(500), nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class FullText(Base):
    """Full text content for papers"""

    __tablename__ = "full_texts"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(
        Integer,
        ForeignKey("papers.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Content
    full_text = Column(Text, nullable=True)  # Full paper text

    # Structured Sections
    introduction = Column(Text, nullable=True)
    methods = Column(Text, nullable=True)
    results = Column(Text, nullable=True)
    discussion = Column(Text, nullable=True)
    conclusion = Column(Text, nullable=True)
    acknowledgments = Column(Text, nullable=True)
    references_text = Column(Text, nullable=True)

    # Metadata
    word_count = Column(Integer, nullable=True)
    character_count = Column(Integer, nullable=True)
    has_equations = Column(Boolean, default=False)
    has_figures = Column(Boolean, default=False)
    has_tables = Column(Boolean, default=False)
    figure_count = Column(Integer, default=0)
    table_count = Column(Integer, default=0)

    # Processing
    extracted_at = Column(DateTime, server_default=func.now(), nullable=False)
    extraction_method = Column(String(50), nullable=True)  # "pdf", "xml", "html"
    extraction_quality = Column(Float, nullable=True)  # 0.0 to 1.0

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    paper = relationship("Paper", back_populates="full_text")


class Summary(Base):
    """AI-generated summaries"""

    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(
        Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Summary Content
    executive_summary = Column(Text, nullable=True)  # 2-3 sentences
    detailed_summary = Column(Text, nullable=True)  # 1 paragraph

    # Structured Breakdown
    key_findings = Column(ARRAY(Text), nullable=True)
    main_claims = Column(ARRAY(Text), nullable=True)
    methodology_summary = Column(Text, nullable=True)
    results_summary = Column(Text, nullable=True)
    limitations = Column(ARRAY(Text), nullable=True)
    future_work = Column(ARRAY(Text), nullable=True)

    # Simplification Levels
    simplified_summary = Column(Text, nullable=True)  # Plain language version
    technical_summary = Column(Text, nullable=True)  # For experts

    # Extracted Information
    research_questions = Column(ARRAY(Text), nullable=True)
    hypotheses = Column(ARRAY(Text), nullable=True)
    datasets_used = Column(ARRAY(String), nullable=True)
    methods_used = Column(ARRAY(String), nullable=True)

    # Highlights
    highlights = Column(ARRAY(Text), nullable=True)  # Bullet points

    # Tags and Categories
    auto_tags = Column(ARRAY(String), nullable=True)
    difficulty_level = Column(
        String(20), nullable=True
    )  # "beginner", "intermediate", "advanced"
    reading_time_minutes = Column(Integer, nullable=True)

    # Generation Metadata
    model_used = Column(String(100), nullable=True)  # "llama70b", "aella-qwen", etc.
    model_version = Column(String(50), nullable=True)
    generation_time_seconds = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)

    # Quality Metrics
    quality_score = Column(Float, nullable=True)  # 0.0 to 1.0
    factual_accuracy_score = Column(Float, nullable=True)
    readability_score = Column(Float, nullable=True)
    completeness_score = Column(Float, nullable=True)

    # Status
    status = Column(Enum(SummaryStatus), default=SummaryStatus.PENDING, index=True)
    error_message = Column(Text, nullable=True)

    # User Feedback
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    paper = relationship("Paper", back_populates="summaries")

    __table_args__ = (
        UniqueConstraint("paper_id", "model_used", name="uix_paper_model"),
        Index("idx_summary_status", "status"),
    )


class Citation(Base):
    """Citation relationships between papers"""

    __tablename__ = "citations"

    id = Column(Integer, primary_key=True, index=True)
    citing_paper_id = Column(
        Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    cited_paper_id = Column(
        Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Citation Context
    context = Column(Text, nullable=True)  # Text around citation
    intent = Column(
        String(50), nullable=True
    )  # "background", "method", "result_comparison", etc.
    is_influential = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    citing_paper = relationship(
        "Paper", foreign_keys=[citing_paper_id], back_populates="citations_out"
    )
    cited_paper = relationship(
        "Paper", foreign_keys=[cited_paper_id], back_populates="citations_in"
    )

    __table_args__ = (
        UniqueConstraint("citing_paper_id", "cited_paper_id", name="uix_citation"),
        Index("idx_citation_cited", "cited_paper_id"),
    )


class User(Base):
    """User accounts (optional feature)"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Authentication
    username = Column(String(50), unique=True, index=True, nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=True)

    # Anonymous Users
    anonymous_id = Column(String(100), unique=True, index=True, nullable=True)
    is_anonymous = Column(Boolean, default=True)

    # Profile
    display_name = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    institution = Column(String(255), nullable=True)
    field_of_study = Column(String(100), nullable=True)

    # Preferences
    preferences = Column(JSONB, default={})

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    bookmarks = relationship(
        "Bookmark", back_populates="user", cascade="all, delete-orphan"
    )
    collections = relationship(
        "Collection", back_populates="user", cascade="all, delete-orphan"
    )


class Bookmark(Base):
    """User bookmarks"""

    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    paper_id = Column(
        Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Metadata
    notes = Column(Text, nullable=True)
    tags = Column(ARRAY(String), nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="bookmarks")

    __table_args__ = (
        UniqueConstraint("user_id", "paper_id", name="uix_user_paper_bookmark"),
    )


class Collection(Base):
    """User collections/folders"""

    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Collection Details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="collections")
    papers = relationship("Paper", secondary="collection_papers")


class CollectionPaper(Base):
    """Association table for collections and papers"""

    __tablename__ = "collection_papers"

    collection_id = Column(
        Integer, ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True
    )
    paper_id = Column(
        Integer, ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True
    )
    position = Column(Integer, default=0)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class SearchLog(Base):
    """Search query logging for analytics"""

    __tablename__ = "search_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Query Details
    query_text = Column(Text, nullable=False, index=True)
    filters = Column(JSONB, nullable=True)
    result_count = Column(Integer, default=0)

    # User Context
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    session_id = Column(String(100), nullable=True)

    # Timing
    response_time_ms = Column(Float, nullable=True)

    # Timestamp
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)


class SourceSync(Base):
    """Track synchronization status with external sources"""

    __tablename__ = "source_syncs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(Enum(SourceType), nullable=False, unique=True)

    # Sync Status
    last_sync_at = Column(DateTime, nullable=True)
    last_successful_sync_at = Column(DateTime, nullable=True)
    papers_synced = Column(Integer, default=0)
    papers_updated = Column(Integer, default=0)
    papers_failed = Column(Integer, default=0)

    # Error Tracking
    last_error = Column(Text, nullable=True)
    consecutive_failures = Column(Integer, default=0)

    # Metadata
    sync_metadata = Column(JSONB, default={})

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
