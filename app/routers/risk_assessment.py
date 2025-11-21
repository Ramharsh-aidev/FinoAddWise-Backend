from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any
from app.models.schemas import (
    RiskAssessmentRequest,
    RiskAssessmentResponse,
    APIResponse,
    RiskLevel,
    RiskFactor
)
from app.services.financial_agent import financial_agent

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/assess-risk", response_model=APIResponse)
async def assess_financial_risk(request: RiskAssessmentRequest):
    """
    Assess financial risk based on user data and scenario
    
    This endpoint analyzes financial data to identify potential risks and
    provides mitigation strategies using AI-powered risk assessment.
    """
    try:
        # Validate financial data
        if not request.financial_data:
            raise HTTPException(status_code=400, detail="Financial data cannot be empty")
        
        # Perform risk assessment using AI agent
        risk_result = financial_agent.assess_financial_risk(
            financial_data=request.financial_data,
            scenario_type=request.scenario_type
        )
        
        # Convert to response model
        risk_factors = []
        for factor_data in risk_result.get("risk_factors", []):
            risk_factors.append(RiskFactor(
                factor_name=factor_data.get("factor_name", "Unknown Risk"),
                severity=factor_data.get("severity", "medium"),
                impact_score=factor_data.get("impact_score", 0.5),
                mitigation_strategies=factor_data.get("mitigation_strategies", [])
            ))
        
        risk_assessment = RiskAssessmentResponse(
            overall_risk_score=risk_result.get("overall_risk_score", 0.5),
            risk_level=RiskLevel(risk_result.get("risk_level", "moderate")),
            risk_factors=risk_factors,
            recommendations=risk_result.get("recommendations", []),
            confidence_score=risk_result.get("confidence_score", 0.7)
        )
        
        logger.info(f"Risk assessment completed: {risk_assessment.risk_level} risk level")
        
        return APIResponse(
            success=True,
            message="Risk assessment completed successfully",
            data=risk_assessment.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Risk assessment failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during risk assessment")

@router.post("/stress-test", response_model=APIResponse)
async def perform_stress_test(
    portfolio_value: float,
    portfolio_allocation: Dict[str, float],
    stress_scenario: str = "market_crash"
):
    """
    Perform stress testing on portfolio under various market scenarios
    
    Simulates portfolio performance under adverse market conditions.
    """
    try:
        # Validate inputs
        if portfolio_value <= 0:
            raise HTTPException(status_code=400, detail="Portfolio value must be positive")
        
        if not portfolio_allocation:
            raise HTTPException(status_code=400, detail="Portfolio allocation cannot be empty")
        
        # Stress test scenarios (simplified model)
        stress_scenarios = {
            "market_crash": {
                "stocks": -0.30,  # 30% decline
                "bonds": -0.05,   # 5% decline
                "cash": 0.0,      # No change
                "commodities": -0.15,  # 15% decline
                "real_estate": -0.20   # 20% decline
            },
            "recession": {
                "stocks": -0.20,
                "bonds": 0.05,    # Bonds may benefit
                "cash": 0.0,
                "commodities": -0.10,
                "real_estate": -0.15
            },
            "inflation_spike": {
                "stocks": -0.10,
                "bonds": -0.15,   # Bonds hurt by inflation
                "cash": -0.05,    # Cash loses purchasing power
                "commodities": 0.20,  # Commodities benefit
                "real_estate": 0.10   # Real estate hedge
            },
            "interest_rate_shock": {
                "stocks": -0.15,
                "bonds": -0.25,   # Bonds very sensitive
                "cash": 0.02,     # Cash benefits slightly
                "commodities": -0.05,
                "real_estate": -0.10
            }
        }
        
        if stress_scenario not in stress_scenarios:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid stress scenario. Choose from: {list(stress_scenarios.keys())}"
            )
        
        scenario_impacts = stress_scenarios[stress_scenario]
        
        # Calculate portfolio impact
        total_impact = 0.0
        asset_impacts = {}
        
        for asset_class, allocation_pct in portfolio_allocation.items():
            # Normalize allocation percentage
            allocation = allocation_pct / 100 if allocation_pct > 1 else allocation_pct
            
            # Get impact for this asset class (default to -10% if not specified)
            asset_impact = scenario_impacts.get(asset_class.lower(), -0.10)
            
            # Calculate weighted impact
            weighted_impact = allocation * asset_impact
            total_impact += weighted_impact
            
            asset_impacts[asset_class] = {
                "allocation_percentage": allocation * 100,
                "scenario_impact": asset_impact * 100,
                "dollar_impact": portfolio_value * weighted_impact
            }
        
        # Calculate new portfolio value
        new_portfolio_value = portfolio_value * (1 + total_impact)
        dollar_loss = portfolio_value - new_portfolio_value
        
        # Generate risk mitigation recommendations
        recommendations = []
        
        if total_impact < -0.15:  # More than 15% loss
            recommendations.append("Consider reducing portfolio concentration in high-risk assets")
            recommendations.append("Increase emergency fund to 6-12 months of expenses")
            recommendations.append("Review and possibly increase bond allocation for stability")
        
        if abs(total_impact) > 0.20:  # High volatility
            recommendations.append("Portfolio shows high sensitivity to market stress")
            recommendations.append("Consider diversifying across more asset classes")
            recommendations.append("Implement dollar-cost averaging for new investments")
        
        # Add scenario-specific recommendations
        if stress_scenario == "inflation_spike" and portfolio_allocation.get("commodities", 0) < 5:
            recommendations.append("Consider adding commodity exposure as inflation hedge")
        
        if stress_scenario == "interest_rate_shock" and portfolio_allocation.get("bonds", 0) > 40:
            recommendations.append("Consider shorter-duration bonds to reduce interest rate risk")
        
        return APIResponse(
            success=True,
            message=f"Stress test completed for {stress_scenario} scenario",
            data={
                "scenario": stress_scenario,
                "original_portfolio_value": portfolio_value,
                "stressed_portfolio_value": round(new_portfolio_value, 2),
                "total_impact_percentage": round(total_impact * 100, 2),
                "dollar_impact": round(dollar_loss, 2),
                "asset_class_impacts": asset_impacts,
                "risk_level": "high" if abs(total_impact) > 0.20 else "moderate" if abs(total_impact) > 0.10 else "low",
                "recommendations": recommendations
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stress test failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during stress test")

@router.get("/risk-metrics", response_model=APIResponse)
async def get_risk_metrics():
    """
    Get standard risk metrics and their explanations
    
    Returns information about common financial risk metrics used in assessment.
    """
    try:
        risk_metrics = {
            "overall_risk_score": {
                "description": "Composite risk score from 0.0 (lowest risk) to 1.0 (highest risk)",
                "interpretation": {
                    "0.0-0.3": "Low risk - Conservative portfolio suitable for capital preservation",
                    "0.3-0.6": "Moderate risk - Balanced approach with growth potential",
                    "0.6-1.0": "High risk - Aggressive growth strategy with higher volatility"
                }
            },
            "market_risk": {
                "description": "Risk from overall market movements and economic conditions",
                "factors": ["Market volatility", "Economic cycles", "Interest rate changes"]
            },
            "credit_risk": {
                "description": "Risk of default on debt obligations",
                "factors": ["Credit rating", "Debt-to-income ratio", "Payment history"]
            },
            "liquidity_risk": {
                "description": "Risk of not being able to convert investments to cash quickly",
                "factors": ["Asset liquidity", "Market conditions", "Investment type"]
            },
            "inflation_risk": {
                "description": "Risk that inflation will erode purchasing power",
                "factors": ["Asset classes", "Duration", "Economic environment"]
            },
            "concentration_risk": {
                "description": "Risk from lack of diversification",
                "factors": ["Asset allocation", "Geographic exposure", "Sector concentration"]
            }
        }
        
        return APIResponse(
            success=True,
            message="Risk metrics information retrieved successfully",
            data=risk_metrics
        )
        
    except Exception as e:
        logger.error(f"Failed to get risk metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error getting risk metrics")

@router.post("/risk-tolerance-quiz", response_model=APIResponse)
async def risk_tolerance_quiz(answers: Dict[str, Any]):
    """
    Calculate risk tolerance based on quiz responses
    
    Evaluates user responses to determine appropriate risk tolerance level.
    """
    try:
        if not answers:
            raise HTTPException(status_code=400, detail="Quiz answers cannot be empty")
        
        # Simple risk tolerance scoring
        # In production, this would use a more sophisticated questionnaire
        risk_score = 0
        total_questions = 0
        
        # Age factor (younger = higher risk tolerance)
        age = answers.get("age", 40)
        if age < 30:
            risk_score += 3
        elif age < 50:
            risk_score += 2
        else:
            risk_score += 1
        total_questions += 1
        
        # Investment experience
        experience = answers.get("investment_experience", "beginner").lower()
        if experience in ["expert", "advanced"]:
            risk_score += 3
        elif experience in ["intermediate", "moderate"]:
            risk_score += 2
        else:
            risk_score += 1
        total_questions += 1
        
        # Time horizon
        time_horizon = answers.get("time_horizon", 5)
        if time_horizon > 15:
            risk_score += 3
        elif time_horizon > 7:
            risk_score += 2
        else:
            risk_score += 1
        total_questions += 1
        
        # Financial situation
        financial_stability = answers.get("financial_stability", "stable").lower()
        if financial_stability == "very_stable":
            risk_score += 3
        elif financial_stability == "stable":
            risk_score += 2
        else:
            risk_score += 1
        total_questions += 1
        
        # Market reaction
        market_reaction = answers.get("market_drop_reaction", "concerned").lower()
        if market_reaction in ["opportunity", "buy_more"]:
            risk_score += 3
        elif market_reaction in ["hold", "wait"]:
            risk_score += 2
        else:
            risk_score += 1
        total_questions += 1
        
        # Calculate average score
        avg_score = risk_score / total_questions
        
        # Determine risk tolerance
        if avg_score >= 2.5:
            risk_tolerance = "aggressive"
            description = "High risk tolerance - Comfortable with significant market volatility for potential higher returns"
        elif avg_score >= 2.0:
            risk_tolerance = "moderate"
            description = "Moderate risk tolerance - Balanced approach between growth and stability"
        else:
            risk_tolerance = "conservative" 
            description = "Conservative risk tolerance - Prefer stability and capital preservation over high returns"
        
        return APIResponse(
            success=True,
            message="Risk tolerance assessment completed",
            data={
                "risk_tolerance": risk_tolerance,
                "risk_score": round(avg_score, 2),
                "description": description,
                "recommendations": [
                    f"Based on your {risk_tolerance} risk profile, consider investment strategies that align with your comfort level",
                    "Regularly review your risk tolerance as life circumstances change",
                    "Ensure your investment allocation matches your risk profile"
                ]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Risk tolerance quiz failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during risk tolerance assessment")