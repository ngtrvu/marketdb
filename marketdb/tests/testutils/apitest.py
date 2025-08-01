import io
import uuid
from unittest import mock

from PIL import Image
from rest_framework.test import APIClient, APITestCase


class APITest(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def generate_photo_file(self, name=None):
        file = io.BytesIO()
        image = Image.new("RGBA", size=(100, 100), color=(155, 0, 0))
        image.save(file, "png")
        file.name = f"{name if name else uuid.uuid4()}.png"
        file.seek(0)
        return file


class AdminAPITest(APITest):
    def login(self, mock_function):
        self.client.logout()

        # Logged in as current user
        jwt = "jwtAbcXyz"
        auth_header_type = "JWT"

        mock_function.return_value = (
            {},
            jwt,
        )
        self.client.credentials(HTTP_AUTHORIZATION=" ".join([auth_header_type, jwt]))

    @mock.patch("common.auth.google.GoogleAuthentication.authenticate")
    def get(self, url, mock_function, format=None, **kwargs):
        self.login(mock_function)
        return self.client.get(url, format, **kwargs)

    @mock.patch("common.auth.google.GoogleAuthentication.authenticate")
    def post(self, url, data, mock_function, format=None):
        self.login(mock_function)
        return self.client.post(url, data, format)

    @mock.patch("common.auth.google.GoogleAuthentication.authenticate")
    def put(self, url, data, mock_function, format=None):
        self.login(mock_function)
        return self.client.put(url, data, format)

    @mock.patch("common.auth.google.GoogleAuthentication.authenticate")
    def patch(self, url, data, mock_function, format=None):
        self.login(mock_function)
        return self.client.patch(url, data, format)

    @mock.patch("common.auth.google.GoogleAuthentication.authenticate")
    def delete(self, url, mock_function):
        self.login(mock_function)
        return self.client.delete(url)
