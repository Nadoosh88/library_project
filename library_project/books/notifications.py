from django.core.mail import send_mail

class NotificationService:
    @staticmethod
    def notify_reservation_available(reservation):
        """Sends an email alert when a reserved book is returned and available."""
        send_mail(
            subject="Good News: Reserved Book Available",
            message=f"Hello {reservation.member.user.username},\n\n"
                    f"The book '{reservation.book.title}' is now available for pickup.",
            from_email='library@example.com',
            recipient_list=[reservation.member.user.email],
            fail_silently=False,
        )

    @staticmethod
    def notify_due_tomorrow(borrow_record):
        """Sends a reminder for books due tomorrow."""
        send_mail(
            subject="Reminder: Book Due Tomorrow",
            message=f"Hello {borrow_record.member.user.username},\n\n"
                    f"Your book '{borrow_record.book.title}' is due tomorrow.",
            from_email='library@example.com',
            recipient_list=[borrow_record.member.user.email],
            fail_silently=False,
        )

    @staticmethod
    def notify_overdue(borrow_record):
        """Sends an alert for overdue books."""
        send_mail(
            subject="Notice: Book Overdue",
            message=f"Hello {borrow_record.member.user.username},\n\n"
                    f"Your loan for '{borrow_record.book.title}' is overdue. "
                    f"A daily fine will be applied until returned.",
            from_email='library@example.com',
            recipient_list=[borrow_record.member.user.email],
            fail_silently=False,
        )