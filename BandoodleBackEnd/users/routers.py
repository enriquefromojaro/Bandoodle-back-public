from django.conf.urls import url

from users import views

pwd_routes = [
    url(r'^password-remember/(?P<username>[a-zA-ZÑñ_@]+)/$', views.password_remember),
    url(r'^password-reset/(?P<encoded_email>[^\/.]+)/(?P<encoded_token>[^\/.]+)/$',
        views.password_reset)
]
