import json

from django.test import TestCase
from django.test import RequestFactory

from bothub.common.models import RepositoryCategory

from ..views import Categories


class CategoriesTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.category = RepositoryCategory.objects.create(name='Category 1')
        self.business_category = RepositoryCategory.objects.create(
            name='Business',
            icon='business')

    def request(self):
        request = self.factory.get('/api/categories/')
        response = Categories.as_view(
            {'get': 'list'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_default_category_icon(self):
        response, content_data = self.request()
        self.assertEqual(
            content_data[0].get('id'),
            self.category.id)
        self.assertEqual(
            content_data[0].get('icon'),
            'botinho')

    def test_custom_category_icon(self):
        response, content_data = self.request()
        self.assertEqual(
            content_data[1].get('id'),
            self.business_category.id)
        self.assertEqual(
            content_data[1].get('icon'),
            self.business_category.icon)
