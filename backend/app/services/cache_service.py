"""In-memory cache service for caching AI responses (disabled by default)."""

import json
import hashlib
from typing import Optional, Any, Dict
from datetime import datetime, timedelta


class CacheService:
    """Service for caching AI responses using in-memory storage."""
    
    def __init__(self):
        self._enabled = False  # Cache disabled by default
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        self._ttl_analysis = 24  # TTL for analysis results (hours)
        self._ttl_generation = 12  # TTL for generation results (hours)
        print("[CACHE] In-memory cache initialized (disabled by default)")
    
    def _generate_key(self, prefix: str, *args: Any) -> str:
        """Generate cache key from arguments."""
        key_data = json.dumps(args, sort_keys=True, ensure_ascii=False)
        key_hash = hashlib.sha256(key_data.encode('utf-8')).hexdigest()
        return f"bizmail:{prefix}:{key_hash}"
    
    def get(self, prefix: str, *args: Any) -> Optional[Any]:
        """Get cached value."""
        if not self._enabled:
            return None
        
        try:
            key = self._generate_key(prefix, *args)
            if key in self._cache:
                value, expiry = self._cache[key]
                if datetime.now() < expiry:
                    print(f"[CACHE] HIT: {prefix}")
                    return value
                else:
                    del self._cache[key]
            print(f"[CACHE] MISS: {prefix}")
            return None
        except Exception as e:
            print(f"[CACHE] Error getting cache: {e}")
            return None
    
    def set(self, prefix: str, value: Any, ttl_hours: int, *args: Any) -> bool:
        """Set cached value."""
        if not self._enabled:
            return False
        
        try:
            key = self._generate_key(prefix, *args)
            expiry = datetime.now() + timedelta(hours=ttl_hours)
            self._cache[key] = (value, expiry)
            print(f"[CACHE] SET: {prefix} (TTL: {ttl_hours}h)")
            return True
        except Exception as e:
            print(f"[CACHE] Error setting cache: {e}")
            return False
    
    def get_analysis(self, subject: str, body: str, company_context: str) -> Optional[dict]:
        """Get cached analysis result."""
        return self.get("analysis", subject, body, company_context)
    
    def set_analysis(self, subject: str, body: str, company_context: str, result: dict) -> bool:
        """Cache analysis result."""
        return self.set("analysis", result, self._ttl_analysis, subject, body, company_context)
    
    def get_generation(
        self,
        source_subject: str,
        source_body: str,
        company_context: str,
        parameters_hash: str,
        thread_history: Optional[str] = None,
        extra_directives: Optional[list] = None,
        custom_prompt: Optional[str] = None
    ) -> Optional[dict]:
        """Get cached generation result."""
        return self.get(
            "generation",
            source_subject,
            source_body,
            company_context,
            parameters_hash,
            thread_history or "",
            json.dumps(extra_directives or [], sort_keys=True),
            custom_prompt or ""
        )
    
    def set_generation(
        self,
        source_subject: str,
        source_body: str,
        company_context: str,
        parameters_hash: str,
        result: dict,
        thread_history: Optional[str] = None,
        extra_directives: Optional[list] = None,
        custom_prompt: Optional[str] = None
    ) -> bool:
        """Cache generation result."""
        return self.set(
            "generation",
            result,
            self._ttl_generation,
            source_subject,
            source_body,
            company_context,
            parameters_hash,
            thread_history or "",
            json.dumps(extra_directives or [], sort_keys=True),
            custom_prompt or ""
        )
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear cache entries matching pattern."""
        if not self._enabled:
            return 0
        
        try:
            count = 0
            keys_to_delete = [k for k in self._cache.keys() if k.startswith(f"bizmail:{pattern}")]
            for key in keys_to_delete:
                del self._cache[key]
                count += 1
            if count > 0:
                print(f"[CACHE] Cleared {count} entries matching pattern: {pattern}")
            return count
        except Exception as e:
            print(f"[CACHE] Error clearing cache: {e}")
            return 0
    
    def is_enabled(self) -> bool:
        """Check if cache is enabled."""
        return self._enabled


# Singleton instance
_cache_service = None

def get_cache_service() -> CacheService:
    """Get singleton cache service instance."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service
