import unittest
from unittest import mock
from django.urls import reverse
from rest_framework import status

from tests.testutils.apitest import AdminAPITest


class SearchReindexTestCase(AdminAPITest):
    def setUp(self):
        super(SearchReindexTestCase, self).setUp()

    @mock.patch('core.services.search.search_index.SearchReindexService.call')
    def test_search_reindex_success(self, mock_call):
        mock_call.return_value = True

        url = reverse("api_internal:search-reindex")
        data = {}

        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mock_call.assert_called_once()
