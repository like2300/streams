"""
Custom middleware to handle proxy headers correctly
"""
class ProxyHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Handle headers from Render proxy
        if request.META.get('HTTP_X_FORWARDED_PROTO') == 'https':
            request.META['wsgi.url_scheme'] = 'https'
        return self.get_response(request)