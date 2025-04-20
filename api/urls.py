from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, PatientViewSet, MedicalRecordViewSet,
    DoctorViewSet, AppointmentViewSet, PrescriptionViewSet,
    LabTestViewSet, InsuranceClaimViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'medical-records', MedicalRecordViewSet, basename='medical-record')
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')
router.register(r'lab-tests', LabTestViewSet, basename='lab-test')
router.register(r'insurance-claims', InsuranceClaimViewSet, basename='insurance-claim')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]
