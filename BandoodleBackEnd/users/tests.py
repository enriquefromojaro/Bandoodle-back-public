from typing import re

from django.contrib.auth.models import User

# Create your tests here.
from rest_framework import status
from rest_framework.test import APITestCase, APIClient, APIRequestFactory, force_authenticate
from rest_framework.authtoken.models import Token
from django.contrib.sessions.models import Session

from users.models import Musician

URL_PREFIX = 'http://localhost:8000/api/users/'


class UsuarioTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('usuario', 'usuario@mail.com', 'usuario')
        self.user.is_staff = False
        self.admin = User.objects.create_superuser('admin', 'admin@mail.com', 'admin')
        self.user.save()

        # Creamos el cliente para realizar las peticiones y nos logueamos
        self.client = APIClient()
        # Iniciamos sesión con el usuario para que se le creen sesiones y así poder probar si se destruyen al borrarlo, etc.
        # Se usa otro objeto APIClient porque de otra manera, al volver a loguearse con el administrador para hacer los tests,
        # automáticamente hace logout y elimina su sesión, de manera que no podemos probar el que elimine las sesiones del usuario eliminado

        test_client = APIClient()
        test_client.login(username=self.user.username, password='usuario')

        # Nos logueamos como administrador
        self.client.login(username=self.admin.username, password='admin')

    '''
    ------------------------------------------------------------------------------------------------------------------
    *****************		Tests CRUD OK		**********************************************************************
    ------------------------------------------------------------------------------------------------------------------
    '''

    def test_list_ok(self):
        response = self.client.get(URL_PREFIX)

        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Se esperaba un código de respuesta 200 (OK)')

    def test_detail_ok(self):
        response = self.client.get(URL_PREFIX + str(self.user.id) + '/')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Se esperaba un código de respuesta 200 (OK)')

    def test_delete_ok(self):
        response = self.client.delete(URL_PREFIX + str(self.user.id) + '/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                         'Se esperaba un código de respuesta 204 (NO CONTENT)')
        sessions = Session.objects.all()
        sessions = [s for s in sessions if s.get_decoded().get('_auth_user_id') == str(self.user.id)]
        self.assertEqual(0, len(sessions), 'No puede haber ninguna sesión del usuario eliminado')


    def test_update_patch_ok(self):
        data = {
            'email': 'usuario@usu.com',
        }
        response = self.client.patch(URL_PREFIX + str(self.user.id) + '/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Se esperaba un código de respuesta 200 (OK)')

    '''
    ------------------------------------------------------------------------------------------------------------------
    *****************		Tests ERRORES DE AUTENTICACIÓN / PERMISOS	**********************************************
    ------------------------------------------------------------------------------------------------------------------
    '''

    def test_list_not_authenticated_ko(self):
        self.client.logout()
        response = self.client.get(URL_PREFIX)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                         'Se esperaba un código de respuesta 401 (UNAUTHORIZED')

    def test_detail_not_authenticated_ko(self):
        self.client.logout()
        response = self.client.get(URL_PREFIX + str(self.admin) + '/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                         'Se esperaba un código de respuesta 401 (UNAUTHORIZED')

    def test_delete_not_authenticated_ko(self):
        self.client.logout()
        response = self.client.delete(URL_PREFIX + str(self.admin) + '/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                         'Se esperaba un código de respuesta 401 (UNAUTHORIZED')

    def test_create_not_authenticated_ok(self):
        self.client.logout()
        data = {
            'username': 'nuevo_usuario',
            'email': 'usu@usu.com',
            "first_name": "usuario",
            "last_name": "usuarin"
        }
        response = self.client.post(URL_PREFIX, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Se esperaba un código de respuesta 400 (BAD REQUEST')

    def test_update_put_not_authenticated_ko(self):
        self.client.logout()
        data = {
            'username': 'usuario_modificado',
            'email': 'usuario@usu.com',
            "first_name": "usuario",
            "last_name": "usuarin"
        }

        response = self.client.put(URL_PREFIX + str(self.user.id) + '/', data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                         'Se esperaba un código de respuesta 401 (UNAUTHORIZED')

    def test_update_patch_not_authenticated_ko(self):
        self.client.logout()
        data = {
            'email': 'usuario@usu.com',
        }

        response = self.client.patch(URL_PREFIX + str(self.user.id) + '/', data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                         'Se esperaba un código de respuesta 401 (UNAUTHORIZED')

    def test_list_unauthorized_user_ko(self):
        self.client.logout()
        self.client.login(username='usuario', password='usuario')

        response = self.client.get(URL_PREFIX)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         'Se esperaba un código de respuesta 200 (OK')


    def test_delete_unauthorized_user_ko(self):
        self.client.logout()
        self.client.login(username='usuario', password='usuario')
        response = self.client.delete(URL_PREFIX + str(self.admin.id) + '/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         'Se esperaba un código de respuesta 403 (FORBIDDEN)')


    def test_update_patch_authorized_user_ok(self):
        self.client.logout()
        self.client.login(username='usuario', password='usuario')
        data = {
            'email': 'usuario@usu.com',
        }

        response = self.client.patch(URL_PREFIX + str(self.user.id) + '/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         'Se esperaba un código de respuesta 200 (OK')

    '''
    ------------------------------------------------------------------------------------------------------------------
    *****************		Tests ERRORES CRUD		******************************************************************
    ------------------------------------------------------------------------------------------------------------------
    '''

    def test_create_username_repetido_ko(self):
        data = {
            'username': 'usuario',
            'email': 'usu@usu.com',
            "first_name": "usuario",
            "last_name": "usuarin"
        }
        response = self.client.post(URL_PREFIX, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Se esperaba un código de respuesta 400 (BAD REQUEST)')

    def test_create_no_datos_ko(self):
        data = {}
        response = self.client.post(URL_PREFIX, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Se esperaba un código de respuesta 400 (BAD REQUEST)')

    def test_create_falta_campo_obligatorio(self):
        data = {
            'email': 'usu@usu.com',
            "first_name": "usuario",
            "last_name": "usuarin"
        }
        response = self.client.post(URL_PREFIX, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Se esperaba un código de respuesta 400 (BAD REQUEST)')

    def test_create_username_blank_ko(self):
        data = {
            'username': '',
            'email': 'usu@usu.com',
            "first_name": "usuario",
            "last_name": "usuarin"
        }
        response = self.client.post(URL_PREFIX, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Se esperaba un código de respuesta 400 (BAD REQUEST)')

    def test_detail_no_existe_ko(self):
        response = self.client.get(URL_PREFIX + '9999999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND,
                         'Se esperaba un código de respuesta 404 (NOT FOUND)')

    def test_delete_no_existe_ko(self):
        response = self.client.delete(URL_PREFIX + '9999999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND,
                         'Se esperaba un código de respuesta 404 (NOT FOUND)')

    def test_update_put_no_existe_ko(self):
        data = {
            'username': 'usuario_modificado',
            'email': 'usuario@usu.com',
            "first_name": "usuario",
            "last_name": "usuarin"
        }

        response = self.client.put(URL_PREFIX + '9999999999/', data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND,
                         'Se esperaba un código de respuesta 404 (NOT FOUND)')

    def test_update_patch_no_existe_ko(self):
        data = {
            'email': 'usuario@usu.com',
        }
        response = self.client.patch(URL_PREFIX + '9999999999/', data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND,
                         'Se esperaba un código de respuesta 404 (NOT FOUND)')

    def test_update_put_username_repetido_ko(self):
        data = {
            'username': 'admin',
            'email': 'usuario@usu.com',
            "first_name": "usuario",
            "last_name": "usuarin"
        }

        response = self.client.put(URL_PREFIX + str(self.user.id) + '/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Se esperaba un código de respuesta 400 (BAD REQUEST)')

    def test_update_patch_username_repetido_ko(self):
        data = {
            'username': 'admin',
        }

        response = self.client.patch(URL_PREFIX + str(self.user.id) + '/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Se esperaba un código de respuesta 400 (BAD REQUEST)')

    def test_update_put_username_blank_ko(self):
        data = {
            'username': '',
            'email': 'usuario@usu.com',
            "first_name": "usuario",
            "last_name": "usuarin"
        }

        response = self.client.put(URL_PREFIX + str(self.user.id) + '/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Se esperaba un código de respuesta 400 (BAD REQUEST)')

    def test_update_patch_username_blank_ko(self):
        data = {
            'username': '',
        }

        response = self.client.patch(URL_PREFIX + str(self.user.id) + '/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Se esperaba un código de respuesta 400 (BAD REQUEST)')

    def test_update_put_username_longitud_mayor_que_permitida_ko(self):
        data = {
            'username': 'usuariousuariousuariousuariousuariousuariousuariousuariousuario',
            'email': 'usuario@usu.com',
            "first_name": "usuario",
            "last_name": "usuarin"
        }

        response = self.client.put(URL_PREFIX + str(self.user.id) + '/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Se esperaba un código de respuesta 400 (BAD REQUEST)')

    def test_update_patch_username_longitud_mayor_que_permitida_ko(self):
        data = {
            'username': 'usuariousuariousuariousuariousuariousuariousuariousuariousuario',

        }

        response = self.client.patch(URL_PREFIX + str(self.user.id) + '/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Se esperaba un código de respuesta 400 (BAD REQUEST)')

    def test_update_put_first_name_last_name_longitud_mayor_que_permitida_ko(self):
        data = {
            'username': 'usuario_modificado',
            'email': 'usuario@usu.com',
            "first_name": "usuariousuariousuariousuariousuariousuariousuariousuariousuario",
            "last_name": "usuariousuariousuariousuariousuariousuariousuariousuariousuario"
        }

        response = self.client.put(URL_PREFIX + str(self.user.id) + '/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Se esperaba un código de respuesta 400 (BAD REQUEST)')

    def test_update_patch_first_name_last_name_longitud_mayor_que_permitida_ko(self):
        data = {
            "first_name": "usuariousuariousuariousuariousuariousuariousuariousuariousuario",
            "last_name": "usuariousuariousuariousuariousuariousuariousuariousuariousuario"
        }

        response = self.client.patch(URL_PREFIX + str(self.user.id) + '/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Se esperaba un código de respuesta 400 (BAD REQUEST)')

    def test_update_put_username_formato_no_permitido_ko(self):
        data = {
            'username': 'usuario   modificado',
            'email': 'usuario@usu.com',
            "first_name": "usuario",
            "last_name": "usuario"
        }

        response = self.client.put(URL_PREFIX + str(self.user.id) + '/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Se esperaba un código de respuesta 400 (BAD REQUEST)')

    def test_update_patch_username_formato_no_permitido_ko(self):
        data = {
            'username': 'usuario   modificado',
        }

        response = self.client.patch(URL_PREFIX + str(self.user.id) + '/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Se esperaba un código de respuesta 400 (BAD REQUEST)')

    '''
    ------------------------------------------------------------------------------------------------------------------
    *****************		Tests LOGIN / LOGOUT		**************************************************************
    ------------------------------------------------------------------------------------------------------------------
    '''

