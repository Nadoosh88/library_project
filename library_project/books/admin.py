from django.contrib import admin
from .models import Book, Member, BorrowRecord, Reservation, Fine

# Register your models here
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'quantity')

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')

@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ('member', 'book', 'borrow_date', 'due_date', 'status')
    list_filter = ('status', 'due_date')
    search_fields = ('member__user__username', 'book__title')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('member', 'book', 'reservation_date', 'status')

@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ('borrow_record', 'amount', 'status')
    list_filter = ('status',)
