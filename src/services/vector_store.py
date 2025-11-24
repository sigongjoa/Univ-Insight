"""
Vector Store Service using ChromaDB.

This module handles embedding generation and vector similarity search
for research papers using ChromaDB as the vector database.
"""

import os
from typing import List, Dict, Optional
import chromadb


class VectorStore:
    """
    ChromaDB-based vector store for research paper embeddings.
    Stores embeddings and provides similarity search functionality.
    """

    def __init__(
        self,
        persist_dir: str = "./chroma_db",
        persist_enabled: bool = True,
        collection_name: str = "research_papers"
    ):
        """
        Initialize ChromaDB client and collection.

        Args:
            persist_dir: Directory to persist ChromaDB data
            persist_enabled: Whether to persist data to disk
            collection_name: Name of the collection to use
        """
        # Create persist directory if needed
        if persist_enabled and not os.path.exists(persist_dir):
            os.makedirs(persist_dir, exist_ok=True)

        # Initialize ChromaDB client using new API
        if persist_enabled:
            self.client = chromadb.PersistentClient(
                path=persist_dir
            )
        else:
            self.client = chromadb.EphemeralClient()

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )

    def add_embedding(
        self,
        paper_id: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Add a paper embedding to the vector store.

        Args:
            paper_id: Unique identifier for the paper
            content: Text content to embed (title + summary recommended)
            metadata: Optional metadata to store with the embedding

        Returns:
            True if successful, False otherwise
        """
        if metadata is None:
            metadata = {}

        # Add to collection
        self.collection.add(
            ids=[paper_id],
            documents=[content],
            metadatas=[metadata]
        )
        return True

    def search(
        self,
        query: str,
        k: int = 5,
        threshold: float = 0.0
    ) -> List[Dict]:
        """
        Search for similar papers using vector similarity.

        Args:
            query: Search query text
            k: Number of results to return
            threshold: Minimum similarity score (0-1)

        Returns:
            List of dicts with 'id', 'content', 'similarity', and 'metadata'
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )

        # Convert distances to similarity scores (1 - distance for cosine)
        papers = []
        if results["ids"] and len(results["ids"]) > 0:
            for idx, doc_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][idx]
                similarity = 1 - distance  # Convert distance to similarity

                if similarity >= threshold:
                    papers.append({
                        "id": doc_id,
                        "content": results["documents"][0][idx] if results["documents"] else "",
                        "similarity": similarity,
                        "metadata": results["metadatas"][0][idx] if results["metadatas"] else {}
                    })

        return papers

    def delete_embedding(self, paper_id: str) -> bool:
        """
        Delete an embedding from the vector store.

        Args:
            paper_id: ID of the paper to delete

        Returns:
            True if successful, False otherwise
        """
        self.collection.delete(ids=[paper_id])
        return True

    def update_embedding(
        self,
        paper_id: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Update an existing embedding.

        Args:
            paper_id: ID of the paper to update
            content: New text content
            metadata: New metadata

        Returns:
            True if successful, False otherwise
        """
        if metadata is None:
            metadata = {}

        self.collection.update(
            ids=[paper_id],
            documents=[content],
            metadatas=[metadata]
        )
        return True

    def get_collection_count(self) -> int:
        """Get the number of embeddings in the collection"""
        return self.collection.count()

    def persist(self) -> bool:
        """
        Persist the collection to disk (if using persistent client).

        Returns:
            True if successful, False otherwise
        """
        self.client.persist()
        return True

    def clear_collection(self) -> bool:
        """
        Clear all embeddings from the collection (use with caution).

        Returns:
            True if successful, False otherwise
        """
        # Delete the collection and recreate it
        self.client.delete_collection(name=self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"}
        )
        return True
