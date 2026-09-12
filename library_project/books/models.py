import datetime
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


def current_year():
    return datetime.date.today().year


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    publication_year = models.IntegerField(
        validators=[MinValueValidator(1000), MaxValueValidator(current_year)]
    )

    def __str__(self):
        return f"{self.title} by {self.author}"

    @property
    def available_quantity(self):
        # Exclude RETURNED and LOST records when counting active borrows
        active_borrows = self.borrow_records.filter(status__in=['BORROWED', 'OVERDUE']).count()
        return max(0, self.quantity - active_borrows)

    @property
    def is_available(self):
        return self.available_quantity > 0


class Member(models.Model):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrator'),
        ('LIBRARIAN', 'Librarian'),
        ('ASSISTANT', 'Assistant'),
        ('MEMBER', 'Member'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member_profile')
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='MEMBER')
    phone = models.CharField(max_length=20)
    is_active_member = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'ADMIN' or self.user.is_superuser

    @property
    def is_librarian(self):
        return self.role in ['ADMIN', 'LIBRARIAN'] or self.user.is_superuser

    @property
    def is_assistant(self):
        return self.role in ['ADMIN', 'LIBRARIAN', 'ASSISTANT'] or self.user.is_superuser


class BorrowRecord(models.Model):
    STATUS_CHOICES = (
        ('BORROWED', 'Borrowed'),
        ('RETURNED', 'Returned'),
        ('OVERDUE', 'Overdue'),
        ('LOST', 'Lost'),
    )

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='borrow_records')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    borrow_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='BORROWED')

    def __str__(self):
        return f"{self.member} - {self.book.title} ({self.status})"

    @property
    def is_overdue(self):
        if self.status in ['BORROWED', 'OVERDUE'] and timezone.now().date() > self.due_date:
            return True
        return False


class Reservation(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('AVAILABLE', 'Available for Pickup'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='reservations')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    reservation_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')

    class Meta:
        ordering = ['reservation_date']  # First-come, first-served queue

    def __str__(self):
        return f"Reservation: {self.member} for '{self.book.title}' ({self.status})"


class Fine(models.Model):
    STATUS_CHOICES = (
        ('UNPAID', 'Unpaid'),
        ('PAID', 'Paid'),
    )

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='fines')
    borrow_record = models.ForeignKey(
        BorrowRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fines'
    )
    amount = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    reason = models.CharField(max_length=255, default="Overdue Fine")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='UNPAID')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Fine: ${self.amount} - {self.member.user.username} ({self.status})"