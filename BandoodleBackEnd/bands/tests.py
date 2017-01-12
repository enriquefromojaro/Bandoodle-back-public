from django.contrib.auth.models import User
from django.test import TestCase

# Create your tests here.
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from bands.models import Band

URL_PREFIX = 'http://localhost:8000/api/bands/'
class BandTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('usuario', 'usuario@mail.com', 'usuario')
        self.user.is_staff = False
        self.admin = User.objects.create_superuser('admin', 'admin@mail.com', 'admin')
        self.user.save()

        self.band = Band.objects.create( name='nueva banda', genre='Rock')
        Band.objects.create( name='baked potato', genre='Rock')
        self.band.users.add(self.user)
        self.band.users.add(self.admin)

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
        response = self.client.get(URL_PREFIX + str(self.band.id) + '/')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Se esperaba un código de respuesta 200 (OK)')

    def test_delete_ok(self):
        #TODO: HACER EL TEST PARA LAS BANDAS
        response = self.client.delete(URL_PREFIX + str(self.band.id) + '/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                         'Se esperaba un código de respuesta 204 (NO CONTENT)')


    def test_update_patch_ok(self):
        #TODO: Hacer para una banda
        data = {
            'email': 'usuario@usu.com',
        }
        response = self.client.patch(URL_PREFIX + str(self.band.id) + '/', data=data)
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

    def test_create_not_authenticated_ko(self):
        self.client.logout()
        data = {

        }
        response = self.client.post(URL_PREFIX, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                         'Se esperaba un código de respuesta 401 (UNAUTHORIZED)')

    def test_update_put_not_authenticated_ko(self):
        self.client.logout()
        data = {
            'username': 'usuario_modificado',
            'email': 'usuario@usu.com',
            "first_name": "usuario",
            "last_name": "usuarin"
        }

        response = self.client.put(URL_PREFIX + str(self.band.id) + '/', data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                         'Se esperaba un código de respuesta 401 (UNAUTHORIZED')

    def test_update_patch_not_authenticated_ko(self):
        self.client.logout()
        data = {
            'email': 'usuario@usu.com',
        }

        response = self.client.patch(URL_PREFIX + str(self.band.id) + '/', data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                         'Se esperaba un código de respuesta 401 (UNAUTHORIZED')

    def test_list_unauthorized_user_ko(self):
        self.client.logout()
        self.client.login(username='usuario', password='usuario')

        response = self.client.get(URL_PREFIX)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         'Se esperaba un código de respuesta 200 (OK')


    def test_update_patch_authorized_user_ok(self):
        #TODO: Hacer para una banda
        self.client.logout()
        self.client.login(username='usuario', password='usuario')
        data = {
            'email': 'usuario@usu.com',
        }

        response = self.client.patch(URL_PREFIX + str(self.band.id) + '/', data=data)
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
        # TODO: Hacer para una banda
        data = {
            'name': 'admin'
        }

        response = self.client.put(URL_PREFIX + str(self.band.id) + '/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Se esperaba un código de respuesta 400 (BAD REQUEST)')

    def test_update_patch_name_repetido_ko(self):
        # TODO: Hacer para una banda
        data = {
            'name': 'baked potato',
        }

        response = self.client.patch(URL_PREFIX + str(self.band.id) + '/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Se esperaba un código de respuesta 400 (BAD REQUEST)')

    def test_update_put_name_blank_ko(self):
        # TODO: Hacer para una banda
        data = {
            'name': ''
        }

        response = self.client.put(URL_PREFIX + str(self.band.id) + '/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Se esperaba un código de respuesta 400 (BAD REQUEST)')

    def test_update_patch_username_blank_ko(self):
         #TODO: Hacer para una banda
        data = {
            'name': '',
        }

        response = self.client.patch(URL_PREFIX + str(self.band.id) + '/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Se esperaba un código de respuesta 400 (BAD REQUEST)')

