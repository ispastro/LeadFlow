from fastapi import APIRouter, Query
from app.core.analytics import analytics_service

router = APIRouter()


@router.get("/analytics")
async def get_analytics(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze")
):
    """Get analytics data for dashboard"""
    try:
        overview = analytics_service.get_overview_metrics(days)
        lead_quality = analytics_service.get_lead_quality_breakdown(days)
        intent_breakdown = analytics_service.get_intent_breakdown(days)
        time_series = analytics_service.get_time_series_data(days)
        
        return {
            "overview": overview,
            "lead_quality": lead_quality,
            "intent_breakdown": intent_breakdown,
            "time_series": time_series,
            "period_days": days
        }
        
    except Exception as e:
        print(f"❌ Analytics error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "overview": {
                "total_conversations": 0,
                "total_leads": 0,
                "conversion_rate": 0,
                "avg_messages_per_conversation": 0
            },
            "lead_quality": [],
            "intent_breakdown": [],
            "time_series": {"conversations": [], "leads": []}
        }
