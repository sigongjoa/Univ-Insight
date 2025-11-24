"""
Recommendation Service for Univ-Insight.

This module implements personalized recommendation logic for research papers,
including the Plan B (fallback university) suggestion feature.
"""

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from src.domain.models import ResearchPaper, AnalysisResult, UniversityTier
from src.services.vector_store import VectorStore


class RecommendationService:
    """
    Service for generating personalized research paper recommendations.
    Implements:
    - User interest matching (vector similarity)
    - Plan B university suggestions (tier-based fallback)
    """

    def __init__(self, vector_store: Optional[VectorStore] = None):
        """
        Initialize recommendation service.

        Args:
            vector_store: VectorStore instance for similarity search
        """
        self.vector_store = vector_store or VectorStore()

    def get_papers_for_user(
        self,
        db: Session,
        interests: List[str],
        top_k: int = 5,
        min_similarity: float = 0.5
    ) -> List[Dict]:
        """
        Get personalized paper recommendations based on user interests.

        Args:
            db: Database session
            interests: List of user interests (e.g., ["AI", "Machine Learning"])
            top_k: Number of recommendations to return
            min_similarity: Minimum similarity threshold (0-1)

        Returns:
            List of recommendation dicts with paper info and similarity score
        """
        recommendations = []

        # Convert interests to search query
        query = " ".join(interests)

        # Search vector store
        if self.vector_store:
            similar_papers = self.vector_store.search(
                query=query,
                k=top_k,
                threshold=min_similarity
            )

            # Enrich with database info
            for match in similar_papers:
                paper = db.query(ResearchPaper).filter(
                    ResearchPaper.id == match["id"]
                ).first()

                if paper:
                    analysis = db.query(AnalysisResult).filter(
                        AnalysisResult.paper_id == paper.id
                    ).first()

                    recommendations.append({
                        "paper_id": paper.id,
                        "title": paper.title,
                        "university": paper.university,
                        "university_tier": paper.university_tier.value if paper.university_tier else None,
                        "summary": analysis.summary if analysis else paper.content_raw[:200],
                        "job_title": analysis.job_title if analysis else None,
                        "companies": analysis.related_companies if analysis else [],
                        "similarity_score": match["similarity"]
                    })

        return recommendations

    def get_plan_b_suggestions(
        self,
        db: Session,
        paper_id: str,
        similarity_threshold: float = 0.8,
        tier_gap: int = 1
    ) -> List[Dict]:
        """
        Get Plan B (fallback) university suggestions for a given paper.

        Logic:
        - Find papers with similar content (cosine similarity > threshold)
        - Filter to universities with higher tier (harder to enter) than original
        - Return top suggestions

        Args:
            db: Database session
            paper_id: ID of the reference paper
            similarity_threshold: Minimum similarity for matching (0-1)
            tier_gap: Minimum tier difference (1 = at least one tier lower)

        Returns:
            List of Plan B paper suggestions
        """
        # Get the original paper
        original_paper = db.query(ResearchPaper).filter(
            ResearchPaper.id == paper_id
        ).first()

        if not original_paper:
            return []

        plan_b_suggestions = []

        # Search for similar papers
        similar_papers = self.vector_store.search(
            query=original_paper.title + " " + original_paper.content_raw[:500],
            k=20,  # Get more results to filter
            threshold=similarity_threshold
        )

        # Filter by tier (lower-tier universities = easier to enter)
        for match in similar_papers:
            candidate_paper = db.query(ResearchPaper).filter(
                ResearchPaper.id == match["id"]
            ).first()

            if not candidate_paper or candidate_paper.id == paper_id:
                continue

            # Check if tier is higher (higher number = easier to enter)
            if (candidate_paper.university_tier and
                original_paper.university_tier and
                candidate_paper.university_tier.value >=
                original_paper.university_tier.value + tier_gap):

                analysis = db.query(AnalysisResult).filter(
                    AnalysisResult.paper_id == candidate_paper.id
                ).first()

                plan_b_suggestions.append({
                    "paper_id": candidate_paper.id,
                    "title": candidate_paper.title,
                    "university": candidate_paper.university,
                    "university_tier": candidate_paper.university_tier.value,
                    "summary": analysis.summary if analysis else candidate_paper.content_raw[:200],
                    "similarity_score": match["similarity"],
                    "reason": f"Similar research in a more accessible university"
                })

        # Sort by similarity and return top 5
        return sorted(
            plan_b_suggestions,
            key=lambda x: x["similarity_score"],
            reverse=True
        )[:5]

    def calculate_similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
        """
        Calculate cosine similarity between two texts using vector store.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0-1)
        """
        if not self.vector_store:
            return 0.0

        # Search for text1 using text2 as query
        results = self.vector_store.search(
            query=text2,
            k=1,
            threshold=0.0
        )

        # This is a simplified version - ideally we'd compute the actual
        # cosine similarity directly. In production, use sklearn or similar.
        return results[0]["similarity"] if results else 0.0

    def batch_add_to_vector_store(
        self,
        db: Session
    ) -> int:
        """
        Add all papers from database to vector store (for initialization).

        Args:
            db: Database session

        Returns:
            Number of papers successfully added
        """
        if not self.vector_store:
            return 0

        count = 0
        papers = db.query(ResearchPaper).all()

        for paper in papers:
            # Use title + summary as the embedding text
            analysis = db.query(AnalysisResult).filter(
                AnalysisResult.paper_id == paper.id
            ).first()

            embedding_text = paper.title + " "
            if analysis:
                embedding_text += analysis.summary
            else:
                embedding_text += paper.content_raw[:500]

            metadata = {
                "university": paper.university,
                "department": paper.department or "Unknown",
                "date": paper.pub_date.isoformat() if paper.pub_date else None
            }

            if self.vector_store.add_embedding(paper.id, embedding_text, metadata):
                count += 1

        return count
