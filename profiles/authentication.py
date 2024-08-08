from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header:
            return None

        try:
            prefix, token = auth_header.split(' ')
            if prefix.lower() != 'bearer':
                raise AuthenticationFailed('Invalid token header. No credentials provided.')

            jwt_auth = JWTAuthentication()
            return jwt_auth.authenticate(request)
        except ValueError:
            raise AuthenticationFailed('Invalid token header. No credentials provided.')
        except Exception as e:
            raise AuthenticationFailed(str(e))
