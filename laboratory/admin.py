from django.contrib import admin
from .models import LabTest, LabResultItem

class LabResultItemInline(admin.TabularInline):
    model = LabResultItem
    extra = 1

@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ['test_name', 'test_code', 'description']
    list_filter = ['status', 'priority', 'test_date']
    search_fields = ['test_name', 'test_code']
    inlines = [LabResultItemInline]

@admin.register(LabResultItem)
class LabResultItemAdmin(admin.ModelAdmin):
    list_display = ['parameter_name', 'result', 'unit', 'is_abnormal']
    list_filter = ['is_abnormal', 'test']
    search_fields = ['parameter_name', 'test__test_name']
