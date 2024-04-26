class Carrito:
    """
    Clase que representa un carrito de compras para un usuario.

    Args:
        request (HttpRequest): La solicitud HTTP actual que se utiliza para acceder a la sesión del usuario.

    Attributes:
        request (HttpRequest): La solicitud HTTP actual.
        session (dict): El diccionario de sesión que almacena el carrito.
        carrito (dict): El contenido del carrito de compras.

    Methods:
        agregarProductoCarrito(producto): Agrega un producto al carrito.
        guardarCarrito(): Guarda el estado actual del carrito en la sesión del usuario.
        eliminarProductoCarrito(producto): Elimina un producto específico del carrito.
        restar(producto): Reduce la cantidad de un producto en el carrito.
        limpiar(): Elimina todos los productos del carrito y lo deja vacío.
    """
    def __init__(self, request):
        """
        Inicializa un objeto Carrito y carga el carrito desde la sesión si existe o crea uno nuevo.

        Args:
            request: La solicitud HTTP que se utiliza para acceder a la sesión del usuario.
        """
        # self.request = request
        # self.session = request.session
        # carrito = self.session.get("carrito", {})
        # self.carrito = carrito
        
        self.request = request
        self.session = request.session
        carrito = self.session.get('carrito')
        if 'carrito' not in request.session:
            carrito = self.session['carrito'] = {}
        self.carrito = carrito

    def agregarProductoCarrito(self, producto):
        """
        Agrega un producto al carrito.

        Args:
            producto: El objeto de producto que se va a agregar al carrito.
        """
        id = str(producto.id)
        if id not in self.carrito:
            self.carrito[id] = {
                "producto_id": producto.id,
                "nombre": producto.nombreProducto,
                "precio_unitario": producto.precioProducto,
                "acumulado": producto.precioProducto,
                "cantidad": 1
            }
        else:
            self.carrito[id]["cantidad"] += 1
            self.carrito[id]["acumulado"] += producto.precioProducto
        self.guardarCarrito()

    def guardarCarrito(self):
        """
        Guarda el carrito actual en la sesión.
        """
        self.session["carrito"] = self.carrito
        self.session.modified = True

    def eliminarProductoCarrito(self, producto):
        """
        Elimina un producto del carrito.

        Args:
            producto: El objeto de producto que se va a eliminar del carrito.
        """
        id = str(producto.id)
        if id in self.carrito:
            del self.carrito[id]
            self.guardarCarrito()

    def restar(self, producto):
        """
        Reduce la cantidad de un producto en el carrito.

        Args:
            producto: El objeto de producto cuya cantidad se va a reducir.
        """
        id = str(producto.id)
        if id in self.carrito:
            self.carrito[id]["cantidad"] -= 1
            self.carrito[id]["acumulado"] -= producto.precioProducto
            if self.carrito[id]["cantidad"] <= 0:
                self.eliminarProductoCarrito(producto)
            self.guardarCarrito()

    def limpiar(self):
        """
        Limpia el carrito, eliminando todos los productos.
        """
        self.session["carrito"] = {}
        self.session.modified = True

    def obtener_cantidad_total(self):
        total_cantidad = 0
        for producto_id, item in self.carrito.items():
            total_cantidad += item['cantidad']
        return total_cantidad