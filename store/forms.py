from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Category, Product, Supplier, Supply, Client, Employee, Sale, SaleItem


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['article', 'name', 'description', 'price', 'stock', 'category', 'image']
        widgets = {
            'article': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'address', 'phone', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': '+375 (29) XXX-XX-XX'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['phone', 'address', 'birth_date']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': '+375 (29) XXX-XX-XX'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = timezone.now().date()
            age = (today - birth_date).days // 365
            if age < 18:
                raise ValidationError('Клиент должен быть старше 18 лет.')
        return birth_date


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['client', 'employee', 'date']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['product', 'quantity', 'price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }