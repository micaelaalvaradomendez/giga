from django.urls import path
from .views_auth import login_view, logout_view, recover_password, update_profile, check_session

app_name = 'personas_auth'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('check-session/', check_session, name='check_session'),
    path('recover-password/', recover_password, name='recover_password'),
    path('update-profile/', update_profile, name='update_profile'),
]
