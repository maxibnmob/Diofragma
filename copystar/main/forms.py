from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Order
from django import forms
User = get_user_model()
class UserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'address', 'phone']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'address': 'Адрес',
            'phone': 'Телефон',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Введите ваше имя'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Введите вашу фамилию'}),
            'address': forms.TextInput(attrs={'placeholder': 'Введите ваш адрес'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Введите ваш телефон'}),
        }
