from django.contrib import admin
from .models import Category, Supplier, Product, Supply, Client, Employee, Sale, SaleItem


class SupplyInline(admin.TabularInline):
    model = Supply
    extra = 1


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'phone', 'email', 'created_at']
    search_fields = ['name', 'phone']
    list_filter = ['created_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['article', 'name', 'price', 'stock', 'category', 'created_at']
    search_fields = ['article', 'name']
    list_filter = ['category', 'created_at']
    list_editable = ['price', 'stock']
    inlines = [SupplyInline]


@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ['product', 'supplier', 'quantity', 'price', 'date']
    search_fields = ['product__name', 'supplier__name']
    list_filter = ['supplier', 'date']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'birth_date', 'age', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'phone']
    list_filter = ['created_at']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'position', 'birth_date', 'hired_at']
    search_fields = ['user__first_name', 'user__last_name', 'position']
    list_filter = ['position', 'hired_at']


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['pk', 'client', 'employee', 'date', 'total']
    search_fields = ['client__user__last_name', 'employee__user__last_name']
    list_filter = ['date', 'employee']
    inlines = [SaleItemInline]


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['sale', 'product', 'quantity', 'price', 'total_price']
    search_fields = ['product__name']