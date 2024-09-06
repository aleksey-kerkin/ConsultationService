import logging

from django.core.cache import cache
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Consultation, Slot, Specialist, User
from .permissions import IsClientOrReadOnly, IsSpecialistOrReadOnly
from .serializers import (
    ConsultationSerializer,
    CustomUserSerializer,
    SlotSerializer,
    SpecialistSerializer,
)
from .utils import (
    send_cancellation_notification,
    send_consultation_notification,
)

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAdminUser]


class SpecialistViewSet(viewsets.ModelViewSet):
    queryset = Specialist.objects.all()
    serializer_class = SpecialistSerializer
    permission_classes = [permissions.IsAuthenticated]


class SlotViewSet(viewsets.ModelViewSet):
    queryset = Slot.objects.all()
    serializer_class = SlotSerializer
    permission_classes = [permissions.IsAuthenticated, IsSpecialistOrReadOnly]

    def perform_create(self, serializer):
        if Slot.objects.filter(
            specialist=self.request.user.specialist,
            start_time=serializer.validated_data["start_time"],
        ).exists():
            raise ValidationError("Slot already exists for this time.")
        serializer.save(specialist=self.request.user.specialist)

    def list(self, request, *args, **kwargs):
        cached_slots = cache.get("slots")
        if cached_slots is None:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            cache.set("slots", serializer.data, 60 * 15)  # Кешируем на 15 минут
            return Response(serializer.data)
        return Response(cached_slots)


class ConsultationViewSet(viewsets.ModelViewSet):
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated, IsClientOrReadOnly]

    def perform_create(self, serializer):
        try:
            consultation = serializer.save()
            send_consultation_notification(consultation)
            logger.info(f"Consultation created: {consultation.id}")
        except Exception as e:
            logger.error(f"Error creating consultation: {str(e)}")
            raise

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        try:
            consultation = self.get_object()
            consultation.cancellation_reason = request.data.get(
                "reason", "No reason provided"
            )
            consultation.save()
            send_cancellation_notification(consultation)
            logger.info(f"Consultation cancelled: {consultation.id}")
            return Response({"status": "cancelled"})
        except Exception as e:
            logger.error(f"Error cancelling consultation: {str(e)}")
            raise
