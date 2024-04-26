from django.shortcuts import render
from django.http import HttpResponseNotFound
from .views import page_not_found_view

class NotFoundMiddleware:
    """
    Middleware que maneja las respuestas con el código de estado 404 (no encontrado).

    Este middleware intercepta las respuestas con un código de estado 404 y redirige
    al usuario a una página de error personalizada.

    Args:
        get_response (callable): La función de llamada que procesa la solicitud.
    """
    def __init__(self, get_response):
        """
        Inicializa el middleware con la función de llamada proporcionada.

        Args:
            get_response (callable): La función de llamada que procesa la solicitud.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Procesa la solicitud y maneja las respuestas con código de estado 404.

        Si la respuesta tiene un código de estado 404, redirige al usuario a una página
        de error personalizada.

        Args:
            request (HttpRequest): La solicitud HTTP.
        """
        response = self.get_response(request)
        if response.status_code == 404:
            return page_not_found_view(request, None)
        return response