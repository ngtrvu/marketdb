import re
from six import text_type

from django.conf import settings
from django.utils.encoding import smart_str
from rest_framework import exceptions, HTTP_HEADER_ENCODING
from rest_framework.authentication import BaseAuthentication
from google.oauth2 import id_token
from google.auth.transport import requests


SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']
SAFE_URL_PATTERN = [r'^\/(.*)']  # This will be set at the main app
JWT_AUTH_HEADER_PREFIX = "Bearer"

class GoogleAuthentication(BaseAuthentication):
    """

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string specified in the setting
    `JWT_AUTH_HEADER_PREFIX`. For example:

    Authorization: Bearer eyJhbGciOiAiSFMyNTYiLCAidHlwIj
    Authorization: eyJhbGciOiAiSFMyNTYiLCAidHlwIj

    """
    www_authenticate_realm = 'api'

    def get_jwt_value(self, request):
        """
        Support both two cases:

        Authorization: Bearer eyJhbGciOiAiSFMyNTYiLCAidHlwIj
        Authorization: eyJhbGciOiAiSFMyNTYiLCAidHlwIj
        """
        auth_header = self.__get_authorization_header(request).strip()
        auth_header_prefix = JWT_AUTH_HEADER_PREFIX.lower()

        if not auth_header:
            msg = 'Invalid Authorization header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)

        auth_header_parts = auth_header.split()
        if auth_header_prefix and smart_str(auth_header_parts[0].lower()) != auth_header_prefix:
            msg = 'Invalid Authorization header.'
            raise exceptions.AuthenticationFailed(msg)

        if len(auth_header_parts) > 2:
            msg = 'Invalid Authorization header. Credentials string \
                should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        return auth_header_parts[1] if len(auth_header_parts) > 1 else auth_header_parts[0]

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return '{0} realm="{1}"'.format(JWT_AUTH_HEADER_PREFIX, self.www_authenticate_realm)

    def is_uri_by_pass_token(self, request):
        return (
            request.method in SAFE_METHODS and
            self.__is_match_with_pattern(
                SAFE_URL_PATTERN, request.META.get('PATH_INFO')
            )
        )

    def __is_match_with_pattern(self, list_pattern, path):
        for pattern in list_pattern:
            result = re.search(pattern, path)
            if result:
                return True
        return False

    def __get_authorization_header(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION', b'')
        if isinstance(auth, text_type):
            auth = auth.encode(HTTP_HEADER_ENCODING)
        return auth

    def authenticate(self, request):
        jwt_token = self.get_jwt_value(request)
        if not jwt_token:
            return None

        user = self.authenticate_credentials(jwt_token)
        if user:
            return user, jwt_token
        return None

    def authenticate_credentials(self, jwt_token):
        token = jwt_token.decode('utf-8')

        try:
            # get user from google
            user = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_OAUTH_CLIENT_ID)

            if user['aud'] not in [settings.GOOGLE_OAUTH_CLIENT_ID]:
                raise ValueError('Could not verify audience.')

            if hasattr(settings, 'GSUITE_DOMAIN_NAME') and settings.GSUITE_DOMAIN_NAME:
                if ('hd' not in user) or (user['hd'] != settings.GSUITE_DOMAIN_NAME):
                    raise ValueError("Wrong hosted domain. Should be in %s" % settings.GSUITE_DOMAIN_NAME)

        except Exception as error:
            raise exceptions.AuthenticationFailed("Fail auth: %s" % str(error))

        return user
