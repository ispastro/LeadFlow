from typing import Dict, List
from datetime import datetime, timedelta
from app.db.pg_direct import get_pg_connection


class AnalyticsService:
    
    def get_overview_metrics(self, days: int = 30) -> Dict:
        """Get high-level overview metrics"""
        conn = get_pg_connection()
        cur = conn.cursor()
        
        try:
            # Total conversations - FIXED: Using parameterized query
            cur.execute(
                "SELECT COUNT(*) FROM conversations WHERE created_at >= NOW() - INTERVAL %s",
                (f"{days} days",)
            )
            total_conversations = cur.fetchone()[0]
            
            # Total leads - FIXED: Using parameterized query
            cur.execute(
                "SELECT COUNT(*) FROM leads WHERE captured_at >= NOW() - INTERVAL %s",
                (f"{days} days",)
            )
            total_leads = cur.fetchone()[0]
            
            # Conversion rate
            conversion_rate = (total_leads / total_conversations * 100) if total_conversations > 0 else 0
            
            # Average messages per conversation - FIXED: Using parameterized query
            cur.execute("""
                SELECT AVG(message_count) FROM (
                    SELECT conversation_id, COUNT(*) as message_count 
                    FROM messages 
                    WHERE created_at >= NOW() - INTERVAL %s
                    GROUP BY conversation_id
                ) as msg_counts
            """, (f"{days} days",))
            avg_messages = cur.fetchone()[0] or 0
            
            return {
                'total_conversations': total_conversations,
                'total_leads': total_leads,
                'conversion_rate': round(conversion_rate, 2),
                'avg_messages_per_conversation': round(float(avg_messages), 2)
            }
            
        finally:
            cur.close()
            conn.close()
    
    def get_lead_quality_breakdown(self, days: int = 30) -> List[Dict]:
        """Get lead quality distribution"""
        conn = get_pg_connection()
        cur = conn.cursor()
        
        try:
            # FIXED: Using parameterized query
            cur.execute("""
                SELECT 
                    metadata->>'quality' as quality,
                    COUNT(*) as count
                FROM leads
                WHERE captured_at >= NOW() - INTERVAL %s
                GROUP BY metadata->>'quality'
            """, (f"{days} days",))
            
            results = cur.fetchall()
            return [
                {'quality': row[0] or 'UNKNOWN', 'count': row[1]}
                for row in results
            ]
            
        finally:
            cur.close()
            conn.close()
    
    def get_intent_breakdown(self, days: int = 30) -> List[Dict]:
        """Get intent distribution"""
        conn = get_pg_connection()
        cur = conn.cursor()
        
        try:
            # FIXED: Using parameterized query
            cur.execute("""
                SELECT 
                    intent,
                    COUNT(*) as count
                FROM leads
                WHERE captured_at >= NOW() - INTERVAL %s AND intent IS NOT NULL
                GROUP BY intent
            """, (f"{days} days",))
            
            results = cur.fetchall()
            return [
                {'intent': row[0], 'count': row[1]}
                for row in results
            ]
            
        finally:
            cur.close()
            conn.close()
    
    def get_time_series_data(self, days: int = 30) -> Dict:
        """Get conversations and leads over time"""
        conn = get_pg_connection()
        cur = conn.cursor()
        
        try:
            # Conversations per day - FIXED: Using parameterized query
            cur.execute("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as count
                FROM conversations
                WHERE created_at >= NOW() - INTERVAL %s
                GROUP BY DATE(created_at)
                ORDER BY date
            """, (f"{days} days",))
            
            conversations_data = [
                {'date': row[0].isoformat(), 'count': row[1]}
                for row in cur.fetchall()
            ]
            
            # Leads per day - FIXED: Using parameterized query
            cur.execute("""
                SELECT 
                    DATE(captured_at) as date,
                    COUNT(*) as count
                FROM leads
                WHERE captured_at >= NOW() - INTERVAL %s
                GROUP BY DATE(captured_at)
                ORDER BY date
            """, (f"{days} days",))
            
            leads_data = [
                {'date': row[0].isoformat(), 'count': row[1]}
                for row in cur.fetchall()
            ]
            
            return {
                'conversations': conversations_data,
                'leads': leads_data
            }
            
        finally:
            cur.close()
            conn.close()


# Singleton instance
analytics_service = AnalyticsService()
