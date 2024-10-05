from django import forms
from .models import Book, Member, Transaction
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'authors', 'isbn', 'publisher', 'num_pages', 'stock']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'authors': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'publisher': forms.TextInput(attrs={'class': 'form-control'}),
            'num_pages': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'email', 'outstanding_debt']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'outstanding_debt': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['member', 'book', 'transaction_type', 'due_date']
        widgets = {
            'member': forms.Select(attrs={'class': 'form-control'}),
            'book': forms.Select(attrs={'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class ImportBooksForm(forms.Form):
    num_books = forms.IntegerField(
        label="Number of Books to Import",
        min_value=1,
        max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    title = forms.CharField(
        label="Title",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    authors = forms.CharField(
        label="Authors",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    isbn = forms.CharField(
        label="ISBN",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    publisher = forms.CharField(
        label="Publisher",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text='Required. Enter a valid email address.'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        # Add Bootstrap classes to each field
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].widget.attrs['required'] = 'required'