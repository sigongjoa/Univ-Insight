"""
벡터 스토어 및 임베딩 서비스 (Phase 3)

주요 기능:
1. ChromaDB 기반 벡터 스토어
2. 문서 임베딩 및 저장
3. 의미론적 유사도 검색 (semantic search)
4. 배치 임베딩 처리
"""

import logging
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime

import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """임베딩 서비스"""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """초기화"""
        self.model_name = model_name
        from sentence_transformers import SentenceTransformer
        self.embedding_model = SentenceTransformer(model_name)
        logger.info(f"✅ 임베딩 모델 로드: {model_name}")

    def embed_text(self, text: str) -> List[float]:
        """텍스트를 벡터로 변환"""
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """배치 임베딩"""
        embeddings = self.embedding_model.encode(texts)
        return embeddings.tolist()


class ChromaVectorStore:
    """ChromaDB 벡터 스토어"""

    def __init__(
        self,
        collection_name: str = "research_papers",
        persist_dir: str = "./chroma_db",
        embedding_service: Optional[EmbeddingService] = None,
    ):
        """초기화"""
        self.collection_name = collection_name
        self.persist_dir = persist_dir
        self.embedding_service = embedding_service or EmbeddingService()
        self.client = None
        self.collection = None
        logger.info(f"🚀 ChromaVectorStore 초기화 ({collection_name})")

    async def initialize(self):
        """벡터 스토어 초기화"""
        os.makedirs(self.persist_dir, exist_ok=True)

        settings = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=self.persist_dir,
            anonymized_telemetry=False,
        )

        self.client = chromadb.Client(settings)
        logger.info("✅ ChromaDB 클라이언트 생성")

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        logger.info(f"✅ 컬렉션 준비: {self.collection_name}")
        return True

    async def add_document(
        self,
        doc_id: str,
        content: str,
        title: str = "",
        metadata: Optional[Dict] = None,
    ) -> bool:
        """문서 추가"""
        embedding = self.embedding_service.embed_text(content)

        meta = metadata or {}
        meta["title"] = title
        meta["created_at"] = datetime.now().isoformat()

        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[meta],
            documents=[content],
        )

        logger.info(f"📝 문서 추가: {doc_id}")
        return True

    async def add_batch(self, documents: List[Dict]) -> int:
        """배치 문서 추가"""
        ids = [doc["id"] for doc in documents]
        contents = [doc["content"] for doc in documents]

        embeddings = self.embedding_service.embed_batch(contents)

        metadatas = []
        for doc in documents:
            meta = doc.get("metadata", {})
            meta["title"] = doc.get("title", "")
            meta["created_at"] = datetime.now().isoformat()
            metadatas.append(meta)

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=contents,
        )

        logger.info(f"📦 {len(ids)}개 문서 배치 추가")
        return len(ids)

    async def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """의미론적 검색"""
        query_embedding = self.embedding_service.embed_text(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                result = {
                    "id": doc_id,
                    "content": results["documents"][0][i] if results["documents"] else "",
                    "title": results["metadatas"][0][i].get("title", "") if results["metadatas"] else "",
                    "distance": results["distances"][0][i] if results["distances"] else 0,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                }
                search_results.append(result)

        logger.info(f"🔍 검색 완료: {len(search_results)}개 결과")
        return search_results

    async def delete_document(self, doc_id: str) -> bool:
        """문서 삭제"""
        self.collection.delete(ids=[doc_id])
        logger.info(f"🗑️  문서 삭제: {doc_id}")
        return True

    async def get_stats(self) -> Dict:
        """통계 조회"""
        count = self.collection.count()
        return {
            "collection": self.collection_name,
            "document_count": count,
            "persist_dir": self.persist_dir,
            "embedding_model": self.embedding_service.model_name,
        }

    async def clear(self) -> bool:
        """컬렉션 비우기"""
        results = self.collection.get()
        if results["ids"]:
            self.collection.delete(ids=results["ids"])
        logger.info("🗑️  컬렉션 비우기 완료")
        return True


_vector_store_instance: Optional[ChromaVectorStore] = None


async def get_vector_store(
    collection_name: str = "research_papers",
    persist_dir: str = "./chroma_db",
) -> ChromaVectorStore:
    """전역 벡터 스토어 인스턴스"""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = ChromaVectorStore(
            collection_name=collection_name,
            persist_dir=persist_dir,
        )
        await _vector_store_instance.initialize()
    return _vector_store_instance

VectorStore = ChromaVectorStore
