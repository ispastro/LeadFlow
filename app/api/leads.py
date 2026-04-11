from fastapi import APIRouter, HTTPException
from typing import List
from app.models.lead import LeadResponse
from app.db import leads as leads_db

router = APIRouter()


@router.get("/leads", response_model=List[LeadResponse])
async def get_all_leads():
    """Get all captured leads"""
    try:
        leads = leads_db.get_all_leads()
        return leads
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: str):
    """Get specific lead by ID"""
    try:
        # This would need a get_lead_by_id function in leads_db
        raise HTTPException(status_code=501, detail="Not implemented yet")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
