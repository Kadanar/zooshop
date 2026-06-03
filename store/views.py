from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count
import requests
import logging

from .models import Category, Product, Supplier, Sale, SaleItem, Client, Employee
from .forms import ProductForm, SupplierForm, ClientForm, SaleForm

logger = logging.getLogger(__name__)


def get_dog_image():
    try:
        response = requests.get('https://dog.ceo/api/breeds/image/random', timeout=5)
        data = response.json()
        return data.get('message', '')
    except Exception as e:
        logger.error(f'Dogs API error: {e}')
        return ''


def get_weather(city='Minsk'):
    try:
        api_key = 'bd5e378503939ddaee76f12ad7a97608'
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&lang=ru&appid={api_key}'
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get('cod') == 200:
            return {
                'city': data['name'],
                'temp': round(data['main']['temp']),
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
            }
    except Exception as e:
        logger.error(f'Weather API error: {e}')
    return None


def home(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_suppliers': Supplier.objects.count(),
        'total_sales': Sale.objects.count(),
        'dog_image': get_dog_image(),
        'weather': get_weather(),
    }
    return render(request, 'store/home.html', context)


def product_list(request):
    products = Product.objects.select_related('category').all()
    categories = Category.objects.all()

    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(article__icontains=query) |
            Q(description__icontains=query)
        )

    sort = request.GET.get('sort', 'name')
    if sort in ['name', '-name', 'price', '-price']:
        products = products.order_by(sort)

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'query': query,
        'sort': sort,
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'store/category_list.html', {'categories': categories})


@login_required
def cabinet(request):
    try:
        client = request.user.client
        sales = Sale.objects.filter(client=client).order_by('-date')
        context = {'client': client, 'sales': sales}
    except Client.DoesNotExist:
        context = {}
    return render(request, 'store/cabinet.html', context)


@login_required
def statistics(request):
    if not request.user.is_staff:
        messages.error(request, 'Доступ запрещён.')
        return redirect('home')

    sales = Sale.objects.all()
    sale_totals = [s.total() for s in sales]

    category_stats = Product.objects.values('category__name').annotate(count=Count('id')).order_by('-count')

    context = {
        'total_sales': len(sale_totals),
        'total_revenue': sum(sale_totals),
        'avg_sale': round(sum(sale_totals) / len(sale_totals), 2) if sale_totals else 0,
        'products': Product.objects.select_related('category').order_by('name'),
        'category_stats': category_stats,
    }
    return render(request, 'store/statistics.html', context)


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        if password1 != password2:
            messages.error(request, 'Пароли не совпадают.')
            return render(request, 'store/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует.')
            return render(request, 'store/register.html')

        user = User.objects.create_user(
            username=username,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        login(request, user)
        messages.success(request, 'Регистрация прошла успешно!')
        return redirect('home')

    return render(request, 'store/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Неверный логин или пароль.')
    return render(request, 'store/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Вы вышли из системы.')
    return redirect('home')


# ===== CRUD для товаров =====

@login_required
def product_create(request):
    if not request.user.is_staff:
        messages.error(request, 'Доступ запрещён.')
        return redirect('product_list')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар успешно добавлен!')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'store/product_form.html', {'form': form, 'title': 'Добавить товар'})


@login_required
def product_update(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Доступ запрещён.')
        return redirect('product_list')
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар успешно обновлён!')
            return redirect('product_detail', pk=pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/product_form.html', {'form': form, 'title': 'Редактировать товар'})


@login_required
def product_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Доступ запрещён.')
        return redirect('product_list')
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Товар успешно удалён!')
        return redirect('product_list')
    return render(request, 'store/product_confirm_delete.html', {'product': product})


# ===== CRUD для поставщиков =====

@login_required
def supplier_list(request):
    if not request.user.is_staff:
        messages.error(request, 'Доступ запрещён.')
        return redirect('home')
    suppliers = Supplier.objects.all()
    return render(request, 'store/supplier_list.html', {'suppliers': suppliers})


@login_required
def supplier_create(request):
    if not request.user.is_staff:
        messages.error(request, 'Доступ запрещён.')
        return redirect('home')
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Поставщик успешно добавлен!')
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'store/supplier_form.html', {'form': form, 'title': 'Добавить поставщика'})


@login_required
def supplier_update(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Доступ запрещён.')
        return redirect('home')
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Поставщик успешно обновлён!')
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'store/supplier_form.html', {'form': form, 'title': 'Редактировать поставщика'})


@login_required
def supplier_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Доступ запрещён.')
        return redirect('home')
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Поставщик успешно удалён!')
        return redirect('supplier_list')
    return render(request, 'store/supplier_confirm_delete.html', {'supplier': supplier})