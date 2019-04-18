from rest_framework.authentication import SessionAuthentication


class SessionAuthenticationWoCsrf(SessionAuthentication):
    def enforce_csrf(self, request):
        pass
