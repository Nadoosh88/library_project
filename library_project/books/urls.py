
from django.urls import path , include
from . import views
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as token_views
from .api_views import BookViewSet, MemberViewSet, BorrowRecordViewSet, ReservationViewSet


router = DefaultRouter()
router.register(r'books', BookViewSet, basename='api-books')
router.register(r'members', MemberViewSet, basename='api-members')
router.register(r'loans', BorrowRecordViewSet, basename='api-loans')
router.register(r'reservations', ReservationViewSet, basename='api-reservations')

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='books/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Books
    path('', views.book_list, name='book_list'),
    path('add/', views.book_add, name='book_add'),
    path('<int:pk>/', views.book_detail, name='book_detail'),
    path('<int:pk>/edit/', views.book_edit, name='book_edit'),
    path('<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('<int:book_id>/reserve/', views.reserve_book_view, name='reserve_book'),

    # Members
    path('members/', views.member_list, name='member_list'),
    path('members/register/', views.member_register, name='member_register'),
    path('members/<int:pk>/toggle/', views.toggle_member_status, name='toggle_member_status'),

    # Circulation
    path('borrow/', views.borrow_book_view, name='borrow_book'),
    path('return/<int:pk>/', views.return_book_view, name='return_book'),

    # Reports
    path('reports/active-loans/', views.active_loans_view, name='active_loans'),
    path('reports/overdue/', views.overdue_books_view, name='overdue_books'),
    path('reports/dashboard/', views.reports_dashboard, name='reports_dashboard'),


    # ... existing routes ...
    path('fines/', views.fine_list_view, name='fine_list'),
    path('fines/<int:pk>/pay/', views.pay_fine_view, name='pay_fine'),

    path('borrow/<int:pk>/return/', views.return_book_view, name='return_book'),

    path('reservations/', views.reservation_list_view, name='reservation_list'),
    path('reservations/add/', views.reserve_book_view, name='reserve_book'),

    # API endpoints
    path('api/', include(router.urls)),

    # Endpoint to obtain Auth Token: POST username & password to receive token
    path('api/token-auth/', token_views.obtain_auth_token, name='api_token_auth'),

    path('loans/<int:record_id>/lost/', views.mark_book_lost, name='mark_book_lost'),
    path('fines/<int:fine_id>/pay/', views.pay_fine, name='pay_fine'),


]