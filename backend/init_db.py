import os

from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://researchnow:changeme123@postgres:5432/researchnow"
)

engine = create_engine(DATABASE_URL)

# Create tables
with engine.connect() as conn:
    # Create papers table
    conn.execute(
        text("""
        CREATE TABLE IF NOT EXISTS papers (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            abstract TEXT,
            doi VARCHAR(255),
            arxiv_id VARCHAR(100),
            publication_year INTEGER,
            citation_count INTEGER DEFAULT 0,
            is_open_access BOOLEAN DEFAULT FALSE,
            pdf_url TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
    """)
    )

    # Create summaries table
    conn.execute(
        text("""
        CREATE TABLE IF NOT EXISTS summaries (
            id SERIAL PRIMARY KEY,
            paper_id INTEGER REFERENCES papers(id) ON DELETE CASCADE,
            executive_summary TEXT,
            detailed_summary TEXT,
            simplified_summary TEXT,
            key_findings TEXT[],
            main_claims TEXT[],
            highlights TEXT[],
            model_used VARCHAR(100),
            status VARCHAR(50) DEFAULT 'completed',
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    )

    conn.commit()
    print("✓ Database tables created successfully!")

engine.dispose()
