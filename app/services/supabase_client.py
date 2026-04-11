from supabase import create_client, Client
from config import settings


class SupabaseService:
    _instance = None
    _client: Client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._client = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
        return cls._instance
    
    @property
    def client(self) -> Client:
        return self._client


# Singleton instance
supabase_service = SupabaseService()
supabase = supabase_service.client
