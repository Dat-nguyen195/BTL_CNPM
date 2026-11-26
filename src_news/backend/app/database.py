from postgrest import SyncPostgrestClient
from supabase import create_client

from app.config import settings

if settings.POSTGREST_URL:
    supabase = SyncPostgrestClient(settings.POSTGREST_URL)
elif settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
else:
    raise RuntimeError("Configure POSTGREST_URL or the Supabase URL and service-role key.")
