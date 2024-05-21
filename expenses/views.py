import pandas as pd
import plotly.express as px
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Expense
from .forms import ExpenseForm, UserRegisterForm
from django.db.models import Sum
from datetime import datetime

@login_required
def expense_list(request):
    query = request.GET.get('query', '')
    category = request.GET.get('category', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    expenses = Expense.objects.filter(user=request.user)
    
    if query:
        expenses = expenses.filter(title__icontains=query)
    if category:
        expenses = expenses.filter(category=category)
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)
    
    income = expenses.filter(type='income').aggregate(total_income=Sum('amount'))['total_income'] or 0
    expense = expenses.filter(type='expense').aggregate(total_expense=Sum('amount'))['total_expense'] or 0
    remaining_balance = income - expense

    bank_balances = expenses.filter(type='income').values('bank').annotate(total_amount=Sum('amount'))

    return render(request, 'expenses/expense_list.html', {
        'expenses': expenses,
        'query': query,
        'category': category,
        'start_date': start_date,
        'end_date': end_date,
        'remaining_balance': remaining_balance,
        'bank_balances': bank_balances
    })

@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, '記帳條目已成功創建！')
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'expenses/expense_form.html', {'form': form})

@login_required
def expense_edit(request, pk):
    expense = Expense.objects.get(pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, '記帳條目已成功更新！')
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/expense_form.html', {'form': form})

@login_required
def expense_delete(request, pk):
    expense = Expense.objects.get(pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, '記帳條目已成功刪除！')
        return redirect('expense_list')
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'帳號 {username} 已成功創建！')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'expenses/register.html', {'form': form})

@login_required
def expense_chart(request):
    current_month = request.GET.get('month', datetime.now().month)
    current_year = request.GET.get('year', datetime.now().year)
    current_month = int(current_month)
    current_year = int(current_year)
    
    expenses = Expense.objects.filter(user=request.user, date__year=current_year, date__month=current_month)
    df = pd.DataFrame(list(expenses.values('category', 'amount', 'type')))
    
    if not df.empty:
        category_map = {
            'food': '食品',
            'transport': '交通',
            'entertainment': '娛樂',
            'other': '其他'
        }
        df['category'] = df['category'].map(category_map)

        type_map = {
            'income': '收入',
            'expense': '支出'
        }
        df['type'] = df['type'].map(type_map)
        
        pie_chart = px.pie(df, values='amount', names='category', title='支出類別分布', labels={'category': '類別', 'amount': '金額'})
        bar_chart = px.bar(df, x='category', y='amount', color='type', barmode='group', title='收入和支出', labels={'category': '類別', 'amount': '金額', 'type': '類型'})
        
        pie_chart.update_traces(textinfo='label+percent')
        bar_chart.update_traces(texttemplate='%{y:.2f}', textposition='outside')
        pie_chart.update_layout(legend_title_text='類別')
        bar_chart.update_layout(legend_title_text='類型')
        
        pie_chart_html = pie_chart.to_html(full_html=False)
        bar_chart_html = bar_chart.to_html(full_html=False)
    else:
        pie_chart_html = "<p>沒有數據可顯示圖表。</p>"
        bar_chart_html = "<p>沒有數據可顯示圖表。</p>"
    
    years = range(2022, 2027)
    months = range(1, 13)
    
    return render(request, 'expenses/expense_chart.html', {
        'pie_chart': pie_chart_html,
        'bar_chart': bar_chart_html,
        'current_month': current_month,
        'current_year': current_year,
        'years': years,
        'months': months
    })
@login_required
def expense_report(request):
    expenses = Expense.objects.filter(user=request.user)
    df = pd.DataFrame(list(expenses.values('date', 'amount', 'type')))
    if not df.empty:
        df = df.rename(columns={
            'date': '日期',
            'amount': '金額',
            'type': '類型'
        })
        report = df.groupby(['日期', '類型']).sum().unstack().fillna(0)
        report_html = report.to_html(classes='table table-striped')
    else:
        report_html = "<p>沒有數據可顯示報告。</p>"
    return render(request, 'expenses/expense_report.html', {'report': report_html})

@login_required
def monthly_summary(request):
    current_month = request.GET.get('month', datetime.now().month)
    current_year = request.GET.get('year', datetime.now().year)
    current_month = int(current_month)
    current_year = int(current_year)
    income = Expense.objects.filter(user=request.user, type='income', date__year=current_year, date__month=current_month).aggregate(total_income=Sum('amount'))['total_income'] or 0
    expense = Expense.objects.filter(user=request.user, type='expense', date__year=current_year, date__month=current_month).aggregate(total_expense=Sum('amount'))['total_expense'] or 0
    total = income - expense
    years = range(2022, 2027)
    months = range(1, 13)
    return render(request, 'expenses/monthly_summary.html', {'income': income, 'expense': expense, 'total': total, 'current_month': current_month, 'current_year': current_year, 'years': years, 'months': months})

def home(request):
    return render(request, 'expenses/home.html')
