import base64
from _md5 import md5

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, renderer_classes, detail_route
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from BandoodleBackEnd.permissions import UserPermissions
from BandoodleBackEnd.settings import EMAIL_HOST_USER, HOST_NAME
from bands.models import Band
from bands.serializers import BandSerializer
from users.forms import PasswordResetForm
from users.serializers import UserSerializer

# Create your views here.


RAW_SIGN = '_kEU9>3Xa$hZRtrw8j5<G-e4{Z4R!Uf55B}wqZ)qv(6#]#.Z+K'

FORGOTEN_PASSWORD_MESSAGE = '''
Se ha solicitado un cambio de contraseña. Haga click en el siguiente enlace para cambiarla.
INSERTLINK

Si no ha sido usted, alguien inentó iniciar sesión con su cuenta.
'''
API_ROOT_URL = 'http://'+HOST_NAME+':8000/'
URL_PREFIX = API_ROOT_URL + 'usuario/'


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def password_remember(request, username):
    try:
        user = User.objects.get(username=username)

        encoded_email = base64.urlsafe_b64encode(user.email.encode('utf-8'))
        decoded_token = user.email + RAW_SIGN + user.username
        encoded_token = md5(decoded_token.encode(encoding='utf-8')).digest()
        encoded_token = base64.urlsafe_b64encode(encoded_token)
        data = {
            'detail': 'Se ha enviado un email',
        }
        link = API_ROOT_URL + 'password-reset/' + encoded_email.decode('utf-8') + '/' \
               + encoded_token.decode('utf-8') + '/'

        mail_message = FORGOTEN_PASSWORD_MESSAGE.replace('INSERTLINK', link)
        send_mail('Contraseña olvidada', mail_message,
                  EMAIL_HOST_USER, [user.email])
        return Response(data=data, status=status.HTTP_200_OK)
    except:
        return Response(data={'detail': 'No existe dicho usuario'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@renderer_classes([JSONRenderer])
def password_reset(request, encoded_email, encoded_token):
    errors = {}
    email = base64.urlsafe_b64decode(encoded_email).decode('utf-8')
    email_users = User.objects.filter(email=email)
    if len(email_users) != 0:
        '''---------------------------------------------------------------------------------------------------------
                    Parte común. tanto si se van a procesar os datos del formulario como si se va a mandar el mismo,
                    validamos las credenciales y hallamos el usuario al que pertenece
        ----------------------------------------------------------------------------------------------------------'''
        valid_users = [
            u for u in email_users if md5((email + RAW_SIGN + email_users[0].username).encode('utf-8')).digest()
            == base64.urlsafe_b64decode(encoded_token)
            ]
        if len(valid_users) == 0:
            # ERROR: Petición NO válida
            context = {
                'detail': 'No existe ese usuario'
            }

            return render(request, 'password_reset_error.html', context)
        else:
            # Debido a cómo está hecho, sólo se puede correspnder con un usuario ya que el username es único
            user = valid_users[0]

        '''--------------------------------------------------------------------------------------------------------
                    Parte no común. discernir entre la petición del formulario (GET)
                     y el procesado de lo puesto en el mismo (POST)
        -----------------------------------------------------------------------------------------------------------'''
        form = PasswordResetForm()
        context = {
            'form': form,
            'errors': None,
            'success': False,
            'username': user.username,
            'api_root': API_ROOT_URL,
        }

        if request.method == 'POST':
            form = PasswordResetForm(data=request.POST)
            if form.is_valid(user):
                user.set_password(form.cleaned_data.get('password'))
                user.save()
                context['success'] = True
            else:
                context['errors'] = form.errors.as_data().get('__all__')
                context['errors'] += form.errors.as_data().get('password', [])
                context['errors'] = [' , '.join(e.messages) for e in context.get('errors')]

        return render(request, 'password_reset_form.html', context)


    else:
        context = {
            'detail': 'url inválida'
        }
        return render(request, 'password_reset_error.html', context)


class MusicianViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (UserPermissions,)
    parser_classes = (JSONParser, MultiPartParser)

    def destroy(self, request, *args, **kwargs):
        try:
            user = User.objects.get(pk=kwargs.get('pk'))
            sessions = [s for s in Session.objects.all() if s.get_decoded().get('_auth_user_id') == str(user.id)]
            for s in sessions:
                s.delete()
        finally:
            return super().destroy(request, *args, **kwargs)





# LOG IN
@api_view(['POST'])
@renderer_classes([JSONRenderer])
def login(request):
    data = request.data
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        data = {
            'errors': [

            ]
        }
        if not username:
            data.get('errors').append('username is required')
        if not password:
            data.get('errors').append('password is required')
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
    try:

        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None
    if user and password and user.check_password(password):
        token_key = Token.objects.get(user=user).key
        data = {
            'message': 'Successful login',
            'user': UserSerializer(instance=user).data,
            'Token': token_key
        }
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        data = {
            'message': 'Incorrect username and/or password'
        }
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


# ----------------------------------------------------------------------------------

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
