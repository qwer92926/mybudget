from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.home, name='home'),  # 設置首頁URL
    path('list/', views.expense_list, name='expense_list'),  # 確保這行存在並且正確
    path('create/', views.expense_create, name='expense_create'),
    path('edit/<int:pk>/', views.expense_edit, name='expense_edit'),
    path('delete/<int:pk>/', views.expense_delete, name='expense_delete'),
    path('chart/', views.expense_chart, name='expense_chart'),
    path('report/', views.expense_report, name='expense_report'),
    path('summary/', views.monthly_summary, name='monthly_summary'),  # 添加這行
]
