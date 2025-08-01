import os
import requests
import json

from rest_framework import permissions


class AdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        email = self.get_user_email(request)
        if not email:
            return False

        namespace = self.get_namespace(request)
        if not namespace:
            return False

        return self.check_access(email, namespace)

    def get_user_email(self, request):
        email = ""
        if request.user and request.user.get("email"):
            email = request.user.get("email")

        return email

    def get_namespace(self, request):
        namespace = ""

        path = request.path
        if "stagedu-api" in path:
            namespace = "stagedu"
        elif "marketdb-api" in path:
            namespace = "marketdb"

        return namespace

    def check_access(self, email, namespace):
        iamcore_host = os.environ.get("IAMCORE_HOST", "iamcore-api.iamcore:8088")
        url = "http://{0}/iamcore-api/admin/v1/check-access".format(iamcore_host)
        payload = {
            "email": email,
            "namespace": namespace,
        }
        response = requests.post(url, data=json.dumps(payload))
        if response.status_code == 200 or response.status_code == 201:
            return True

        return False
