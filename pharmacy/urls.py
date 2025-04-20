from django.urls import path
from . import views

app_name = 'pharmacy'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('prescriptions/', views.prescription_list, name='prescription_list'),
    path('prescription/<int:prescription_id>/process/', views.process_prescription, name='process_prescription'),

    # Invoice routes
    path('dispensing/<int:dispensing_id>/invoice/create/', views.create_invoice, name='create_invoice'),
    path('invoice/<int:invoice_id>/', views.view_invoice, name='view_invoice'),
    
    # Delivery routes
    path('dispensing/<int:dispensing_id>/delivery/', views.manage_delivery, name='manage_delivery'),
    path('delivery/<int:delivery_id>/', views.view_delivery, name='view_delivery'),
]
