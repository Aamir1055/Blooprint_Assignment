from django.utils.cache import add_never_cache_headers
from django.core.cache import cache

class CacheMiddleware:
    """
    Middleware to add an X-Cache header indicating whether a response was
    served from the cache or not.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Before view (pre-processing)
        response = self.get_response(request)
        
        # After view (post-processing)
        cache_key = f"item_{request.path}"
        cached_response = cache.get(cache_key)

        # Check if the response was served from cache
        if cached_response:
            response['X-Cache'] = 'HIT'
        else:
            response['X-Cache'] = 'MISS'

        return response
class YourCustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Add custom processing for request here
        
        response = self.get_response(request)
        
        # Add custom processing for response here
        
        return response
