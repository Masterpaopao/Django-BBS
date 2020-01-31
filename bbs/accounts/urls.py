from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path('personal/',views.personal,name='personal'),
    path('confirm/',views.confirm,name='confirm'),
    path('prompt/',views.prompt,name='prompt'),
    path('login/', views.login_user, name="login_user"),
    path('logout/',views.logout_user, name='logout_user'),
    path('register/',views.register_user, name='register_user')
]