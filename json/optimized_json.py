
import json
from typing import Any, Dict, Optional, Set
import sys

class FastCachedJSONEncoder:
    """
    A simple, fast JSON encoder that caches serialized strings for repeated objects.
    
    Key optimizations:
    - Single pass encoding with inline caching
    - Minimal overhead - only cache large objects worth the effort
    - Direct string caching without complex analysis
    - Falls back to standard json.dumps for edge cases
    """
    
    def __init__(self, **json_kwargs):
        """Initialize with same arguments as json.dumps()."""
        self.json_kwargs = json_kwargs
        self.reset()
    
    def reset(self):
        """Reset cache for new encoding session."""
        self._cache: Dict[int, str] = {}
        self._encoding: set = set()  # Track objects being encoded (circular ref)
        self.cache_hits = 0
        self.cache_misses = 0
    
    def encode(self, obj: Any) -> str:
        """
        Encode object to JSON with simple caching for performance.
        Falls back to standard json.dumps() to ensure correctness.
        """
        self.reset()
        try:
            result = self._encode_fast(obj)
            return result
        except Exception:
            # If anything goes wrong, fall back to standard encoder
            return json.dumps(obj, **self.json_kwargs)
    
    def _should_cache(self, obj: Any) -> bool:
        """Only cache objects that are worth the overhead."""
        if not isinstance(obj, (dict, list)):
            return False
        
        # Quick size heuristic - only cache substantial objects
        if isinstance(obj, dict):
            return len(obj) >= 3  # At least 3 keys
        else:  # list
            return len(obj) >= 5  # At least 5 items
    
    def _encode_fast(self, obj: Any) -> str:
        """Fast encoding with minimal overhead caching."""
        
        # Handle primitives directly (fastest path)
        if obj is None:
            return 'null'
        elif obj is True:
            return 'true'
        elif obj is False:
            return 'false'
        elif isinstance(obj, (int, float)):
            return json.dumps(obj)  # Let json handle number formatting
        elif isinstance(obj, str):
            return json.dumps(obj, **{k: v for k, v in self.json_kwargs.items() 
                                    if k in ['ensure_ascii']})
        
        # For containers, try caching
        if self._should_cache(obj):
            obj_id = id(obj)
            
            # Check cache first
            if obj_id in self._cache:
                self.cache_hits += 1
                return self._cache[obj_id]
            
            # Detect circular references
            if obj_id in self._encoding:
                # Fall back to standard encoder for circular refs
                return json.dumps(obj, **self.json_kwargs)
            
            # Encode and cache
            self._encoding.add(obj_id)
            try:
                if isinstance(obj, dict):
                    result = self._encode_dict_fast(obj)
                else:  # list
                    result = self._encode_list_fast(obj)
                
                self._cache[obj_id] = result
                self.cache_misses += 1
                return result
            finally:
                self._encoding.remove(obj_id)
        
        else:
            # Small objects - encode directly without caching overhead
            if isinstance(obj, dict):
                return self._encode_dict_fast(obj)
            elif isinstance(obj, list):
                return self._encode_list_fast(obj)
            else:
                # Unknown type - use standard encoder
                return json.dumps(obj, **self.json_kwargs)
    
    def _encode_dict_fast(self, obj: dict) -> str:
        """Fast dict encoding."""
        if not obj:
            return '{}'
        
        # Get formatting parameters
        indent = self.json_kwargs.get('indent')
        sort_keys = self.json_kwargs.get('sort_keys', False)
        separators = self.json_kwargs.get('separators', (',', ':' if indent is None else ': '))
        
        # Build key-value pairs
        items = []
        keys = sorted(obj.keys()) if sort_keys else obj.keys()
        
        for key in keys:
            # Keys must be strings
            if not isinstance(key, str):
                # Fall back to standard encoder for non-string keys
                return json.dumps(obj, **self.json_kwargs)
            
            key_json = json.dumps(key, ensure_ascii=self.json_kwargs.get('ensure_ascii', True))
            value_json = self._encode_fast(obj[key])
            items.append(f'{key_json}{separators[1]}{value_json}')
        
        # Format output
        if indent is not None:
            # Pretty printing
            indent_str = ' ' * indent if isinstance(indent, int) else '\t'
            items_str = f'{separators[0]}\n{indent_str}'.join(items)
            return f'{{\n{indent_str}{items_str}\n}}'
        else:
            # Compact
            return f'{{{separators[0].join(items)}}}'
    
    def _encode_list_fast(self, obj: list) -> str:
        """Fast list encoding."""
        if not obj:
            return '[]'
        
        # Get formatting parameters  
        indent = self.json_kwargs.get('indent')
        separators = self.json_kwargs.get('separators', (',', ':' if indent is None else ': '))
        
        # Encode items
        items = [self._encode_fast(item) for item in obj]
        
        # Format output
        if indent is not None:
            # Pretty printing
            indent_str = ' ' * indent if isinstance(indent, int) else '\t'
            items_str = f'{separators[0]}\n{indent_str}'.join(items)
            return f'[\n{indent_str}{items_str}\n]'
        else:
            # Compact
            return f'[{separators[0].join(items)}]'