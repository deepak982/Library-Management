from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Book(models.Model):
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    publisher = models.CharField(max_length=255)
    num_pages = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    stock = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.title} by {self.authors}"

class Member(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    outstanding_debt = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    ISSUE = 'issue'
    RETURN = 'return'
    TRANSACTION_TYPE_CHOICES = [
        (ISSUE, 'Issue'),
        (RETURN, 'Return'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPE_CHOICES)
    date = models.DateTimeField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    fee_charged = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.book.title} by {self.member.name}"
