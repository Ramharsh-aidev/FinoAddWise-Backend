from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import logging
from app.models.schemas import (
    StrategyRequest, 
    FinancialStrategy,
    APIResponse,
    UserProfile
)
from app.services.financial_agent import financial_agent
from app.utils.helpers import DataValidator

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/generate-strategy", response_model=APIResponse)
async def generate_financial_strategy(request: StrategyRequest):
    """
    Generate personalized financial strategy using AI agents
    
    This endpoint uses autonomous AI agents built with LangChain to create
    personalized financial strategies based on user risk profiles and goals.
    """
    try:
        # Validate user profile data
        profile_data = request.user_profile.dict()
        validation_errors = DataValidator.validate_user_profile(profile_data)
        
        if validation_errors:
            error_details = []
            for field, errors in validation_errors.items():
                error_details.extend([f"{field}: {error}" for error in errors])
            
            raise HTTPException(
                status_code=400, 
                detail=f"Validation errors: {'; '.join(error_details)}"
            )
        
        # Generate strategy using AI agent
        strategy_result = financial_agent.generate_financial_strategy(
            user_profile=request.user_profile,
            preferences=request.preferences
        )
        
        # Validate that allocations are reasonable
        if "investment_recommendations" in strategy_result:
            valid_allocation = DataValidator.validate_allocation_percentages(
                strategy_result["investment_recommendations"]
            )
            
            if not valid_allocation:
                logger.warning("Generated allocation percentages don't sum to 100%")
        
        # Convert to response model
        financial_strategy = FinancialStrategy(**strategy_result)
        
        logger.info(f"Generated financial strategy for user aged {request.user_profile.age}")
        
        return APIResponse(
            success=True,
            message="Financial strategy generated successfully",
            data=financial_strategy.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Strategy generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during strategy generation")

@router.post("/quick-strategy", response_model=APIResponse)
async def generate_quick_strategy(
    age: int,
    annual_income: float,
    risk_tolerance: str,
    time_horizon: int,
    primary_goal: str
):
    """
    Generate a quick financial strategy with minimal inputs
    
    Simplified endpoint for basic strategy generation without full profile.
    """
    try:
        # Create minimal user profile
        user_profile = UserProfile(
            age=age,
            annual_income=annual_income,
            investment_experience="moderate",  # Default assumption
            risk_tolerance=risk_tolerance,
            financial_goals=[primary_goal],
            time_horizon=time_horizon,
            current_assets=0,
            monthly_expenses=annual_income * 0.7 / 12  # Estimate 70% of income for expenses
        )
        
        # Create strategy request
        strategy_request = StrategyRequest(user_profile=user_profile)
        
        # Generate strategy
        return await generate_financial_strategy(strategy_request)
        
    except Exception as e:
        logger.error(f"Quick strategy generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during quick strategy generation")

@router.get("/strategy-templates", response_model=APIResponse)
async def get_strategy_templates():
    """
    Get pre-defined strategy templates for different user profiles
    
    Returns common investment strategies for different risk profiles and life stages.
    """
    try:
        templates = {
            "young_aggressive": {
                "description": "High-growth strategy for young investors (20-35)",
                "risk_level": "aggressive",
                "typical_allocation": {
                    "stocks": 80,
                    "bonds": 15,
                    "alternatives": 5
                },
                "key_features": [
                    "Focus on growth stocks and emerging markets",
                    "Higher volatility tolerance",
                    "Long-term wealth building"
                ]
            },
            "mid_career_moderate": {
                "description": "Balanced strategy for mid-career professionals (35-50)",
                "risk_level": "moderate",
                "typical_allocation": {
                    "stocks": 65,
                    "bonds": 30,
                    "alternatives": 5
                },
                "key_features": [
                    "Balance between growth and stability",
                    "Diversified across asset classes",
                    "Regular rebalancing"
                ]
            },
            "pre_retirement_conservative": {
                "description": "Capital preservation for pre-retirees (50+)",
                "risk_level": "conservative",
                "typical_allocation": {
                    "stocks": 40,
                    "bonds": 55,
                    "cash": 5
                },
                "key_features": [
                    "Focus on income generation",
                    "Lower volatility",
                    "Capital preservation"
                ]
            }
        }
        
        return APIResponse(
            success=True,
            message="Strategy templates retrieved successfully",
            data=templates
        )
        
    except Exception as e:
        logger.error(f"Failed to get strategy templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error getting strategy templates")

@router.post("/optimize-portfolio", response_model=APIResponse)
async def optimize_portfolio(
    current_allocation: dict,
    target_risk_level: str,
    investment_amount: float
):
    """
    Optimize existing portfolio allocation based on target risk level
    
    Analyzes current portfolio and suggests rebalancing to meet target risk profile.
    """
    try:
        # Validate inputs
        if not current_allocation:
            raise HTTPException(status_code=400, detail="Current allocation cannot be empty")
        
        if target_risk_level not in ["conservative", "moderate", "aggressive"]:
            raise HTTPException(status_code=400, detail="Invalid target risk level")
        
        if investment_amount < 0:
            raise HTTPException(status_code=400, detail="Investment amount must be positive")
        
        # Simple optimization logic (in production, use more sophisticated algorithms)
        target_allocations = {
            "conservative": {"stocks": 30, "bonds": 60, "cash": 10},
            "moderate": {"stocks": 60, "bonds": 35, "cash": 5},
            "aggressive": {"stocks": 80, "bonds": 15, "cash": 5}
        }
        
        target = target_allocations[target_risk_level]
        
        # Calculate rebalancing needed
        recommendations = []
        for asset_class, target_pct in target.items():
            current_pct = current_allocation.get(asset_class, 0)
            difference = target_pct - current_pct
            
            if abs(difference) > 2:  # Only recommend changes > 2%
                action = "increase" if difference > 0 else "decrease"
                amount = abs(difference) * investment_amount / 100
                
                recommendations.append({
                    "asset_class": asset_class,
                    "action": action,
                    "target_percentage": target_pct,
                    "current_percentage": current_pct,
                    "adjustment_amount": round(amount, 2)
                })
        
        return APIResponse(
            success=True,
            message="Portfolio optimization completed",
            data={
                "target_risk_level": target_risk_level,
                "target_allocation": target,
                "recommendations": recommendations
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Portfolio optimization failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during portfolio optimization")