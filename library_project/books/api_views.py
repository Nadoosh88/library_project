from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book, Member, BorrowRecord, Reservation
from .serializers import BookSerializer, MemberSerializer, BorrowRecordSerializer, ReservationSerializer
from .api_permissions import IsLibrarianOrAdmin


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsLibrarianOrAdmin]

    # Filtering, Searching, and Ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['author']
    search_fields = ['title', 'author']
    ordering_fields = ['title', 'id']


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.select_related('user').all()
    serializer_class = MemberSerializer
    permission_classes = [IsLibrarianOrAdmin]
    filterset_fields = ['role', 'is_active_member']
    search_fields = ['user__username', 'user__email', 'phone']


class BorrowRecordViewSet(viewsets.ModelViewSet):
    queryset = BorrowRecord.objects.select_related('member__user', 'book').all()
    serializer_class = BorrowRecordSerializer
    permission_classes = [IsLibrarianOrAdmin]
    filterset_fields = ['status', 'member', 'book']
    search_fields = ['book__title', 'member__user__username']


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related('member__user', 'book').all()
    serializer_class = ReservationSerializer
    permission_classes = [IsLibrarianOrAdmin]
    filterset_fields = ['status', 'member', 'book']