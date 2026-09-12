from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from .models import Book, Member, BorrowRecord, Reservation, Fine
from .forms import BookForm, MemberRegistrationForm, BorrowForm
from .services import CirculationService, FineService, ReservationService
from django.contrib.auth.models import User
from .decorators import role_required  # Import custom role decorator


# --- Book Browsing Views (Accessible to ALL logged-in users: Members, Assistants, Librarians, Admins) ---

@login_required
def book_list(views_request):
    query = views_request.GET.get('q', '')
    if query:
        books = Book.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))
    else:
        books = Book.objects.all()
    return render(views_request, 'books/book_list.html', {'books': books, 'query': query})


@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    pending_reservations = book.reservations.filter(status='PENDING')
    return render(request, 'books/book_detail.html', {'book': book, 'reservations': pending_reservations})


# --- Book Inventory Management Views (Librarians & Admins) ---

@login_required
@role_required(['ADMIN', 'LIBRARIAN'])
def book_add(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form, 'action': 'Add'})


@login_required
@role_required(['ADMIN', 'LIBRARIAN'])
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form, 'action': 'Edit', 'book': book})


@login_required
@role_required(['ADMIN', 'LIBRARIAN'])
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'books/book_confirm_delete.html', {'book': book})


# --- Member Management Views (Assistants, Librarians, Admins) ---

@login_required
@role_required(['ADMIN', 'LIBRARIAN', 'ASSISTANT'])
def member_list(request):
    members = Member.objects.select_related('user').all()
    return render(request, 'books/member_list.html', {'members': members})


@login_required
@role_required(['ADMIN', 'LIBRARIAN', 'ASSISTANT'])
def member_register(request):
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                password='defaultpassword123'
            )
            Member.objects.create(user=user, phone=form.cleaned_data['phone'])
            messages.success(request, "Member registered successfully!")
            return redirect('member_list')
    else:
        form = MemberRegistrationForm()
    return render(request, 'books/member_form.html', {'form': form})


@login_required
@role_required(['ADMIN', 'LIBRARIAN'])
def toggle_member_status(request, pk):
    member = get_object_or_404(Member, pk=pk)
    member.is_active_member = not member.is_active_member
    member.save()
    messages.info(request, f"Member status updated to {'Active' if member.is_active_member else 'Inactive'}.")
    return redirect('member_list')


# --- Circulation, Loans & Reservations (Assistants, Librarians, Admins) ---

@login_required
@role_required(['ADMIN', 'LIBRARIAN', 'ASSISTANT'])
def borrow_book_view(request):
    if request.method == 'POST':
        form = BorrowForm(request.POST)
        if form.is_valid():
            selected_member = form.cleaned_data['member']

            # Check for outstanding unpaid fines before issuing book
            unpaid_fines = Fine.objects.filter(member=selected_member, status='UNPAID').exists()
            if unpaid_fines:
                messages.error(request,
                               f"Cannot issue book: {selected_member.user.username} has outstanding unpaid fines!")
                return redirect('active_loans')

            try:
                CirculationService.borrow_book(
                    member=selected_member,
                    book=form.cleaned_data['book']
                )
                messages.success(request, "Book borrowed successfully!")
                return redirect('active_loans')
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = BorrowForm()
    return render(request, 'books/borrow_form.html', {'form': form})
@login_required
@role_required(['ADMIN', 'LIBRARIAN', 'ASSISTANT'])
def return_book_view(request, pk):
    record = get_object_or_404(BorrowRecord, pk=pk)
    try:
        CirculationService.return_book(record)

        has_waiting_reservation = Reservation.objects.filter(
            book=record.book,
            status='AVAILABLE'
        ).exists()

        if has_waiting_reservation:
            messages.info(request,
                          f"Book '{record.book.title}' returned! A reserved member has been notified for pickup.")
        else:
            messages.success(request, f"Book '{record.book.title}' returned successfully!")

    except Exception as e:
        messages.error(request, str(e))

    return redirect('active_loans')


@login_required
@role_required(['ADMIN', 'LIBRARIAN', 'ASSISTANT'])
def reserve_book_view(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        book_id = request.POST.get('book_id')

        try:
            ReservationService.create_reservation(member_id, book_id)
            messages.success(request, "Reservation placed successfully!")
            return redirect('reservation_list')
        except ValueError as e:
            messages.error(request, str(e))

    members = Member.objects.all()
    unavailable_books = [book for book in Book.objects.all() if book.available_quantity == 0]
    return render(request, 'books/reservations/reserve_form.html', {
        'members': members,
        'books': unavailable_books
    })


@login_required
@role_required(['ADMIN', 'LIBRARIAN', 'ASSISTANT'])
def reservation_list_view(request):
    reservations = Reservation.objects.select_related('member__user', 'book').all()
    return render(request, 'books/reservations/reservation_list.html', {'reservations': reservations})


# --- Reports & Dashboards (Assistants, Librarians, Admins) ---

@login_required
@role_required(['ADMIN', 'LIBRARIAN', 'ASSISTANT'])
def active_loans_view(request):
    loans = BorrowRecord.objects.select_related('member__user', 'book').filter(status='BORROWED')
    return render(request, 'books/reports/active_loans.html', {'loans': loans})


@login_required
@role_required(['ADMIN', 'LIBRARIAN', 'ASSISTANT'])
def overdue_books_view(request):
    today = timezone.now().date()
    overdue_loans = BorrowRecord.objects.select_related('member__user', 'book').filter(
        status='BORROWED', due_date__lt=today
    )
    return render(request, 'books/reports/overdue_books.html', {'loans': overdue_loans})


@login_required
@role_required(['ADMIN', 'LIBRARIAN'])
def reports_dashboard(request):
    most_borrowed = Book.objects.annotate(borrow_count=Count('borrow_records')).order_by('-borrow_count')[:5]
    total_borrows = BorrowRecord.objects.count()
    active_loans_count = BorrowRecord.objects.filter(status='BORROWED').count()
    overdue_count = BorrowRecord.objects.filter(status='BORROWED', due_date__lt=timezone.now().date()).count()

    context = {
        'most_borrowed': most_borrowed,
        'total_borrows': total_borrows,
        'active_loans_count': active_loans_count,
        'overdue_count': overdue_count,
    }
    return render(request, 'books/reports/dashboard.html', context)


# --- Fine Management Views (Librarians & Admins) ---

@login_required
@role_required(['ADMIN', 'LIBRARIAN'])
def fine_list_view(request):
    today = timezone.now().date()
    overdue_records = BorrowRecord.objects.filter(status='BORROWED', due_date__lt=today)
    for record in overdue_records:
        FineService.update_or_create_fine(record)

    fines = Fine.objects.select_related('borrow_record__member__user', 'borrow_record__book').all()
    return render(request, 'books/fines/fine_list.html', {'fines': fines})


@login_required
@role_required(['ADMIN', 'LIBRARIAN'])
def pay_fine_view(request, pk):
    try:
        FineService.pay_fine(pk)
        messages.success(request, "Fine marked as paid successfully!")
    except Exception as e:
        messages.error(request, str(e))
    return redirect('fine_list')






@role_required(['ADMIN', 'LIBRARIAN', 'ASSISTANT'])
def mark_book_lost(request, record_id):
    loan = get_object_or_404(BorrowRecord, id=record_id)

    if request.method == 'POST':
        replacement_cost = request.POST.get('replacement_cost', 50.00)  # Default fine if not entered

        # 1. Update loan status
        loan.status = 'LOST'
        loan.return_date = timezone.now().date()
        loan.save()

        # 2. Decrement TOTAL inventory stock (book is permanently lost)
        book = loan.book
        if book.quantity > 0:
            book.quantity -= 1
            book.save()

        # 3. Create unpaid fine for the member
        Fine.objects.create(
            member=loan.member,
            borrow_record=loan,
            amount=replacement_cost,
            reason=f"Lost Book: {book.title}",
            status='UNPAID'
        )

        messages.error(request,
                       f"Book '{book.title}' marked as LOST. Fine of ${replacement_cost} issued to {loan.member.user.username}.")
        return redirect('active_loans')

    return render(request, 'books/mark_lost_confirm.html', {'loan': loan})


@role_required(['ADMIN', 'LIBRARIAN'])
def pay_fine(request, fine_id):
    fine = get_object_or_404(Fine, id=fine_id)
    fine.status = 'PAID'
    fine.save()
    messages.success(request, f"Fine for {fine.member.user.username} marked as PAID.")
    return redirect('fines_list')