from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Book, Member, BorrowRecord, Reservation , Fine


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Member
        fields = ['id', 'user', 'role', 'phone', 'is_active_member']


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author','publication_year',  'quantity', 'available_quantity']


class BorrowRecordSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    member_name = serializers.CharField(source='member.user.username', read_only=True)

    class Meta:
        model = BorrowRecord
        fields = ['id', 'member', 'member_name', 'book', 'book_title', 'borrow_date', 'due_date', 'return_date', 'status']


class ReservationSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    member_name = serializers.CharField(source='member.user.username', read_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'member', 'member_name', 'book', 'book_title', 'reservation_date', 'status']

class FineSerializer(serializers.ModelSerializer):
    member_username = serializers.CharField(source='member.user.username', read_only=True)

    class Meta:
        model = Fine
        fields = ['id', 'member', 'member_username', 'borrow_record', 'amount', 'reason', 'status', 'created_at']