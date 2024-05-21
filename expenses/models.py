from django.db import models
from django.contrib.auth.models import User

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('food', '食品'),
        ('transport', '交通'),
        ('entertainment', '娛樂'),
        ('other', '其他')
    ]

    TYPE_CHOICES = [
        ('income', '收入'),
        ('expense', '支出')
    ]

    BANK_CHOICES = [
        ('bank1', '銀行1'),
        ('bank2', '銀行2'),
        ('cash', '現金')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    bank = models.CharField(max_length=20, choices=BANK_CHOICES, default='cash')

    def __str__(self):
        return self.title
