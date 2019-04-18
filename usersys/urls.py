from django.conf.urls import url, include
from usersys.views import (
    login,
    user,
)

urlpatterns = [
    url(r'^login/$', login.LoginView.as_view()),  # Login
    url(r'^user/$', user.UserView.as_view()),  # Obtain user detail; Update user's pn and password.
]
