from django.db.models.functions import ExtractMonth, ExtractWeek, TruncMonth
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Sum, Max, Count, Avg, Prefetch
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import gettext as _
from django.template.loader import get_template
from rest_framework.generics import ListAPIView
from datetime import date, datetime, timedelta
from django.contrib.auth.models import Group
from rest_framework.response import Response
from django.core.paginator import Paginator             
from matplotlib.ticker import MaxNLocator
from django.contrib import auth, messages
from django.db import Error, transaction
from rest_framework.views import APIView
# from app_DAlbas.pedidoPdf import PDF
from app_DAlbas.Carrito import Carrito
from email.mime.text import MIMEText
from django.http import JsonResponse
from app_DAlbas.serializers import *
from rest_framework import generics
from smtplib import SMTPException
from rest_framework import status
from django.conf import settings
from app_DAlbas.models import *
import matplotlib.pyplot as plt
from django.urls import reverse
from collections import Counter
from decimal import Decimal
from django import forms
import qrcode.image.svg
from io import BytesIO
import urllib.request
import urllib.parse
import numpy as np
import matplotlib
import threading
#import requests
import calendar
import smtplib
import sqlite3
import urllib
import random
import atexit
import string
import locale
import qrcode
import base64
import json
import time
import os
import re

# Create your views here.

class MyPagination(PageNumberPagination):
    """
    Esta clase extiende la clase base 'PageNumberPagination' de Django REST framework
    y personaliza la paginación para las vistas de la API. Permite configurar el número
    de objetos por página y el tamaño máximo de la página.

    Atributos:
    page_size (int): Número de objetos por página.
    page_size_query_param (str): Parámetro de consulta utilizado para especificar el tamaño de la página.
    max_page_size (int): Tamaño máximo permitido para una página.
    """
    page_size = 10 
    page_size_query_param = 'page_size'
    max_page_size = 100 

# API RESTFRAMEWOR

class UsuariosAPI(APIView):
    def get(self, request):
        """
        Maneja la solicitud GET para obtener la cantidad de administradores y clientes registrados.
        Retorna un JSON que muestra la cantidad de administradores y clientes.

        Args:
            request (HttpRequest): La solicitud HTTP recibida.

        Returns:
            Response: Un objeto Response con la cantidad de administradores y clientes.
        """
        administradores_count = Administradores.objects.count()

        clientes_count = Clientes.objects.count()

        data = {
            'cantidad_administradores': administradores_count,
            'cantidad_clientes': clientes_count,
        }

        return Response(data, status=status.HTTP_200_OK)

class ProductosPorCategoriaAPI(APIView):
    def get(self, request):
        """
        Maneja la solicitud GET para obtener la cantidad de productos por categoría.
        Retorna un JSON que muestra el nombre de cada categoría y la cantidad de productos asociados.

        Args:
            request (HttpRequest): La solicitud HTTP recibida.

        Returns:
            Response: Un objeto Response con la cantidad de productos por categoría.
        """
        categorias_con_numero_de_productos = Categorias.objects.annotate(numero_de_productos=Count('categoria_producto'))
        
        data = []
        for categoria in categorias_con_numero_de_productos:
            data.append({
                'categoria': categoria.nombreCategoria,
                'numero_de_productos': categoria.numero_de_productos,
            })
        
        return Response(data, status=status.HTTP_200_OK)
    
class ProductosPorTematicaAPI(APIView):
    def get(self, request):
        """
        Maneja la solicitud GET para obtener la cantidad de productos por temática.
        Retorna un JSON que muestra el nombre de cada temática y la cantidad de productos asociados.

        Args:
            request (HttpRequest): La solicitud HTTP recibida.

        Returns:
            Response: Un objeto Response con la cantidad de productos por temática.
        """
        tematicas_con_numero_de_productos = Tematicas.objects.annotate(numero_de_productos=Count('tematica_producto'))
        
        data = []
        
        for tematica in tematicas_con_numero_de_productos:
            data.append({
                'tematica': tematica.nombreTematica,
                'numero_de_productos': tematica.numero_de_productos,
            })
        
        return Response(data, status=status.HTTP_200_OK)
    
class ProductosPorCategoriaTematicaAPI(APIView):
    def get(self, request):
        """
        Maneja la solicitud GET para obtener la cantidad de productos por categoría y temática.
        Retorna un JSON que muestra el nombre de cada categoría/temática y la cantidad de productos asociados.

        Args:
            request (HttpRequest): La solicitud HTTP recibida.

        Returns:
            Response: Un objeto Response con la cantidad de productos por categoría y temática.
        """
        categorias_con_numero_de_productos = Categorias.objects.annotate(numero_de_productos=Count('categoria_producto'))
        tematicas_con_numero_de_productos = Tematicas.objects.annotate(numero_de_productos=Count('tematica_producto'))
        
        data = {
            'categorias': [],
            'tematicas': [],
        }
        
        for categoria in categorias_con_numero_de_productos:
            data['categorias'].append({
                'categoria': categoria.nombreCategoria,
                'numero_de_productos': categoria.numero_de_productos,
            })
        
        for tematica in tematicas_con_numero_de_productos:
            data['tematicas'].append({
                'tematica': tematica.nombreTematica,
                'numero_de_productos': tematica.numero_de_productos,
            })
        
        return Response(data, status=status.HTTP_200_OK)
    
class PedidosPorUsuarioAPI(APIView):
    def get(self, request):
        """
        Maneja la solicitud GET para obtener la cantidad de pedidos por usuario.
        Retorna un JSON que muestra el nombre completo del usuario, su correo y la cantidad de pedidos que ha realizado.

        Args:
            request (HttpRequest): La solicitud HTTP recibida.

        Returns:
            Response: Un objeto Response con la cantidad de pedidos por usuario.
        """
        pedidos_por_usuario = User.objects.annotate(numero_de_pedidos=Count('pedido_usuario'))

        data = []

        for usuario in pedidos_por_usuario:
            nombre_completo = f"{usuario.first_name} {usuario.last_name}"
            data.append({
                'nombre_usuario': nombre_completo,
                'correo': usuario.username,
                'cantidad_pedidos': usuario.numero_de_pedidos,
            })

        return Response(data, status=status.HTTP_200_OK)

class ProductosMasVendidosAPI(APIView):
    def get(self, request):
        """
        Maneja la solicitud GET para obtener los productos más vendidos.
        Retorna un JSON que muestra los nombres de los productos más vendidos y la cantidad vendida de cada uno.

        Args:
            request (HttpRequest): La solicitud HTTP recibida.

        Returns:
            Response: Un objeto Response con los productos más vendidos.
        """
        productos_mas_vendidos = DetallePedido.objects.values('detalleProducto__nombreProducto') \
            .annotate(cantidad_vendida=Sum('cantidadProducto')) \
            .order_by('-cantidad_vendida')[:5]  # Obtener los 5 productos más vendidos

        productos_data = []
        for producto in productos_mas_vendidos:
            productos_data.append({
                'producto': producto['detalleProducto__nombreProducto'],
                'cantidad_vendida': producto['cantidad_vendida'],
            })

        return Response({'productos_mas_vendidos': productos_data}, status=status.HTTP_200_OK)
    
class DetalleUsuarioAPI(APIView):
    def get(self, request, pk):
        """
        Maneja la solicitud GET para obtener detalles de un usuario por su ID.

        Args:
            request (HttpRequest): La solicitud HTTP recibida.
            pk (int): La clave primaria (ID) del usuario que se desea obtener.

        Returns:
            Response: Un objeto Response con los detalles del usuario o un mensaje de error si no se encuentra el usuario.
        """
        try:
            usuario = User.objects.get(pk=pk)
            data = {
                'id': usuario.id,
                'username': usuario.username,
                'first_name': usuario.first_name,
                'last_name': usuario.last_name,
                'fotoUsuario': usuario.fotoUsuario.url if usuario.fotoUsuario else None,
                'tipoUsuario': usuario.get_tipoUsuario_display(), 
                'estadoUsuario': usuario.get_estadoUsuario_display(), 
                'fechaHoraCreacion': usuario.fechaHoraCreacion,
                'fechaHoraActualizacion': usuario.fechaHoraActualizacion,
            }
            return Response(data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
class EstadisticasComentariosAPI(APIView):
    def get(self, request):
        """
        Maneja la solicitud GET para calcular estadísticas de comentarios por puntaje.
        Retorna un JSON que muestra la cantidad de comentarios y los detalles de cada comentario por puntaje.

        Args:
            request (HttpRequest): La solicitud HTTP recibida.

        Returns:
            Response: Un objeto Response con estadísticas de comentarios por puntaje.
        """
        estadisticas = {
            '1_estrellas': {
                'cantidad': 0,
                'comentarios': [],
            },
            '2_estrellas': {
                'cantidad': 0,
                'comentarios': [],
            },
            '3_estrellas': {
                'cantidad': 0,
                'comentarios': [],
            },
            '4_estrellas': {
                'cantidad': 0,
                'comentarios': [],
            },
            '5_estrellas': {
                'cantidad': 0,
                'comentarios': [],
            },
        }

        comentarios = Comentarios.objects.all()
        for comentario in comentarios:
            puntaje = comentario.puntajeComentario
            if puntaje >= 1 and puntaje <= 5:
                clave = f'{puntaje}_estrellas'
                estadisticas[clave]['cantidad'] += 1
                estadisticas[clave]['comentarios'].append({
                    'contenido': comentario.contenidoComentario,
                    'usuario': comentario.usuarioComentario.username,
                    'fecha_creacion': comentario.fechaHoraCreacion,
                })

        return Response(estadisticas, status=status.HTTP_200_OK)
    
class DiasCompraAPI(APIView):
    def get(self, request):
        """
        Maneja la solicitud GET para obtener estadísticas de pedidos por día de la semana.
        Retorna un JSON que muestra el total de pedidos por día de la semana y detalles por día.

        Args:
            request (HttpRequest): La solicitud HTTP recibida.

        Returns:
            Response: Un objeto Response con la información de los pedidos por día de la semana.
        """
        # Mapeo de días en inglés a días en español
        dias_mapping = {
            'Monday': _('lunes'),
            'Tuesday': _('martes'),
            'Wednesday': _('miércoles'),
            'Thursday': _('jueves'),
            'Friday': _('viernes'),
            'Saturday': _('sábado'),
            'Sunday': _('domingo'),
        }

        pedidos_por_dia = Pedidos.objects.extra({'dia_pedido': "date(fechaPedido)"}).values('dia_pedido').annotate(cantidad_pedidos=Count('id'))

        resultados = {}

        for pedido in pedidos_por_dia:
            fecha_pedido = datetime.strptime(pedido['dia_pedido'], '%Y-%m-%d')
            cantidad_pedidos = pedido['cantidad_pedidos']
            dia_semana = fecha_pedido.strftime('%A')  # Obtiene el nombre del día de la semana

            if dia_semana not in resultados:
                resultados[dia_semana] = {
                    'nombre_dia': dias_mapping.get(dia_semana, dia_semana),
                    'total_pedidos': 0,
                    'dias': []
                }

            resultados[dia_semana]['total_pedidos'] += cantidad_pedidos
            resultados[dia_semana]['dias'].append({
                'fecha': fecha_pedido.strftime('%Y-%m-%d'),
                'cantidad_pedidos': cantidad_pedidos,
            })

        return Response(resultados, status=200)

# -----------------------------------------------------

class UserList(generics.ListCreateAPIView):
    """
    Esta clase define una vista que permite listar y crear objetos de usuario utilizando
    Django REST framework. Utiliza el modelo 'User' y el serializador 'UserSerializer' para
    gestionar las operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de usuario.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de usuario.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # pagination_class = MyPagination
    
class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Esta clase define una vista que permite recuperar, actualizar y eliminar objetos de usuario utilizando
    Django REST framework. Utiliza el modelo 'User' y el serializador 'UserSerializer' para
    gestionar estas operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de usuario.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de usuario.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserImagen(APIView):
    """
    Esta clase define una vista que permite crear objetos de usuario con una imagen asociada.
    Utiliza el serializador 'UserSerializerJson' para validar y procesar los datos del usuario
    junto con la imagen. La imagen se renombra como 'usuario.png' antes de guardarla junto con el usuario.
    """
    def post(self,request):
        """
        Maneja las solicitudes POST para crear un usuario con una imagen.
        
        Args:
            request (HttpRequest): La solicitud HTTP POST que contiene los datos del usuario y la imagen.

        Returns:
            Response: Devuelve el objeto de usuario y su información si se crea con éxito,
                    o errores de validación si la solicitud no es válida.
        """
        serializer = UserSerializerJson(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            archivo = validated_data['fotoUsuario']
            archivo.name = 'usuario.png'
            validated_data['fotoUsuario'] = archivo
            user = User(**validated_data)
            user.save()
            serializer_response = UserSerializer(user)
            return Response(serializer_response.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# -----------------------------------------------------

class ClientesList(generics.ListCreateAPIView):
    """
    Esta clase define una vista que permite listar y crear objetos de clientes utilizando
    Django REST framework. Utiliza el modelo 'Clientes' y el serializador 'ClientesSerializer' para
    gestionar las operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de clientes.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de clientes.
    """
    queryset = Clientes.objects.all()
    serializer_class = ClientesSerializer
    # pagination_class = MyPagination
    
class ClientesDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Esta clase define una vista que permite recuperar, actualizar y eliminar objetos de clientes utilizando
    Django REST framework. Utiliza el modelo 'Clientes' y el serializador 'ClientesSerializer' para
    gestionar estas operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de clientes.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de clientes.
    """
    queryset = Clientes.objects.all()
    serializer_class = ClientesSerializer
    
# -----------------------------------------------------

class AdministradoresList(generics.ListCreateAPIView):
    """
    Esta clase define una vista que permite listar y crear objetos de administradores utilizando
    Django REST framework. Utiliza el modelo 'Administradores' y el serializador 'AdministradoresSerializer' para
    gestionar las operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de administradores.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de administradores.
    """
    queryset = Administradores.objects.all()
    serializer_class = AdministradoresSerializer
    # pagination_class = MyPagination
    
class AdministradoresDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Esta clase define una vista que permite recuperar, actualizar y eliminar objetos de administradores utilizando
    Django REST framework. Utiliza el modelo 'Administradores' y el serializador 'AdministradoresSerializer' para
    gestionar estas operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de administradores.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de administradores.
    """
    queryset = Administradores.objects.all()
    serializer_class = AdministradoresSerializer
    
# -----------------------------------------------------

class PedidosList(generics.ListCreateAPIView):
    """
    Esta clase define una vista que permite listar y crear objetos de pedidos utilizando
    Django REST framework. Utiliza el modelo 'Pedidos' y el serializador 'PedidosSerializer' para
    gestionar las operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de pedidos.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de pedidos.
    """
    queryset = Pedidos.objects.all()
    serializer_class = PedidosSerializer
    # pagination_class = MyPagination
    
class PedidosDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Esta clase define una vista que permite recuperar, actualizar y eliminar objetos de pedidos utilizando
    Django REST framework. Utiliza el modelo 'Pedidos' y el serializador 'PedidosSerializer' para
    gestionar estas operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de pedidos.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de pedidos.
    """
    queryset = Pedidos.objects.all()
    serializer_class = PedidosSerializer

# -----------------------------------------------------

class DetalleProductoPedidoList(generics.ListCreateAPIView):
    """
    Esta clase define una vista que permite listar y crear objetos de detalles de producto de pedidos utilizando
    Django REST framework. Utiliza el modelo 'DetalleProductoPedido' y el serializador 'DetalleProductoPedidoSerializer'
    para gestionar las operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de detalles de producto de pedidos.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de detalles de producto de pedidos.
    """
    queryset = DetalleProductoPedido.objects.all()
    serializer_class = DetalleProductoPedidoSerializer
    # pagination_class = MyPagination
    
class DetalleProductoPedidoDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Esta clase define una vista que permite recuperar, actualizar y eliminar objetos de detalles de producto de pedidos
    utilizando Django REST framework. Utiliza el modelo 'DetalleProductoPedido' y el serializador 'DetalleProductoPedidoSerializer'
    para gestionar estas operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de detalles de producto de pedidos.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de detalles de producto de pedidos.
    """
    queryset = DetalleProductoPedido.objects.all()
    serializer_class = DetalleProductoPedidoSerializer
    
class DetalleProductoPedidoImagen(APIView):
    """
    Esta clase define una vista que permite crear objetos de detalles de producto de pedidos con una imagen asociada.
    Utiliza el serializador 'DetalleProductoPedidoSerializerJson' para validar y procesar los datos del detalle de producto
    junto con la imagen. La imagen se renombra como 'pedido_cliente.png' antes de guardarla junto con el detalle de producto.
    """
    def post(self,request):
        """
        Maneja las solicitudes POST para crear un detalle de producto de pedido con una imagen.

        Args:
            request (HttpRequest): La solicitud HTTP POST que contiene los datos del detalle de producto y la imagen.

        Returns:
            Response: Devuelve el objeto de detalle de producto y su información si se crea con éxito,
                    o errores de validación si la solicitud no es válida.
        """
        serializer = DetalleProductoPedidoSerializerJson(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            archivo = validated_data['imagenPedidoDetalle']
            archivo.name = 'pedido_cliente.png'
            validated_data['imagenPedidoDetalle'] = archivo
            detalleProduct = DetalleProductoPedido(**validated_data)
            detalleProduct.save()
            serializer_response = DetalleProductoPedidoSerializer(detalleProduct)
            return Response(serializer_response.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# -----------------------------------------------------

class AbonosList(generics.ListCreateAPIView):
    """
    Esta clase define una vista que permite listar y crear objetos de abonos utilizando
    Django REST framework. Utiliza el modelo 'Abonos' y el serializador 'AbonosSerializer'
    para gestionar las operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de abonos.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de abonos.
    """
    queryset = Abonos.objects.all()
    serializer_class = AbonosSerializer
    # pagination_class = MyPagination
    
class AbonosDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Esta clase define una vista que permite recuperar, actualizar y eliminar objetos de abonos
    utilizando Django REST framework. Utiliza el modelo 'Abonos' y el serializador 'AbonosSerializer'
    para gestionar estas operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de abonos.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de abonos.
    """
    queryset = Abonos.objects.all()
    serializer_class = AbonosSerializer
    
class AbonoImagen(APIView):
    """
    Esta clase define una vista que permite crear objetos de abonos con una imagen de comprobante de abono asociada.
    Utiliza el serializador 'AbonosSerializerJson' para validar y procesar los datos del abono junto con la imagen del comprobante.
    La imagen se renombra como 'comprobante_abono.png' antes de guardarla junto con el abono.
    """
    def post(self,request):
        """
        Maneja las solicitudes POST para crear un abono con una imagen de comprobante de abono.

        Args:
            request (HttpRequest): La solicitud HTTP POST que contiene los datos del abono y la imagen del comprobante.

        Returns:
            Response: Devuelve el objeto de abono y su información si se crea con éxito,
                    o errores de validación si la solicitud no es válida.
        """
        serializer = AbonosSerializerJson(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            archivo = validated_data['fotoComprobanteAbono']
            archivo.name = 'comprobante_abono.png'
            validated_data['fotoComprobanteAbono'] = archivo
            abono = Abonos(**validated_data)
            abono.save()
            serializer_response = AbonosSerializer(abono)
            return Response(serializer_response.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -----------------------------------------------------

class CategoriasList(generics.ListCreateAPIView):
    """
    Esta clase define una vista que permite listar y crear objetos de categorías utilizando
    Django REST framework. Utiliza el modelo 'Categorias' y el serializador 'CategoriasSerializer'
    para gestionar las operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de categorías.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de categorías.
    """
    queryset = Categorias.objects.all()
    serializer_class = CategoriasSerializer
    # pagination_class = MyPagination
    
class CategoriasDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Esta clase define una vista que permite recuperar, actualizar y eliminar objetos de categorías
    utilizando Django REST framework. Utiliza el modelo 'Categorias' y el serializador 'CategoriasSerializer'
    para gestionar estas operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de categorías.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de categorías.
    """
    queryset = Categorias.objects.all()
    serializer_class = CategoriasSerializer
    
# -----------------------------------------------------

class TematicasList(generics.ListCreateAPIView):
    """
    Esta clase define una vista que permite listar y crear objetos de temáticas utilizando
    Django REST framework. Utiliza el modelo 'Tematicas' y el serializador 'TematicasSerializer'
    para gestionar las operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de temáticas.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de temáticas.
    """
    queryset = Tematicas.objects.all()
    serializer_class = TematicasSerializer
    # pagination_class = MyPagination
    
class TematicasDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Esta clase define una vista que permite recuperar, actualizar y eliminar objetos de temáticas
    utilizando Django REST framework. Utiliza el modelo 'Tematicas' y el serializador 'TematicasSerializer'
    para gestionar estas operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de temáticas.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de temáticas.
    """
    queryset = Tematicas.objects.all()
    serializer_class = TematicasSerializer
    
# -----------------------------------------------------

class ProductosList(generics.ListCreateAPIView):
    """
    Esta clase define una vista que permite listar y crear objetos de productos utilizando
    Django REST framework. Utiliza el modelo 'Productos' y el serializador 'ProductosSerializer'
    para gestionar las operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de productos.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de productos.
    """
    queryset = Productos.objects.all()
    serializer_class = ProductosSerializer
    # pagination_class = MyPagination
    
class ProductosDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Esta clase define una vista que permite recuperar, actualizar y eliminar objetos de productos
    utilizando Django REST framework. Utiliza el modelo 'Productos' y el serializador 'ProductosSerializer'
    para gestionar estas operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de productos.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de productos.
    """
    queryset = Productos.objects.all()
    serializer_class = ProductosSerializer
    
class ProductoImagen(APIView):
    """
    Esta clase define una vista que permite crear objetos de producto con una imagen asociada.
    Utiliza el serializador 'ProductosSerializerJson' para validar y procesar los datos del producto
    junto con la imagen. La imagen se renombra como 'producto.png' antes de guardarla junto con el producto.
    """
    def post(self,request):
        """
        Maneja las solicitudes POST para crear un producto con una imagen.
        
        Args:
            request (HttpRequest): La solicitud HTTP POST que contiene los datos del producto y la imagen.

        Returns:
            Response: Devuelve el objeto de producto y su información si se crea con éxito,
                    o errores de validación si la solicitud no es válida.
        """
        serializer = ProductosSerializerJson(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            archivo = validated_data['imagenProducto']
            archivo.name = 'producto.png'
            validated_data['imagenProducto'] = archivo
            producto = Productos(**validated_data)
            producto.save()
            serializer_response = ProductosSerializer(producto)
            return Response(serializer_response.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# -----------------------------------------------------

class DetallePedidoList(generics.ListCreateAPIView):
    """
    Esta clase define una vista que permite listar y crear objetos de detalles de pedido utilizando
    Django REST framework. Utiliza el modelo 'DetallePedido' y el serializador 'DetallePedidoSerializer'
    para gestionar las operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de detalles de pedido.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de detalles de pedido.
    """
    queryset = DetallePedido.objects.all()
    serializer_class = DetallePedidoSerializer
    # pagination_class = MyPagination
    
class DetallePedidoDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Esta clase define una vista que permite recuperar, actualizar y eliminar objetos de detalles de pedido
    utilizando Django REST framework. Utiliza el modelo 'DetallePedido' y el serializador 'DetallePedidoSerializer'
    para gestionar estas operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de detalles de pedido.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de detalles de pedido.
    """
    queryset = DetallePedido.objects.all()
    serializer_class = DetallePedidoSerializer
    
# -----------------------------------------------------

class IngredientesList(generics.ListCreateAPIView):
    """
    Esta clase define una vista que permite listar y crear objetos de ingredientes utilizando
    Django REST framework. Utiliza el modelo 'Ingredientes' y el serializador 'IngredientesSerializer'
    para gestionar las operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de ingredientes.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de ingredientes.
    """
    queryset = Ingredientes.objects.all()
    serializer_class = IngredientesSerializer
    # pagination_class = MyPagination
    
class IngredientesDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Esta clase define una vista que permite recuperar, actualizar y eliminar objetos de ingredientes
    utilizando Django REST framework. Utiliza el modelo 'Ingredientes' y el serializador 'IngredientesSerializer'
    para gestionar estas operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de ingredientes.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de ingredientes.
    """
    queryset = Ingredientes.objects.all()
    serializer_class = IngredientesSerializer
    
# -----------------------------------------------------

class AdicionDetalleList(generics.ListCreateAPIView):
    """
    Esta clase define una vista que permite listar y crear objetos de adiciones de detalles utilizando
    Django REST framework. Utiliza el modelo 'AdicionDetalle' y el serializador 'AdicionDetalleSerializer'
    para gestionar las operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de adiciones de detalles.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de adiciones de detalles.
    """
    queryset = AdicionDetalle.objects.all()
    serializer_class = AdicionDetalleSerializer
    # pagination_class = MyPagination
    
class AdicionDetalleDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Esta clase define una vista que permite recuperar, actualizar y eliminar objetos de adiciones de detalles
    utilizando Django REST framework. Utiliza el modelo 'AdicionDetalle' y el serializador 'AdicionDetalleSerializer'
    para gestionar estas operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de adiciones de detalles.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de adiciones de detalles.
    """
    queryset = AdicionDetalle.objects.all()
    serializer_class = AdicionDetalleSerializer
    
# -----------------------------------------------------

class ComentariosList(generics.ListCreateAPIView):
    """
    Esta clase define una vista que permite listar y crear objetos de comentarios utilizando
    Django REST framework. Utiliza el modelo 'Comentarios' y el serializador 'ComentariosSerializer'
    para gestionar las operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de comentarios.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de comentarios.
    """
    queryset = Comentarios.objects.all()
    serializer_class = ComentariosSerializer
    # pagination_class = MyPagination
    
class ComentariosDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Esta clase define una vista que permite recuperar, actualizar y eliminar objetos de comentarios
    utilizando Django REST framework. Utiliza el modelo 'Comentarios' y el serializador 'ComentariosSerializer'
    para gestionar estas operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de comentarios.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de comentarios.
    """
    queryset = Comentarios.objects.all()
    serializer_class = ComentariosSerializer
    
# -----------------------------------------------------

class RolesList(generics.ListCreateAPIView):
    """
    Esta clase define una vista que permite listar y crear objetos de roles utilizando
    Django REST framework. Utiliza el modelo 'Group' y el serializador 'RolesSerializer'
    para gestionar las operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de roles.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de roles.
    """
    queryset = Group.objects.all()
    serializer_class = RolesSerializer
    # pagination_class = MyPagination
    
class RolesDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Esta clase define una vista que permite recuperar, actualizar y eliminar objetos de roles
    utilizando Django REST framework. Utiliza el modelo 'Group' y el serializador 'RolesSerializer'
    para gestionar estas operaciones.

    Atributos:
    ----------
    queryset (QuerySet): Conjunto de consultas que representa todos los objetos de roles.
    serializer_class (Serializer): Clase del serializador utilizada para serializar y deserializar
                                   los objetos de roles.
    """
    queryset = Group.objects.all()
    serializer_class = RolesSerializer
    
# -----------------------------------------------------

def loginApi(request, usuario, contrasena):
    """
    Vista de API para el inicio de sesión de usuarios.

    Permite a los usuarios iniciar sesión y devuelve información del usuario autenticado,
    incluyendo la foto de usuario en formato base64 si está disponible.

    Args:
        request (HttpRequest): La solicitud HTTP.
        usuario (str): Nombre de usuario del usuario que intenta iniciar sesión.
        contrasena (str): Contraseña del usuario que intenta iniciar sesión.

    Returns:
        JsonResponse: Un objeto JSON que contiene información sobre el resultado del inicio de sesión.
    """
    try:
        username = usuario
        password = contrasena

        try:
            client = User.objects.get(username=usuario)

            if not client.check_password(contrasena):
                return JsonResponse({'mensaje': 'La contraseña es incorrecta.', 'estado': False})
        
        except User.DoesNotExist:
            return JsonResponse({'mensaje': 'El usuario no existe.', 'estado': False})

        user = authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            if user.groups.filter(name='Cliente').exists():
                cliente = Clientes.objects.get(username=user.username)

                foto_base64 = None
                if cliente.fotoUsuario:
                    with open(cliente.fotoUsuario.path, "rb") as image_file:
                        foto_base64 = base64.b64encode(image_file.read()).decode('utf-8')

                return JsonResponse({
                    'mensaje': 'Inicio de sesión exitoso',
                    'estado': True,
                    'username': cliente.username,
                    'correo': cliente.email,
                    'nombre': cliente.first_name,
                    'apellidos': cliente.last_name,
                    'identificacionCliente': cliente.identificacionCliente,
                    'telefonoCliente': cliente.telefonoCliente,
                    'tipoUsuario': cliente.tipoUsuario,
                    'fotoUsuario': foto_base64,
                })
            else:
                mensaje = "Solos los clientes pueden ingresar"
                return JsonResponse({'mensaje':mensaje, 'estado':False})
        else:
            mensaje = "El usuario o contraseña son incorrectas"
            return JsonResponse({'mensaje': mensaje, 'estado': False})
    except Exception as e:
        return JsonResponse({'mensaje': str(e), 'estado': False})
    
def resetPasswordApi(request, email):
    try:
        username = email
        if not is_valid_email(email):
            return JsonResponse({'mensaje': 'El correo electrónico no tiene un formato válido.', 'estado': False})
        
        try:
            user = User.objects.get(email=username)
            
            newPassword = generarPassword()
            user.set_password(newPassword)
            user.save()
            
            asunto = "Reset Password - D'Albas Pastelería"
            contenido = f"""
                        <html>
                            <head></head>
                            <body>
                                <p>Cordial saludo, {user.first_name} {user.last_name}.</p>
                                <p>Hemos recibido una solicitud para cambiar la contraseña de su cuenta en la pasteleria D'Albas.</p>
                                <p>Si usted no realizó esta solicitud, por favor ignore este correo.</p>
                                <ul>
                                    <li>Nueva contraseña: {newPassword}</li>
                                </ul>
                            </body>
                        </html>
                        """

            threa = threading.Thread(
                target=enviarCorreo, args=(asunto, contenido, user.email))
            threa.start()
            
            mensaje = "Contraseña restablecida, revisa tu correo"
            return JsonResponse({'new_password':newPassword,'mensaje':mensaje, 'estado':True})
        
        except User.DoesNotExist:
            return JsonResponse({'mensaje': 'No existe ningún usuario con ese correo electrónico.', 'estado': False})
    except Exception as e:
        return JsonResponse({"mensaje": str(e), "estado":False})
    
def registroClienteApi(request, nombre, apellido, identificacion, telefono, correo, contrasena): 
    try:
        nombres = nombre
        apellidos = apellido
        num_idenf = identificacion
        num_tel = telefono
        e_mail = correo
        password = contrasena
        tipo_user = "Cliente"
        idRol = 2
        
        phone = f"+57{num_tel}"
        
        with transaction.atomic():
            user = Clientes(identificacionCliente=num_idenf,
                            telefonoCliente=phone,
                            username = e_mail,
                            first_name = nombres,
                            last_name = apellidos,
                            email = e_mail,
                            password = password,
                            tipoUsuario = tipo_user)
            user.save()
            rol = Group.objects.get(pk=idRol)
            user.groups.add(rol)
            
            user.save()
            print(f"password: {password}")
            user.set_password(password)
            user.save()
            
            asunto = "Registro Cliente - D'Albas Pastelería"
            contenido = f"""
                    <html>
                        <head></head>
                        <body>
                            <p>Cordial saludo, {user.first_name} {user.last_name}.</p>
                            <p>¡Bienvenido(a) a nuestro sistema D'Albas! Su registro ha sido exitoso.</p>
                            <p>A continuación, le proporcionamos sus datos de acceso:</p>
                            <ul>
                                <li>Nombre de usuario: {user.username}</li>
                                <li>Contraseña: {password}</li>
                            </ul>
                            <p>Le recomendamos que mantenga su contraseña confidencial y no la comparta con nadie.</p>
                            <p>Por favor, ingrese al sistema utilizando los datos de acceso establecidos</p>
                            <p>Si tiene alguna pregunta o necesita ayuda, no dude en contactarnos:</p>
                            <ul>
                                <li>Teléfonos: 3185504427 - 3178860724</li>
                                <li>Correo: dalbas.288@gmail.com</li>
                            </ul>
                            <p class="">Te invitamos a que visites nuestra página de <a href="https://www.facebook.com/dalbaspasteleria" style="text-decoration: none; color: #F26699;">Facebook</a>.</p>
                        </body>
                    </html>
                    """
            threa = threading.Thread(target=enviarCorreo, args=(asunto, contenido, user.email))
            threa.start()
            
            mensaje = "El registro se realizo con exito"
            return JsonResponse({'mensaje':mensaje, 'estado':True})
        
    except Exception as e:
        return JsonResponse({"mensaje": str(e), "estado":False})
    
# -----------------------------------------------------

def is_valid_email(email):
    email_regex = r'^[\w\.-]+@[\w\.-]+$'
    return re.match(email_regex, email)

def es_administrador(user):
    return user.groups.filter(name='Administrador').exists()

def es_cliente(user):
    return user.groups.filter(name='Cliente').exists()

# -----------------------------------------------------

# VISTAS INICIALES

def inicio(request):
    """
    Muestra la página de inicio y carga los últimos 6 comentarios.

    Esta función se utiliza para renderizar la página de inicio de la aplicación web.
    Recupera los últimos 6 comentarios almacenados en la base de datos y los pasa al
    contexto de la plantilla 'inicio.html' para su visualización.

    Args:
        request (HttpRequest): La solicitud HTTP realizada por el cliente.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza la página de inicio junto con los comentarios.
    """
    comentarios = Comentarios.objects.all().order_by('-fechaHoraCreacion')[:6]

    context = {
        'comentarios': comentarios
    }
    return render(request, 'inicio.html', context)

def page_not_found_view(request, exception):
    """
    Maneja errores 404 (Página no encontrada).

    Esta vista toma dos argumentos:
    - request: La solicitud HTTP que generó el error.
    - exception: La excepción que provocó el error (generalmente es una instancia de Http404).

    Devuelve una respuesta HTTP con código de estado 404 y renderiza la plantilla 'error.html'.

    Args:
        request (HttpRequest): La solicitud HTTP que generó el error.
        exception (Http404 o subclass): La excepción que provocó el error.

    Returns:
        HttpResponse: Una respuesta HTTP con código de estado 404 y la plantilla 'error.html' renderizada.
    """
    return render(request, 'error.html', status=404)

def vistaInicioProductos(request):
    """
    Muestra la página de productos.

    Esta función se utiliza para renderizar la página de productos de la aplicación web.

    Args:
        request (HttpRequest): La solicitud HTTP realizada por el cliente.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza la página de productos.
    """
    return render(request, "productos.html")

def vistaInicioNosotros(request):
    """
    Muestra la página 'Nosotros'.

    Esta función se utiliza para renderizar la página 'Nosotros.html' de la aplicación web.

    Args:
        request (HttpRequest): La solicitud HTTP realizada por el cliente.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza la página 'Nosotros'.
    """
    return render(request, "nosotros.html")

def mostrarProductos(request):
    """
    Muestra la página de productos con una lista de productos disponibles y cuenta los productos en categorías y temáticas específicas.

    Esta función se utiliza para recuperar y mostrar una lista de productos almacenados en la base de datos.
    Además, cuenta la cantidad de productos en categorías y temáticas específicas y muestra estos totales en la página.

    Args:
        request (HttpRequest): La solicitud HTTP realizada por el cliente.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza la página 'productos.html' con la lista de productos y los totales
        en categorías y temáticas.
    """
    try:
        mensaje = ""
        
        categorias = ["Tortas en pastillaje", "Tortas en crema", "Cupcakes", "Galletas"]
        tematicas = ["Cumpleaños", "Bautizos", "Primera comunión", "Grados", "Matrimonios", "Aniversarios", "Quinces"]

        categorias_obj = Categorias.objects.filter(nombreCategoria__in=categorias)
        tematicas_obj = Tematicas.objects.filter(nombreTematica__in=tematicas)

        total_productos_por_categoria = {}
        total_productos_por_tematica = {}

        productos_por_categoria = Productos.objects.filter(categoriaProducto__in=categorias_obj) \
            .values('categoriaProducto__nombreCategoria') \
            .annotate(total=Count('id'))

        productos_por_tematica = Productos.objects.filter(tematicaProducto__in=tematicas_obj) \
            .values('tematicaProducto__nombreTematica') \
            .annotate(total=Count('id'))

        for categoria_info in productos_por_categoria:
            nombre_categoria = categoria_info['categoriaProducto__nombreCategoria'].replace(" ", "_")
            total_productos = categoria_info['total']
            total_productos_por_categoria[nombre_categoria] = total_productos

        for tematica_info in productos_por_tematica:
            nombre_tematica = tematica_info['tematicaProducto__nombreTematica'].replace(" ", "_")
            total_productos = tematica_info['total']
            total_productos_por_tematica[nombre_tematica] = total_productos

        productos = Productos.objects.all()
    except Exception as error:
        mensaje = f"Problemas al alistar los productos: {error}"

    for categoria in categorias:
        if categoria not in total_productos_por_categoria:
            total_productos_por_categoria[categoria] = 0

    for tematica in tematicas:
        if tematica not in total_productos_por_tematica:
            total_productos_por_tematica[tematica] = 0

    retorno = {
        "mensaje": mensaje,
        "listaProductos": productos,
        **total_productos_por_categoria,
        **total_productos_por_tematica,
    }
    return render(request, "productos.html", retorno)

# FUNCIÓN PARA GENERAR UNA CONTRASEÑA
def generarPassword():
    """
    Genera una contraseña aleatoria de longitud fija.

    Esta función genera una contraseña aleatoria de 8 caracteres que puede incluir letras mayúsculas, letras minúsculas,
    dígitos y caracteres especiales. La contraseña es generada de manera completamente aleatoria.

    Returns:
        str: Una cadena de caracteres que representa la contraseña generada.
    """
    longitud = 8
    caracteres = string.ascii_lowercase + \
        string.ascii_uppercase + string.digits + string.punctuation
    password = ''
    for i in range(longitud):
        password += ''.join(random.choice(caracteres))
    return password

# FUNCIONES PARA ENVIAR CORREO ELECTRONICO
def enviarCorreo(asunto=None, mensaje=None, destinatario=None):
    """
    Envía un correo electrónico utilizando las configuraciones de correo de la aplicación.

    Esta función permite enviar un correo electrónico con un asunto y mensaje específicos
    al destinatario proporcionado. Utiliza las configuraciones de correo electrónico definidas
    en la configuración de la aplicación Django.

    Args:
        asunto (str): El asunto del correo electrónico.
        mensaje (str): El cuerpo del correo electrónico.
        destinatario (str): La dirección de correo electrónico del destinatario.

    Returns:
        None: Esta función no devuelve un valor directamente.

    Raises:
        SMTPException: Se produce una excepción si hay un error en el envío del correo.
        El error se imprime en la consola, pero la función no se bloquea.
    """
    remitente = settings.EMAIL_HOST_USER
    template = get_template('enviarCorreo.html')
    contenido = template.render({
        'destinatario': destinatario,
        'mensaje': mensaje,
        'asunto': asunto,
        'remitente': remitente,
    })
    try:
        correo = EmailMultiAlternatives(
            asunto, mensaje, remitente, [destinatario])
        correo.attach_alternative(contenido, 'text/html')
        correo.send(fail_silently=True)
    except SMTPException as error:
        print(f"Error al enviar el correo: {error}")
        raise SMTPException(error)
        
def enviarCorreoDos(asunto=None,mensaje=None,destinatarios=None,archivo=None):
    """
    Función para enviar correos electrónicos con Django.

    Args:
        asunto (str): El asunto del correo electrónico.
        mensaje (str): El cuerpo del mensaje del correo electrónico.
        destinatarios (list): Una lista de direcciones de correo electrónico a las que se enviará el correo.
        archivo (str): Ruta al archivo que se adjuntará al correo electrónico (opcional).

    Returns:
        None
    """
    remitente = settings.EMAIL_HOST_USER
    template = get_template('enviarCorreo.html')
    contenido = template.render({
        'destinatarios': ', '.join(destinatarios),
        'mensaje': mensaje,
        'asunto': asunto,
        'remitente': remitente,
    })
    try:
        correo = EmailMultiAlternatives(asunto, mensaje, remitente, destinatarios)
        correo.attach_alternative(contenido, 'text/html')
        if archivo != None:
            correo.attach_file(archivo)
        correo.send(fail_silently=True)
    except SMTPException as error:
        print(f"Error al enviar el correo: {error}")
    
# REGISTRO CLIENTE
def vistaRegistrarCliente(request):
    """
    Renderiza la página de registro de clientes.

    Esta función se utiliza para mostrar la página de registro de clientes en la aplicación web.
    Recupera los roles disponibles desde la base de datos y crea un diccionario de retorno que
    contiene la lista de roles y otros datos necesarios para la vista.

    Args:
        request (HttpRequest): La solicitud HTTP recibida por la vista.

    Returns:
        HttpResponse: Una respuesta HTTP que representa la página de registro de clientes
        renderizada con la información necesaria.
    """
    roles = Group.objects.all()
    retorno = {"roles": roles, "user": None, "tipoUsuario": TIPO_USUARIOS}
    return render(request, "registrarCliente.html", retorno)

def registrarCliente(request):
    """
    Registra un cliente en el sistema y envía un correo de bienvenida.

    Esta función maneja las solicitudes POST para registrar a un cliente en el sistema.
    Los datos del cliente se obtienen de la solicitud HTTP y se utilizan para crear un
    nuevo objeto de cliente en la base de datos. Se asocia al cliente con el rol de "Cliente"
    y se envía un correo de bienvenida con los detalles de inicio de sesión.

    Args:
        request (HttpRequest): La solicitud HTTP POST que contiene los datos del cliente.

    Returns:
        HttpResponseRedirect: Una respuesta HTTP que redirige al usuario a la página de inicio
        de sesión después de un registro exitoso.
        HttpResponse: Una respuesta HTTP que muestra un mensaje de error si se produce un
        error durante el registro.
    """
    estado = False
    mensaje = f""
    try:
        nombres = request.POST["txtNombres"]
        apellidos = request.POST["txtApellidos"]
        identificacion = request.POST["txtIdentificacion"]
        telefono = request.POST["txtTelefono"]
        correo = request.POST["txtCorreoConfirmado"]
        password = request.POST["txtPasswordConfirmada"]
        tipoUser = "Cliente"
        foto = request.FILES.get("fileFoto", False)
        # passwordGenerado = generarPassword()
        idRol = 2
        
        phone = f'+57{telefono}'

        with transaction.atomic():
            user = Clientes(identificacionCliente=identificacion, telefonoCliente=phone, username=correo, first_name=nombres, last_name=apellidos,
                            email=correo, fotoUsuario=foto, password=password, tipoUsuario=tipoUser)
            user.save()
            
            rol = Group.objects.get(pk=idRol)
            user.groups.add(rol)

            user.save()

            # Ecriptar contraseña
            print(f"constraseña: {password}")

            user.set_password(password)

            user.save()

            estado = True
            mensaje = f"Ususario agregado correctamente"
            retorno = {"mensaje": mensaje, "estado": estado}

            # enviar correo al usuario
            asunto = "Registro Cliente - D'Albas Pastelería"
            mensaje = f"""
                    <html>
                        <head></head>
                        <body>
                            <p>Cordial saludo, {user.first_name} {user.last_name}.</p>
                            <p>¡Bienvenido(a) a nuestro sistema D'Albas! Su registro ha sido exitoso.</p>
                            <p>A continuación, le proporcionamos sus datos de acceso:</p>
                            <ul>
                                <li>Nombre de usuario: {user.username}</li>
                                <li>Contraseña: {password}</li>
                            </ul>
                            <p>Le recomendamos que mantenga su contraseña confidencial y no la comparta con nadie.</p>
                            <p>Por favor, ingrese al sistema utilizando los datos de acceso establecidos</p>
                            <p>Si tiene alguna pregunta o necesita ayuda, no dude en contactarnos:</p>
                            <ul>
                                <li>Teléfonos: 3185504427 - 3178860724</li>
                                <li>Correo: dalbas.288@gmail.com</li>
                            </ul>
                            <p class="">Te invitamos a que visites nuestra página de <a href="https://www.facebook.com/dalbaspasteleria" style="text-decoration: none; color: #F26699;">Facebook</a>.</p>
                        </body>
                    </html>
                    """
            threa = threading.Thread(target=enviarCorreo, args=(asunto, mensaje, user.email))
            threa.start()
            # time.sleep(5)
            return redirect("/vistaLogin/", retorno)
    except Error as error:
        transaction.rollback()
        mensaje = f"{error}"
    retorno = {"mensaje": mensaje, "user": user, "estado": estado}
    return render(request, "registrarCliente.html", retorno)

# REGISTRO ADMINISTRADOR
def vistaRegistrarAdministrador(request):
    """
    Maneja la página "Registrar Administrador" para el rol de Administrador.

    Esta función verifica si el usuario está autenticado como Administrador y, si es así, muestra la página "Registrar Administrador" con la lista de roles disponibles.
    En caso contrario, redirige al usuario a la página de inicio de sesión.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra la página "Registrar Administrador" para el Administrador
        o redirige al usuario a la página de inicio de sesión en caso de no estar autenticado.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Administrador').exists():
            roles = Group.objects.all()
            retorno = {"roles": roles, "tipoUsuario": TIPO_USUARIOS}
            return render(request, "administrador/registrarAdministrador.html", retorno)
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)
    
def vistaConfirmarAdministrador(request):
    return render(request, "confirm_admin.html")
    
def verificarAdministrador(request):
    if request.method == 'POST':
        numero1 = request.POST.get('num1')
        numero2 = request.POST.get('num2')
        numero3 = request.POST.get('num3')
        numero4 = request.POST.get('num4')
        
        codigo_ingresado = numero1 + numero2 + numero3 + numero4
        
        codigo_valido = codigo_ingresado == '1234'
        
        if codigo_valido:
            return redirect('/vistaRegistrarAdministrador_inicio/')
        else:
            messages.error(request, 'El código ingresado no es válido. Por favor, verifique.')
    
    return render(request, 'registrarCliente.html')

def vistaRegistrarAdministrador_inicio(request):
    roles = Group.objects.all()
    retorno = {"roles": roles, "tipoUsuario": TIPO_USUARIOS}
    return render(request, "registrarAdmin.html", retorno)

def registrarAdministrador(request):
    """
    Maneja el registro de un administrador en la plataforma.

    Esta función permite registrar un nuevo administrador con los datos proporcionados en el formulario. 
    El usuario registrado tendrá el rol de Administrador. Cuando el usuario haya llenado el formulario
    se le envía un correo electrónico con sus credenciales de acceso.

    Args:
        request (HttpRequest): La solicitud HTTP que contiene los datos del formulario.

    Returns:
        HttpResponse: Una respuesta HTTP que redirige al usuario a la página de lista de usuarios después de un registro exitoso o muestra un mensaje de error si el registro falla.
    """
    estado = False
    mensaje = f""
    try:
        nombres = request.POST["txtNombres"]
        apellidos = request.POST["txtApellidos"]
        correo = request.POST["txtCorreoConfirmado"]
        password = request.POST["txtPasswordConfirmada"]
        cargo = request.POST["txtCargo"]
        telefono = request.POST["txtTelefono"]
        tipoUser = "Administrativo"
        foto = request.FILES.get("fileFoto", False)
        idRol = 1
        
        phone = f'+57{telefono}'

        with transaction.atomic():
            user = Administradores(cargoAdministrador=cargo, username=correo, first_name=nombres,
                                last_name=apellidos, email=correo, tipoUsuario=tipoUser,
                                fotoUsuario=foto, password=password, telefonoAdministrador=phone)
            
            user.save()

            rol = Group.objects.get(pk=idRol)
            user.groups.add(rol)
            
            if(rol.name=="Administrador"):
                user.is_staff = True
                user.is_superuser = True

            user.save()

            # Ecriptar contraseña
            print(f"contraseña: {password}")

            user.set_password(password)

            user.save()

            estado = True
            mensaje = f"Ususario agregado correctamente"
            retorno = {"mensaje": mensaje, "estado": estado}

            # enviar correo al usuario
            asunto = "Registro Administrador - D'Albas Pastelería"
            mensaje = f"""
                    <html>
                        <head></head>
                        <body>
                            <p>Cordial saludo, {user.first_name} {user.last_name}.</p>
                            <p>Felicidades, has sido registrado como administrador en nuestra plataforma.</p>
                            <p>¡Es hora de poner manos a la obra y mantener todo funcionando sin problemas!</p>
                            <p>A continuación, le proporcionamos sus datos de acceso:</p>
                            <ul>
                                <li>Nombre de usuario: {user.username}</li>
                                <li>Contraseña: {password}</li>
                            </ul>
                            <p>Le recomendamos que mantenga su contraseña confidencial y no la comparta con nadie.</p>
                            <p>Por favor, ingrese al sistema utilizando los datos de acceso establecidos</p>
                            <p>Si tiene alguna pregunta o necesita ayuda, escribenos: dalbas.288@gmail.com</p>
                        </body>
                    </html>
                    """
            threa = threading.Thread(target=enviarCorreo, args=(asunto, mensaje, user.email))
            threa.start()
            # time.sleep(5)
            return redirect("/vistaListaUsuarios/", retorno)
            # return redirect('vistaListaUsuarios')
    except Error as error:
        transaction.rollback()
        mensaje = f"{error}"
    retorno = {"mensaje": mensaje, "user": user, "estado": estado}
    return render(request, "administrador/registrarAdministrador.html", retorno)
    
# REGISTRO DE PRODUCTOS 
def ver_producto(request, producto_id):
    """
    Vista que permite ver los detalles de un producto.

    Muestra los detalles de un producto específico, identificado por su ID, en una página web.

    Args:
        request (HttpRequest): La solicitud HTTP.
        producto_id (int): El ID del producto que se desea ver.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra los detalles del producto en la página 'ver_producto.html'.
    """
    producto = get_object_or_404(Productos, pk=producto_id)
    return render(request, 'ver_producto.html', {'producto': producto})

def generar_codigo_producto(categoria):
    """
    Genera un código de producto único basado en la categoría.

    El código de producto se compone de las tres primeras letras de la categoría en mayúsculas
    seguidas por un número aleatorio de cuatro dígitos.

    Args:
        categoria (Categoria): El objeto de la categoría a partir del cual se generará el código.

    Returns:
        str: Un código de producto único generado.
    """
    categoria_iniciales = categoria.nombreCategoria[:3].upper()

    numero_aleatorio = str(random.randint(1000, 9999))

    codigo_producto = f"{categoria_iniciales}{numero_aleatorio}"
    
    return codigo_producto

def vistaRegistrarProducto(request):
    """
    Muestra el formulario de registro de productos para los administradores.

    Esta función permite a los administradores ver el formulario de registro de productos, donde pueden ingresar información sobre un nuevo producto que se agregará a la plataforma. Se obtienen las categorías de productos y las temáticas disponibles para su selección.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra el formulario de registro de productos o redirige al usuario a la página de inicio de sesión si no está autenticado.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Administrador').exists():
            categoriasProducto = Categorias.objects.all()
            tematicaProducto = Tematicas.objects.all()
            retorno = {"categoriasProducto":categoriasProducto,"tematicaProducto":tematicaProducto,"pesoTortas":PESO_TORTAS,"saboresTortas":SABORES_TORTAS}
            return render(request, "administrador/registrarProducto.html", retorno)
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)
    
def registrarProductos(request):
    """
    Registra un nuevo producto en la plataforma.

    Esta función permite a los administradores registrar un nuevo producto en la plataforma. Se valida la información ingresada, como el nombre, el precio y la categoría del producto. Además, se puede seleccionar una temática, peso, sabor, descripción e imagen para el producto. Si se completa con éxito el registro del producto, se redirige a la página que muestra la lista de productos.

    Args:
        request (HttpRequest): La solicitud HTTP que contiene la información del producto a registrar.

    Returns:
        HttpResponse: Una respuesta HTTP que redirige al usuario a la lista de productos o muestra un mensaje de error si hay problemas en el proceso de registro.
    """
    if request.user.is_authenticated:
        estado = False
        mensaje = ""
        try:
            nombre = request.POST["txtNombreProducto"]
            precio = int(request.POST["txtPrecio"])
            idCategoria = int(request.POST["cbCategoria"])
            
            catProducto = Categorias.objects.get(pk=idCategoria)
            
            if nombre and precio and catProducto:
                idTematica_str = request.POST.get("cbTematica", "")
                
                if idTematica_str:
                    idTematica = int(idTematica_str)
                else:
                    idTematica = None
                    
                peso = request.POST.get("cbPeso", "")
                sabor = request.POST.get("cbSabor", "")
                descripcion = request.POST.get("txtDescripcion", "")
                imagen = request.FILES.get("fileFoto", False)
                    
                temaProducto = Tematicas.objects.get(pk=idTematica) if idTematica else None
                
                codigo_producto = generar_codigo_producto(catProducto)
                
                with transaction.atomic():
                    product = Productos(nombreProducto=nombre,
                                        precioProducto=precio,
                                        descripcionProducto=descripcion,
                                        imagenProducto=imagen,
                                        categoriaProducto=catProducto,
                                        tematicaProducto=temaProducto,
                                        unidadMedidaProducto=peso,
                                        saborProducto=sabor,
                                        codigoProducto=codigo_producto)
                    
                    product.save()
                    product.generar_qr(request)
                    estado = True
                    mensaje="Producto agregado correctamente"
                    return redirect("/listarProductos/")
            else:
                mensaje = "Faltan campos obligatorios. Por favor, complete todos los campos obligatorios."
        except Error as error:
            transaction.rollback()
            mensaje=f"Problemas al realizar el proceso de agregar un producto: {error}"
        retorno={"mensaje":mensaje,"estado":estado}
        return render(request, "administrador/registrarProducto.html", retorno)
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
        return render(request, "login.html", retorno)

def listarProductos(request):
    """
    Muestra una lista de productos registrados en la plataforma para administradores.

    Esta función permite a los administradores ver una lista de todos los productos registrados en la plataforma. También se muestra una lista de categorías disponibles para filtrar los productos.

    Args:
        request (HttpRequest): La solicitud HTTP para mostrar la lista de productos.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra la lista de productos y categorías disponibles o redirige al usuario a la página de inicio de sesión si no está autenticado.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Administrador').exists():
            try:
                productos = Productos.objects.all()
                categorias = Categorias.objects.all()
                mensaje=""
                # print(productos)
            except Error as error:
                mensaje=f"Problemas al alistar los productos {error}"
            retorno={"mensaje":mensaje,"listaProductos":productos,"categorias":categorias}
            return render(request,"administrador/listarProducto.html", retorno)
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)
    
# LOGIN
def vistaLogin(request):
    """
    Muestra la página de inicio de sesión de la aplicación web.

    Esta función se encarga de renderizar la página de inicio de sesión de la aplicación web.
    Cuando un usuario accede a esta vista, se le presenta un formulario de inicio de sesión
    donde puede ingresar su nombre de usuario y contraseña.

    Args:
        request (HttpRequest): La solicitud HTTP para mostrar la página de inicio de sesión.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra la página de inicio de sesión.
    """
    return render(request, "login.html")

def cerrarSesion(request):
    """
    Cierra la sesión de un usuario en la aplicación web.

    Esta función se encarga de cerrar la sesión de un usuario en la aplicación web.
    Al ser llamada, cierra la sesión activa del usuario y redirige a la página de inicio de sesión.

    Args:
        request (HttpRequest): La solicitud HTTP para cerrar la sesión del usuario.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra un mensaje de confirmación y redirige a la página de inicio de sesión.
    """
    logout(request)
    request.session.flush()
    mensaje = "Has cerrado sesión."
    retorno = {"mensaje": mensaje}
    return render(request, "login.html", retorno)

def login(request):
    """
    Maneja el proceso de inicio de sesión de un usuario en la aplicación web.

    Esta función realiza las siguientes tareas:
    1. Valida el reCAPTCHA para asegurarse de que el usuario no sea un robot.
    2. Verifica las credenciales del usuario (nombre de usuario y contraseña) utilizando la función `authenticate`.
    3. Si las credenciales son válidas, inicia sesión en la aplicación utilizando `auth.login`.
    4. Redirige al usuario a la página de inicio correspondiente según su rol (Administrador o Cliente).

    Args:
        request (HttpRequest): La solicitud HTTP que contiene los datos de inicio de sesión y reCAPTCHA.

    Returns:
        HttpResponse: Una respuesta HTTP que redirige al usuario a la página de inicio correspondiente
        o muestra un mensaje de error si las credenciales son incorrectas o el reCAPTCHA no se valida.
    """
    # validar recaptcha
    """ Begin reCAPTCHA validation """
    recaptcha_response = request.POST.get('g-recaptcha-response')
    url = 'https://www.google.com/recaptcha/api/siteverify'
    values = {
        'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response
    }
    data = urllib.parse.urlencode(values).encode()
    req = urllib.request.Request(url, data=data)
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode())
    print(result)
    """ End reCAPTCHA validation """
    
    if result['success']:
        username = request.POST['txtUsername']
        password = request.POST['txtPassword']
        user = authenticate(username=username, password=password)
        if user is not None:
            # registrar la varibale de sesión
            auth.login(request, user)
            if user.groups.filter(name='Administrador').exists():
                return redirect('inicioAdministrador')
            else:
                return redirect('inicioCliente')
        else:
            mensaje = f"Usuario o contraseña incorrectas"
            return render(request,"login.html",{"mensaje":mensaje})
    else:
        mensaje = f"Debe validar primero el recaptcha"
        return render(request,"login.html",{"mensaje":mensaje})
    
def inicioAdministrador(request):
    """
    Maneja la página de inicio para el rol de Administrador.

    Esta función verifica si el usuario está autenticado como Administrador.
    Si el usuario está autenticado, muestra la página de inicio de Administrador.
    Si el usuario no está autenticado, redirige al usuario a la página de inicio de sesión con un mensaje de error.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra la página de inicio de Administrador
        o redirige al usuario a la página de inicio de sesión si no está autenticado.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Administrador').exists():
            return render(request, "administrador/inicioAdministrador.html")
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)

def inicioCliente(request): 
    """
    Maneja la página de inicio para el rol de Cliente.

    Esta función verifica si el usuario está autenticado como Cliente.
    Si el usuario está autenticado, obtiene los comentarios más recientes y los muestra en la página de inicio de Cliente.
    Si el usuario no está autenticado, redirige al usuario a la página de inicio de sesión con un mensaje de error.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra la página de inicio de Cliente
        con comentarios recientes o redirige al usuario a la página de inicio de sesión si no está autenticado.
    """                                                       
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Cliente').exists():
            comentarios = Comentarios.objects.all().order_by('-fechaHoraCreacion')[:6]   
            retorno = {
                "comentarios":comentarios
            }
            return render(request,"cliente/inicioCliente.html",retorno)
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)
    
def nosotrosCliente(request):
    """
    Maneja la página "Nosotros" para el rol de Cliente.

    Esta función verifica si el usuario está autenticado como Cliente.
    Si el usuario está autenticado, muestra la página "Nosotros" para el Cliente.
    Si el usuario no está autenticado, redirige al usuario a la página de inicio de sesión con un mensaje de error.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra la página "Nosotros" para el Cliente
        o redirige al usuario a la página de inicio de sesión si no está autenticado.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Cliente').exists():
            return render(request, "cliente/nosotros.html")
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)
    
def nosotrosAdministrador(request):
    """
    Maneja la página "Nosotros" para el rol de Administrador.

    Esta función verifica si el usuario está autenticado como Administrador.
    Si el usuario está autenticado, muestra la página "Nosotros" para el Administrador.
    Si el usuario no está autenticado, redirige al usuario a la página de inicio de sesión con un mensaje de error.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra la página "Nosotros" para el Administrador
        o redirige al usuario a la página de inicio de sesión si no está autenticado.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Administrador').exists():
            return render(request, "administrador/nosotros.html")
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)

def mostrarProductosCliente (request):
    """
    Maneja la página "Productos" para el rol de Cliente.

    Esta función verifica si el usuario está autenticado como Cliente.
    Si el usuario está autenticado, muestra la página "Productos" para el Cliente.
    Si el usuario no está autenticado, redirige al usuario a la página de inicio de sesión con un mensaje de error.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra la página "Productos" para el Cliente
        o redirige al usuario a la página de inicio de sesión si no está autenticado.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Cliente').exists():
            return render(request, "cliente/productos.html")
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)

def vistaProductosCliente(request):
    """
    Esta vista muestra una lista de productos disponibles para los clientes, junto con estadísticas de productos
    por categoría y temática.

    Args:
        request: El objeto de solicitud de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza la página de productos para el cliente.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Cliente').exists():
            try:
                mensaje = ""
                
                categorias = ["Tortas en pastillaje", "Tortas en crema", "Cupcakes", "Galletas"]
                tematicas = ["Cumpleaños", "Bautizos", "Primera comunión", "Grados", "Matrimonios", "Aniversarios", "Quinces"]

                categorias_obj = Categorias.objects.filter(nombreCategoria__in=categorias)
                tematicas_obj = Tematicas.objects.filter(nombreTematica__in=tematicas)

                total_productos_por_categoria = {}
                total_productos_por_tematica = {}

                productos_por_categoria = Productos.objects.filter(categoriaProducto__in=categorias_obj) \
                    .values('categoriaProducto__nombreCategoria') \
                    .annotate(total=Count('id'))

                productos_por_tematica = Productos.objects.filter(tematicaProducto__in=tematicas_obj) \
                    .values('tematicaProducto__nombreTematica') \
                    .annotate(total=Count('id'))

                for categoria_info in productos_por_categoria:
                    nombre_categoria = categoria_info['categoriaProducto__nombreCategoria'].replace(" ", "_")
                    total_productos = categoria_info['total']
                    total_productos_por_categoria[nombre_categoria] = total_productos

                for tematica_info in productos_por_tematica:
                    nombre_tematica = tematica_info['tematicaProducto__nombreTematica'].replace(" ", "_")
                    total_productos = tematica_info['total']
                    total_productos_por_tematica[nombre_tematica] = total_productos

                productos = Productos.objects.all()
            except Exception as error:
                mensaje = f"Problemas al alistar los productos: {error}"

            for categoria in categorias:
                if categoria not in total_productos_por_categoria:
                    total_productos_por_categoria[categoria] = 0

            for tematica in tematicas:
                if tematica not in total_productos_por_tematica:
                    total_productos_por_tematica[tematica] = 0

            retorno = {
                "mensaje": mensaje,
                "listaProductos": productos,
                **total_productos_por_categoria,
                **total_productos_por_tematica,
            }
            return render(request, "cliente/productos.html", retorno)
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)

def mostrarProductosCremaCliente(request):
    """
    Muestra la página de "Productos de Crema" para el rol de Cliente.

    Esta función muestra la página de "Productos de Crema" para el Cliente si el usuario está autenticado.
    En caso contrario, redirige al usuario a la página de inicio de sesión.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra la página de "Productos de Crema" para el Cliente
        o redirige al usuario a la página de inicio de sesión en caso de no estar autenticado.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Cliente').exists():
            return render(request, "cliente/productosCrema.html")
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)
    
def vistaProductosCremaCliente(request):
    """
    Maneja la página "Productos de Crema" para el rol de Cliente y muestra una lista de productos de crema disponibles.

    Esta función recupera todos los productos de crema disponibles en la base de datos y los muestra en la página "Productos de Crema" para el Cliente.
    Si se producen errores al recuperar los productos, se muestra un mensaje de error.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra la página "Productos de Crema" para el Cliente
        junto con la lista de productos de crema disponibles o un mensaje de error en caso de problemas.
    """
    try:
        productos = Productos.objects.all()
        mensaje = ""
        # print(productos)
    except Error as error:
        mensaje = f"Problemas al alistar los productos {error}"
    retorno = {"mensaje": mensaje, "listaProductos": productos}
    return render(request, "cliente/productosCrema.html", retorno)

def mostrarProductosCupcakeCliente(request):
    """
    Muestra la página de "Cupcakes" para el rol de Cliente.

    Esta función muestra la página de "Cupcakes" para el Cliente si el usuario está autenticado.
    En caso contrario, redirige al usuario a la página de inicio de sesión.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra la página de "Cupcakes" para el Cliente
        o redirige al usuario a la página de inicio de sesión en caso de no estar autenticado.
    """
    if request.user.is_authenticated:
        return render(request, "cliente/productosCupcakes.html")
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
        return render(request, "login.html", retorno)

def vistaProductosCupcakeCliente(request):
    """
    Maneja la página "Productos de Cupcakes" para el rol de Cliente y muestra una lista de productos de cupcakes disponibles.

    Esta función recupera todos los productos de cupcakes disponibles en la base de datos y los muestra en la página "Productos de Cupcakes" para el Cliente.
    Si se producen errores al recuperar los productos, se muestra un mensaje de error.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra la página "Productos de Cupcakes" para el Cliente
        junto con la lista de productos de cupcakes disponibles o un mensaje de error en caso de problemas.
    """
    try:
        productos = Productos.objects.all()
        mensaje = ""
        # print(productos)
    except Error as error:
        mensaje = f"Problemas al alistar los productos {error}"
    retorno = {"mensaje": mensaje, "listaProductos": productos}
    return render(request, "cliente/productosCupcakes.html", retorno)

def mostrarProductosGalletaCliente(request):
    """
    Muestra la página de "Productos de Galletas" para el rol de Cliente.

    Esta función muestra la página de "Productos de Galletas" para el Cliente si el usuario está autenticado.
    En caso contrario, redirige al usuario a la página de inicio de sesión.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra la página de "Productos de Galletas" para el Cliente
        o redirige al usuario a la página de inicio de sesión en caso de no estar autenticado.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Cliente').exists():
            return render(request, "cliente/productosGalletas.html")
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)

def vistaProductosGalletaCliente(request):
    """
    Maneja la página "Productos de Galletas" para el rol de Cliente y muestra una lista de productos de galletas disponibles.

    Esta función recupera todos los productos de galletas disponibles en la base de datos y los muestra en la página "Productos de Galletas" para el Cliente.
    Si se producen errores al recuperar los productos, se muestra un mensaje de error.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra la página "Productos de Galletas" para el Cliente
        junto con la lista de productos de galletas disponibles o un mensaje de error en caso de problemas.
    """
    try:
        productos = Productos.objects.all()
        mensaje = ""
        # print(productos)
    except Error as error:
        mensaje = f"Problemas al alistar los productos {error}"
    retorno = {"mensaje": mensaje, "listaProductos": productos}
    return render(request, "cliente/productosGalletas.html", retorno)

def vistaRegistrarPedido(request):
    """
    Maneja la página "Registrar Pedido" para el rol de Cliente.

    Esta función verifica si el usuario está autenticado como Cliente y, si es así, muestra la página "Registrar Pedido".
    En caso contrario, redirige al usuario a la página de inicio de sesión.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra la página "Registrar Pedido" para el Cliente
        o redirige al usuario a la página de inicio de sesión en caso de no estar autenticado.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Cliente').exists():
            return render(request, "cliente/registrarPedido.html")
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)
    
def mostrarPedidosCliente(request):
    """
    Muestra la lista de pedidos para un cliente autenticado.

    Si el usuario está autenticado, esta vista obtiene todos los pedidos registrados en la base de datos y los
    muestra en la página 'cliente/registrarPedido.html'. Si el usuario no está autenticado, redirige a la página de inicio de sesión.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra la lista de pedidos o redirige a la página de inicio de sesión.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Cliente').exists():
            try:
                pedidos = Pedidos.objects.all()
                mensaje = ""
                # print(productos)
            except Error as error:
                mensaje = f"Problemas al alistar los pedidos {error}"
            retorno = {"mensaje": mensaje, "listaPedidos": pedidos}
            return render(request, "cliente/registrarPedido.html", retorno)
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)

def vistaPerfilUsuario(request):
    """
    Muestra el perfil de usuario para un cliente autenticado.

    Si el usuario está autenticado, esta vista obtiene el perfil del usuario a partir de su ID de usuario,
    y muestra los detalles en la página 'cliente/perfilusuario.html'. Si el usuario no está autenticado,
    redirige a la página de inicio de sesión.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra el perfil de usuario o redirige a la página de inicio de sesión.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Cliente').exists():
            user_id = request.user.id
            cliente = get_object_or_404(Clientes, pk=user_id)
            retorno = {"cliente": cliente}
            return render(request, "cliente/perfilusuario.html", retorno)
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)

def vistaPerfilAdministrador(request):
    """
    Muestra el perfil de un administrador y estadísticas relacionadas.

    Esta vista muestra el perfil de un administrador autenticado junto con varias gráficas estadísticas.
    Las gráficas incluyen la cantidad de pedidos por estado, la proporción de usuarios por rol,
    pedidos mensuales a lo largo del año, la distribución de métodos de pago y las calificaciones de los comentarios.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra el perfil del administrador y las gráficas estadísticas.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Administrador').exists():
            user_id = request.user.id
            administrador = get_object_or_404(Administradores, pk=user_id)
            retorno = {"administrador": administrador}
            
            # Grafica - cantidad de pedidos por estado
            estados = ['Pendiente', 'En proceso', 'Entregado', 'Cancelado']
            cantidad_por_estado = [Pedidos.objects.filter(estadoPedido=estado).count() for estado in estados]

            plt.figure(figsize=(8, 6))
            plt.plot(estados, cantidad_por_estado, marker='o', color='#ff6961', linestyle='-')
            plt.xlabel('Estado del Pedido')
            plt.ylabel('Cantidad de Pedidos')
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            rutaImagen = os.path.join(settings.MEDIA_ROOT, "grafica_pedidos.png")
            plt.savefig(rutaImagen)

            #----------------------------------------------------------------------

            # Grafica - proporción de los usuarios por sus roles
            usuarios_administrativos = Administradores.objects.count()
            usuarios_clientes = Clientes.objects.count()

            tipos_de_usuarios = ['Administrativos', 'Clientes']
            cantidad_de_usuarios = [usuarios_administrativos, usuarios_clientes]
            colores = ['#f9d99a', '#95b8f6']

            plt.figure(figsize=(8, 6))
            plt.pie(cantidad_de_usuarios, labels=tipos_de_usuarios, colors=colores, autopct='%1.1f%%', startangle=140)
            plt.axis('equal') 

            ruta_imagen2 = os.path.join(settings.MEDIA_ROOT, "grafica_usuarios.png")
            plt.savefig(ruta_imagen2)

            #----------------------------------------------------------------------
            
            # Grafica - Pedidos mensuales a lo largo del año
            year = datetime.now().year
            month_data = Pedidos.objects.filter(fechaPedido__year=year).annotate(
                month=ExtractMonth('fechaPedido')
            ).values('month').annotate(count=Count('id')).order_by('month')

            months = [month['month'] for month in month_data]
            order_counts = [month['count'] for month in month_data]

            month_names = [calendar.month_name[month_num] for month_num in months]

            plt.figure(figsize=(10, 6))
            plt.plot(month_names, order_counts, marker='o', linestyle='-')
            plt.xlabel('Mes')
            plt.ylabel('Cantidad de Pedidos')
            plt.xticks(rotation=45)
            plt.grid(axis='y', linestyle='--', alpha=0.7)

            ax = plt.gca()
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))

            ruta_imagen3 = os.path.join(settings.MEDIA_ROOT, "grafica_pedidos_mensuales.png")
            plt.savefig(ruta_imagen3)
            
            #----------------------------------------------------------------------
            
            # Grafica - Distribución de Métodos de Pago
            metodos_pago = ['Transferencia', 'Efectivo']
            cantidad_por_metodo = [Pedidos.objects.filter(metodoPago=metodo).count() for metodo in metodos_pago]
            colores = ['#b0f2c2', '#fcb7af']

            plt.figure(figsize=(8, 6))
            plt.bar(metodos_pago, cantidad_por_metodo, color=colores)
            plt.xlabel('Método de Pago')
            plt.ylabel('Cantidad de Pedidos')
            plt.grid(axis='y', linestyle='--', alpha=0.7)

            ruta_imagen4 = os.path.join(settings.MEDIA_ROOT, "grafica_metodos_pago.png")
            plt.savefig(ruta_imagen4)
            
            #----------------------------------------------------------------------
            
            # Consulta para obtener las calificaciones de los comentarios
            comentarios = Comentarios.objects.filter(puntajeComentario__gte=0).values('puntajeComentario')

            calificaciones_comentarios = [comentario['puntajeComentario'] for comentario in comentarios]

            plt.figure(figsize=(8, 6))
            plt.hist(calificaciones_comentarios, bins=np.arange(1, 7) - 0.5, rwidth=0.8, alpha=0.7, color='#fdcae1')
            plt.xlabel('Calificación')
            plt.ylabel('Número de Comentarios')
            plt.xticks(range(6))
            plt.grid(axis='y', linestyle='--', alpha=0.7)

            ruta_imagen5 = os.path.join(settings.MEDIA_ROOT, "grafica_calificaciones_comentarios.png")
            plt.savefig(ruta_imagen5)
            
            atexit.register(plt.close)
            
            return render(request, "administrador/perfilAdmin.html", retorno)
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)

def consultarProducto(request, id):
    """
    Consulta y muestra los detalles de un producto para su edición.

    Esta vista permite a un usuario autenticado consultar los detalles de un producto específico,
    identificado por su ID, para su posible edición.

    Args:
        request (HttpRequest): La solicitud HTTP.
        id (int): El ID del producto que se desea consultar.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra los detalles del producto en un formulario de edición.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Administrador').exists():
            try:
                producto=Productos.objects.get(id=id)
                categoriasProducto = Categorias.objects.all()
                tematicaProducto = Tematicas.objects.all()
                mensaje=""
            except Error as error:
                mensaje=f"Problemas {error}"
                
            retorno={"mensaje":mensaje,"producto":producto,"tematicaProducto":tematicaProducto,"categoriasProducto":categoriasProducto,"pesoTortas":PESO_TORTAS,"saborTortas":SABORES_TORTAS}
            return render(request,"administrador/frmEditar.html",retorno)
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)

def actualizarProductos(request):
    """
    Actualiza los detalles de un producto en la base de datos.

    Esta vista permite a un usuario autenticado actualizar los detalles de un producto en la base de datos.
    Los detalles se obtienen a través de un formulario HTML enviado mediante una solicitud POST.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que indica el resultado de la actualización.
    """
    if request.user.is_authenticated:
        mensaje = ""
        estado = False
        if request.method == "POST":
            idProducto = int(request.POST.get('idProducto'))
            nombre = request.POST.get("txtNombreProducto")
            precio = int(request.POST.get("txtPrecio"))
            idCategoria = int(request.POST.get("cbCategoria"))
            idTematica = int(request.POST.get("cbTematica"))
            peso = request.POST.get("cbPeso")
            sabor = request.POST.get("cbSabor")
            descripcion = request.POST.get("txtDescripcion")
            archivo = request.FILES.get("fileFoto", False)
            try:
                
                producto=Productos.objects.get(id=idProducto)
                
                producto.nombreProducto = nombre
                producto.precioProducto = precio
                producto.descripcionProducto = descripcion
                producto.categoriaProducto_id = idCategoria
                producto.unidadMedidaProducto = peso
                producto.saborProducto = sabor

                if idTematica == 0:
                    producto.tematicaProducto = None
                else:
                    producto.tematicaProducto_id = idTematica

                if (archivo):
                    if (producto.imagenProducto):
                        producto.imagenProducto.storage.delete(producto.imagenProducto.name)
                    producto.imagenProducto=archivo
                else:
                    producto.imagenProducto = producto.imagenProducto
                    
                producto.save()
                
                mensaje = "Producto actualizado correctamente"
                estado = True
                messages.success(request, mensaje)
                
                return redirect("/listarProductos/")
            
            except Productos.DoesNotExist:
                mensaje = "Producto no encontrado"
                messages.error(request, mensaje)
            
            except Error as error:
                mensaje=f"Problemas al realizar el proceso de actualizar el producto {error}"
                messages.error(request, mensaje)
                
        retorno={"mensaje":mensaje,"estado":estado,"producto":producto}
        return render(request,"administrador/frmEditar.html",retorno)
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
        return render(request, "login.html", retorno)

#AQUI COMIENZA LO QUE HE AGREGADO
"""
def vistaCarrito(request):
    if request.user.is_authenticated:
        #tres el usuario que esta actualmente en sesion y lo vuelve un objeto tipo user
        usuario = request.user
        idUsuario = usuario.id
        cliente = User.objects.get(pk=idUsuario)
        # Busca en el carrito si existen productos agregados por el usuario y los trae
        productos = CarritoCompras.objects.filter(Carritocliente=cliente)
        #variable para hacer el total 
        total=0
        # Extrae los productos de los elementos del carrito de compras (si.... nose bien como funciona cosas de ChatGpt)
        productos2 = [item.Carritoproducto for item in productos]       
        # Crea un contador de productos para contar cuántas veces se repite cada uno
        contador_productos = Counter(productos2)
        #Recorrer los productos para sacar el total
        for p in productos:
            total+=p.Carritoproducto.precioProducto
        #Crear el retorno con los datos que se requieren
        retorno = {"productos": [{"producto": p, "cantidad": contador_productos[p]} for p in contador_productos], "total": total,"cantidad_productos": len(productos)}
        return render(request, "cliente/carrito.html",retorno)

def vistaCarritoCompras(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            try:
                with transaction.atomic():
                    #traer el id por medio de la peticion ajax
                    producto_id = request.POST.get("idProducto")
                    # busca el usuario que este actualmente en la sesion
                    usuario = request.user
                    idUsuario = usuario.id
                    #vuelve los valores obtenidos anteriomente en su clase correspondiente
                    producto = Productos.objects.get(id=producto_id)
                    cliente = User.objects.get(pk=idUsuario)
                    #agrega al la tabla carrito de compras los datos que obtenemos y lo guardamos
                    carritoCompras = CarritoCompras(Carritoproducto=producto, Carritocliente=cliente)
                    carritoCompras.save()
                    mensaje="PRODUCTO AGREGADO AL CARRITO"
                    estado = True
            except Error as error:
                transaction.rollback()
                mensaje = f"{error}"
            retorno = {"mensaje":mensaje,"estado":estado}
            return JsonResponse(retorno) 
    else:
        mensaje="Debe ingresar con sus credenciales"
        return render(request, "login.html", retorno)
     
# AQUI TERMINA LO QUE HE AGREGADO (ATT: VARGAS)

#?Eliminar producto del carro
    
def eliminarProductoCarrito(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            try:
                with transaction.atomic():
                    # Obtener el ID del producto y el usuario
                    producto_id = request.POST.get("idProducto")
                    usuario = request.user
                    idUsuario = usuario.id
                    
                    # Obtener el objeto del producto y del cliente
                    producto = Productos.objects.get(id=producto_id)
                    cliente = User.objects.get(pk=idUsuario)
                    
                    # Eliminar el producto del carrito de compras
                    carritoCompras = CarritoCompras.objects.get(Carritoproducto=producto, Carritocliente=cliente)
                    carritoCompras.delete()
                    
                    mensaje = "PRODUCTO ELIMINADO DEL CARRITO"
                    estado = True
            except Error as error:
                transaction.rollback()
                mensaje = f"{error}"
            
            retorno = {"mensaje": mensaje, "estado": estado}
            return JsonResponse(retorno)
    else:
        mensaje = "Debe ingresar con sus credenciales"
        return render(request, "login.html", {"mensaje": mensaje})

#?Finaliza el eliminar producto del carro
"""

def tu_vista(request):
    """
    Consulta y muestra categorías con la cantidad de productos asociados.

    Esta vista consulta las categorías en la base de datos y cuenta la cantidad de productos
    asociados a cada categoría. Luego, muestra las categorías junto con la cantidad de productos
    en una plantilla HTML.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra las categorías con la cantidad de productos en una plantilla.
    """
    categorias_con_cantidad = Categorias.objects.annotate(
        cantidad_productos=Count('categoria_producto')
    )
    return render(request, 'tu_plantilla.html', {'categorias_con_cantidad': categorias_con_cantidad})

def setPassword_view(request):
    """
    Muestra una página para restablecer la contraseña.

    Esta vista muestra una página HTML que permite a un usuario restablecer su contraseña.
    La página generalmente contiene un formulario donde el usuario puede ingresar una nueva contraseña.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra la página para restablecer la contraseña.
    """
    return render(request, "recuperarPassword.html")

def recuperarPassword(request):
    """
    Procesa la solicitud de restablecimiento de contraseña y envía un correo electrónico con la nueva contraseña.

    Esta vista permite a un usuario solicitar el restablecimiento de su contraseña. Se verifica si el correo electrónico
    proporcionado pertenece a un usuario registrado. Si es así, se genera una nueva contraseña, se actualiza en la base de
    datos y se envía al usuario por correo electrónico.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que redirige al usuario a la página de inicio de sesión con un mensaje de confirmación
        o error.
    """
    if request.method == 'POST':
        email = request.POST.get('email')

        mensaje = ""
        estado = False
        
        try:
            with transaction.atomic():
                try:
                    user = User.objects.get(email=email)
                    print(user)
                
                    nuevaContraseña = generarPassword()

                    user.set_password(nuevaContraseña)
                            
                    user.save()
                    
                    messages.success(request, 'Correo enviado') 
                    
                    estado = True
                    retorno = {"mensaje": mensaje, "estado": estado}
                      

                    asunto = "Recuperar Contraseña - D'Albas Pastelería"
                    mensaje = f"""
                        <html>
                            <head></head>
                            <body>
                                <p>Cordial saludo, {user.first_name} {user.last_name}.</p>
                                <p>Hemos recibido una solicitud para cambiar la contraseña de su cuenta en la pasteleria D'Albas.</p>
                                <p>Si usted no realizó esta solicitud, por favor ignore este correo.</p>
                                <ul>
                                    <li>Nueva contraseña: {nuevaContraseña}</li>
                                </ul>
                            </body>
                        </html>
                        """

                    threa = threading.Thread(
                        target=enviarCorreo, args=(asunto, mensaje, user.email))
                    threa.start()
                         
                except ObjectDoesNotExist:
                    estado = False
                    retorno = {"mensaje": mensaje, "estado": estado}
                    messages.error(request, 'No existe ningún usuario con ese correo electrónico.')
                    return redirect("/vistaLogin/", retorno)
            
        except Error as error:
            transaction.rollback()
            mensaje = f"{error}"
        retorno = {"mensaje": mensaje, "estado": estado}
        return redirect("/vistaLogin/", retorno)

def crearComentario(request):
    """
    Crea y guarda un nuevo comentario sobre un producto.

    Esta vista permite a un usuario autenticado crear y guardar un nuevo comentario sobre un producto.
    El usuario puede proporcionar un contenido de comentario y puntuación mediante un formulario HTML.
    El comentario se guarda en la base de datos.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que redirige al usuario a la página de inicio del cliente
        con un mensaje de confirmación o error.
    """
    if request.user.is_authenticated:
        if request.method == 'POST':
            contenido = request.POST.get('contenidoComentario')
            puntuacion = request.POST.get('puntuacionEstrellas') 

            if contenido.strip() == '':
                messages.error(request, 'Cuentanos tu opinion, no te quedes sin palabras')
            else:
                usuario = request.user  
                comentario = Comentarios(contenidoComentario=contenido, usuarioComentario=usuario, puntajeComentario=puntuacion)
                comentario.save()
                return redirect('/inicioCliente/')
        return render(request, 'cliente/inicioCliente.html')
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
        return render(request, "login.html", retorno)

def mostrarComentarios(request):
    """
    Muestra una lista de comentarios paginados.

    Esta vista consulta todos los comentarios en la base de datos y los muestra en una página
    web de comentarios paginada. Los comentarios se ordenan por fecha y hora de creación de forma
    descendente.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra una página de comentarios paginada.
    """
    comentarios = Comentarios.objects.all().order_by('-fechaHoraCreacion')
    paginator = Paginator(comentarios, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }
    
    return render(request, 'verComentarios.html', context)

def mostrarComentariosCliente(request):
    """
    Muestra una lista de comentarios para un cliente autenticado, paginados.

    Esta vista consulta todos los comentarios en la base de datos y los muestra en una página web
    de comentarios paginada para un cliente autenticado. Los comentarios se ordenan por fecha y hora
    de creación de forma descendente.

    Si el usuario no está autenticado, se le redirige a la página de inicio de sesión.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra una página de comentarios paginada para un cliente autenticado,
        o redirige al usuario a la página de inicio de sesión si no está autenticado.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Cliente').exists():
            comentarios = Comentarios.objects.all().order_by('-fechaHoraCreacion')
            paginator = Paginator(comentarios, 10) 
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            context = {
                'page_obj': page_obj
            }
            
            return render(request, 'cliente/verComentarios.html', context)
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)

def vistaCarrito(request):
    """
    Muestra el contenido del carrito de compras de un cliente autenticado.

    Esta vista permite a un cliente autenticado ver el contenido de su carrito de compras.
    Se utiliza la clase Carrito para gestionar los productos en el carrito y calcular la
    cantidad total de productos en él.

    Si el usuario no está autenticado, se le redirige a la página de inicio de sesión.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra la página del carrito de compras
        con la cantidad total de productos, o redirige al usuario a la página de inicio de sesión
        si no está autenticado.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Cliente').exists():
            today = date.today()
            carrito = Carrito(request)
            cantidad_productos = carrito.obtener_cantidad_total()
            return render(request, "cliente/carrito.html", {'cantidad_productos': cantidad_productos,'METODOS_DE_PAGO':METODOS_DE_PAGO,'today':today})
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)

def vistaRegistrarPedidoAdmin(request):
    """
    Muestra una página para que un administrador pueda registrar un nuevo pedido.

    Esta vista permite a un administrador autenticado registrar un nuevo pedido en el sistema.
    Proporciona opciones para seleccionar productos, métodos de pago y otras informaciones relacionadas
    con el pedido.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra la página de registro de pedidos para
        el administrador con las opciones necesarias para registrar un nuevo pedido, o redirige al
        usuario a la página de inicio de sesión si no está autenticado.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Administrador').exists():
            today = date.today()
            productos = Productos.objects.all()
            retorno = {"METODOS_DE_PAGO":METODOS_DE_PAGO,"productos":productos,"today":today}
            return render(request, "administrador/registrarPedido.html",retorno)
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)

def registrarPedidoAdmin(request):
    """
    Registra un nuevo pedido por parte del administrador en el sistema.

    Esta vista permite a un usuario administrativo autenticado registrar un nuevo pedido en el sistema.
    El pedido incluye información sobre el cliente, la fecha y hora de requerimiento, el método de pago
    y los productos solicitados con sus cantidades correspondientes. Además, se envía un correo electrónico
    de confirmación al cliente y al administrador.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        JsonResponse: Una respuesta JSON que indica si el pedido se registró correctamente o si se produjo un error.
        La respuesta incluye un mensaje y un estado (True para éxito, False para error).
    """
    if request.method == 'POST':
        estado = False
        mensaje = ""
        try:
            with transaction.atomic():
                nombreCliente = request.POST['nombreCliente']
                telefonoCliente = request.POST['telefonoCliente']
                fechaHoraRequiere = request.POST.get('fechaHoraPedido',None)
                metodoDePago = request.POST['metodoPago']
                correoCliente = request.POST['correoCliente']
                pedido = Pedidos(nombreClientePedido = nombreCliente,
                                 telefonoClientePedido = telefonoCliente,
                                 fechaHoraPedido = fechaHoraRequiere,
                                 metodoPago = metodoDePago,
                                 userPedido = request.user)
                pedido.save()
                
                detalleSolicitudPedidos = json.loads(request.POST["detalle"])
                
                detalleSolicitudCorreo = []
                                
                valorTotal = 0 
                
                for detalle in detalleSolicitudPedidos:
                    producto = Productos.objects.get(id=int(detalle['idProducto']))
                    cantidad = int(detalle['cantidad'])
                    costoAcumulable = producto.precioProducto * cantidad
                    valorTotal += costoAcumulable
                    detallePedido = DetallePedido(detallePedido = pedido,
                                                  cantidadProducto = cantidad,
                                                  costoProductos = costoAcumulable,
                                                  detalleProducto = producto)
                    detallePedido.save()
                    detalleSolicitudCorreo.append([producto.nombreProducto, cantidad, costoAcumulable])
                                        
                pedido.valorPedido = valorTotal
                pedido.save()
                
                asunto = "Registro de Pedido - D'Albas Pastelería"
                
                usuarios = User.objects.all()
                
                for usuario in usuarios:
                    if usuario.groups.filter(name='Administrador').exists():
                        correoAdministrador = usuario.email
                        break
                    
                mensaje = f"""
                    <html>
                        <head></head>
                        <body>
                            <p>Estimado(a) {nombreCliente},</p>
                            <p>¡Gracias por elegir la Pastelería D'Albas! Su pedido ha sido registrado con éxito.</p>
                            <p>A continuación, le proporcionamos los detalles de su pedido:</p>
                            <ul>
                                <li>Nombre del Cliente: {nombreCliente}</li>
                                <li>Teléfono de Contacto: {telefonoCliente}</li>
                                <li>Fecha y Hora del Pedido: {fechaHoraRequiere}</li>
                                <li>Método de Pago: {metodoDePago}</li>
                                <li>Correo Electrónico: {correoCliente}</li>
                            </ul>
                            <p>Detalles del Pedido:</p>
                            <ul>
                                {"".join([f"<li>{item[0]} - Cantidad: {item[1]} - ${item[2]}</li>" for item in detalleSolicitudCorreo])}
                            </ul>
                            <p>Total del Pedido: ${valorTotal}</p>
                            <p>Su pedido está siendo procesado, se le notificará cuando ya se haya finalizado la compra de sus productos.</p>
                            <p>Si tiene alguna pregunta o necesita ayuda, no dude en contactarnos:</p>
                            <ul>
                                <li>Teléfonos: 3185504427 - 3178860724</li>
                                <li>Correo: dalbas.288@gmail.com</li>
                            </ul>
                            <p>Le invitamos a visitar nuestra página de <a href="https://www.facebook.com/dalbaspasteleria" style="text-decoration: none; color: #F26699;">Facebook</a>.</p>
                        </body>
                    </html>
                    """
                threa = threading.Thread(target=enviarCorreoDos, args=(asunto,mensaje,[correoCliente, correoAdministrador])) 
                threa.start()
                
                estado = True
                mensaje = "Pedido registrado exitosamente."
        except Error as error:
            transaction.rollback()
            mensaje = f"Error: {error}"
        retorno = {"estado":estado,"mensaje":mensaje}
        return JsonResponse(retorno)
                
def vistaRegistrarUsuario(request):
    """
    Muestra el formulario para registrar un nuevo usuario en el sistema.

    Esta vista permite a un usuario administrativo autenticado acceder al formulario
    para registrar un nuevo usuario en el sistema. Proporciona opciones para seleccionar
    el tipo de usuario y el rol asociado.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza la página de registro de usuarios.
        La respuesta incluye los roles disponibles y los tipos de usuario.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Administrador').exists():
            roles = Group.objects.all()
            retorno = {"roles": roles, "tipoUsuario": TIPO_USUARIOS}
            return render(request, "administrador/registrarUsuario.html", retorno)
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)

def registrarUsuarioAdmin(request):
    estado = False
    mensaje = f""
    try:
        nombres = request.POST["txtNombres"]
        apellidos = request.POST["txtApellidos"]
        correo = request.POST["txtCorreoConfirmado"]
        password = request.POST["txtPasswordConfirmada"]
        cargo = request.POST["txtCargo"]
        telefono = request.POST["txtTelefono"]
        tipoUser = "Administrativo"
        foto = request.FILES.get("fileFoto", False)
        idRol = 1
        
        phone = f'+57{telefono}'

        with transaction.atomic():
            user = Administradores(cargoAdministrador=cargo, username=correo, first_name=nombres,
                                last_name=apellidos, email=correo, tipoUsuario=tipoUser,
                                fotoUsuario=foto, password=password, telefonoAdministrador=phone)
            
            user.save()

            rol = Group.objects.get(pk=idRol)
            user.groups.add(rol)
            
            if(rol.name=="Administrador"):
                user.is_staff = True
                user.is_superuser = True

            user.save()

            # Ecriptar contraseña
            print(f"contraseña: {password}")

            user.set_password(password)

            user.save()

            estado = True
            mensaje = f"Ususario agregado correctamente"
            retorno = {"mensaje": mensaje, "estado": estado}

            # enviar correo al usuario
            asunto = "Registro Administrador - D'Albas Pastelería"
            contenido = f"""
                    <html>
                        <head></head>
                        <body>
                            <p>Cordial saludo, {user.first_name} {user.last_name}.</p>
                            <p>Felicidades, has sido registrado como administrador en nuestra plataforma.</p>
                            <p>¡Es hora de poner manos a la obra y mantener todo funcionando sin problemas!</p>
                            <p>A continuación, le proporcionamos sus datos de acceso:</p>
                            <ul>
                                <li>Nombre de usuario: {user.username}</li>
                                <li>Contraseña: {password}</li>
                            </ul>
                            <p>Le recomendamos que mantenga su contraseña confidencial y no la comparta con nadie.</p>
                            <p>Por favor, ingrese al sistema utilizando los datos de acceso establecidos</p>
                            <p>Si tiene alguna pregunta o necesita ayuda, escribenos: dalbas.288@gmail.com</p>
                        </body>
                    </html>
                    """
            threa = threading.Thread(target=enviarCorreo, args=(asunto, contenido, user.email))
            threa.start()
            # time.sleep(5)
            return redirect("/vistaLogin/", retorno)
    except Error as error:
        transaction.rollback()
        mensaje = f"{error}"
    retorno = {"mensaje": mensaje, "user": user, "estado": estado}
    return render(request, "registrarAdmin.html", retorno)

def registrarUsuario(request):
    """
    Registra un nuevo usuario en el sistema y envía una confirmación por correo electrónico.

    Esta vista permite a un administrador agregar un nuevo usuario al sistema. Se capturan
    los datos del usuario, se generan las credenciales y se envía una confirmación por correo electrónico
    al usuario recién registrado.

    Args:
        request (HttpRequest): La solicitud HTTP que contiene los datos del formulario.

    Returns:
        HttpResponse: Una respuesta HTTP que redirige al administrador a la lista de usuarios
        o muestra un mensaje de error si ocurre un problema durante el registro.
    """
    estado = False
    mensaje = f""
    try:
        nombres = request.POST["txtNombres"]
        apellidos = request.POST["txtApellidos"]
        identificacion = request.POST["txtIdentificacion"]
        telefono = request.POST["txtTelefono"]
        correo = request.POST["txtCorreoConfirmado"]
        password = request.POST["txtPasswordConfirmada"]
        tipoUser = "Cliente"
        foto = request.FILES.get("fileFoto", False)
        # passwordGenerado = generarPassword()
        idRol = 2
        
        phone = f'+57{telefono}'

        with transaction.atomic():
            user = Clientes(identificacionCliente=identificacion, telefonoCliente=phone, username=correo, first_name=nombres, last_name=apellidos,
                            email=correo, fotoUsuario=foto, password=password, tipoUsuario=tipoUser)
            user.save()
            
            rol = Group.objects.get(pk=idRol)
            user.groups.add(rol)

            user.save()

            # Ecriptar contraseña
            print(f"constraseña: {password}")

            user.set_password(password)

            user.save()

            estado = True
            mensaje = f"Ususario agregado correctamente"
            retorno = {"mensaje": mensaje, "estado": estado}

            # enviar correo al usuario
            asunto = "Registro Cliente - D'Albas Pastelería"
            mensaje = f"""
                    <html>
                        <head></head>
                        <body>
                            <p>Cordial saludo, {user.first_name} {user.last_name}.</p>
                            <p>¡Bienvenido(a) a nuestro sistema D'Albas! Su registro ha sido exitoso.</p>
                            <p>A continuación, le proporcionamos sus datos de acceso:</p>
                            <ul>
                                <li>Nombre de usuario: {user.username}</li>
                                <li>Contraseña: {password}</li>
                            </ul>
                            <p>Le recomendamos que mantenga su contraseña confidencial y no la comparta con nadie.</p>
                            <p>Por favor, ingrese al sistema utilizando los datos de acceso establecidos</p>
                            <p>Si tiene alguna pregunta o necesita ayuda, no dude en contactarnos:</p>
                            <ul>
                                <li>Teléfonos: 3185504427 - 3178860724</li>
                                <li>Correo: dalbas.288@gmail.com</li>
                            </ul>
                            <p class="">Te invitamos a que visites nuestra página de <a href="https://www.facebook.com/dalbaspasteleria" style="text-decoration: none; color: #F26699;">Facebook</a>.</p>
                        </body>
                    </html>
                    """
            threa = threading.Thread(
                target=enviarCorreo, args=(asunto, mensaje, user.email))
            threa.start()
            # time.sleep(5)
            return redirect("/vistaListaUsuarios/", retorno)
    except Error as error:
        transaction.rollback()
        mensaje = f"{error}"
    retorno = {"mensaje": mensaje, "user": user, "estado": estado}
    return render(request, "administrador/registrarUsuario.html", retorno)

def vistaManual(request):
    """
    Renderiza la página del manual del usuario.

    Esta vista renderiza la página que contiene el manual del usuario, proporcionando
    información sobre cómo utilizar el sistema, sus características y funciones.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.

    Returns:
        HttpResponse: Una respuesta HTTP que contiene la página del manual del usuario.
    """
    return render(request,"manual.html")

def productosPorCategoria(request,catNombre):
    """
    Muestra los productos pertenecientes a una categoría específica.

    Esta vista recibe un nombre de categoría como parámetro y muestra todos los productos
    que pertenecen a esa categoría.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.
        catNombre (str): El nombre de la categoría de productos a mostrar.

    Returns:
        HttpResponse: Una respuesta HTTP que contiene los productos de la categoría y su información.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Cliente').exists():
            categoria = Categorias.objects.get(Categorias=catNombre)
            producto = Productos.objects.filter(categoria=categoria)
            context = {'categoria':categoria, 'producto':producto}
            return render(request,"cliente/productos.html",context)
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)

# CARRITO

def agregarProductoCarrito(request, producto_id):
    """
    Agrega un producto al carrito de compras del cliente.

    Esta vista recibe el ID de un producto y lo agrega al carrito de compras del cliente
    almacenado en la sesión.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.
        producto_id (int): El ID del producto que se va a agregar al carrito.

    Returns:
        HttpResponse: Una respuesta HTTP que redirige al cliente a la página de productos.
    """
    carrito = Carrito(request)
    producto = Productos.objects.get(id=producto_id)
    carrito.agregarProductoCarrito(producto)
    mensaje = "Producto agregado al carrito de compras"
    messages.success(request, mensaje)
    return redirect("/vistaProductosCliente/")

def aumentarProductoCarrito(request, producto_id):
    """
    Aumenta la cantidad de un producto en el carrito de compras del cliente.

    Esta vista recibe el ID de un producto y aumenta su cantidad en el carrito de compras del cliente
    almacenado en la sesión.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.
        producto_id (int): El ID del producto cuya cantidad se va a aumentar en el carrito.

    Returns:
        HttpResponse: Una respuesta HTTP que redirige al cliente a la página del carrito de compras.
    """
    carrito = Carrito(request)
    producto = Productos.objects.get(id=producto_id)
    carrito.agregarProductoCarrito(producto)
    return redirect("/vistaCarrito/")

def eliminarProductoCarrito(request, producto_id):
    """
    Elimina un producto del carrito de compras del cliente.

    Esta vista recibe el ID de un producto y lo elimina del carrito de compras del cliente
    almacenado en la sesión.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.
        producto_id (int): El ID del producto que se va a eliminar del carrito.

    Returns:
        HttpResponse: Una respuesta HTTP que redirige al cliente a la página del carrito de compras.
    """
    carrito = Carrito(request)
    producto = Productos.objects.get(id=producto_id)
    carrito.eliminarProductoCarrito(producto)
    return redirect("/vistaCarrito/")

def restarProducto(request, producto_id):
    """
    Resta la cantidad de un producto en el carrito de compras del cliente.

    Esta vista recibe el ID de un producto y disminuye en uno la cantidad de ese producto en el carrito de compras
    del cliente almacenado en la sesión. Si la cantidad llega a cero, el producto se eliminará del carrito.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.
        producto_id (int): El ID del producto del cual se va a restar la cantidad en el carrito.

    Returns:
        HttpResponse: Una respuesta HTTP que redirige al cliente a la página del carrito de compras.
    """
    carrito = Carrito(request)
    producto = Productos.objects.get(id=producto_id)
    carrito.restar(producto)
    return redirect("/vistaCarrito/")

def limpiarCarrito(request):
    """
    Limpia el carrito de compras del cliente, eliminando todos los productos almacenados en él.

    Esta vista elimina todos los productos presentes en el carrito de compras del cliente,
    lo que significa que el carrito quedará vacío después de usar esta función.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.

    Returns:
        HttpResponse: Una respuesta HTTP que redirige al cliente a la página del carrito de compras vacío.
    """
    carrito = Carrito(request)
    carrito.limpiar()
    return redirect("/vistaCarrito/")
#--------------------------------------------------------------------

def vistaListaUsuarios(request):
    """
    Muestra una lista de usuarios registrados en el sistema.

    Esta vista muestra una lista de usuarios registrados en el sistema, incluyendo tanto clientes como administradores.
    Solo los usuarios autenticados con permisos de administrador pueden acceder a esta lista.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza la página de lista de usuarios con los usuarios registrados en el sistema.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Administrador').exists():
            listaClientes = Clientes.objects.all()
            listaAdministradores = Administradores.objects.all()
            retorno = {"listaClientes":listaClientes,"listaAdministradores":listaAdministradores}
            return render(request,"administrador/listaUsuarios.html",retorno)
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)

def vistaListaPedidosAdministrador(request):
    """
    Muestra una lista de pedidos realizados en el sistema.

    Esta vista muestra una lista de todos los pedidos registrados en el sistema, incluyendo información sobre su estado.
    Solo los usuarios autenticados con permisos de administrador pueden acceder a esta lista.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza la página de lista de pedidos con los pedidos registrados.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Administrador').exists():
            listaPedidos = Pedidos.objects.all()
            retorno = {"listaPedidos":listaPedidos,"estados":ESTADOS_PEDIDO}
            return render(request,"administrador/listaPedidos.html",retorno)
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)

def actualizarCliente(request):
    """
    Actualiza los datos del perfil de un cliente.

    Esta vista permite a un cliente autenticado actualizar sus datos personales, incluyendo
    su nombre, apellidos, identificación, teléfono, correo electrónico y foto de perfil.
    También permite cambiar la contraseña de la cuenta.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.

    Returns:
        HttpResponse: Una respuesta HTTP que redirige al perfil del cliente o muestra
        un mensaje de error en caso de problemas.
    """
    mensaje = ""
    estado = False

    if request.method == "POST":
        idCliente = int(request.POST.get('idCliente'))
        identificacion = request.POST.get("txtIdentificacion")
        nombre = request.POST.get("txtNombre")
        apellido = request.POST.get("txtApellido")
        telefono = request.POST.get("txtTelefono")
        correo = request.POST.get("txtCorreo")
        correo_confirmado = request.POST.get("txtCorreoConfirmado")
        password = request.POST.get("txtPassword")
        password_confirm = request.POST.get("txtPasswordConfirmada")
        archivo = request.FILES.get("fileFoto", False)

        try:
            cliente = Clientes.objects.get(id=idCliente)

            if correo and correo == correo_confirmado and correo_confirmado != cliente.email:
                cliente.username = correo_confirmado
            
            cliente.identificacionCliente = identificacion
            cliente.first_name = nombre
            cliente.last_name = apellido
            cliente.telefonoCliente = telefono
            cliente.email = correo_confirmado

            if archivo:
                if cliente.fotoUsuario:
                    cliente.fotoUsuario.storage.delete(cliente.fotoUsuario.name)
                cliente.fotoUsuario = archivo

            if password and password_confirm and password == password_confirm:
                cliente.set_password(password_confirm)
                cliente.save()
                
                user = authenticate(request, username=cliente.username, password=password_confirm)
                
                if user is not None:
                    auth.login(request, user)
                    update_session_auth_hash(request, user)
            
            cliente.save()

            mensaje = "Datos actualizados correctamente"
            estado = True
            messages.success(request, mensaje)
            
            asunto = "Actualización de Datos - D'Albas Pastelería"
            contenido = f"""
                <html>
                    <head></head>
                    <body>
                        <p>Cordial saludo, {nombre} {apellido}.</p>
                        <p>Le informamos que sus datos han sido actualizados con éxito en nuestro sistema D'Albas.</p>
                        <p>Si usted realizó esta acción, no necesita hacer nada más.</p>
                        <p>Si no realizó esta acción, por favor, póngase en contacto con nosotros de inmediato.</p>
                        <p>Si tiene alguna pregunta o necesita ayuda, no dude en contactarnos:</p>
                        <ul>
                            <li>Teléfonos: 3185504427 - 3178860724</li>
                            <li>Correo: dalbas.288@gmail.com</li>
                        </ul>
                    </body>
                </html>
                """

            threa = threading.Thread(
                target=enviarCorreo, args=(asunto, contenido, cliente.email))
            threa.start()

            retorno = {"mensaje": mensaje, "estado": estado, "cliente": cliente}
            # return render(request, "cliente/perfilUsuario.html", retorno)
            return redirect("/vistaPerfilUsuario/")
        
        except Clientes.DoesNotExist:
            mensaje = "Cliente no encontrado"
            messages.error(request, mensaje)
        
        except Error as error:
            mensaje = f"Problemas al realizar el proceso de actualizar datos {error}"
            messages.error(request, mensaje)
            
    retorno = {"mensaje": mensaje, "estado": estado, "cliente": cliente}
    return render(request, "cliente/editarCliente.html", retorno)

def consultarCliente(request, id):
    """
    Consulta y muestra los detalles del perfil de un cliente.

    Esta vista permite a un cliente autenticado consultar y ver los detalles de su propio perfil
    o del perfil de otro cliente, identificado por su ID.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.
        id (int): El ID del cliente cuyo perfil se desea consultar.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra los detalles del perfil del cliente o
        un mensaje de error en caso de problemas.
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Cliente').exists():
            try:
                cliente=Clientes.objects.get(id=id)
                mensaje=""
            except Error as error:
                mensaje=f"Problemas {error}"
                
            retorno={"mensaje":mensaje,"cliente":cliente}
            return render(request,"cliente/editarCliente.html",retorno)
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)

def actualizarAdmin(request):
    """
    Actualiza los datos del perfil de un administrador.

    Esta vista permite a un administrador autenticado actualizar sus datos de perfil,
    incluyendo nombre, apellido, teléfono, cargo, correo electrónico, foto de perfil
    y contraseña.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra un mensaje de éxito o error después
        de actualizar los datos del perfil del administrador. 
    """
    mensaje = ""
    estado = False
    if request.method == "POST":
        idAdmin = int(request.POST.get('idAdmin'))
        nombre = request.POST.get("txtNombre")
        apellido = request.POST.get("txtApellido")
        telefono = request.POST.get("txtTelefono")
        cargo = request.POST.get("txtCargo")
        correo = request.POST.get("txtCorreo")
        correo_confirmado = request.POST.get("txtCorreoConfirmado")
        password = request.POST.get("txtPassword")
        password_confirm = request.POST.get("txtPasswordConfirmada")
        archivo = request.FILES.get("fileFoto", False)
        # print(idAdmin)
        try:
            
            administrador=Administradores.objects.get(id=idAdmin)
            
            if correo and correo == correo_confirmado and correo_confirmado != administrador.email:
                administrador.username = correo_confirmado

            administrador.email=correo_confirmado
            administrador.last_name=apellido
            administrador.first_name=nombre
            administrador.telefonoAdministrador=telefono
            administrador.cargoAdministrador=cargo

            if (archivo):
                if (administrador.fotoUsuario):
                    administrador.fotoUsuario.storage.delete(administrador.fotoUsuario.name)
                administrador.fotoUsuario=archivo
            else:
                administrador.fotoUsuario = administrador.fotoUsuario
                
            if password and password_confirm and password == password_confirm:
                administrador.set_password(password_confirm)
                administrador.save()
                
                user = authenticate(request, username=administrador.username, password=password_confirm)
                
                if user is not None:
                    auth.login(request, user)
                    update_session_auth_hash(request, user)

            administrador.save()
            
            mensaje = "Datos actualizados correctamente"
            estado = True
            messages.success(request, mensaje)
            
            return redirect("/vistaPerfilAdministrador/")
        
        except Administradores.DoesNotExist:
            mensaje = "Administrador no encontrado"
            messages.error(request, mensaje)
        
        except Error as error:
            mensaje=f"Problemas al realizar el proceso de actualizar datos {error}"
            messages.error(request, mensaje)
            
    retorno={"mensaje":mensaje,"estado":estado,"Administrador":administrador}
    return render(request,"administrador/editarAdministrador.html",retorno)

def consultarAdmin(request, id):
    """
    Consulta los datos de un administrador.

    Esta vista permite a un administrador autenticado consultar y visualizar los datos
    de otro administrador mediante su identificador único.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.
        id (int): El identificador único del administrador que se va a consultar.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra los datos del administrador consultado
        o un mensaje de error si el administrador no existe o si el usuario no está autenticado. 
    """
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Administrador').exists():
            try:
                administrador=Administradores.objects.get(id=id)
                mensaje=""
            except Error as error:
                mensaje=f"Problemas {error}"
                
            retorno={"mensaje":mensaje,"administrador":administrador}
            return render(request,"administrador/editarAdmin.html",retorno)
        else:
            retorno = {"mensaje": "No tienes permiso para ingresar a esta vista"}
    else:
        retorno = {"mensaje": "Debe ingresar con sus credenciales"}
    return render(request, "login.html", retorno)

def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('txtCurrentPassword')
        new_password = request.POST.get('txtNewPassword')
        confirm_password = request.POST.get('txtConfirmPassword')

        user = request.user

        if user.check_password(current_password):
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user) 
                
                asunto = "Cambio de contraseña - D'Albas Pastelería"
                contenido = f"""
                    <html>
                        <head></head>
                        <body>
                            <p>Cordial saludo, {user.first_name} {user.last_name}.</p>
                            <p>Le informamos que la contraseña de su cuenta ha sido cambiada con éxito. Si usted realizó este cambio, puede ignorar este mensaje.</p>
                            <p>Si no ha realizado esta acción o considera que su cuenta ha sido comprometida, le recomendamos que se comunique con nuestro equipo de soporte de inmediato para garantizar la seguridad de su cuenta.</p>
                            <p>Le recordamos la importancia de mantener su contraseña segura y de no compartirla con nadie. Si tiene alguna pregunta o necesita asistencia adicional, no dude en ponerse en contacto con nosotros.</p>
                            <p>Si tiene alguna pregunta o necesita ayuda, no dude en contactarnos:</p>
                            <ul>
                                <li>Teléfonos: 3185504427 - 3178860724</li>
                                <li>Correo: dalbas.288@gmail.com</li>
                            </ul>
                        </body>
                    </html>
                    """

                threa = threading.Thread(
                    target=enviarCorreo, args=(asunto, contenido, user.email))
                threa.start()
                
                messages.success(request, 'Contraseña cambiada con éxito.')
                return redirect('/vistaPerfilUsuario/') 
            else:
                messages.error(request, 'La nueva contraseñas no coinciden.')
        else:
            messages.error(request, 'La contraseña es incorrecta.')
            
    return redirect("/vistaPerfilUsuario/")

def change_password_admin(request):
    if request.method == 'POST':
        current_password = request.POST.get('txtCurrentPassword')
        new_password = request.POST.get('txtNewPassword')
        confirm_password = request.POST.get('txtConfirmPassword')

        user = request.user

        if user.check_password(current_password):
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user) 
                messages.success(request, 'Contraseña cambiada con éxito.')
                return redirect('/vistaPerfilAdministrador/') 
            else:
                messages.error(request, 'La nueva contraseñas no coinciden.')
        else:
            messages.error(request, 'La contraseña es incorrecta.')
            
    return redirect("/vistaPerfilAdministrador/")

def actualizar_estado_pedido(request):
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        nuevo_estado = request.POST.get('nuevo_estado')
        try:
            pedido = Pedidos.objects.get(id=pedido_id)
            pedido.estadoPedido = nuevo_estado
            pedido.save()
            return JsonResponse({'success': True, 'message': 'Estado actualizado correctamente.'})
        except Pedidos.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Pedido no encontrado'})
    return JsonResponse({'success': False, 'error': 'Solicitud no válida'})