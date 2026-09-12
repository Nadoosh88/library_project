from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Reservation, Book, Member, BorrowRecord, Fine
from decimal import Decimal
from .notifications import NotificationService  # From Phase 3 Notifications setup


MAX_BORROW_LIMIT = 5
DEFAULT_BORROW_DAYS = 14

class CirculationService:

    @staticmethod
    @transaction.atomic
    def borrow_book(member: Member, book: Book) -> BorrowRecord:
        # Rule 1: Member must be active
        if not member.is_active_member:
            raise ValidationError("Member account is inactive.")

        # Check if this specific member holds a reservation that is ready for pickup
        has_available_reservation = Reservation.objects.filter(
            member=member, book=book, status='AVAILABLE'
        ).exists()

        # Rule 2: Cannot borrow unavailable books (unless reserved for this member)
        if not book.is_available and not has_available_reservation:
            raise ValidationError("Book is currently unavailable.")

        # Rule 3: Prevent duplicate active borrow
        active_borrow = BorrowRecord.objects.filter(
            member=member, book=book, status='BORROWED'
        ).exists()
        if active_borrow:
            raise ValidationError("You already have an active loan for this book.")

        # Rule 4: Maximum 5 books per member
        current_active_count = BorrowRecord.objects.filter(
            member=member, status='BORROWED'
        ).count()
        if current_active_count >= MAX_BORROW_LIMIT:
            raise ValidationError(f"Member has reached the maximum limit of {MAX_BORROW_LIMIT} active borrows.")

        # Create record
        due_date = timezone.now().date() + timedelta(days=DEFAULT_BORROW_DAYS)
        borrow_record = BorrowRecord.objects.create(
            member=member,
            book=book,
            due_date=due_date,
            status='BORROWED'
        )

        # Mark any pending or available reservation for this member as FULFILLED

        Reservation.objects.filter(
            member=member,
            book=book,
            status__in=['PENDING', 'AVAILABLE']
        ).update(status='FULFILLED')

        return borrow_record

    @staticmethod
    @transaction.atomic
    def return_book(record: BorrowRecord):
        # 1. Update borrow record status and return date
        record.status = 'RETURNED'
        record.return_date = timezone.now().date()
        record.save()

        # 2. Check if another member is waiting in line for this book
        pending_reservation = Reservation.objects.filter(
            book=record.book,
            status='PENDING'
        ).first()

        # 3. If someone reserved it, mark their reservation ready and notify them
        if pending_reservation:
            pending_reservation.status = 'AVAILABLE'
            pending_reservation.save()

            # Send email/terminal alert to the reserving member
        NotificationService.notify_reservation_available(pending_reservation)

        return record

    @staticmethod
    def reserve_book(member: Member, book: Book) -> Reservation:
        if book.is_available:
            raise ValidationError("Book is currently available for direct borrowing; reservation not needed.")

        if Reservation.objects.filter(member=member, book=book, status='PENDING').exists():
            raise ValidationError("You already have a pending reservation for this book.")

        return Reservation.objects.create(member=member, book=book, status='PENDING')





class FineService:
        @staticmethod
        def update_or_create_fine(borrow_record: BorrowRecord, DAILY_FINE_RATE= Decimal('1.00')) -> Fine:
            """Calculates and updates fine amount based on overdue days."""
            today = timezone.now().date()

            # If not overdue, return None or clear fine
            if borrow_record.due_date >= today:
                return None

            # Calculate days past due date
            days_overdue = (today - borrow_record.due_date).days
            total_fine = Decimal(days_overdue) * DAILY_FINE_RATE

            # Get or create fine instance
            fine, _ = Fine.objects.get_or_create(borrow_record=borrow_record)

            # Only update amount if it hasn't been paid off yet
            if fine.status == 'UNPAID':
                fine.amount = total_fine
                fine.save()

            return fine


        @staticmethod
        def pay_fine(Fine_id: int) -> Fine:
            fine = Fine.objects.get(id=Fine_id)
            fine.status = 'PAID'
            fine.save()
            return fine




class ReservationService:
    @staticmethod
    def create_reservation(member_id: int, book_id: int):
        member = Member.objects.get(pk=member_id)
        book = Book.objects.get(pk=book_id)

        # Rule 1: Cannot reserve a book if copies are currently available to borrow
        if book.available_quantity > 0:
            raise ValueError("This book currently has available copies for direct checkout.")

        # Rule 2: Cannot create duplicate active pending reservations for the same book
        existing = Reservation.objects.filter(member=member, book=book, status='PENDING').exists()
        if existing:
            raise ValueError("You already have an active pending reservation for this book.")

        return Reservation.objects.create(member=member, book=book, status='PENDING')

    @staticmethod
    def process_returned_book_reservations(book: Book):
        """Checks if anyone is waiting for this book when it gets returned."""
        next_reservation = Reservation.objects.filter(book=book, status='PENDING').first()
        if next_reservation:
            next_reservation.status = 'AVAILABLE'
            next_reservation.save()

            # Send notification email (Console Backend)
            NotificationService.notify_reservation_available(next_reservation)
            return next_reservation
        return None


