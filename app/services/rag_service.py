from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import List, Dict, Any, Optional
import logging
import json
import re
from app.core.config import settings
from app.services.pinecone_service import pinecone_service

logger = logging.getLogger(__name__)

class RAGService:
    """
    Retrieval-Augmented Generation service for financial document analysis
    """
    
    def __init__(self):
        """
        Initialize RAG service with LangChain components
        """
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
        self.llm = ChatOpenAI(
            openai_api_key=settings.openai_api_key,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            model="gpt-3.5-turbo"
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Define compliance checking prompt
        self.compliance_prompt = PromptTemplate(
            input_variables=["document_text", "context"],
            template="""
            You are a financial compliance expert. Analyze the following document for compliance issues.
            
            Context from similar documents:
            {context}
            
            Document to analyze:
            {document_text}
            
            Please analyze this document and provide:
            1. Overall compliance status (compliant/non_compliant/needs_review)
            2. Confidence score (0.0 to 1.0)
            3. List of flagged clauses (if any)
            4. Recommendations for improvement
            5. Risk factors identified
            
            Focus on:
            - Regulatory compliance issues
            - Risk disclosure adequacy
            - Fair lending practices
            - Consumer protection violations
            - Data privacy concerns
            
            Respond in JSON format:
            {{
                "compliance_status": "compliant|non_compliant|needs_review",
                "confidence_score": 0.95,
                "flagged_clauses": ["clause 1", "clause 2"],
                "recommendations": ["rec 1", "rec 2"],
                "risk_factors": ["risk 1", "risk 2"]
            }}
            """
        )
        
        self.compliance_chain = LLMChain(
            llm=self.llm,
            prompt=self.compliance_prompt
        )
        
        logger.info("RAG service initialized successfully")
    
    def process_document(self, document_text: str) -> List[Dict[str, Any]]:
        """
        Process a document by splitting into chunks and generating embeddings
        
        Args:
            document_text: Raw document text
            
        Returns:
            List of document chunks with embeddings
        """
        try:
            # Split document into chunks
            chunks = self.text_splitter.split_text(document_text)
            logger.info(f"Split document into {len(chunks)} chunks")
            
            # Generate embeddings for each chunk
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                try:
                    embedding = self.embeddings.embed_query(chunk)
                    processed_chunks.append({
                        "id": f"chunk_{i}",
                        "text": chunk,
                        "embedding": embedding,
                        "metadata": {
                            "chunk_index": i,
                            "text_length": len(chunk)
                        }
                    })
                except Exception as e:
                    logger.error(f"Failed to process chunk {i}: {str(e)}")
                    continue
            
            logger.info(f"Successfully processed {len(processed_chunks)} chunks")
            return processed_chunks
            
        except Exception as e:
            logger.error(f"Failed to process document: {str(e)}")
            return []
    
    def retrieve_relevant_context(self, query: str, top_k: int = 5) -> str:
        """
        Retrieve relevant context from vector database for a query
        
        Args:
            query: Query text
            top_k: Number of relevant chunks to retrieve
            
        Returns:
            Concatenated relevant context
        """
        try:
            # Generate embedding for the query
            query_embedding = self.embeddings.embed_query(query)
            
            # Search for similar documents
            similar_docs = pinecone_service.similarity_search(
                query_embedding=query_embedding,
                top_k=top_k
            )
            
            # Concatenate relevant context
            context_parts = []
            for doc in similar_docs:
                if "text" in doc.get("metadata", {}):
                    context_parts.append(doc["metadata"]["text"])
            
            context = "\n\n".join(context_parts)
            logger.info(f"Retrieved context with {len(context_parts)} relevant chunks")
            return context
            
        except Exception as e:
            logger.error(f"Failed to retrieve context: {str(e)}")
            return ""
    
    def analyze_compliance(self, document_text: str) -> Dict[str, Any]:
        """
        Analyze document for compliance issues using RAG
        
        Args:
            document_text: Document text to analyze
            
        Returns:
            Compliance analysis results
        """
        try:
            # Retrieve relevant context
            context = self.retrieve_relevant_context(document_text)
            
            # Run compliance analysis
            result = self.compliance_chain.run(
                document_text=document_text,
                context=context
            )
            
            # Parse JSON response
            try:
                analysis = json.loads(result.strip())
                logger.info("Compliance analysis completed successfully")
                return analysis
            except json.JSONDecodeError:
                # Fallback parsing if JSON is malformed
                logger.warning("Failed to parse JSON response, using fallback")
                return self._parse_fallback_response(result)
                
        except Exception as e:
            logger.error(f"Failed to analyze compliance: {str(e)}")
            return {
                "compliance_status": "needs_review",
                "confidence_score": 0.0,
                "flagged_clauses": [],
                "recommendations": ["Manual review required due to analysis error"],
                "risk_factors": ["Analysis system error"]
            }
    
    def _parse_fallback_response(self, response: str) -> Dict[str, Any]:
        """
        Fallback parsing when JSON parsing fails
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed compliance analysis
        """
        try:
            # Extract compliance status
            status_match = re.search(r'compliance_status.*?["\'](\w+)["\']', response, re.IGNORECASE)
            status = status_match.group(1) if status_match else "needs_review"
            
            # Extract confidence score
            confidence_match = re.search(r'confidence_score.*?(\d+\.?\d*)', response)
            confidence = float(confidence_match.group(1)) if confidence_match else 0.5
            
            # Extract lists (simplified approach)
            flagged_clauses = re.findall(r'"([^"]*clause[^"]*)"', response, re.IGNORECASE)
            recommendations = re.findall(r'"([^"]*recommend[^"]*)"', response, re.IGNORECASE)
            risk_factors = re.findall(r'"([^"]*risk[^"]*)"', response, re.IGNORECASE)
            
            return {
                "compliance_status": status,
                "confidence_score": min(confidence, 1.0),
                "flagged_clauses": flagged_clauses[:5],  # Limit to 5
                "recommendations": recommendations[:5],
                "risk_factors": risk_factors[:5]
            }
        except Exception as e:
            logger.error(f"Fallback parsing failed: {str(e)}")
            return {
                "compliance_status": "needs_review",
                "confidence_score": 0.0,
                "flagged_clauses": [],
                "recommendations": ["Manual review required"],
                "risk_factors": ["Analysis parsing error"]
            }
    
    def store_document(self, document_text: str, document_id: str, 
                      metadata: Optional[Dict] = None) -> bool:
        """
        Process and store document in vector database
        
        Args:
            document_text: Document text
            document_id: Unique document identifier
            metadata: Additional document metadata
            
        Returns:
            Success status
        """
        try:
            # Process document into chunks
            chunks = self.process_document(document_text)
            
            if not chunks:
                logger.error("No chunks processed from document")
                return False
            
            # Add document metadata to chunks
            base_metadata = metadata or {}
            for chunk in chunks:
                chunk["id"] = f"{document_id}_{chunk['id']}"
                chunk["metadata"].update({
                    "document_id": document_id,
                    "text": chunk["text"],
                    **base_metadata
                })
            
            # Store in Pinecone
            success = pinecone_service.upsert_documents(chunks)
            
            if success:
                logger.info(f"Successfully stored document {document_id}")
            else:
                logger.error(f"Failed to store document {document_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to store document: {str(e)}")
            return False

# Global instance
rag_service = RAGService()