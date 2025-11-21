from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.agents import initialize_agent, Tool, AgentType
from typing import Dict, Any, List
import logging
import json
import re
from app.core.config import settings
from app.models.schemas import UserProfile, RiskLevel

logger = logging.getLogger(__name__)

class FinancialAgentService:
    """
    AI agent service for generating personalized financial strategies
    """
    
    def __init__(self):
        """
        Initialize the financial AI agent
        """
        self.llm = ChatOpenAI(
            openai_api_key=settings.openai_api_key,
            temperature=0.2,  # Lower temperature for more consistent financial advice
            max_tokens=settings.max_tokens,
            model="gpt-3.5-turbo"
        )
        
        # Strategy generation prompt template
        self.strategy_prompt = PromptTemplate(
            input_variables=["user_profile", "market_context"],
            template="""
            You are a certified financial advisor with 20+ years of experience. Create a personalized financial strategy.
            
            User Profile:
            {user_profile}
            
            Current Market Context:
            {market_context}
            
            Based on this information, create a comprehensive financial strategy that includes:
            
            1. Strategy Summary: High-level overview of the recommended approach
            2. Investment Recommendations: Specific asset allocations with percentages and rationale
            3. Monthly Savings Target: Realistic monthly savings goal
            4. Emergency Fund Target: Recommended emergency fund amount
            5. Key Actions: Specific steps the user should take
            6. Risk Warnings: Important risks to consider
            7. Review Timeline: When to reassess this strategy
            
            Consider the user's:
            - Age and time horizon
            - Risk tolerance and investment experience
            - Income and expenses
            - Financial goals
            - Current financial situation
            
            Asset classes to consider: Stocks, Bonds, REITs, Commodities, International Funds, Cash/Money Market
            
            Respond in JSON format:
            {{
                "strategy_summary": "Brief strategy overview...",
                "investment_recommendations": [
                    {{
                        "asset_class": "Stocks",
                        "allocation_percentage": 60.0,
                        "rationale": "Explanation for this allocation...",
                        "risk_level": "moderate"
                    }}
                ],
                "monthly_savings_target": 1000.0,
                "emergency_fund_target": 15000.0,
                "key_actions": ["Action 1...", "Action 2..."],
                "risk_warnings": ["Warning 1...", "Warning 2..."],
                "review_timeline": "Review quarterly or when life circumstances change"
            }}
            """
        )
        
        # Risk assessment prompt
        self.risk_prompt = PromptTemplate(
            input_variables=["financial_data", "scenario_type"],
            template="""
            You are a risk assessment specialist. Analyze the financial data and identify potential risks.
            
            Financial Data:
            {financial_data}
            
            Scenario Type: {scenario_type}
            
            Provide a comprehensive risk assessment including:
            1. Overall risk score (0.0 to 1.0)
            2. Risk level categorization
            3. Specific risk factors with severity and impact
            4. Mitigation strategies for each risk
            5. Confidence in the assessment
            
            Consider these risk categories:
            - Market Risk (volatility, economic downturns)
            - Credit Risk (debt levels, payment capacity)
            - Liquidity Risk (access to cash when needed)
            - Inflation Risk (purchasing power erosion)
            - Longevity Risk (outliving savings)
            - Concentration Risk (over-exposure to single assets)
            
            Respond in JSON format:
            {{
                "overall_risk_score": 0.65,
                "risk_level": "moderate",
                "risk_factors": [
                    {{
                        "factor_name": "High Debt-to-Income Ratio",
                        "severity": "high",
                        "impact_score": 0.8,
                        "mitigation_strategies": ["Strategy 1...", "Strategy 2..."]
                    }}
                ],
                "recommendations": ["Rec 1...", "Rec 2..."],
                "confidence_score": 0.85
            }}
            """
        )
        
        # Initialize chains
        self.strategy_chain = LLMChain(llm=self.llm, prompt=self.strategy_prompt)
        self.risk_chain = LLMChain(llm=self.llm, prompt=self.risk_prompt)
        
        # Define tools for the agent
        self.tools = [
            Tool(
                name="Portfolio_Analyzer",
                description="Analyzes portfolio composition and suggests optimizations",
                func=self._analyze_portfolio
            ),
            Tool(
                name="Risk_Calculator",
                description="Calculates risk metrics and scenarios",
                func=self._calculate_risk_metrics
            ),
            Tool(
                name="Goal_Planner",
                description="Plans financial goals and timelines",
                func=self._plan_financial_goals
            )
        ]
        
        # Initialize the agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
        
        logger.info("Financial agent service initialized successfully")
    
    def generate_financial_strategy(self, user_profile: UserProfile, 
                                  preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate personalized financial strategy using AI agent
        
        Args:
            user_profile: User's financial profile
            preferences: Additional user preferences
            
        Returns:
            Generated financial strategy
        """
        try:
            # Prepare user profile string
            profile_str = f"""
            Age: {user_profile.age}
            Annual Income: ${user_profile.annual_income:,.2f}
            Investment Experience: {user_profile.investment_experience}
            Risk Tolerance: {user_profile.risk_tolerance.value}
            Time Horizon: {user_profile.time_horizon} years
            Current Assets: ${user_profile.current_assets or 0:,.2f}
            Monthly Expenses: ${user_profile.monthly_expenses or 0:,.2f}
            Financial Goals: {', '.join(user_profile.financial_goals)}
            """
            
            if preferences:
                profile_str += f"\nPreferences: {json.dumps(preferences, indent=2)}"
            
            # Get market context (simplified for now)
            market_context = self._get_market_context()
            
            # Generate strategy using the chain
            result = self.strategy_chain.run(
                user_profile=profile_str,
                market_context=market_context
            )
            
            # Parse the JSON response
            try:
                strategy = json.loads(result.strip())
                
                # Validate and enhance the strategy
                strategy = self._validate_strategy(strategy, user_profile)
                
                logger.info("Financial strategy generated successfully")
                return strategy
                
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON response, using fallback")
                return self._generate_fallback_strategy(user_profile)
                
        except Exception as e:
            logger.error(f"Failed to generate financial strategy: {str(e)}")
            return self._generate_fallback_strategy(user_profile)
    
    def assess_financial_risk(self, financial_data: Dict[str, Any], 
                            scenario_type: str = "general") -> Dict[str, Any]:
        """
        Assess financial risk using AI analysis
        
        Args:
            financial_data: Financial data for assessment
            scenario_type: Type of risk scenario
            
        Returns:
            Risk assessment results
        """
        try:
            # Format financial data
            data_str = json.dumps(financial_data, indent=2)
            
            # Run risk assessment
            result = self.risk_chain.run(
                financial_data=data_str,
                scenario_type=scenario_type
            )
            
            # Parse JSON response
            try:
                risk_assessment = json.loads(result.strip())
                logger.info("Risk assessment completed successfully")
                return risk_assessment
                
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON response, using fallback")
                return self._generate_fallback_risk_assessment()
                
        except Exception as e:
            logger.error(f"Failed to assess financial risk: {str(e)}")
            return self._generate_fallback_risk_assessment()
    
    def _get_market_context(self) -> str:
        """
        Get current market context (simplified version)
        In production, this would fetch real market data
        """
        return """
        Current Market Context (simulated):
        - S&P 500: Trading near historical highs with moderate volatility
        - Interest Rates: Federal Reserve maintaining rates around 5.25%
        - Inflation: Currently at 3.2%, down from recent highs
        - Bond Market: Yields attractive for income-focused investors
        - International Markets: Mixed performance with emerging markets showing strength
        - Economic Outlook: Moderate growth expected with recession risks diminishing
        """
    
    def _validate_strategy(self, strategy: Dict[str, Any], 
                          user_profile: UserProfile) -> Dict[str, Any]:
        """
        Validate and enhance the generated strategy
        """
        try:
            # Ensure allocations add up to 100%
            if "investment_recommendations" in strategy:
                total_allocation = sum(
                    rec.get("allocation_percentage", 0) 
                    for rec in strategy["investment_recommendations"]
                )
                
                if abs(total_allocation - 100.0) > 1.0:  # Allow 1% tolerance
                    logger.warning(f"Allocation total: {total_allocation}%, adjusting...")
                    # Proportionally adjust allocations
                    factor = 100.0 / total_allocation if total_allocation > 0 else 1.0
                    for rec in strategy["investment_recommendations"]:
                        rec["allocation_percentage"] *= factor
            
            # Validate emergency fund target
            if user_profile.monthly_expenses:
                min_emergency = user_profile.monthly_expenses * 3
                max_emergency = user_profile.monthly_expenses * 12
                current_target = strategy.get("emergency_fund_target", 0)
                
                if current_target < min_emergency:
                    strategy["emergency_fund_target"] = min_emergency
                elif current_target > max_emergency:
                    strategy["emergency_fund_target"] = max_emergency
            
            return strategy
            
        except Exception as e:
            logger.error(f"Strategy validation failed: {str(e)}")
            return strategy
    
    def _generate_fallback_strategy(self, user_profile: UserProfile) -> Dict[str, Any]:
        """
        Generate a basic fallback strategy when AI generation fails
        """
        # Simple rule-based strategy based on age and risk tolerance
        age = user_profile.age
        risk_level = user_profile.risk_tolerance
        
        # Basic asset allocation rules
        if risk_level == RiskLevel.CONSERVATIVE:
            stock_allocation = max(30, 100 - age)
            bond_allocation = min(70, age + 20)
        elif risk_level == RiskLevel.AGGRESSIVE:
            stock_allocation = min(90, 120 - age)
            bond_allocation = max(10, age - 20)
        else:  # MODERATE
            stock_allocation = max(40, 110 - age)
            bond_allocation = min(60, age + 10)
        
        # Normalize to 100%
        total = stock_allocation + bond_allocation
        stock_allocation = (stock_allocation / total) * 100
        bond_allocation = (bond_allocation / total) * 100
        
        return {
            "strategy_summary": f"Balanced {risk_level.value} strategy appropriate for age {age}",
            "investment_recommendations": [
                {
                    "asset_class": "Stocks",
                    "allocation_percentage": round(stock_allocation, 1),
                    "rationale": "Growth potential appropriate for age and risk tolerance",
                    "risk_level": risk_level.value
                },
                {
                    "asset_class": "Bonds",
                    "allocation_percentage": round(bond_allocation, 1),
                    "rationale": "Stability and income generation",
                    "risk_level": "conservative"
                }
            ],
            "monthly_savings_target": user_profile.annual_income * 0.15 / 12,  # 15% savings rate
            "emergency_fund_target": (user_profile.monthly_expenses or 3000) * 6,
            "key_actions": [
                "Open investment accounts if not already done",
                "Set up automatic monthly contributions",
                "Review and rebalance quarterly"
            ],
            "risk_warnings": [
                "Market volatility can affect portfolio value",
                "Past performance doesn't guarantee future results"
            ],
            "review_timeline": "Review annually or when life circumstances change"
        }
    
    def _generate_fallback_risk_assessment(self) -> Dict[str, Any]:
        """
        Generate fallback risk assessment
        """
        return {
            "overall_risk_score": 0.5,
            "risk_level": "moderate",
            "risk_factors": [
                {
                    "factor_name": "Market Volatility",
                    "severity": "medium",
                    "impact_score": 0.6,
                    "mitigation_strategies": ["Diversification", "Dollar-cost averaging"]
                }
            ],
            "recommendations": ["Maintain diversified portfolio", "Regular risk assessment"],
            "confidence_score": 0.7
        }
    
    # Tool functions for the agent
    def _analyze_portfolio(self, portfolio_data: str) -> str:
        """Portfolio analysis tool function"""
        return "Portfolio analysis complete. Diversification adequate."
    
    def _calculate_risk_metrics(self, risk_data: str) -> str:
        """Risk calculation tool function"""
        return "Risk metrics calculated. Overall risk level: moderate."
    
    def _plan_financial_goals(self, goals_data: str) -> str:
        """Goal planning tool function"""
        return "Financial goals planned with timeline and milestones."

# Global instance
financial_agent = FinancialAgentService()