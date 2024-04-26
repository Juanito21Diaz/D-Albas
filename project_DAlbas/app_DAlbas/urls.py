from django.urls import path
from . import views
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path('user',views.UserList.as_view()),
    path('user/<int:pk>',views.UserDetail.as_view()),
    path('userImagen/',views.UserImagen.as_view()),

    path('cliente',views.ClientesList.as_view()),
    path('cliente/<int:pk>',views.ClientesDetail.as_view()),

    path('administrador',views.AdministradoresList.as_view()),
    path('administrador/<int:pk>',views.AdministradoresDetail.as_view()),

    path('pedido',views.PedidosList.as_view()),
    path('pedido/<int:pk>',views.PedidosDetail.as_view()),

    path('detalleProductoPedido',views.DetalleProductoPedidoList.as_view()),
    path('detalleProductoPedido/<int:pk>',views.DetalleProductoPedidoDetail.as_view()),
    path('detalleProductoPedidoImagen/',views.DetalleProductoPedidoImagen.as_view()),

    path('abono',views.AbonosList.as_view()),
    path('abono/<int:pk>',views.AbonosDetail.as_view()),
    path('abonoImagen/',views.AbonoImagen.as_view()),

    path('categoria',views.CategoriasList.as_view()),
    path('categoria/<int:pk>',views.CategoriasDetail.as_view()),

    path('tematica',views.TematicasList.as_view()),
    path('tematica/<int:pk>',views.TematicasDetail.as_view()),

    path('producto',views.ProductosList.as_view()),
    path('producto/<int:pk>',views.ProductosDetail.as_view()),
    # path('producto/<int:proCodigo>',views.ProductosDetail.as_view()),
    path('productoImagen/',views.ProductoImagen.as_view()),

    path('detallePedido',views.DetallePedidoList.as_view()),
    path('detallePedido/<int:pk>',views.DetallePedidoDetail.as_view()),

    path('ingrediente',views.IngredientesList.as_view()),
    path('ingrediente/<int:pk>',views.IngredientesDetail.as_view()),

    path('adicionDetalle',views.AdicionDetalleList.as_view()),
    path('adicionDetalle/<int:pk>',views.AdicionDetalleDetail.as_view()),

    path('comentario',views.ComentariosList.as_view()),
    path('comentario/<int:pk>',views.ComentariosDetail.as_view()),

    path('rol',views.RolesList.as_view()),
    path('rol/<int:pk>',views.RolesDetail.as_view()),

    path('usuariosAPI/',views.UsuariosAPI.as_view()),
    path('productosPorCategoria/',views.ProductosPorCategoriaAPI.as_view()),
    path('productosPorTematica/',views.ProductosPorTematicaAPI.as_view()),
    path('productos/Tematica_Categoria/',views.ProductosPorCategoriaTematicaAPI.as_view()),
    path('pedidosPorUsuario/',views.PedidosPorUsuarioAPI.as_view()),
    path('productosMasVendidos/',views.ProductosMasVendidosAPI.as_view()),
    path('detalleUsuarioAPI/<int:pk>/',views.DetalleUsuarioAPI.as_view()),
    path('estadisticasComentariosAPI/',views.EstadisticasComentariosAPI.as_view()),
    path('diasCompraAPI/',views.DiasCompraAPI.as_view()),

    path('loginApi/<str:usuario>/<str:contrasena>/',views.loginApi),
    path('resetPasswordApi/<str:email>/',views.resetPasswordApi),
    path('registroClienteApi/<str:nombre>/<str:apellido>/<str:identificacion>/<str:telefono>/<str:correo>/<str:contrasena>/',views.registroClienteApi),

    path('docs/',include_docs_urls(title='Documentación API')),
]