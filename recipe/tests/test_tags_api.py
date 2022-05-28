"""
Tests for the tags API.
"""
from django.urls import reverse
from django.test import TestCase
from django.db.models import QuerySet
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.response import Response
from recipe.tests.utils import (
    create_user,
    create_tag,
    tag_detail_url
)
from core.models import (
    User as CustomUser,
    Tag
)
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """
    Test unauthenticated API requests.
    """

    def setUp(self) -> None:
        self.client: APIClient = APIClient()

    def test_auth_required(self):
        """
        Test auth is required for retrieving tags.
        """
        res: Response = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """
    Test authenticated API requests.
    """

    def setUp(self) -> None:
        self.user: CustomUser = create_user(
            email='user@example.com',
            password='testpass123')
        self.client: APIClient = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """
        Test retrieving a list of tags.
        """
        for i in range(3):
            create_tag(user=self.user, name=f'Tag{i+1}')

        res: Response = self.client.get(TAGS_URL)
        tags: QuerySet[Tag] = Tag.objects.all().order_by('-name')
        serializer: TagSerializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_request_user(self):
        """
        Test list of a tags is limitied to authenticated request
        user.
        """
        user2: CustomUser = create_user(
            email='user2@example.com',
            password='testpass123')
        create_tag(user=user2, name='Fruity')
        tag: Tag = create_tag(user=self.user, name='Comfort Food')
        res: Response = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], str(tag.id))

    def test_update_tag(self) -> None:
        """
        Test updating a tag.
        """
        tag: Tag = create_tag(user=self.user, name='After Dinner')
        payload: dict = {'name': 'Desert'}
        url = tag_detail_url(tag_id=tag.id)

        res: Response = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """
        Test deleting a tag.
        """
        tag: Tag = create_tag(user=self.user, name='Breakfast')
        url: str = tag_detail_url(tag_id=tag.id)
        res: Response = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags: QuerySet[Tag] = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())
