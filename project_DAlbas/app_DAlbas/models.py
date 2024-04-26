from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import post_save, post_migrate
from django.contrib.auth.models import AbstractUser, Group
from PIL import Image, ImageDraw, ImageFont
from django.dispatch import receiver
from django.http import HttpRequest
from django.core.files import File
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from datetime import datetime
from django.db import models
from io import BytesIO
import qrcode

# Create your models here.

TIPO_USUARIOS = [
    ('Administrativo', 'Administrativo'),
    ('Cliente', 'Cliente'),
]

ESTADOS_PEDIDO = [
    ('Pendiente', 'Pendiente'),
    ('En proceso', 'En proceso'),
    ('Entregado', 'Entregado'),
    ('Cancelado', 'Cancelado'),
]

METODOS_DE_PAGO = [
    ('Transferencia', 'Transferencia'),
    ('Efectivo', 'Efectivo'),
]

PESO_TORTAS = [
    ('Unidad', 'Unidad'),
    ('Media libra', 'Media libra'),
    ('Libra', 'Libra'),
    ('Libra y media', 'Libra y media'),
    ('Dos Libras', 'Dos libras'),
]

SABORES_TORTAS = [
    ('Arequipe', 'Arequipe'),
    ('Vainilla', 'Vainilla'),
    ('Chocolate', 'Chocolate'),
    ('Ponque', 'Ponque'),
]

ESTADOS_USUARIOS = [
    ('A','Activo'),
    ('I','Inactivo'),
]

ESTADOS_PRODUCTOS = [
    ('A','Activo'),
    ('I','Inactivo'),
]

class User(AbstractUser):
    fotoUsuario = models.ImageField(upload_to=f"usuarios/",null=True,blank=True,db_comment="Foto del Usuario")
    tipoUsuario = models.CharField(max_length=15,choices=TIPO_USUARIOS,db_comment="Nombre del Tipo de usuario")
    estadoUsuario = models.CharField(max_length=10,choices=ESTADOS_USUARIOS,default='Activo',db_comment="Estado de los usuarios, deben estar activos para poder ingresar")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self) -> str:
        return f"{self.username}"
    
class Clientes(User):
    identificacionCliente = models.CharField(max_length=20,unique=True,db_comment='Identificación del cliente, puede ser cédula o NUIP')
    telefonoCliente = models.CharField(max_length=20,null=True,db_comment='Número telefono del cliente')
    fechaHoraCreacionCliente = models.DateTimeField(auto_now_add=True,db_comment='Fecha y hora del registro del cliente')
    fechaHoraActualizacionCliente = models.DateTimeField(auto_now=True,db_comment='Fecha y hora última actualización')

    def __str__(self) -> str:
        return f'{self.identificacionCliente}'

class Administradores(User):
    telefonoAdministrador = models.CharField(max_length=20,null=True,db_comment='Número telefono del administrador')
    cargoAdministrador = models.CharField(max_length=50,null=True,db_comment='Cargo que ocupa el administrador a registrar')
    fechaHoraCreacionAdmin = models.DateTimeField(auto_now_add=True,db_comment='Fecha y hora del registro')
    fechaHoraActualizacionAdmin = models.DateTimeField(auto_now=True,db_comment='Fecha y hora última actualización')

    def __str__(self) -> str:
        return f'{self.cargoAdministrador}'
    
class Pedidos(models.Model):
    nombreClientePedido = models.CharField(max_length=50,db_comment="nombre del cliente que quiere el pedido")
    telefonoClientePedido = models.CharField(max_length=20,null=True,db_comment='Número telefono del cliente')
    fechaPedido = models.DateTimeField(default=timezone.now,db_comment="Fecha en que realiza el pedido")
    fechaHoraPedido = models.DateTimeField(db_comment="Día y hora en la que se requiere el pedido")
    metodoPago = models.CharField(max_length=20,choices=METODOS_DE_PAGO,db_comment="Metodos de pago disponibles")
    estadoPedido = models.CharField(max_length=15,choices=ESTADOS_PEDIDO,default='Pendiente',db_comment="Estado")
    userPedido = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='pedido_usuario',on_delete=models.PROTECT,null=True,default=None,db_comment="Fk del cliente que realiza el pedido")
    valorPedido = models.IntegerField(null=True,db_comment="valor del pedido")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self) -> str:
        return f"{self.nombreClientePedido}-{self.estadoPedido}"
    
class DetalleProductoPedido(models.Model):
    pedidoDetalle = models.ForeignKey(Pedidos,related_name='detalles_producto',on_delete=models.PROTECT,default=None,db_comment="Fk del pedido ")
    nombrePersonaDetalle = models.CharField(max_length=50,null=True,blank=True,db_comment="nombre de la persona a la que se le quiere festejar")
    edadPersonaDetalle = models.IntegerField(null=True,blank=True,db_comment="Edad de la persona")
    imagenPedidoDetalle = models.ImageField(upload_to=f"pedidos_cliente/",null=True,blank=True,db_comment="Foto de ejemplo de como el clinte quiere su producto, ejemplo un pastel")
    
    def __str__(self) -> str:
        return f'{self.nombrePersonaDetalle}-{self.imagenPedidoDetalle}'
    
class Abonos(models.Model):
    fotoComprobanteAbono = models.ImageField(upload_to=f"abonos/",null=True,blank=True,db_comment="Foto del comprobante de pago del primer abono del pedido")
    codigoComprobanteAbono = models.CharField(max_length=50,unique=True,db_comment="Código del comprobante del pago del primer abono")
    valorAbono = models.IntegerField(db_comment="Valor de pago del primer abono cincuenta porciento del valor del pedido")
    pedidoAbono = models.ForeignKey(Pedidos,on_delete=models.PROTECT,related_name='abono_pedido',default=None,db_comment="Fk de la tabla pedidos")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self) -> str:
        return f"{self.pedidoAbono}-{self.valorAbono}-{self.codigoComprobanteAbono}"
    
class Categorias(models.Model):
    nombreCategoria = models.CharField(max_length=50,unique=True,db_comment="Nombre de la categoria")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self) -> str:
        return self.nombreCategoria
    
class Tematicas(models.Model):
    nombreTematica = models.CharField(max_length=50,unique=True,db_comment="Nombre de la tematica")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self) -> str:
        return self.nombreTematica
    
class Productos(models.Model):
    nombreProducto = models.CharField(max_length=50,db_comment="Nombre de producto")
    codigoProducto = models.CharField(max_length=50,unique=True,db_comment="Código unico de cada producto")
    precioProducto = models.IntegerField(db_comment="precio unitario del producto")
    descripcionProducto = models.TextField(null=True,db_comment="Descripción de cada producto de la pasteleria")
    imagenProducto = models.ImageField(upload_to=f"productos/",null=True,blank=True,db_comment="Imagen del producto")
    qrProducto = models.ImageField(upload_to=f"codigos_qr/",null=True,blank=True,db_comment="Imagen del código qr del producto")
    categoriaProducto = models.ForeignKey(Categorias,related_name='categoria_producto',on_delete=models.PROTECT,default=None,db_comment="Fk de la categoria a la que pertenece el producto")
    tematicaProducto = models.ForeignKey(Tematicas,related_name='tematica_producto',on_delete=models.PROTECT,null=True,default=None,db_comment="Fk de la tematica a la que pertenece el producto")
    unidadMedidaProducto = models.CharField(max_length=15,choices=PESO_TORTAS,null=True,db_comment="Cantidad o peso de las tortas")
    saborProducto = models.CharField(max_length=15,choices=SABORES_TORTAS,null=True,db_comment="Tipo de sabor de la torta")
    estadoProducto = models.CharField(max_length=10,choices=ESTADOS_PRODUCTOS,default='Activo',db_comment="Estado de los productos")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self) -> str:
        return f"{self.nombreProducto}-{self.precioProducto}-{self.categoriaProducto}-{self.tematicaProducto}"
    
    def generar_qr(self, request: HttpRequest):
        producto_url = reverse('ver_producto', args=[str(self.id)])
        producto_url_abs = request.build_absolute_uri(producto_url)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(producto_url_abs)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        qr_img.save(buffer, format="PNG")
        filename = f"qr_{self.nombreProducto}.png"

        self.qrProducto.save(filename, File(buffer), save=False)
        self.save()
    
# class CarritoCompras(models.Model):
#     Carritoproducto = models.ForeignKey(Productos,related_name='producto_carrito',on_delete=models.PROTECT,default=None,db_comment="Hace referencia al producto del carrito")
#     Carritocliente = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='cliente_carrito',on_delete=models.PROTECT,default=None,db_comment="Hace referencia al Cliente")
#     fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
#     fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
#     def __str__(self) -> str:
#         return f"{self.Carritoproducto}"
    
class DetallePedido(models.Model):
    cantidadProducto = models.IntegerField(db_comment="Cantidad de productos que se el cliente comprará")
    costoProductos = models.IntegerField(db_comment="Costo acumulable de los productos que se van a pedir")
    detalleProducto = models.ForeignKey(Productos,related_name='producto_detalle',on_delete=models.PROTECT,default=None,db_comment="Llave forane de prodcutos")
    detallePedido = models.ForeignKey(Pedidos,related_name='pedido_detalle',on_delete=models.PROTECT,default=None,db_comment="Llave forane de pedidos")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self) -> str:
        return f"{self.cantidadProducto}-{self.costoProductos}"
    
class Ingredientes(models.Model):
    nombreIngrediente = models.CharField(max_length=20,db_comment="Nombre del ingrediente que se desea adicionar")
    precioIngrediente = models.IntegerField(db_comment="Precio unitario del ingrediente")
    cantidadIngrediente = models.IntegerField(db_comment="Cantidad del ingrediente que se adicionará")
    unidadMedida = models.CharField(max_length=50,null=True,db_comment="unidad de medida del ingrediente")
    color = models.CharField(max_length=30,null=True,db_comment="Color del ingrediente")
    sabor = models.CharField(max_length=30,null=True,db_comment="tipo de sabor del ingrediente si llegase a ser necesario")
    descripcionIngrediente = models.TextField(db_comment="descripción detallada del ingrediente")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self) -> str:
        return f"{self.nombreIngrediente}-{self.descripcion}"
    
class AdicionDetalle(models.Model):
    descripcionAdicion = models.TextField(db_comment="Descripción detallada de la adición que se la va a hacer al pedido")
    valorAdicion = models.IntegerField(db_comment="valor que le agregará al valor del pedio por realizar un adición extra")
    pedidoAdicion = models.ForeignKey(Pedidos,related_name='pedido_adicion',on_delete=models.PROTECT,default=None,db_comment="Fk del pedido al que se le hará la adición")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self) -> str:
        return f"{self.valorAdicion}"
    
class Comentarios(models.Model):
    contenidoComentario = models.TextField(db_comment="Contenido del comentario")
    usuarioComentario = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="comentario_usuario",default=None,on_delete=models.PROTECT,db_comment="FK del usuario que escribe el comentario")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    puntajeComentario = models.IntegerField(default=0,
                validators=[
                    MaxValueValidator(5),
                    MinValueValidator(0),
                ],db_comment="Puntaje de 1 a 5")
    
    def __str__(self) -> str:
        return f"{self.contenidoComentario}-{self.puntajeComentario}"
    
class ComentariosProductos(models.Model):
    contenidoComentarioProducto = models.TextField(db_comment="Contenido del comentario")
    productoComentarioProducto = models.ForeignKey(Productos,related_name="comentario_producto",default=None,on_delete=models.PROTECT,db_comment="FK del producto que se va a reseñar")
    usuarioComentarioProducto = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="comentario_usuarioProducto",default=None,on_delete=models.PROTECT,db_comment="FK del usuario que escribe el comentario")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    puntajeComentarioProducto = models.IntegerField(default=0,
                validators=[
                    MaxValueValidator(5),
                    MinValueValidator(0),
                ],db_comment="Puntaje de 1 a 5")
    
    def __str__(self) -> str:
        return f"{self.contenidoComentarioProducto}-{self.puntajeComentarioProducto}"
    
    
#  INSERSIONES SQL AUTOMATICAS

def insertarCategorias(sender, **kwargs):
    """
    Esta función se encarga de insertar categorías predeterminadas en la base de datos si aún no existen.
    Las categorías se utilizan para clasificar los productos.

    Args:
        sender: El objeto que envía la señal. No se utiliza en la función.
        **kwargs: Argumentos adicionales. No se utilizan en la función.

    Returns:
        None
    """
    if not Categorias.objects.exists():
        Categorias.objects.create(nombreCategoria="Tortas en pastillaje")
        Categorias.objects.create(nombreCategoria="Tortas en crema")
        Categorias.objects.create(nombreCategoria="Cupcakes")
        Categorias.objects.create(nombreCategoria="Galletas")

def insertarTematicas(sender, **kwargs):
    """
    Esta función se encarga de insertar temáticas predeterminadas en la base de datos si aún no existen.
    Las temáticas se utilizan para clasificar los productos según ocasiones especiales.

    Args:
        sender: El objeto que envía la señal. No se utiliza en la función.
        **kwargs: Argumentos adicionales. No se utilizan en la función.

    Returns:
        None
    """
    if not Tematicas.objects.exists():
        Tematicas.objects.create(nombreTematica="Cumpleaños")
        Tematicas.objects.create(nombreTematica="Bautizos")
        Tematicas.objects.create(nombreTematica="Primera comunión")
        Tematicas.objects.create(nombreTematica="Grados")
        Tematicas.objects.create(nombreTematica="Matrimonios")
        Tematicas.objects.create(nombreTematica="Aniversarios")
        Tematicas.objects.create(nombreTematica="Quinces")
        
def insertarRoles(sender, **kwargs):
    """
    Esta función se encarga de insertar roles predeterminados en la base de datos si aún no existen.
    Los roles se utilizan para asignar permisos y roles a los usuarios del sistema.

    Args:
        sender: El objeto que envía la señal. No se utiliza en la función.
        **kwargs: Argumentos adicionales. No se utiliza en la función.

    Returns:
        None
    """
    if not Group.objects.exists():
        Group.objects.create(name="Administrador")
        Group.objects.create(name="Cliente")
        

# Conecta la función a la señal post_migrate
@receiver(post_migrate)
def run_after_migrations(sender, **kwargs):
    """
    Esta función actúa como un decorador para ejecutar funciones después de que las migraciones se hayan aplicado
    satisfactoriamente. En este caso, se utiliza para insertar categorías, temáticas y roles predeterminados en la base
    de datos cuando la aplicación de migraciones está completa.

    Args:
        sender: El objeto que envía la señal. Se utiliza para verificar si las migraciones pertenecen a la aplicación
                'app_DAlbas'.
        **kwargs: Argumentos adicionales.

    Returns:
        None
    """
    if sender.name == 'app_DAlbas':
        insertarCategorias(sender, **kwargs)
        insertarTematicas(sender, **kwargs)
        insertarRoles(sender, **kwargs)