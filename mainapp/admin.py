from django.contrib import admin
from .models import Book, Member, Transaction

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'authors', 'isbn', 'publisher', 'num_pages', 'stock')
    search_fields = ('title', 'authors', 'isbn')

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'outstanding_debt')
    search_fields = ('name', 'email')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'book', 'member', 'date', 'due_date', 'fee_charged')
    list_filter = ('transaction_type', 'date')
    search_fields = ('book__title', 'member__name')