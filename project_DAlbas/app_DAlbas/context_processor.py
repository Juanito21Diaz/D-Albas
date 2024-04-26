from app_DAlbas.Carrito import Carrito

def totalCarrito(request):
    """
    Calcula el total del carrito de compras del usuario.

    Args:
        request (HttpRequest): La solicitud HTTP actual.

    Returns:
        dict: Un diccionario que contiene el total del carrito de compras con la clave "total_carrito".
    """
    total = 0

    # Verifica si el usuario está autenticado y si la clave "carrito" existe en la sesión.
    if request.user.is_authenticated and "carrito" in request.session:
        carrito = request.session["carrito"]

        for key, value in carrito.items():
            try:
                acumulado = int(value.get("acumulado", 0))
                total += acumulado
            except (TypeError, ValueError):
                # Maneja las excepciones si el valor no es convertible a entero.
                pass

    return {"total_carrito": total}


def cantidad_productos_carrito(request):
    carrito = Carrito(request)
    cantidad_productos = carrito.obtener_cantidad_total()
    return {'cantidad_productos_carrito': cantidad_productos}