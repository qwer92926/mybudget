from django import forms
from .models import Expense
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ExpenseForm(forms.ModelForm):
    title = forms.CharField(label='標題', max_length=100)
    amount = forms.DecimalField(label='金額', max_digits=10, decimal_places=2)
    date = forms.DateField(label='日期', widget=forms.SelectDateWidget)
    description = forms.CharField(label='描述', widget=forms.Textarea, required=False)
    category = forms.ChoiceField(label='類別', choices=[
        ('food', '食品'),
        ('transport', '交通'),
        ('entertainment', '娛樂'),
        ('other', '其他'),
    ])
    type = forms.ChoiceField(label='類型', choices=[
        ('income', '收入'),
        ('expense', '支出'),
    ])

    class Meta:
        model = Expense
        fields = ['title', 'amount', 'date', 'description', 'category', 'type', 'bank']

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(label='用戶名', max_length=150)
    email = forms.EmailField(label='電子郵件')
    password1 = forms.CharField(label='密碼', widget=forms.PasswordInput)
    password2 = forms.CharField(label='確認密碼', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
