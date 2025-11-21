import PyPDF2
from typing import Optional, List, Dict, Any
import logging
import re
from io import BytesIO

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Utility class for processing various document types
    """
    
    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes) -> str:
        """
        Extract text content from PDF bytes
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            Extracted text content
        """
        try:
            pdf_file = BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_content = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content += page.extract_text() + "\n"
            
            logger.info(f"Successfully extracted text from PDF ({len(text_content)} characters)")
            return text_content.strip()
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            return ""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text content
        
        Args:
            text: Raw text content
            
        Returns:
            Cleaned text
        """
        try:
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Remove special characters that might interfere with processing
            text = re.sub(r'[^\w\s\.,;:!?()-]', '', text)
            
            # Normalize line breaks
            text = text.replace('\r\n', '\n').replace('\r', '\n')
            
            # Remove multiple consecutive periods
            text = re.sub(r'\.{3,}', '...', text)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Failed to clean text: {str(e)}")
            return text
    
    @staticmethod
    def extract_financial_terms(text: str) -> List[str]:
        """
        Extract financial terms and concepts from text
        
        Args:
            text: Text content to analyze
            
        Returns:
            List of identified financial terms
        """
        financial_terms = [
            # Investment terms
            "portfolio", "diversification", "asset allocation", "risk tolerance",
            "return on investment", "roi", "dividend", "yield", "capital gains",
            "mutual fund", "etf", "bond", "stock", "equity", "fixed income",
            
            # Risk terms
            "market risk", "credit risk", "liquidity risk", "inflation risk",
            "volatility", "beta", "standard deviation", "sharpe ratio",
            
            # Compliance terms
            "fiduciary", "suitability", "disclosure", "regulation", "compliance",
            "sec", "finra", "know your customer", "kyc", "anti-money laundering",
            "aml", "privacy policy", "data protection",
            
            # Financial planning
            "retirement planning", "estate planning", "tax planning",
            "emergency fund", "insurance", "annuity", "ira", "401k",
            "pension", "social security"
        ]
        
        found_terms = []
        text_lower = text.lower()
        
        for term in financial_terms:
            if term.lower() in text_lower:
                found_terms.append(term)
        
        return list(set(found_terms))  # Remove duplicates
    
    @staticmethod
    def identify_document_type(text: str) -> str:
        """
        Identify the type of financial document based on content
        
        Args:
            text: Document text content
            
        Returns:
            Document type classification
        """
        text_lower = text.lower()
        
        # Policy document indicators
        policy_indicators = ["policy", "terms and conditions", "agreement", "contract"]
        
        # Prospectus indicators
        prospectus_indicators = ["prospectus", "fund information", "investment objectives"]
        
        # Report indicators
        report_indicators = ["annual report", "quarterly report", "financial statement"]
        
        # Disclosure indicators
        disclosure_indicators = ["disclosure", "risk factors", "important information"]
        
        for indicator in policy_indicators:
            if indicator in text_lower:
                return "policy"
        
        for indicator in prospectus_indicators:
            if indicator in text_lower:
                return "prospectus"
        
        for indicator in report_indicators:
            if indicator in text_lower:
                return "report"
        
        for indicator in disclosure_indicators:
            if indicator in text_lower:
                return "disclosure"
        
        return "general"

class DataValidator:
    """
    Utility class for data validation
    """
    
    @staticmethod
    def validate_user_profile(profile_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate user profile data
        
        Args:
            profile_data: User profile dictionary
            
        Returns:
            Dictionary with validation errors
        """
        errors = {}
        
        # Age validation
        age = profile_data.get('age')
        if not age or not isinstance(age, int) or age < 18 or age > 100:
            errors['age'] = ['Age must be between 18 and 100']
        
        # Income validation
        income = profile_data.get('annual_income')
        if not income or not isinstance(income, (int, float)) or income < 0:
            errors['annual_income'] = ['Annual income must be a positive number']
        
        # Risk tolerance validation
        risk_tolerance = profile_data.get('risk_tolerance')
        valid_risk_levels = ['conservative', 'moderate', 'aggressive']
        if not risk_tolerance or risk_tolerance not in valid_risk_levels:
            errors['risk_tolerance'] = [f'Risk tolerance must be one of: {", ".join(valid_risk_levels)}']
        
        # Time horizon validation
        time_horizon = profile_data.get('time_horizon')
        if not time_horizon or not isinstance(time_horizon, int) or time_horizon < 1:
            errors['time_horizon'] = ['Time horizon must be at least 1 year']
        
        # Financial goals validation
        goals = profile_data.get('financial_goals')
        if not goals or not isinstance(goals, list) or len(goals) == 0:
            errors['financial_goals'] = ['At least one financial goal must be specified']
        
        return errors
    
    @staticmethod
    def validate_allocation_percentages(recommendations: List[Dict[str, Any]]) -> bool:
        """
        Validate that allocation percentages sum to approximately 100%
        
        Args:
            recommendations: List of investment recommendations
            
        Returns:
            True if valid, False otherwise
        """
        try:
            total = sum(rec.get('allocation_percentage', 0) for rec in recommendations)
            return abs(total - 100.0) <= 1.0  # Allow 1% tolerance
        except:
            return False

class SecurityUtils:
    """
    Security-related utility functions
    """
    
    @staticmethod
    def sanitize_input(input_text: str) -> str:
        """
        Sanitize user input to prevent injection attacks
        
        Args:
            input_text: Raw input text
            
        Returns:
            Sanitized text
        """
        if not isinstance(input_text, str):
            return ""
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', input_text)
        
        # Limit length
        max_length = 10000
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.strip()
    
    @staticmethod
    def mask_sensitive_data(data: Dict[str, Any], sensitive_fields: List[str] = None) -> Dict[str, Any]:
        """
        Mask sensitive data in dictionary
        
        Args:
            data: Data dictionary
            sensitive_fields: List of fields to mask
            
        Returns:
            Dictionary with masked sensitive data
        """
        if sensitive_fields is None:
            sensitive_fields = ['ssn', 'account_number', 'routing_number', 'credit_card']
        
        masked_data = data.copy()
        
        for field in sensitive_fields:
            if field in masked_data:
                value = str(masked_data[field])
                if len(value) > 4:
                    masked_data[field] = '*' * (len(value) - 4) + value[-4:]
                else:
                    masked_data[field] = '*' * len(value)
        
        return masked_data