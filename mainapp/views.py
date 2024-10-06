import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from .models import Book, Member, Transaction
from .forms import BookForm, MemberForm, TransactionForm, ImportBooksForm, SignUpForm
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count

# Signup View
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect authenticated users to home
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Optionally, log the user in immediately after signup
            login(request, user)
            messages.success(request, 'Your account has been created successfully!')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

# Home Page

@login_required
def home(request):
    # Get counts for number cards
    total_books = Book.objects.count()
    total_members = Member.objects.count()
    total_transactions = Transaction.objects.count()
    
    # Get data for transactions graph (default: last 30 days, all types)
    last_30_days = timezone.now() - datetime.timedelta(days=30)
    transactions_by_day = (
        Transaction.objects.filter(date__gte=last_30_days)
        .values('date__date')  # Group by date only
        .annotate(count=Count('id'))
        .order_by('date__date')
    )
    
    # Get data for report section (latest 10 transactions)
    recent_transactions = Transaction.objects.all().order_by('-date')[:10]
    
    context = {
        'total_books': total_books,
        'total_members': total_members,
        'total_transactions': total_transactions,
        'transactions_by_day': list(transactions_by_day),
        'recent_transactions': recent_transactions,
    }
    return render(request, 'home.html', context)

# Book Views
@login_required
def book_list(request):
    query = request.GET.get('q')
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) | Q(authors__icontains=query)
        )
    else:
        books = Book.objects.all()
    return render(request, 'books/book_list.html', {'books': books, 'query': query})

@login_required
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

@login_required
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

@login_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully.')
        return redirect('book_list')
    return render(request, 'books/book_confirm_delete.html', {'book': book})

# Member Views
@login_required
def member_list(request):
    members = Member.objects.all()
    return render(request, 'members/member_list.html', {'members': members})

@login_required
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

@login_required
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

@login_required
def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        member.delete()
        messages.success(request, 'Member deleted successfully.')
        return redirect('member_list')
    return render(request, 'members/member_confirm_delete.html', {'member': member})

# Transaction Views
@login_required
def transaction_list(request):
    transactions = Transaction.objects.select_related('member', 'book').all().order_by('-date')
    return render(request, 'transactions/transaction_list.html', {'transactions': transactions})

@login_required
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
@login_required
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

# AJAX Endpoint for Real-Time Dashboard Updates
@login_required
def dashboard_data(request):
    # Common data
    total_books = Book.objects.count()
    total_members = Member.objects.count()
    total_transactions = Transaction.objects.count()
    
    # Identify which section is requesting data
    is_graph = request.GET.get('graph', 'false').lower() == 'true'
    is_report = request.GET.get('report', 'false').lower() == 'true'
    
    data = {
        'total_books': total_books,
        'total_members': total_members,
        'total_transactions': total_transactions,
    }
    
    if is_graph:
        # Get graph-specific filters
        transaction_type = request.GET.get('transaction_type', 'all')
        # Build filter conditions
        graph_filters = {}
        if transaction_type and transaction_type.lower() != 'all':
            graph_filters['transaction_type__iexact'] = transaction_type.lower()
        
        # Get data for transactions graph
        last_30_days = timezone.now() - datetime.timedelta(days=30)
        transactions_by_day = (
            Transaction.objects.filter(date__gte=last_30_days, **graph_filters)
            .values('date__date')
            .annotate(count=Count('id'))
            .order_by('date__date')
        )
        
        data['transactions_by_day'] = [
            {'day': item['date__date'].strftime('%Y-%m-%d'), 'count': item['count']}
            for item in transactions_by_day
        ]
    
    if is_report:
        # Get report-specific filters
        transaction_type = request.GET.get('transaction_type', 'all')
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        
        # Build filter conditions
        report_filters = {}
        if transaction_type and transaction_type.lower() != 'all':
            report_filters['transaction_type__iexact'] = transaction_type.lower()
        if start_date:
            report_filters['date__date__gte'] = start_date
        if end_date:
            report_filters['date__date__lte'] = end_date
        
        # Get data for report section (latest 10 transactions based on filters)
        recent_transactions = Transaction.objects.filter(**report_filters).order_by('-date')[:10]
        
        data['recent_transactions'] = [
            {
                'date': t.date.strftime('%Y-%m-%d %H:%M'),
                'type': t.get_transaction_type_display(),
                'book': t.book.title,
                'member': t.member.name
            }
            for t in recent_transactions
        ]
    
    return JsonResponse(data)