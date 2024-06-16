from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя категории')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_id': self.pk})

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Product(models.Model):
    photo = models.ImageField(upload_to="product_photos")
    name = models.CharField(max_length=150, verbose_name='Имя товара')
    description = models.TextField(verbose_name='Описание товара')
    production_year = models.DateField(verbose_name='Дата производства')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Стоимость')
    quantity = models.IntegerField(verbose_name='Количество шт.')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория товара')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product', kwargs={'product_id': self.pk})

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class Order(models.Model):
    STATUS_CHOICES = (
        ('New', 'Новый(В обработке)'),
        ('Confirmed', 'Подтвержденный'),
        ('Closed', 'Закрытый')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Чей заказ')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New', verbose_name='Статус заказа')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания заказа')
    user_message = models.TextField(blank=True, null=True, verbose_name='Сообщение для пользователя')
    first_name = models.CharField(max_length=30,default='SOME STRING')
    last_name = models.CharField(max_length=30,default='SOME STRING')
    address = models.TextField(default='SOME STRING')
    phone = models.CharField(max_length=15,default='SOME STRING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def __str__(self):
        return f'{self.user} - {self.created_at}'

    def get_absolute_url(self):
        return reverse('order')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='ЗаказЗаказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.IntegerField(default=1, verbose_name='Количество')

    def __str__(self):
        return f'{self.product.name} - {self.quantity} шт.'

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'


class Cart(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Product, on_delete=models.CASCADE)  # Изменено на item
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.item.name} {self.client.username}'

    def get_absolute_url(self):
        return reverse('cart')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
