"""
AI Summarization Service using Groq API
Fast, free, and powerful
"""

import json
import logging
import os
import time
from typing import Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


class PaperSummarizer:
    """AI-powered research paper summarizer using Groq"""

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama3-70b-8192"  # Free Llama 3 70B

    async def summarize_paper(
        self,
        title: str,
        abstract: str,
        full_text: Optional[str] = None,
        structured_sections: Optional[Dict[str, str]] = None,
    ) -> Dict:
        """Generate comprehensive summary of a research paper"""

        start_time = time.time()

        try:
            # Build context
            context = f"Title: {title}\n\nAbstract: {abstract}"

            if full_text:
                context += f"\n\nFull Text (excerpt): {full_text[:3000]}"

            # Create prompt
            prompt = f"""{context}

Please analyze this research paper and provide a comprehensive summary in JSON format with these exact fields:

{{
  "executive_summary": "2-3 sentence overview of the main point and findings",
  "detailed_summary": "1 paragraph summary covering research question, methods, key results, and conclusions",
  "simplified_summary": "Explain this research in simple language that a high school student would understand. Avoid jargon.",
  "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
  "main_claims": ["Claim 1", "Claim 2"],
  "methodology_summary": "Brief description of the research methods used",
  "results_summary": "Summary of the main results",
  "limitations": ["Limitation 1", "Limitation 2"],
  "highlights": ["Highlight 1", "Highlight 2", "Highlight 3"],
  "research_questions": ["Question 1"],
  "auto_tags": ["tag1", "tag2", "tag3"],
  "difficulty_level": "beginner/intermediate/advanced",
  "reading_time_minutes": 10
}}

Provide only the JSON, no additional text."""

            # Call Groq API
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }

                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a research paper summarization expert. Provide clear, accurate summaries in JSON format.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000,
                }

                async with session.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]

                        # Try to parse JSON
                        try:
                            # Remove markdown code blocks if present
                            if "```json" in content:
                                content = content.split("```json")[1].split("```")[0]
                            elif "```" in content:
                                content = content.split("```")[1].split("```")[0]

                            summary_data = json.loads(content.strip())

                            # Add metadata
                            summary_data.update(
                                {
                                    "model_used": self.model,
                                    "generation_time_seconds": time.time() - start_time,
                                    "temperature": 0.3,
                                    "status": "completed",
                                }
                            )

                            return summary_data

                        except json.JSONDecodeError:
                            logger.warning("Failed to parse JSON, extracting manually")
                            return self._extract_manual(content, start_time)

                    else:
                        error_text = await response.text()
                        logger.error(f"Groq API error {response.status}: {error_text}")
                        return {
                            "status": "failed",
                            "error_message": f"API error: {response.status}",
                            "generation_time_seconds": time.time() - start_time,
                        }

        except Exception as e:
            logger.error(f"Summarization error: {e}", exc_info=True)
            return {
                "status": "failed",
                "error_message": str(e),
                "generation_time_seconds": time.time() - start_time,
            }

    def _extract_manual(self, content: str, start_time: float) -> Dict:
        """Manual extraction if JSON parsing fails"""
        return {
            "executive_summary": content[:200],
            "detailed_summary": content[:500],
            "simplified_summary": content[:300],
            "key_findings": [content[:100]],
            "main_claims": [content[:100]],
            "highlights": [content[:100]],
            "auto_tags": ["research", "paper"],
            "difficulty_level": "intermediate",
            "reading_time_minutes": 10,
            "model_used": self.model,
            "generation_time_seconds": time.time() - start_time,
            "status": "completed",
        }


# Convenience function
async def summarize_paper(
    title: str,
    abstract: str,
    full_text: Optional[str] = None,
    structured_sections: Optional[Dict[str, str]] = None,
) -> Dict:
    """
    Convenience function to summarize a paper
    """
    summarizer = PaperSummarizer()
    return await summarizer.summarize_paper(
        title=title,
        abstract=abstract,
        full_text=full_text,
        structured_sections=structured_sections,
    )
