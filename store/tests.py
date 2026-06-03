from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
from .models import Category, Product, Supplier, Client as ClientModel, Employee, Sale, SaleItem


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Корм для собак',
            description='Тестовое описание'
        )

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Корм для собак')

    def test_category_name(self):
        self.assertEqual(self.category.name, 'Корм для собак')

    def test_category_description(self):
        self.assertEqual(self.category.description, 'Тестовое описание')


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Тестовая категория')
        self.product = Product.objects.create(
            article='TEST-001',
            name='Тестовый товар',
            description='Описание',
            price=10.99,
            stock=50,
            category=self.category
        )

    def test_product_str(self):
        self.assertIn('TEST-001', str(self.product))

    def test_product_price(self):
        self.assertEqual(float(self.product.price), 10.99)

    def test_product_stock(self):
        self.assertEqual(self.product.stock, 50)

    def test_product_category(self):
        self.assertEqual(self.product.category, self.category)


class SupplierModelTest(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(
            name='Тестовый поставщик',
            address='г. Минск, ул. Тестовая, 1',
            phone='+375 (29) 123-45-67',
            email='test@test.com'
        )

    def test_supplier_str(self):
        self.assertEqual(str(self.supplier), 'Тестовый поставщик')

    def test_supplier_phone(self):
        self.assertEqual(self.supplier.phone, '+375 (29) 123-45-67')

    def test_supplier_email(self):
        self.assertEqual(self.supplier.email, 'test@test.com')


class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_status(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_template(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'store/home.html')

    def test_home_page_contains_text(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Зоомагазин')


class ProductListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Тестовая категория')
        self.product = Product.objects.create(
            article='TEST-001',
            name='Тестовый товар',
            price=10.99,
            stock=50,
            category=self.category
        )

    def test_product_list_status(self):
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)

    def test_product_list_template(self):
        response = self.client.get(reverse('product_list'))
        self.assertTemplateUsed(response, 'store/product_list.html')

    def test_product_list_contains_product(self):
        response = self.client.get(reverse('product_list'))
        self.assertContains(response, 'Тестовый товар')

    def test_product_list_search(self):
        response = self.client.get(reverse('product_list'), {'q': 'Тестовый'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый товар')

    def test_product_list_filter_by_category(self):
        response = self.client.get(reverse('product_list'), {'category': self.category.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый товар')


class ProductDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Тестовая категория')
        self.product = Product.objects.create(
            article='TEST-001',
            name='Тестовый товар',
            price=10.99,
            stock=50,
            category=self.category
        )

    def test_product_detail_status(self):
        response = self.client.get(reverse('product_detail', args=[self.product.pk]))
        self.assertEqual(response.status_code, 200)

    def test_product_detail_template(self):
        response = self.client.get(reverse('product_detail', args=[self.product.pk]))
        self.assertTemplateUsed(response, 'store/product_detail.html')

    def test_product_detail_contains_name(self):
        response = self.client.get(reverse('product_detail', args=[self.product.pk]))
        self.assertContains(response, 'Тестовый товар')


class AuthViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='Тест',
            last_name='Пользователь'
        )

    def test_login_page_status(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_login_wrong_password(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)

    def test_register_page_status(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_register_success(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'newpass123!',
            'password2': 'newpass123!',
            'first_name': 'Новый',
            'last_name': 'Пользователь',
            'email': 'new@test.com'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)


class StaffViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='staffuser',
            password='staffpass123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regularuser',
            password='regularpass123'
        )

    def test_supplier_list_requires_staff(self):
        self.client.login(username='regularuser', password='regularpass123')
        response = self.client.get(reverse('supplier_list'))
        self.assertEqual(response.status_code, 302)

    def test_supplier_list_staff_access(self):
        self.client.login(username='staffuser', password='staffpass123')
        response = self.client.get(reverse('supplier_list'))
        self.assertEqual(response.status_code, 200)

    def test_statistics_requires_staff(self):
        self.client.login(username='regularuser', password='regularpass123')
        response = self.client.get(reverse('statistics'))
        self.assertEqual(response.status_code, 302)

    def test_statistics_staff_access(self):
        self.client.login(username='staffuser', password='staffpass123')
        response = self.client.get(reverse('statistics'))
        self.assertEqual(response.status_code, 200)


class ProductCRUDTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='staffuser',
            password='staffpass123',
            is_staff=True
        )
        self.category = Category.objects.create(name='Тестовая категория')

    def test_product_create_page(self):
        self.client.login(username='staffuser', password='staffpass123')
        response = self.client.get(reverse('product_create'))
        self.assertEqual(response.status_code, 200)

    def test_product_create(self):
        self.client.login(username='staffuser', password='staffpass123')
        response = self.client.post(reverse('product_create'), {
            'article': 'NEW-001',
            'name': 'Новый товар',
            'description': 'Описание',
            'price': '15.99',
            'stock': '10',
            'category': self.category.pk
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(article='NEW-001').exists())

    def test_product_update(self):
        self.client.login(username='staffuser', password='staffpass123')
        product = Product.objects.create(
            article='UPD-001',
            name='Старое название',
            price=10.00,
            stock=5,
            category=self.category
        )
        response = self.client.post(
            reverse('product_update', args=[product.pk]), {
                'article': 'UPD-001',
                'name': 'Новое название',
                'price': '20.00',
                'stock': '10',
                'category': self.category.pk
            }
        )
        self.assertEqual(response.status_code, 302)
        product.refresh_from_db()
        self.assertEqual(product.name, 'Новое название')

    def test_product_delete(self):
        self.client.login(username='staffuser', password='staffpass123')
        product = Product.objects.create(
            article='DEL-001',
            name='Удаляемый товар',
            price=10.00,
            stock=5,
            category=self.category
        )
        response = self.client.post(reverse('product_delete', args=[product.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Product.objects.filter(article='DEL-001').exists())