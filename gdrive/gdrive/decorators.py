from functools import wraps
from django.http import JsonResponse
from .models import User

def auth_layer(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        # Get the authorization token from the request headers
        auth_token = request.headers.get('Authorization')

        # Check if the token is provided
        if not auth_token:
            return JsonResponse({'error': 'Authorization token is missing'}, status=401)

        try:
            # Validate the token
            user = User.objects.get(token=auth_token)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid authorization token'}, status=401)

        # If token is valid, attach the user to the request object
        request.user = user
        
        # Proceed with the original function
        return func(self, request, *args, **kwargs)
    
    return wrapper

