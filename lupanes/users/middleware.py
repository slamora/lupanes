from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class HandleCsrfViewMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Intercept 403 responses here.
        if response.status_code == 403:
            # For example, redirect to login or another page.
            return redirect('users:login')
        return response
