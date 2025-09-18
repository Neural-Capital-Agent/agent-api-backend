"""
Explainer Agent API Routes
Handles decision explanations, jargon translation, and risk communication.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from agent.explainability_agent import ExplainabilityAgent
from .shared import get_user_id

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Explainer Agent"], prefix="/explainer")

# Initialize agent
explainer_agent = ExplainabilityAgent()


@router.post("/explain-decision")
async def explain_decision(
    action: Dict[str, Any] = Body(..., description="Action or decision to explain"),
    context: Optional[Dict[str, Any]] = Body(None, description="Additional context"),
    user_id: str = Depends(get_user_id)
):
    """Generate comprehensive explanation for a financial decision."""
    try:
        explanation = await explainer_agent.explain_decision(action, context)

        return {
            "success": True,
            "agent": "explainability_agent",
            "explanation": explanation,
            "action": action,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error explaining decision for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "explanation_failed", "message": str(e)}
        )


@router.post("/translate-jargon")
async def translate_jargon(
    technical_text: str = Body(..., description="Text containing financial jargon"),
    user_id: str = Depends(get_user_id)
):
    """Convert technical financial terms to plain English."""
    try:
        translation = await explainer_agent.translate_jargon(technical_text)

        return {
            "success": True,
            "agent": "explainability_agent",
            "original_text": technical_text,
            "translation": translation,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error translating jargon for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "translation_failed", "message": str(e)}
        )


@router.get("/jargon-definition/{term}")
async def get_jargon_definition(
    term: str,
    user_id: str = Depends(get_user_id)
):
    """Get plain English definition for a financial term."""
    try:
        definition = explainer_agent.get_jargon_definition(term)

        return {
            "success": True,
            "agent": "explainability_agent",
            "term": term,
            "definition": definition,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting definition for term {term}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "definition_failed", "message": str(e), "term": term}
        )


@router.post("/risk-explanation")
async def explain_risk_level(
    risk_level: str = Body(..., description="Risk level to explain"),
    user_id: str = Depends(get_user_id)
):
    """Explain what a risk level means in plain English."""
    try:
        explanation = explainer_agent.explain_risk_level(risk_level)

        return {
            "success": True,
            "agent": "explainability_agent",
            "risk_level": risk_level,
            "explanation": explanation,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error explaining risk level {risk_level}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "risk_explanation_failed", "message": str(e), "risk_level": risk_level}
        )