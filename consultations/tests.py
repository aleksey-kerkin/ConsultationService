from django.test import TestCase
from rest_framework.test import APIClient

from .models import Consultation, Slot, Specialist, User


class ConsultationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_consultation(self):
        specialist = Specialist.objects.create(user=self.user)
        slot = Slot.objects.create(
            specialist=specialist,
            start_time="2023-10-10T10:00:00Z",
            end_time="2023-10-10T11:00:00Z",
            cost=100,
            service_type="Test Service",
        )
        response = self.client.post(
            "/api/consultations/", {"slot": slot.pk, "client": self.user.pk}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Consultation.objects.count(), 1)

    def test_cancel_consultation(self):
        specialist = Specialist.objects.create(user=self.user)
        slot = Slot.objects.create(
            specialist=specialist,
            start_time="2023-10-10T10:00:00Z",
            end_time="2023-10-10T11:00:00Z",
            cost=100,
            service_type="Test Service",
        )
        consultation = Consultation.objects.create(slot=slot, client=self.user)
        response = self.client.post(
            f"/api/consultations/{consultation.pk}/cancel/",
            {"reason": "Test reason"},
        )
        self.assertEqual(response.status_code, 200)
        consultation.refresh_from_db()
        self.assertEqual(consultation.cancellation_reason, "Test reason")
