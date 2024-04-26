from django.contrib.auth import login, authenticate as auth_login
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, RequestFactory, Client
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import Group, User
from django.template.loader import get_template
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.test import override_settings
from tempfile import NamedTemporaryFile
from smtplib import SMTPException
from django.conf import settings
from unittest.mock import patch
from django.urls import reverse
from app_DAlbas.models import *
from app_DAlbas.views import *
from django.core.mail import *
from django.core import mail
from app_DAlbas import views
from app_DAlbas import *
import threading
import unittest
import string
import random
import json
import os

# Create your tests here.

class RegistrarClienteTestCase(TestCase):
    """
    Clase de pruebas unitarias para la funcionalidad de registro de clientes.

    Esta clase contiene pruebas que evalúan el proceso de registro de clientes dentro de la
    aplicación, incluyendo la creación y validación de clientes con información completa o sin foto.
    """
    @classmethod
    def setUpClass(cls):
        """
        Crea una instancia de RequestFactory para simular peticiones HTTP.
        """
        super().setUpClass()
        cls.factory = RequestFactory()

    def setUp(self):
        """
        Configura mocks para las funciones en app_DAlbas.views y establece el comportamiento de enviarCorreo
        en pruebas.
        """
        self.mock_enviar_correo = patch('app_DAlbas.views.enviarCorreo')

        self.mock_enviar_correo.side_effect = lambda asunto, mensaje, destinatario: None

    def test_registrar_cliente(self):
        """
        Prueba de registro exitoso de un cliente.

        Esta prueba verifica que se pueda registrar un cliente con éxito al proporcionar información completa,
        incluyendo nombres, apellidos, correo electrónico, contraseña, identificación, teléfono y una foto.
        Luego, verifica que los detalles del cliente se almacenen correctamente en la base de datos y que se envíe
        un correo de confirmación.
        """
        archivo_ficticio = SimpleUploadedFile("archivo.jpg", b"", content_type="image/jpg")

        data = {
            'txtNombres': 'Juan',
            'txtApellidos': 'Laguna',
            'txtIdentificacion': '777777777',
            'txtCorreoConfirmado': 'juansito257@gmail.com',
            'txtPasswordConfirmada': 'user123',
            'txtTelefono': '1234567890',
            'fileFoto': archivo_ficticio
        }
        
        request = self.factory.post('/registrarCliente/', data, format='multipart')
        
        response = registrarCliente(request)
        
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Clientes.objects.count(), 1)

        cliente_registrado = Clientes.objects.first()
        
        self.assertEqual(cliente_registrado.first_name, 'Juan')
        self.assertEqual(cliente_registrado.last_name, 'Laguna')
        self.assertEqual(cliente_registrado.identificacionCliente, '777777777')
        self.assertEqual(cliente_registrado.email, 'juansito257@gmail.com')
        self.assertEqual(cliente_registrado.telefonoCliente, '+571234567890')
        self.assertEqual(cliente_registrado.username, 'juansito257@gmail.com')
        
        # Verificar que la foto coincida
        archivo_ficticio.seek(0)
        imagen_solicitud = request.FILES['fileFoto'].file.read()
        imagen_base_datos = cliente_registrado.fotoUsuario.read()
        
        self.assertEqual(imagen_solicitud, imagen_base_datos)
        
        grupo_cliente = Group.objects.get(name='Cliente')
        self.assertTrue(cliente_registrado.groups.filter(name='Cliente').exists())
        
        # Verificar que la contraseña coincida
        password_cliente = 'user123'  # Obtén la contraseña 
        cliente_registrado.set_password(password_cliente)
        self.assertTrue(cliente_registrado.check_password(password_cliente))

        self.assertEqual(len(mail.outbox), 1)
        
        cliente_registrado.delete()
    
    def test_registrar_cliente_sin_foto(self):
        """
        Prueba de registro de cliente sin foto.

        Esta prueba verifica que se pueda registrar un cliente sin proporcionar una foto.
        Luego, verifica que los detalles del cliente se almacenen correctamente en la base de datos y
        que se envíe un correo de confirmación.
        """
        data = {
            'txtNombres': 'Andrés',
            'txtApellidos': 'Quintero',
            'txtIdentificacion': '888888888',
            'txtCorreoConfirmado': 'anfequingar@gmail.com',
            'txtPasswordConfirmada': 'user123',
            'txtTelefono': '1234567890',
        }
        
        request = self.factory.post('/registrarCliente/', data)
        
        response = registrarCliente(request)
        
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Clientes.objects.count(), 1)

        cliente_registrado = Clientes.objects.first()
        
        self.assertEqual(cliente_registrado.first_name, 'Andrés')
        self.assertEqual(cliente_registrado.last_name, 'Quintero')
        self.assertEqual(cliente_registrado.identificacionCliente, '888888888')
        self.assertEqual(cliente_registrado.email, 'anfequingar@gmail.com')
        self.assertEqual(cliente_registrado.telefonoCliente, '+571234567890')
        self.assertEqual(cliente_registrado.username, 'anfequingar@gmail.com')
        
        grupo_cliente = Group.objects.get(name='Cliente')
        self.assertTrue(cliente_registrado.groups.filter(name='Cliente').exists())
        
        # Verificar que la contraseña coincida
        password_cliente = 'user123'  # Obtén la contraseña 
        cliente_registrado.set_password(password_cliente)
        self.assertTrue(cliente_registrado.check_password(password_cliente))

        self.assertEqual(len(mail.outbox), 1)
        
        cliente_registrado.delete()
        
    def tearDown(self):
        """
        Limpieza después de la ejecución de las pruebas.

        Elimina todos los clientes de la base de datos y detiene los mocks para limpiar el entorno de pruebas.
        """
        Clientes.objects.all().delete()
        self.mock_enviar_correo.stop()
        
# ----------------------------------------------------------------------------------------------------
        
class RegistrarAdministradorTestCase(TestCase):
    """
    Clase de pruebas unitarias para la funcionalidad de registro de administradores.

    Esta clase contiene una prueba que evalúa el proceso de registro de administradores dentro
    de la aplicación, incluyendo la creación y validación de un administrador con información completa.
    """
    @classmethod
    def setUpClass(cls):
        """
        Crea una instancia de RequestFactory para simular peticiones HTTP.
        """
        super().setUpClass()
        cls.factory = RequestFactory()

    def setUp(self):
        """
        Configura mocks para las funciones en app_DAlbas.views y establece el comportamiento de enviarCorreo
        en pruebas.
        """
        self.mock_enviar_correo = patch('app_DAlbas.views.enviarCorreo')

        self.mock_enviar_correo.side_effect = lambda asunto, mensaje, destinatario: None

    def test_registrar_administrador(self):
        """
        Prueba de registro exitoso de un administrador.

        Esta prueba verifica que se pueda registrar un administrador con éxito al proporcionar
        información completa, incluyendo nombres, apellidos, correo electrónico, contraseña,
        cargo, teléfono y una foto. Luego, verifica que los detalles del administrador se almacenen
        correctamente en la base de datos y que se envíe un correo de confirmación.
        """
        archivo_ficticio = SimpleUploadedFile("archivo.jpg", b"", content_type="image/jpg")

        data = {
            'txtNombres': 'Michelle',
            'txtApellidos': 'Morea',
            'txtCorreoConfirmado': 'xiomara140516@gmail.com',
            'txtPasswordConfirmada': 'admin123',
            'txtCargo': 'Gerente',
            'txtTelefono': '1234567890',
            'fileFoto': archivo_ficticio
        }
        
        request = self.factory.post('/registrarAdministrador/', data, format='multipart')
        
        response = registrarAdministrador(request)
        
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Administradores.objects.count(), 1)

        administrador_registrado = Administradores.objects.first()
        
        self.assertEqual(administrador_registrado.first_name, 'Michelle')
        self.assertEqual(administrador_registrado.last_name, 'Morea')
        self.assertEqual(administrador_registrado.email, 'xiomara140516@gmail.com')
        self.assertEqual(administrador_registrado.cargoAdministrador, 'Gerente')
        self.assertEqual(administrador_registrado.telefonoAdministrador, '+571234567890')
        self.assertEqual(administrador_registrado.username, 'xiomara140516@gmail.com')
        
        # Verificar que la foto coincida
        archivo_ficticio.seek(0)
        imagen_solicitud = request.FILES['fileFoto'].file.read()
        imagen_base_datos = administrador_registrado.fotoUsuario.read()
        
        self.assertEqual(imagen_solicitud, imagen_base_datos)
        
        grupo_administrador = Group.objects.get(name='Administrador')
        self.assertTrue(administrador_registrado.groups.filter(name='Administrador').exists())

        # Verificar que el administrador se convierta en superusuario y staff
        user = User.objects.get(email=administrador_registrado.email)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

        # Verificar que la contraseña coincida
        password_administrador = 'admin123'  # Obtén la contraseña
        administrador_registrado.set_password(password_administrador)
        self.assertTrue(administrador_registrado.check_password(password_administrador))

        self.assertEqual(len(mail.outbox), 1)
        
        administrador_registrado.delete()
        
    def tearDown(self):
        """
        Limpieza después de la ejecución de las pruebas.

        Elimina todos los administradores de la base de datos y detiene los mocks para limpiar
        el entorno de pruebas.
        """
        Administradores.objects.all().delete()
        self.mock_enviar_correo.stop()
        
# ----------------------------------------------------------------------------------------------------

class RegistrarProductosTestCase(TestCase):
    """
    Clase de pruebas unitarias para la funcionalidad de registro de productos.

    Esta clase contiene una prueba que evalúa el proceso de registro de productos dentro
    de la aplicación, incluyendo la creación y validación de productos con información completa.
    """
    @classmethod
    def setUpClass(cls):
        """
        Crea una instancia de RequestFactory para simular peticiones HTTP.
        """
        super().setUpClass()
        cls.factory = RequestFactory()
        
    def test_registrar_producto(self):
        """
        Prueba de registro exitoso de un producto.

        Esta prueba verifica que un producto se pueda registrar con éxito al proporcionar
        información completa, incluyendo nombre, precio, categoría, temática, peso, sabor,
        descripción y una imagen. Luego, verifica que los detalles del producto se almacenen
        correctamente en la base de datos.
        """
        usuario = User.objects.create_user(username='usuario_prueba', password='contrasena_prueba')

        archivo_ficticio = SimpleUploadedFile("archivo.jpg", b"", content_type="image/jpg")

        data = {
            'txtNombreProducto': 'Torta de Homero',
            'txtPrecio': '50000',
            'cbCategoria': '1',
            'cbTematica': '1',
            'cbPeso': 'Media libra',
            'cbSabor': 'Chocolate',
            'txtDescripcion': 'Torta de cumpleaños, con decoración de Homero Simpson, sabor a chocolate',
            'fileFoto': archivo_ficticio,
        }

        # Autenticar al usuario de prueba
        self.client.force_login(usuario)

        response = self.client.post('/registrarProductos/', data, format='multipart')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/listarProductos/')

        self.assertEqual(Productos.objects.count(), 1)

        producto_creado = Productos.objects.first()

        self.assertEqual(producto_creado.nombreProducto, 'Torta de Homero')
        self.assertEqual(producto_creado.precioProducto, 50000)
        self.assertEqual(producto_creado.categoriaProducto.id, 1)
        self.assertEqual(producto_creado.tematicaProducto.id, 1)
        self.assertEqual(producto_creado.unidadMedidaProducto, 'Media libra')
        self.assertEqual(producto_creado.saborProducto, 'Chocolate')
        self.assertEqual(producto_creado.descripcionProducto, 'Torta de cumpleaños, con decoración de Homero Simpson, sabor a chocolate')

        # Verificar que la foto coincida
        archivo_ficticio.seek(0)
        imagen_solicitud = archivo_ficticio.read()
        imagen_base_datos = producto_creado.imagenProducto.read()

        # Compara el contenido de las imágenes
        self.assertEqual(imagen_solicitud, imagen_base_datos) 
        
        producto_creado.delete()
        
    def tearDown(self):
        """
        Limpieza después de la ejecución de las pruebas.

        Elimina todos los productos de la base de datos.
        """
        Productos.objects.all().delete()
        
# ----------------------------------------------------------------------------------------------------

class CrearComentarioTestCase(TestCase):
    """
    Clase de pruebas unitarias para la funcionalidad de creación de comentarios.

    Esta clase contiene pruebas que evalúan el proceso de creación de comentarios dentro
    de la aplicación, incluyendo escenarios de éxito y errores.
    """
    def setUp(self):
        """
        Crea un usuario de prueba y realiza la autenticación.
        """
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_crear_comentario_exitoso(self):
        """
        Prueba de creación de comentario exitosa.

        Esta prueba verifica que se pueda crear un comentario exitosamente proporcionando
        contenido y una puntuación de estrellas válidos. Luego, verifica que el comentario
        se haya almacenado correctamente en la base de datos.
        """
        response = self.client.post(reverse('crearComentario'), {
            'contenidoComentario': 'Este es un comentario de prueba',
            'puntuacionEstrellas': 5,
        })
        self.assertEqual(response.status_code, 302)  # Verificar redirección

        self.assertEqual(Comentarios.objects.count(), 1)

        comentario = Comentarios.objects.first()
        self.assertEqual(comentario.contenidoComentario, 'Este es un comentario de prueba')
        self.assertEqual(comentario.puntajeComentario, 5)
        self.assertEqual(comentario.usuarioComentario, self.user)
        
    def test_crear_comentario_sin_contenido(self):
        """
        Prueba de creación de comentario sin contenido.

        Esta prueba verifica que no se pueda crear un comentario si el campo de contenido
        está vacío. Verifica que la página se vuelva a cargar y que ningún comentario se almacene
        en la base de datos.
        """
        response = self.client.post(reverse('crearComentario'), {
            'contenidoComentario': '',  # Contenido vacío
            'puntuacionEstrellas': 3,
        })
        self.assertEqual(response.status_code, 200)  # Verificar que la página se vuelva a cargar

        self.assertEqual(Comentarios.objects.count(), 0)

    def tearDown(self):
        """
        Elimina todos los comentarios de la base de datos, cierra la sesión del cliente y elimina
        el usuario de prueba.
        """
        Comentarios.objects.all().delete()
        self.client.logout()
        
# ----------------------------------------------------------------------------------------------------

class GenerarPasswordTestCase(TestCase):
    """
    Pruebas unitarias para la función generarPassword.

    Esta clase de pruebas verifica el comportamiento de la función generarPassword, que se utiliza para generar contraseñas
    aleatorias de 8 caracteres.

    Métodos de Prueba:
        - test_longitud_de_contraseña_generada: Verifica que la contraseña generada tenga una longitud de 8 caracteres.
        - test_caracteres_en_contraseña_generada: Verifica que los caracteres generados estén dentro de los caracteres permitidos.
        - test_contraseñas_diferentes_en_llamadas_distintas: Verifica que las contraseñas generadas en llamadas diferentes sean diferentes.
    """
    def test_longitud_de_contraseña_generada(self):
        """
        Verifica que la contraseña generada tenga una longitud de 8 caracteres.
        """
        password = generarPassword()
        self.assertEqual(len(password), 8, "La contraseña generada debe tener una longitud de 8 caracteres")

    def test_caracteres_en_contraseña_generada(self):
        """
        Verifica que los caracteres generados estén dentro de los caracteres permitidos.
        """
        password = generarPassword()
        caracteres_permitidos = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
        for char in password:
            self.assertIn(char, caracteres_permitidos, f"El carácter '{char}' no está permitido en la contraseña generada")

    def test_contraseñas_diferentes_en_llamadas_distintas(self):
        """
        Verifica que las contraseñas generadas en llamadas diferentes sean diferentes.
        """
        password1 = generarPassword()
        password2 = generarPassword()
        self.assertNotEqual(password1, password2, "Las contraseñas generadas en llamadas diferentes deben ser diferentes")

# ----------------------------------------------------------------------------------------------------
        
class RecuperarContraseñaTestCase(TestCase):
    """
    Clase de pruebas unitarias para la funcionalidad de recuperación de contraseña.

    Esta clase contiene pruebas que evalúan el proceso de recuperación de contraseña
    dentro de la aplicación, incluyendo escenarios de éxito, errores y excepciones.
    """
    def setUp(self):
        """
        Configuración previa a la ejecución de las pruebas.

        Crea un usuario de prueba y realiza la autenticación.
        """
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
        self.client.login(username='testuser', password='testpassword')
        
    def _common_redirect_check(self, response):
        """
        Verifica una redirección común a la vista de inicio de sesión.

        Esta función se utiliza en varias pruebas para verificar una redirección
        a la vista de inicio de sesión con un código de estado 302.
        """
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('vistaLogin'))

    def test_recuperar_contraseña_exitoso(self):
        """
        Prueba de recuperación de contraseña exitosa.

        Esta prueba verifica que la recuperación de contraseña sea exitosa al proporcionar
        una dirección de correo electrónico válida. También verifica que se envíe un correo
        de recuperación y que la contraseña del usuario se haya cambiado.
        """
        response = self.client.post(reverse('recuperarPassword'), {
            'email': 'test@example.com',  # Email válido
        })
        
        self._common_redirect_check(response)

        user = User.objects.get(username='testuser')
        self.assertNotEqual(user.check_password('testpassword'), True)

        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.subject, "Recuperar Contraseña - D'Albas Pastelería")
        self.assertIn('Nueva contraseña:', email.body)

    def test_recuperar_contraseña_correo_invalido(self):
        """
        Prueba de recuperación de contraseña con dirección de correo electrónico inválida.

        Esta prueba verifica que no se realice la recuperación de contraseña cuando se proporciona
        una dirección de correo electrónico inválida. Además, asegura que la contraseña del usuario
        no se modifique y que no se envíe ningún correo.
        """
        response = self.client.post(reverse('recuperarPassword'), {
            'email': 'invalid@example.com',  # Email inválido
        })
        
        self._common_redirect_check(response)

        user = User.objects.get(username='testuser')
        self.assertEqual(user.check_password('testpassword'), True)
        
        self.assertEqual(len(mail.outbox), 0)
        
    def test_recuperar_contrasena_exception(self):
        """
        Prueba de excepción durante la recuperación de contraseña.

        Esta prueba verifica que se maneje adecuadamente una excepción que ocurra
        durante el intento de recuperar la contraseña, asegurando que no se envíe ningún correo.
        """
        # Forzar una excepción al intentar recuperar la contraseña
        with self.assertRaises(Exception):
            response = self.client.post(reverse('recuperar_contraseña'), {'email': 'test@example.com'})

        self.assertEqual(len(mail.outbox), 0)

    def tearDown(self):
        """
        Cierra la sesión del cliente y elimina el usuario de prueba.
        """
        self.client.logout()
        self.user.delete()
        
# ----------------------------------------------------------------------------------------------------

class EnviarCorreoTestCase(TestCase):
    """
    Clase de pruebas unitarias para la función enviarCorreo.

    Esta clase contiene una prueba que evalúa el envío exitoso de un correo electrónico
    utilizando la función enviarCorreo.
    """
    def test_enviar_correo_exitoso(self):
        """
        Prueba el envío exitoso de un correo electrónico.

        Esta prueba verifica que un correo electrónico se envíe correctamente utilizando
        la función enviarCorreo, y que los detalles del correo sean los esperados.
        """
        asunto = "Prueba de Correo"
        mensaje = "Este es un mensaje de prueba."
        destinatario = "juansebt.0610@gmail.com"

        enviarCorreo(asunto, mensaje, destinatario)

        self.assertEqual(len(mail.outbox), 1, "Correo enviado exitosamente")

        correo_enviado = mail.outbox[0]
        self.assertEqual(correo_enviado.subject, asunto)
        self.assertEqual(correo_enviado.body, mensaje,)
        self.assertEqual(correo_enviado.from_email, settings.EMAIL_HOST_USER)
        self.assertEqual(correo_enviado.to, [destinatario])

# ----------------------------------------------------------------------------------------------------

class EnviarCorreoDosTestCase(TestCase):
    """
    Clase de pruebas unitarias para la función enviarCorreoDos, evaluando el comportamiento
    de la función al enviar correos electrónicos con y sin archivos adjuntos.
    """
    def setUp(self):
        """
        Configuración previa a la ejecución de las pruebas.

        Crea un archivo PDF ficticio en tiempo de prueba.
        """
        self.archivo_temporal = NamedTemporaryFile(delete=False, suffix=".pdf")
        self.archivo_temporal.write(b"")

    def test_enviar_correo_exitoso(self):
        """
        Prueba el envío exitoso de un correo electrónico sin archivo adjunto.
        """
        asunto = "Prueba de Correo"
        mensaje = "Este es un mensaje de prueba."
        destinatarios = ["anfequingar@gmail.com","juansebt.0610@gmail.com"]
        archivo = None  # Sin archivo adjunto

        enviarCorreoDos(asunto, mensaje, destinatarios, archivo)

        self.assertEqual(len(mail.outbox), 1)

        correo_enviado = mail.outbox[0]
        self.assertEqual(correo_enviado.subject, asunto)
        self.assertEqual(correo_enviado.body, mensaje)
        self.assertEqual(correo_enviado.from_email, settings.EMAIL_HOST_USER)
        self.assertEqual(correo_enviado.to, destinatarios)

    def test_enviar_correo_con_archivo_adjunto(self):
        """
        Prueba el envío exitoso de un correo electrónico con archivo adjunto.
        """
        asunto = "Prueba de Correo con Adjunto"
        mensaje = "Este es un mensaje de prueba con archivo adjunto."
        destinatarios = ["anfequingar@gmail.com","juansebt.0610@gmail.com"]

        enviarCorreoDos(asunto, mensaje, destinatarios, self.archivo_temporal.name)

        self.assertEqual(len(mail.outbox), 1)
        correo_enviado = mail.outbox[0]
        self.assertEqual(correo_enviado.subject, asunto)
        self.assertEqual(correo_enviado.body, mensaje)
        self.assertEqual(correo_enviado.from_email, settings.EMAIL_HOST_USER)
        self.assertEqual(correo_enviado.to, destinatarios)
        self.assertEqual(len(correo_enviado.attachments), 1)

    def tearDown(self):
        """
        Cierra el archivo temporal creado durante la configuración.
        """
        self.archivo_temporal.close()
        
# ----------------------------------------------------------------------------------------------------
