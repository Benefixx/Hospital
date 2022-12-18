from rest_framework.generics import (
            ListCreateAPIView,
            RetrieveUpdateDestroyAPIView,
            ListAPIView,
    )
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import USER, ActionHistory, Patient, userProfile, Visit, CustomUser, Service
from .permissions import ActionPermissionClassesMixin, IsOwnerProfileOrReadOnly, IsTokenAdminAuth, IsEveryoneAllowed
from .serializers import ActionHistorySerializer, VisitSerializer, userProfileSerializer, CustomUserSerializer, ServiceSerializer
from .utils import patient_check, patient_create
from .serializers import PatientSerializer

from django.http import HttpResponse
from django.shortcuts import redirect
from django.db.models import Q

from rest_framework import generics, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated,\
                                                IsAdminUser

from rest_framework.views import APIView
from rest_framework.response import Response

from loguru import logger as l

frontend_url = "http://127.0.0.1:3000"


class PatientAPIView(ActionPermissionClassesMixin, viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    action_permission_classes = {
                                        'create': [IsTokenAdminAuth],
                                        'retrieve': [IsEveryoneAllowed],
                                        'list': [IsEveryoneAllowed],
                                        'update': [IsTokenAdminAuth],
                                        'detail': [IsEveryoneAllowed],
                                        'partial_update': [IsTokenAdminAuth],
                                        'destroy': [IsTokenAdminAuth],
                                }
    def get_queryset(self):
        return Patient.objects.all() \
                .exclude(branch="Не выбрано")

    def create(self, request):
        request.data._mutable = True
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

    @action(methods=["get"], detail=True, url_path="find")
    def patient_find_list(self, request, pk: str):
        search_query = pk
        patients = Patient.objects.filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query)  |
            Q(patronymic__icontains=search_query) | 
            Q(chamber__icontains=search_query)    |
            Q(series__icontains=search_query)
        )
        return Response(PatientSerializer(patients, many=True).data)

    @action(methods=["get"], detail=True, url_path="medical")
    def patient_find_list(self, request, pk: str):
        try:
            return Response(PatientSerializer(Patient.objects.get(pk=pk)).data)
        except Patient.DoesNotExist:
            patient = Patient.objects.get(medical_number=pk) 
            return Response(PatientSerializer(patient).data)

    @action(methods=["get"], detail=True, url_path="branch")
    def branch_list(self, request, pk: str):
        if pk == "endocrinology": pk="Эндокринология"
        elif pk == "therapy": pk="Терапия"
        elif pk == "cardiology": pk="Кардиология"
        elif pk == "neurology": pk="Неврология"
        elif pk == "surgical": pk="Хирургическая"

        patients = Patient.objects.filter(branch=pk)
        return Response(PatientSerializer(patients, many=True).data)


class ActionHistoryAPIView(ActionPermissionClassesMixin, viewsets.ModelViewSet):
    queryset = ActionHistory.objects.all()
    serializer_class = ActionHistorySerializer
    action_permission_classes = {
                                        'create': [IsTokenAdminAuth],
                                        'retrieve': [IsEveryoneAllowed],
                                        'list': [IsEveryoneAllowed],
                                        'detail': [IsTokenAdminAuth],
                                        'update': [IsTokenAdminAuth],
                                        'partial_update': [IsTokenAdminAuth],
                                        'destroy': [IsTokenAdminAuth],
                                }

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        actions = ActionHistory.objects.filter(user=pk)
        return Response(ActionHistorySerializer(actions, many=True).data)


class VisitAPIView(ActionPermissionClassesMixin, viewsets.ModelViewSet):
    queryset = Visit.objects.all()
    serializer_class = VisitSerializer
    action_permission_classes = {
                                        'create': [IsEveryoneAllowed],
                                        'retrieve': [IsEveryoneAllowed],
                                        'list': [IsEveryoneAllowed],
                                        'update': [IsEveryoneAllowed],
                                        'detail': [IsEveryoneAllowed],
                                        'partial_update': [IsEveryoneAllowed],
                                        'destroy': [IsEveryoneAllowed],
                                }
    def list(self, request, *args, **kwargs):
        visitors = Visit.objects.filter(solution=None)
        return Response(VisitSerializer(visitors, many=True).data)

    def create(self, request, *args, **kwargs):
        PATIENT = Patient.objects.get(pk=request.data.get('patient'))
        PHONE = request.data.get('phone')
        VISIT_TIME = request.data.get('visit_time')

        response = Visit.objects.create(
            patient=PATIENT,
            phone=PHONE,
            visit_time=VISIT_TIME
        )

        return Response(VisitSerializer(response).data)
    

class StatisticAPIView(APIView):
    def get(self, request):

        patients = Patient.objects.all() \
            .exclude(branch="Не выбрано") \

        doctors = USER.objects.all() \
            .count()

        actions = ActionHistory.objects.all() \
            .count()

        return Response({
                                "patients": patients.count(),
                                "doctors": doctors,
                                "actions": actions,

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


class PersonalAPIView(ActionPermissionClassesMixin, viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    action_permission_classes = {
                                        'create': [IsTokenAdminAuth],
                                        'retrieve': [IsTokenAdminAuth],
                                        'list': [IsEveryoneAllowed],
                                        'update': [IsTokenAdminAuth],
                                        'detail': [IsEveryoneAllowed],
                                        'partial_update': [IsTokenAdminAuth],
                                        'destroy': [IsTokenAdminAuth],
                                }

    def list(self, request, *args, **kwargs):
        personal = CustomUser.objects.filter(is_staff=True)[0:4]
        return Response(CustomUserSerializer(personal, many=True).data)  


class ServiceAPIView(ActionPermissionClassesMixin, viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    action_permission_classes = {
                                        'create': [IsTokenAdminAuth],
                                        'retrieve': [IsTokenAdminAuth],
                                        'list': [IsEveryoneAllowed],
                                        'update': [IsTokenAdminAuth],
                                        'detail': [IsEveryoneAllowed],
                                        'partial_update': [IsTokenAdminAuth],
                                        'destroy': [IsTokenAdminAuth],
                                }


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