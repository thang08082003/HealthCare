from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from users.models import User
from patient.models import Patient, MedicalRecord
from doctor.models import Doctor, Specialization
from appointment.models import Appointment
from prescription.models import Prescription, PrescriptionItem
from laboratory.models import LabTest, TestResult
from insurance.models import InsuranceProvider, InsurancePolicy, InsuranceClaim
from .serializers import (
    UserSerializer, PatientSerializer, MedicalRecordSerializer, 
    DoctorSerializer, AppointmentSerializer, PrescriptionSerializer,
    PrescriptionItemSerializer, LabTestSerializer, TestResultSerializer,
    InsuranceProviderSerializer, InsurancePolicySerializer, InsuranceClaimSerializer
)

class IsOwnerOrMedicalStaff(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or medical staff to access it.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Medical staff can access all records
        if user.is_doctor or user.is_nurse or user.is_admin:
            return True
        
        # Patients can only access their own records
        if hasattr(obj, 'user') and obj.user == user:
            return True
        
        if hasattr(obj, 'patient'):
            if hasattr(obj.patient, 'user') and obj.patient.user == user:
                return True
        
        return False


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing user information"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=user.id)


class PatientViewSet(viewsets.ModelViewSet):
    """ViewSet for patients"""
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrMedicalStaff]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_doctor or user.is_nurse or user.is_admin or user.is_superuser:
            return Patient.objects.all()
        if user.is_patient:
            return Patient.objects.filter(user=user)
        return Patient.objects.none()


class MedicalRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for medical records"""
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrMedicalStaff]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_doctor or user.is_nurse or user.is_admin or user.is_superuser:
            return MedicalRecord.objects.all()
        
        if user.is_patient:
            try:
                return MedicalRecord.objects.filter(patient__user=user)
            except:
                pass
        
        return MedicalRecord.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DoctorViewSet(viewsets.ModelViewSet):
    """ViewSet for doctors"""
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated, IsOwnerOrMedicalStaff]
        return super().get_permissions()


class AppointmentViewSet(viewsets.ModelViewSet):
    """ViewSet for appointments"""
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return Appointment.objects.all()
        
        if user.is_doctor:
            try:
                return Appointment.objects.filter(doctor__user=user)
            except:
                pass
        
        if user.is_patient:
            try:
                return Appointment.objects.filter(patient__user=user)
            except:
                pass
        
        return Appointment.objects.none()
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change the status of an appointment"""
        appointment = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Appointment.STATUS_CHOICES):
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
        
        appointment.status = new_status
        appointment.save()
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)


class PrescriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for prescriptions"""
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrMedicalStaff]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_doctor or user.is_pharmacist or user.is_admin or user.is_superuser:
            return Prescription.objects.all()
        
        if user.is_patient:
            try:
                return Prescription.objects.filter(patient__user=user)
            except:
                pass
        
        return Prescription.objects.none()


class LabTestViewSet(viewsets.ModelViewSet):
    """ViewSet for lab tests"""
    serializer_class = LabTestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_lab_technician or user.is_doctor or user.is_admin or user.is_superuser:
            return LabTest.objects.all()
        
        if user.is_patient:
            try:
                return LabTest.objects.filter(patient__user=user)
            except:
                pass
        
        return LabTest.objects.none()


class InsuranceClaimViewSet(viewsets.ModelViewSet):
    """ViewSet for insurance claims"""
    serializer_class = InsuranceClaimSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_insurance or user.is_admin or user.is_superuser:
            return InsuranceClaim.objects.all()
        
        if user.is_patient:
            try:
                return InsuranceClaim.objects.filter(patient__user=user)
            except:
                pass
        
        return InsuranceClaim.objects.none()
    
    @action(detail=True, methods=['post'])
    def process_claim(self, request, pk=None):
        """Process an insurance claim"""
        claim = self.get_object()
        
        # Only insurance providers can process claims
        if not request.user.is_insurance and not request.user.is_admin and not request.user.is_superuser:
            return Response({"error": "Only insurance providers can process claims"}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        approval_status = request.data.get('approval_status')
        approved_amount = request.data.get('approved_amount')
        notes = request.data.get('notes', '')
        
        if approval_status not in ['approved', 'rejected', 'partial']:
            return Response({"error": "Invalid approval status"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        claim.approval_status = approval_status
        
        if approval_status in ['approved', 'partial']:
            try:
                claim.approved_amount = float(approved_amount)
            except (TypeError, ValueError):
                return Response({"error": "Invalid approved amount"}, 
                               status=status.HTTP_400_BAD_REQUEST)
        
        claim.notes = notes
        claim.processed_date = timezone.now()
        claim.processed_by = request.user
        claim.save()
        
        serializer = self.get_serializer(claim)
        return Response(serializer.data)
