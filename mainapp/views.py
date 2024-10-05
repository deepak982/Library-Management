import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from .models import Book, Member, Transaction
from .forms import BookForm, MemberForm, TransactionForm, ImportBooksForm
import datetime

# Home Page
def home(request):
    return render(request, 'home.html')

# Book Views

def book_list(request):
    query = request.GET.get('q')
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) | Q(authors__icontains=query)
        )
    else:
        books = Book.objects.all()
    return render(request, 'books/book_list.html', {'books': books, 'query': query})

def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book added successfully.')
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form})

def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully.')
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form, 'book': book})

def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully.')
        return redirect('book_list')
    return render(request, 'books/book_confirm_delete.html', {'book': book})

# Member Views

def member_list(request):
    members = Member.objects.all()
    return render(request, 'members/member_list.html', {'members': members})

def member_create(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Member added successfully.')
            return redirect('member_list')
    else:
        form = MemberForm()
    return render(request, 'members/member_form.html', {'form': form})

def member_update(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Member updated successfully.')
            return redirect('member_list')
    else:
        form = MemberForm(instance=member)
    return render(request, 'members/member_form.html', {'form': form, 'member': member})

def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        member.delete()
        messages.success(request, 'Member deleted successfully.')
        return redirect('member_list')
    return render(request, 'members/member_confirm_delete.html', {'member': member})

# Transaction Views

def transaction_list(request):
    transactions = Transaction.objects.select_related('member', 'book').all().order_by('-date')
    return render(request, 'transactions/transaction_list.html', {'transactions': transactions})

def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            member = transaction.member
            book = transaction.book

            if transaction.transaction_type == Transaction.ISSUE:
                if book.stock < 1:
                    messages.error(request, 'Book is out of stock.')
                    return redirect('transaction_create')
                if member.outstanding_debt > 500:
                    messages.error(request, 'Member has outstanding debt exceeding Rs.500.')
                    return redirect('transaction_create')
                book.stock -= 1
                transaction.due_date = timezone.now().date() + datetime.timedelta(days=14)
            elif transaction.transaction_type == Transaction.RETURN:
                # Find the corresponding issue transaction
                try:
                    issue_transaction = Transaction.objects.get(
                        member=member,
                        book=book,
                        transaction_type=Transaction.ISSUE,
                        fee_charged=0.00
                    )
                    days_overdue = (timezone.now().date() - issue_transaction.due_date).days
                    if days_overdue > 0:
                        fee = days_overdue * 10  # Rs.10 per day
                        transaction.fee_charged = fee
                        member.outstanding_debt += fee
                        member.save()
                        messages.warning(request, f'Book returned with a fee of Rs.{fee}.')
                except Transaction.DoesNotExist:
                    messages.error(request, 'No corresponding issue transaction found.')
                    return redirect('transaction_create')
                book.stock += 1
            book.save()
            transaction.save()
            messages.success(request, 'Transaction recorded successfully.')
            return redirect('transaction_list')
    else:
        form = TransactionForm()
    return render(request, 'transactions/transaction_form.html', {'form': form})

# Import Books from External API

def import_books(request):
    if request.method == 'POST':
        form = ImportBooksForm(request.POST)
        if form.is_valid():
            num_books = form.cleaned_data['num_books']
            title = form.cleaned_data.get('title')
            authors = form.cleaned_data.get('authors')
            isbn = form.cleaned_data.get('isbn')
            publisher = form.cleaned_data.get('publisher')

            imported = 0
            page = 1
            while imported < num_books:
                params = {'page': page}
                if title:
                    params['title'] = title
                if authors:
                    params['authors'] = authors
                if isbn:
                    params['isbn'] = isbn
                if publisher:
                    params['publisher'] = publisher

                response = requests.get('https://frappe.io/api/method/frappe-library', params=params)
                if response.status_code != 200:
                    messages.error(request, 'Failed to fetch data from external API.')
                    break
                data = response.json().get('message', [])
                if not data:
                    break  # No more data

                for item in data:
                    if imported >= num_books:
                        break
                    # Clean data fields
                    book_data = {
                        'title': item.get('title', 'No Title'),
                        'authors': item.get('authors', 'Unknown'),
                        'isbn': item.get('isbn', ''),
                        'publisher': item.get('publisher', 'Unknown'),
                        'num_pages': item.get('num_pages', 0),
                        'stock': 1  # Default stock
                    }
                    # Create or update book
                    book, created = Book.objects.update_or_create(
                        isbn=book_data['isbn'],
                        defaults=book_data
                    )
                    if created:
                        imported += 1
                page += 1
            messages.success(request, f'Successfully imported {imported} books.')
            return redirect('book_list')
    else:
        form = ImportBooksForm()
    return render(request, 'import_books.html', {'form': form})
