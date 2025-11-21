import pinecone
from typing import List, Dict, Any, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class PineconeService:
    """
    Service for managing Pinecone vector database operations
    """
    
    def __init__(self):
        """
        Initialize Pinecone connection
        """
        try:
            pinecone.init(
                api_key=settings.pinecone_api_key,
                environment=settings.pinecone_environment
            )
            self.index_name = settings.pinecone_index_name
            self.index = None
            self._connect_to_index()
            logger.info("Successfully initialized Pinecone service")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {str(e)}")
            raise
    
    def _connect_to_index(self):
        """
        Connect to or create the Pinecone index
        """
        try:
            # Check if index exists
            if self.index_name not in pinecone.list_indexes():
                logger.info(f"Creating new Pinecone index: {self.index_name}")
                pinecone.create_index(
                    name=self.index_name,
                    dimension=1536,  # OpenAI embedding dimension
                    metric="cosine"
                )
            
            self.index = pinecone.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
        except Exception as e:
            logger.error(f"Failed to connect to Pinecone index: {str(e)}")
            raise
    
    def upsert_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Insert or update documents in the vector database
        
        Args:
            documents: List of documents with id, values, and metadata
            
        Returns:
            bool: Success status
        """
        try:
            if not self.index:
                raise Exception("Pinecone index not initialized")
            
            # Prepare vectors for upsert
            vectors = []
            for doc in documents:
                vectors.append({
                    "id": doc["id"],
                    "values": doc["embedding"],
                    "metadata": doc.get("metadata", {})
                })
            
            # Upsert in batches to avoid rate limits
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
                logger.info(f"Upserted batch {i//batch_size + 1} with {len(batch)} documents")
            
            return True
        except Exception as e:
            logger.error(f"Failed to upsert documents: {str(e)}")
            return False
    
    def similarity_search(self, query_embedding: List[float], top_k: int = 5, 
                         filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Perform similarity search in the vector database
        
        Args:
            query_embedding: Query vector embedding
            top_k: Number of top results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            List of similar documents with scores
        """
        try:
            if not self.index:
                raise Exception("Pinecone index not initialized")
            
            # Perform similarity search
            search_kwargs = {
                "vector": query_embedding,
                "top_k": top_k,
                "include_metadata": True
            }
            
            if filter_metadata:
                search_kwargs["filter"] = filter_metadata
            
            results = self.index.query(**search_kwargs)
            
            # Format results
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                })
            
            logger.info(f"Found {len(formatted_results)} similar documents")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to perform similarity search: {str(e)}")
            return []
    
    def delete_documents(self, document_ids: List[str]) -> bool:
        """
        Delete documents from the vector database
        
        Args:
            document_ids: List of document IDs to delete
            
        Returns:
            bool: Success status
        """
        try:
            if not self.index:
                raise Exception("Pinecone index not initialized")
            
            self.index.delete(ids=document_ids)
            logger.info(f"Deleted {len(document_ids)} documents")
            return True
        except Exception as e:
            logger.error(f"Failed to delete documents: {str(e)}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the Pinecone index
        
        Returns:
            Dictionary with index statistics
        """
        try:
            if not self.index:
                raise Exception("Pinecone index not initialized")
            
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness
            }
        except Exception as e:
            logger.error(f"Failed to get index stats: {str(e)}")
            return {}

# Global instance
pinecone_service = PineconeService()