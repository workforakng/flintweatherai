import threading
from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ThreadSafeLRUCache:
    """Thread-safe LRU cache with TTL support"""
    
    def __init__(self, max_size: int = 1000):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.lock = threading.Lock()
        self.stats = {'hits': 0, 'misses': 0, 'evictions': 0, 'sets': 0}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            if key not in self.cache:
                self.stats['misses'] += 1
                return None
            
            entry = self.cache[key]
            if self._is_expired(entry):
                del self.cache[key]
                self.stats['misses'] += 1
                return None
            
            self.cache.move_to_end(key)
            self.stats['hits'] += 1
            return entry['data']
    
    def set(self, key: str, data: Any, ttl: int = 300):
        """Set value in cache with TTL"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
            elif len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
                self.stats['evictions'] += 1
            
            self.cache[key] = {
                'data': data,
                'timestamp': datetime.now(),
                'ttl': ttl
            }
            self.stats['sets'] += 1
    
    def _is_expired(self, entry: Dict) -> bool:
        """Check if cache entry is expired"""
        age = (datetime.now() - entry['timestamp']).total_seconds()
        return age >= entry['ttl']
    
    def clear(self):
        """Clear all cache"""
        with self.lock:
            self.cache.clear()
    
    def size(self) -> int:
        """Get cache size"""
        with self.lock:
            return len(self.cache)
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with self.lock:
            return self.stats.copy()
