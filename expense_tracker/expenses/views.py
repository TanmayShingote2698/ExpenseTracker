from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum
from django.contrib.auth.models import User
from reportlab.pdfgen import canvas
import json
from reportlab.lib.pagesizes import A4 
from .models import Expense
from .forms import ExpenseForm
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
# ==============================
# 🚀 DASHBOARD VIEW WITH PIE CHART
# ==============================
import json
from django.shortcuts import render
from django.db.models import Sum
from .models import Expense
from decimal import Decimal  # Import Decimal

@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user)

    # Calculate total expense sum
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0  # If no expenses, default to 0

    # Group expenses by category
    category_expenses = expenses.values('category').annotate(total=Sum('amount'))
    categories = [expense['category'] for expense in category_expenses]
    amounts = [float(expense['total']) for expense in category_expenses]  # Convert Decimal to float for JSON

    context = {
        'expenses': expenses,
        'total_expense': total_expense,  # Pass total sum
        'categories': json.dumps(categories),  
        'amounts': json.dumps(amounts),  
    }
    return render(request, 'expenses/dashboard.html', context)


# ==============================
# 📄 GENERATE PDF REPORT
# ==============================
@login_required
def generate_pdf(request):
    from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle  # ✅ Correct import
from .models import Expense
from datetime import datetime

def generate_pdf(request):
    """ Generate PDF report of expenses in a tabular format with total sum """
    
    # Get the current month and year for dynamic file naming
    current_date = datetime.now()
    month_name = current_date.strftime("%B")  # Get the full month name (e.g., March)
    year = current_date.year  # Get the current year (e.g., 2025)

    # Define dynamic PDF filename based on the month and year
    filename = f"month_expense_{month_name}_{year}.pdf"

    # Set up the response to serve the PDF file
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'  # Dynamic filename

    # Create the PDF object
    pdf = canvas.Canvas(response, pagesize=A4)
    pdf.setTitle(f"Expense Report - {month_name} {year}")

    # Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, 800, f"Expense Report - {month_name} {year}")

    # Table Header
    data = [["Title", "Category", "Amount (₹)", "Date"]]
    
    # Fetch all expenses for the current month and year
    expenses = Expense.objects.filter(user=request.user, date__month=current_date.month, date__year=current_date.year)
    
    # Add each expense to the table
    total_expense = 0
    for expense in expenses:
        data.append([expense.title, expense.category, f"₹{expense.amount:.2f}", expense.date.strftime("%d-%m-%Y")])
        total_expense += expense.amount

    # Add Total Row
    data.append(["", "Total", f"₹{total_expense:.2f}", ""])

    # Define Table Styles
    table = Table(data, colWidths=[150, 100, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.red),  # Total row color
    ]))

    # Draw table on PDF
    table.wrapOn(pdf, 400, 500)
    table.drawOn(pdf, 80, 600 - (len(data) * 20))  # Adjust height based on rows

    # Save PDF
    pdf.showPage()
    pdf.save()

    return response


# ==============================
# ➕ ADD EXPENSE
# ==============================
@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm()
    return render(request, 'expenses/add_expense.html', {'form': form})

# ==============================
# ✏️ EDIT EXPENSE
# ==============================
@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/edit_expense.html', {'form': form, 'expense': expense})

# ==============================
# ❌ DELETE EXPENSE
# ==============================
@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == 'POST':
        expense.delete()
        return redirect('dashboard')
    return render(request, 'expenses/delete_expense.html', {'expense': expense})

# ==============================
# 📊 AJAX: FETCH EXPENSE DATA
# ==============================
@login_required
def fetch_expenses(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date').values()
    return JsonResponse(list(expenses), safe=False)

# ==============================
# 🔐 USER AUTHENTICATION
# ==============================
# 📝 Register New User
def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()

        # Validation
        if not username or not password1 or not password2:
            messages.error(request, "All fields are required!")
            return redirect('register')

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect('register')

        # Create user
        user = User.objects.create_user(username=username, password=password1)

        # Authenticate user before logging in
        user = authenticate(username=username, password=password1)
        if user is not None:
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('dashboard')
        else:
            messages.error(request, "Something went wrong. Please login manually.")
            return redirect('login')

    return render(request, 'expenses/register.html')

# 🔑 Login User
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'dashboard'))
        
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'expenses/login.html')

# 🚪 Logout User
@login_required
def user_logout(request):
    logout(request)
    return redirect('login')
