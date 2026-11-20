from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class ChatbotPermissionsTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_intents", stdout=StringIO())
        users = get_user_model().objects
        cls.staff = users.create_user(
            username="staff-test", password="test-password-only", is_staff=True
        )
        cls.student = users.create_user(
            username="student-test", password="test-password-only"
        )

    def test_student_chat_is_public(self):
        response = self.client.post(
            "/api/chat/", {"message": "What is the fee structure?"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["matched_intent"], "fee_structure")

    def test_admin_login_requires_staff(self):
        for user, expected in [
            (self.student, status.HTTP_401_UNAUTHORIZED),
            (self.staff, status.HTTP_200_OK),
        ]:
            with self.subTest(username=user.username):
                response = self.client.post(
                    "/api/auth/login/",
                    {"username": user.username, "password": "test-password-only"},
                    format="json",
                )
                self.assertEqual(response.status_code, expected)

    def test_non_staff_cannot_access_admin_api_with_an_existing_token(self):
        token = Token.objects.create(user=self.student)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        self.assertEqual(
            self.client.get("/api/admin/dashboard/stats/").status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.post("/api/admin/categories/", {}, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_staff_can_read_admin_dashboard(self):
        token = Token.objects.create(user=self.staff)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        self.assertEqual(
            self.client.get("/api/admin/dashboard/stats/").status_code,
            status.HTTP_200_OK,
        )
