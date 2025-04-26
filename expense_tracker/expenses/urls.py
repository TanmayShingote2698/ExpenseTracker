from django.urls import path
from .views import dashboard, add_expense, edit_expense, delete_expense, user_login, user_logout, user_register
from django.urls import path
from .views import generate_pdf
urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('add/', add_expense, name='add_expense'),
    path('edit/<int:expense_id>/', edit_expense, name='edit_expense'),
    path('delete/<int:expense_id>/', delete_expense, name='delete_expense'),
    path('login/', user_login, name='login'),  # ✅ Make sure this line exists
    path('logout/', user_logout, name='logout'),
    path('register/', user_register, name='register'),
        path('download-pdf/', generate_pdf, name='download_pdf'),
        path('generate-pdf/',generate_pdf, name='generate_pdf'),
    
]
