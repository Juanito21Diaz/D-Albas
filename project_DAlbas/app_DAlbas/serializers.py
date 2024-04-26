from rest_framework import serializers
from app_DAlbas.models import *
from drf_extra_fields.fields import Base64ImageField

# ----------------------------------------------------

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('__all__')
        
class UserSerializerJson(serializers.ModelSerializer):
    fotoUsuario = Base64ImageField(required=False)
    class Meta:
        model = User
        fields = ('__all__')
        
# ----------------------------------------------------
        
class ClientesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clientes
        fields = ('__all__')
        
# ----------------------------------------------------
        
class AdministradoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administradores
        fields = ('__all__')
        
# ----------------------------------------------------

class PedidosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedidos
        fields = ('__all__')
        
# ----------------------------------------------------

class DetalleProductoPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleProductoPedido
        fields = ('__all__')

class DetalleProductoPedidoSerializerJson(serializers.ModelSerializer):
    imagenPedidoDetalle = Base64ImageField(required=False)
    class Meta:
        model = DetalleProductoPedido
        fields = ('__all__')
        
# ----------------------------------------------------

class AbonosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Abonos
        fields = ('__all__')

class AbonosSerializerJson(serializers.ModelSerializer):
    fotoComprobanteAbono = Base64ImageField(required=False)
    class Meta:
        model = Abonos
        fields = ('__all__')
        
# ----------------------------------------------------

class CategoriasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorias
        fields = ('__all__')
        
# ----------------------------------------------------

class TematicasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tematicas
        fields = ('__all__')
        
# ----------------------------------------------------

class ProductosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Productos
        fields = ('__all__')

class ProductosSerializerJson(serializers.ModelSerializer):
    imagenProducto = Base64ImageField(required=False)
    class Meta:
        model = Productos
        fields = ('__all__')
        
# ----------------------------------------------------

class DetallePedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePedido
        fields = ('__all__')
        
# ----------------------------------------------------

class IngredientesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredientes
        fields = ('__all__')
        
# ----------------------------------------------------

class AdicionDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdicionDetalle
        fields = ('__all__')
        
# ----------------------------------------------------

class ComentariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comentarios
        fields = ('__all__')
        
# ----------------------------------------------------

class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('__all__')
        
# ----------------------------------------------------