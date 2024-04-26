"""
URL configuration for project_DAlbas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.views.generic import RedirectView
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from app_DAlbas import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('',include('app_DAlbas.urls')),
    path("inicio/", views.inicio),
    path("", RedirectView.as_view(url="/inicio/")),
    path("vistaInicioNosotros/", views.vistaInicioNosotros),
    path("vistaProductos/", views.vistaInicioProductos),
    path("vistaInicioProductos/", views.mostrarProductos),
    path("vistaRegistrarCliente/", views.vistaRegistrarCliente),
    path("registrarCliente/", views.registrarCliente),
    path("vistaLogin/", views.vistaLogin, name="vistaLogin"),
    path("vistaPerfilUsuario/", views.vistaPerfilUsuario),
    path('login/', views.login, name='login'),
    path('cerrarSesion/', views.cerrarSesion),
    path('inicioAdministrador/', views.inicioAdministrador, name='inicioAdministrador'),
    path('inicioCliente/', views.inicioCliente, name='inicioCliente'),
    path('vistaRegistrarAdministrador/', views.vistaRegistrarAdministrador),
    path('registrarAdministrador/', views.registrarAdministrador),
    path('vistaRegistrarProducto/', views.vistaRegistrarProducto),
    path('registrarProductos/', views.registrarProductos),
    path('listarProductos/', views.listarProductos),
    path('nosotrosCliente/',views.nosotrosCliente),
    path('nosotrosAdministrador/',views.nosotrosAdministrador),
    path('productoCliente/',views.mostrarProductosCliente),
    path("vistaProductosCliente/", views.vistaProductosCliente),
    path('productoCremaCliente/',views.mostrarProductosCremaCliente),
    path("vistaProductoCremaCliente/", views.vistaProductosCremaCliente),
    path('productoCremaCliente/',views.mostrarProductosCupcakeCliente),
    path("vistaProductoCupcakeCliente/", views.vistaProductosCupcakeCliente),
    path('productoCremaCliente/',views.mostrarProductosGalletaCliente),
    path("vistaProductoGalletaCliente/", views.vistaProductosGalletaCliente),
    path('pedidoCliente',views.vistaRegistrarPedido),
    path("vistaRegistrarPedidos/", views.mostrarPedidosCliente),
    path('consultarProducto/<int:id>/',views.consultarProducto),
    path('actualizarProducto/',views.actualizarProductos),
    # path('vistaCarritoCompras/',views.vistaCarritoCompras),
    # path('eliminarProductoCarrito/',views.eliminarProductoCarrito),
    path('vistaCarrito/', views.vistaCarrito ),
    path('vistaPerfilAdministrador/',views.vistaPerfilAdministrador),
    path('tuVista/',views.tu_vista),
    path('setPassword_view/', views.setPassword_view),
    path('recuperarPassword/', views.recuperarPassword, name="recuperarPassword"),
    path('crearComentario/',views.crearComentario, name="crearComentario"),
    path('mostrarComentarios/',views.mostrarComentarios),
    path('mostrarComentariosCliente/',views.mostrarComentariosCliente),
    path('vistaRegistrarPedidoAdmin/',views.vistaRegistrarPedidoAdmin),
    path('registrarPedidoAdmin/',views.registrarPedidoAdmin, name="registrarPedidoAdmin"),
    path('vistaRegistrarUsuario/',views.vistaRegistrarUsuario),
    path('registrarUsuario/',views.registrarUsuario),
    path('vistaManual/', views.vistaManual),
    path('vistaListaUsuarios/', views.vistaListaUsuarios, name='vistaListaUsuarios'),
    path('vistaListaPedidosAdministrador/', views.vistaListaPedidosAdministrador),
    path('actualizarClientes/', views.actualizarCliente),
    path('consultarClientes/<int:id>/', views.consultarCliente),
    path('actualizarAdministrador/', views.actualizarAdmin),
    path('consultarAdministrador/<int:id>/', views.consultarAdmin),
        
    path('agregarProductoCarrito/<int:producto_id>/',views.agregarProductoCarrito, name="Add"),
    path('aumentarProductoCarrito/<int:producto_id>/',views.aumentarProductoCarrito, name="Aum"),
    path('eliminarProductoCarrito/<int:producto_id>/',views.eliminarProductoCarrito, name="Del"),
    path('restarProducto/<int:producto_id>/',views.restarProducto, name="Sub"),
    path('limpiarCarrito/',views.limpiarCarrito, name="CLS"),
    
    path('producto_tarjeta/<int:producto_id>/', views.ver_producto, name='ver_producto'),
    path('change_password/', views.change_password, name='change_password'),
    path('change_password_admin/', views.change_password_admin, name='change_password_admin'),
    
    path('vistaConfirmarAdministrador/', views.vistaConfirmarAdministrador, name='vistaConfirmarAdministrador'),
    path('vistaRegistrarAdministrador_inicio/', views.vistaRegistrarAdministrador_inicio, name='vistaRegistrarAdministrador_inicio'),
    path('verificarAdministrador/', views.verificarAdministrador, name='verificarAdministrador'),
    path('registrarUsuarioAdmin/', views.registrarUsuarioAdmin, name='registrarUsuarioAdmin'),
        
    path('actualizar_estado_pedido/', views.actualizar_estado_pedido, name='actualizar_estado_pedido'),
]

#Para poder tener acceso a la carpeta media y poder ver las fotos
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
