import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Financial Advisor API" in response.json()["message"]

def test_analyze_compliant_document():
    """Test document analysis with compliant document"""
    # Read sample compliant document
    with open("documents/sample_compliant_policy.md", "r") as f:
        document_text = f.read()
    
    request_data = {
        "document_text": document_text,
        "document_type": "policy"
    }
    
    response = client.post("/api/v1/analyze-document", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "data" in data

def test_analyze_non_compliant_document():
    """Test document analysis with non-compliant document"""
    # Read sample non-compliant document
    with open("documents/sample_non_compliant.md", "r") as f:
        document_text = f.read()
    
    request_data = {
        "document_text": document_text,
        "document_type": "policy"
    }
    
    response = client.post("/api/v1/analyze-document", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    # Should flag this as non-compliant or needs review
    compliance_status = data["data"]["compliance_status"]
    assert compliance_status in ["non_compliant", "needs_review"]

def test_generate_financial_strategy():
    """Test financial strategy generation"""
    request_data = {
        "user_profile": {
            "age": 35,
            "annual_income": 75000,
            "investment_experience": "moderate",
            "risk_tolerance": "moderate",
            "financial_goals": ["retirement", "house purchase"],
            "time_horizon": 20,
            "current_assets": 50000,
            "monthly_expenses": 4000
        }
    }
    
    response = client.post("/api/v1/generate-strategy", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "investment_recommendations" in data["data"]

def test_risk_assessment():
    """Test risk assessment functionality"""
    request_data = {
        "financial_data": {
            "annual_income": 60000,
            "monthly_expenses": 4500,
            "debt_amount": 25000,
            "savings": 15000,
            "investment_portfolio": 30000
        },
        "scenario_type": "general"
    }
    
    response = client.post("/api/v1/assess-risk", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "overall_risk_score" in data["data"]
    assert "risk_level" in data["data"]

def test_document_types():
    """Test getting supported document types"""
    response = client.get("/api/v1/document-types")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "policy" in data["data"]
    assert "prospectus" in data["data"]

def test_strategy_templates():
    """Test getting strategy templates"""
    response = client.get("/api/v1/strategy-templates")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "young_aggressive" in data["data"]
    assert "mid_career_moderate" in data["data"]

def test_risk_metrics():
    """Test getting risk metrics information"""
    response = client.get("/api/v1/risk-metrics")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "overall_risk_score" in data["data"]
    assert "market_risk" in data["data"]