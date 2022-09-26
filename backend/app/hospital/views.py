
from rest_framework.generics import (
            ListCreateAPIView,
            RetrieveUpdateDestroyAPIView,
            ListAPIView,
    )
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .utils import patient_check, patient_create

from .models import USER, ActionHistory, Patient, userProfile
from .permissions import ActionPermissionClassesMixin, IsOwnerProfileOrReadOnly, IsTokenAdminAuth
from .serializers import ActionHistorySerializer, userProfileSerializer

from django.http import HttpResponse
from django.shortcuts import redirect

from rest_framework import generics, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated,\
                                                IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import PatientSerializer

from loguru import logger as l

frontend_url = "http://127.0.0.1:3000"

class PatientAPIView(ActionPermissionClassesMixin, viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    action_permission_classes = {
                                        'create': [IsTokenAdminAuth],
                                        'retrieve': [IsTokenAdminAuth],
                                        'list': [IsTokenAdminAuth],
                                        'update': [IsTokenAdminAuth],
                                        'detail': [IsTokenAdminAuth],
                                        'partial_update': [IsTokenAdminAuth],
                                        'destroy': [IsTokenAdminAuth],
                                }
    def get_queryset(self):
        return Patient.objects.all() \
                .exclude(branch="Не выбрано")

    def create(self, request):
        check = patient_check(data=request.data) # Проверяем пользователя на наличе, если есть то обновляем его
        if check:
            return Response(PatientSerializer(check).data)
        else:
            patient = patient_create(data=request.data)
            if patient == "Не выбрали отделение":
                return Response({"error": "Ошибка! Вы не выбрали отделение"})
            if patient == "Нет мест":
                return Response({"error": "Ошибка! Мест в данном отделении нет"})

            return Response(PatientSerializer(patient).data)

class ActionHistoryAPIView(ActionPermissionClassesMixin, viewsets.ModelViewSet):
    queryset = ActionHistory.objects.all()
    serializer_class = ActionHistorySerializer
    action_permission_classes = {
                                        'create': [IsTokenAdminAuth],
                                        'retrieve': [IsTokenAdminAuth],
                                        'list': [IsTokenAdminAuth],
                                        'detail': [IsTokenAdminAuth],
                                        'update': [IsTokenAdminAuth],
                                        'partial_update': [IsTokenAdminAuth],
                                        'destroy': [IsTokenAdminAuth],
                                }

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        actions = ActionHistory.objects.filter(user=pk)
        return Response(ActionHistorySerializer(actions, many=True).data)

class StatisticAPIView(APIView):
    def get(self, request):

        patients = Patient.objects.all() \
        .exclude(branch="Не выбрано") \

        doctors = USER.objects.all() \
        .count()

        return Response({
                                "patients": patients.count(),
                                "doctors": doctors,
                                
                                "therapy": patients.filter(branch="Терапия") \
                                                    .count(),

                                "cardiology": patients.filter(branch="Кардиология") \
                                                    .count(),
                                                    
                                "neurology": patients.filter(branch="Неврология") \
                                                    .count(),

                                "surgical": patients.filter(branch="Хирургическая") \
                                                    .count(),

                                "endocrinology": patients.filter(branch="Эндокринология") \
                                                    .count(),
        })



class UserProfileListCreateView(ListCreateAPIView):
    queryset = userProfile.objects.all()
    serializer_class = userProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

class userProfileDetailView(RetrieveUpdateDestroyAPIView):
    queryset = userProfile.objects.all()
    serializer_class = userProfileSerializer
    permission_classes = [IsOwnerProfileOrReadOnly,IsAuthenticated]

def email_activate(request, uid, token):
    return redirect(f'{frontend_url}/activate/{uid}/{token}/')