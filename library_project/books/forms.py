from django import forms
from django.contrib.auth.models import User
from .models import Book, Member, BorrowRecord

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'quantity', 'publication_year']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'publication_year': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class MemberRegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Member
        fields = ['phone']

class BorrowForm(forms.Form):
    member = forms.ModelChoiceField(
        queryset=Member.objects.filter(is_active_member=True),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    book = forms.ModelChoiceField(
        queryset=Book.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )