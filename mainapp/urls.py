from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Book URLs
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.book_create, name='book_create'),
    path('books/<int:pk>/edit/', views.book_update, name='book_update'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),

    # Member URLs
    path('members/', views.member_list, name='member_list'),
    path('members/add/', views.member_create, name='member_create'),
    path('members/<int:pk>/edit/', views.member_update, name='member_update'),
    path('members/<int:pk>/delete/', views.member_delete, name='member_delete'),

    # Transaction URLs
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/add/', views.transaction_create, name='transaction_create'),

    # Import Books
    path('import-books/', views.import_books, name='import_books'),
]
