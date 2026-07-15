from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.lead import LeadResponse
from app.db import leads as leads_db
from app.api.auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/leads")
async def get_all_leads(_: dict = Depends(get_current_user)):
    """Get all captured leads"""
    try:
        leads = leads_db.get_all_leads()
        return {
            "leads": leads,
            "total": len(leads)
        }
    except Exception as e:
        logger.error("Failed to fetch leads: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: str, _: dict = Depends(get_current_user)):
    """Get specific lead by ID"""
    try:
        lead = leads_db.get_lead_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        return lead
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to fetch lead %s: %s", lead_id, e)
        raise HTTPException(status_code=500, detail=str(e))
