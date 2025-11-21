from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class RiskLevel(str, Enum):
    """
    Risk tolerance levels for financial strategies
    """
    CONSERVATIVE = "conservative"
    MODERATE = "moderate" 
    AGGRESSIVE = "aggressive"

class ComplianceStatus(str, Enum):
    """
    Document compliance status
    """
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    NEEDS_REVIEW = "needs_review"

class DocumentAnalysisRequest(BaseModel):
    """
    Request model for document analysis
    """
    document_text: str = Field(..., description="Text content of the financial document")
    document_type: str = Field(default="policy", description="Type of document (policy, contract, etc.)")
    
class DocumentAnalysisResponse(BaseModel):
    """
    Response model for document analysis
    """
    compliance_status: ComplianceStatus
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in compliance assessment")
    flagged_clauses: List[str] = Field(default=[], description="Non-compliant clauses identified")
    recommendations: List[str] = Field(default=[], description="Recommendations for compliance")
    risk_factors: List[str] = Field(default=[], description="Identified risk factors")

class UserProfile(BaseModel):
    """
    User financial profile for strategy generation
    """
    age: int = Field(..., ge=18, le=100, description="User age")
    annual_income: float = Field(..., ge=0, description="Annual income in USD")
    investment_experience: str = Field(..., description="Investment experience level")
    risk_tolerance: RiskLevel = Field(..., description="Risk tolerance level")
    financial_goals: List[str] = Field(..., description="Financial goals and objectives")
    time_horizon: int = Field(..., ge=1, description="Investment time horizon in years")
    current_assets: Optional[float] = Field(default=0, description="Current asset value")
    monthly_expenses: Optional[float] = Field(default=0, description="Monthly expenses")

class StrategyRequest(BaseModel):
    """
    Request model for financial strategy generation
    """
    user_profile: UserProfile
    preferences: Optional[Dict[str, Any]] = Field(default={}, description="Additional preferences")

class InvestmentRecommendation(BaseModel):
    """
    Individual investment recommendation
    """
    asset_class: str = Field(..., description="Asset class (stocks, bonds, etc.)")
    allocation_percentage: float = Field(..., ge=0, le=100, description="Recommended allocation percentage")
    rationale: str = Field(..., description="Reasoning for this allocation")
    risk_level: RiskLevel = Field(..., description="Risk level of this investment")

class FinancialStrategy(BaseModel):
    """
    Generated financial strategy response
    """
    strategy_summary: str = Field(..., description="High-level strategy summary")
    investment_recommendations: List[InvestmentRecommendation] = Field(..., description="Investment recommendations")
    monthly_savings_target: float = Field(..., description="Recommended monthly savings")
    emergency_fund_target: float = Field(..., description="Emergency fund target amount")
    key_actions: List[str] = Field(..., description="Key actions to implement strategy")
    risk_warnings: List[str] = Field(default=[], description="Important risk considerations")
    review_timeline: str = Field(..., description="When to review this strategy")

class RiskAssessmentRequest(BaseModel):
    """
    Request model for risk assessment
    """
    financial_data: Dict[str, Any] = Field(..., description="Financial data for assessment")
    scenario_type: str = Field(default="general", description="Type of risk scenario")

class RiskFactor(BaseModel):
    """
    Individual risk factor
    """
    factor_name: str = Field(..., description="Name of the risk factor")
    severity: str = Field(..., description="Severity level (low, medium, high)")
    impact_score: float = Field(..., ge=0, le=1, description="Impact score")
    mitigation_strategies: List[str] = Field(..., description="Suggested mitigation strategies")

class RiskAssessmentResponse(BaseModel):
    """
    Response model for risk assessment
    """
    overall_risk_score: float = Field(..., ge=0, le=1, description="Overall risk score")
    risk_level: RiskLevel = Field(..., description="Categorized risk level")
    risk_factors: List[RiskFactor] = Field(..., description="Identified risk factors")
    recommendations: List[str] = Field(..., description="Risk mitigation recommendations")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in assessment")

class APIResponse(BaseModel):
    """
    Generic API response wrapper
    """
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)