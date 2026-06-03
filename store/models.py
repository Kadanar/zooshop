from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator
from django.utils import timezone


phone_validator = RegexValidator(
    regex=r'^\+375 \(29\) \d{3}-\d{2}-\d{2}$',
    message='Номер телефона должен быть в формате +375 (29) XXX-XX-XX'
)


class Category(models.Model):
    """Категория товара"""
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name='Изображение')
    image_url = models.URLField(blank=True, null=True, verbose_name='URL изображения')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_image(self):
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return None


class Supplier(models.Model):
    """Поставщик"""
    name = models.CharField(max_length=200, verbose_name='Название')
    address = models.TextField(verbose_name='Адрес')
    phone = models.CharField(max_length=20, validators=[phone_validator], verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='Email')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Товар"""
    article = models.CharField(max_length=50, unique=True, verbose_name='Артикул')
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(0)], verbose_name='Цена')
    stock = models.PositiveIntegerField(default=0, verbose_name='Количество на складе')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True,
                                 related_name='products', verbose_name='Категория')
    suppliers = models.ManyToManyField(Supplier, through='Supply',
                                       related_name='products', verbose_name='Поставщики')
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Изображение')
    image_url = models.URLField(blank=True, null=True, verbose_name='URL изображения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name']

    def __str__(self):
        return f'{self.article} - {self.name}'

    def get_image(self):
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return None


class Supply(models.Model):
    """Поставка (связь товара и поставщика)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name='Поставщик')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена поставки')
    date = models.DateField(verbose_name='Дата поставки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Поставка'
        verbose_name_plural = 'Поставки'
        ordering = ['-date']

    def __str__(self):
        return f'{self.supplier} → {self.product} ({self.date})'


class Client(models.Model):
    """Клиент (постоянный покупатель)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='client', verbose_name='Пользователь')
    phone = models.CharField(max_length=20, validators=[phone_validator], verbose_name='Телефон')
    address = models.TextField(blank=True, verbose_name='Адрес')
    birth_date = models.DateField(verbose_name='Дата рождения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['user__last_name']

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.phone})'

    def age(self):
        today = timezone.now().date()
        delta = today - self.birth_date
        return delta.days // 365


class Employee(models.Model):
    """Сотрудник"""
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='employee', verbose_name='Пользователь')
    phone = models.CharField(max_length=20, validators=[phone_validator], verbose_name='Телефон')
    position = models.CharField(max_length=100, verbose_name='Должность')
    birth_date = models.DateField(verbose_name='Дата рождения')
    hired_at = models.DateField(verbose_name='Дата найма')

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ['user__last_name']

    def __str__(self):
        return f'{self.user.get_full_name()} — {self.position}'

    def age(self):
        today = timezone.now().date()
        delta = today - self.birth_date
        return delta.days // 365


class Sale(models.Model):
    """Продажа"""
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True,
                               blank=True, related_name='sales', verbose_name='Клиент')
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True,
                                 related_name='sales', verbose_name='Сотрудник')
    date = models.DateTimeField(default=timezone.now, verbose_name='Дата продажи')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Продажа'
        verbose_name_plural = 'Продажи'
        ordering = ['-date']

    def __str__(self):
        return f'Продажа №{self.pk} от {self.date.strftime("%d/%m/%Y")}'

    def total(self):
        return sum(item.total_price() for item in self.items.all())


class SaleItem(models.Model):
    """Позиция в продаже"""
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE,
                             related_name='items', verbose_name='Продажа')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='sale_items', verbose_name='Товар')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за единицу')

    class Meta:
        verbose_name = 'Позиция продажи'
        verbose_name_plural = 'Позиции продажи'

    def __str__(self):
        return f'{self.product} x {self.quantity}'

    def total_price(self):
        return self.quantity * self.price