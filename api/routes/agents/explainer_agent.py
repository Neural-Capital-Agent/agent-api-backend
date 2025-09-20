"""
Explainer Agent API Routes
Handles decision explanations, jargon translation, and risk communication.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from agent.core.explainability_agent import ExplainabilityAgent
from .shared import get_user_id

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Explainer Agent"], prefix="/explainer")

# Initialize agent
explainer_agent = ExplainabilityAgent()


@router.post("/explain-decision")
async def explain_decision(
    request: Dict[str, Any] = Body(..., description="Request containing action, context, and optional word_limit"),
    user_id: str = Depends(get_user_id)
):
    """Generate comprehensive explanation for a financial decision."""
    try:
        action = request.get("action")
        context = request.get("context")
        word_limit = request.get("word_limit")

        # Set custom word limit if provided
        if word_limit and isinstance(word_limit, int) and word_limit > 0:
            original_limit = explainer_agent.default_word_limit
            explainer_agent.set_word_limit(word_limit)

        logger.info(f"Received explain_decision request - action: {action}, context: {context}")
        explanation = await explainer_agent.explain_decision(action, context)

        # Restore original limit if it was changed
        if word_limit and isinstance(word_limit, int) and word_limit > 0:
            explainer_agent.set_word_limit(original_limit)

        return {
            "success": True,
            "agent": "explainability_agent",
            "explanation": explanation,
            "action": action,
            "word_limit_used": word_limit or explainer_agent.default_word_limit,
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
    request: Dict[str, Any] = Body(..., description="Request containing text and optional word_limit"),
    user_id: str = Depends(get_user_id)
):
    """Convert technical financial terms to plain English."""
    try:
        # Handle both string input and dict input for backward compatibility
        if isinstance(request, str):
            technical_text = request
            word_limit = None
        else:
            technical_text = request.get("text") or request.get("technical_text", "")
            word_limit = request.get("word_limit")

        # Set custom word limit if provided
        if word_limit and isinstance(word_limit, int) and word_limit > 0:
            original_limit = explainer_agent.default_word_limit
            explainer_agent.set_word_limit(word_limit)

        translation = await explainer_agent.translate_jargon(technical_text)

        # Restore original limit if it was changed
        if word_limit and isinstance(word_limit, int) and word_limit > 0:
            explainer_agent.set_word_limit(original_limit)

        return {
            "success": True,
            "agent": "explainability_agent",
            "original_text": technical_text,
            "translation": translation,
            "word_limit_used": word_limit or explainer_agent.default_word_limit,
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


@router.post("/set-word-limit")
async def set_word_limit(
    word_limit: int = Body(..., description="Word limit for explanations (minimum 1)"),
    user_id: str = Depends(get_user_id)
):
    """Set the word limit for all explanation responses."""
    try:
        if word_limit < 1:
            raise HTTPException(
                status_code=400,
                detail={"error": "invalid_word_limit", "message": "Word limit must be at least 1"}
            )

        old_limit = explainer_agent.default_word_limit
        explainer_agent.set_word_limit(word_limit)

        return {
            "success": True,
            "agent": "explainability_agent",
            "previous_word_limit": old_limit,
            "new_word_limit": explainer_agent.default_word_limit,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting word limit for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "word_limit_set_failed", "message": str(e)}
        )


@router.get("/word-limit")
async def get_word_limit(
    user_id: str = Depends(get_user_id)
):
    """Get the current word limit for explanation responses."""
    try:
        return {
            "success": True,
            "agent": "explainability_agent",
            "current_word_limit": explainer_agent.default_word_limit,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting word limit for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "word_limit_get_failed", "message": str(e)}
        )