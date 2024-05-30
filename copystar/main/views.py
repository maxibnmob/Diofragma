from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from .forms import UserCreationForm
from .models import *
from django.views import View
def index(request):
    return render(request, 'main/index.html')

def catalog(request):
    categories = Category.objects.all()  # Получаем список всех категорий
    products = Product.objects.all()

    # Получение параметра сортировки из GET-запроса
    sort_by = request.GET.get('sort_by')

    # Сортировка товаров в зависимости от параметра сортировки
    if sort_by == 'newest':
        products = products.order_by('-production_year')
    elif sort_by == 'oldest':
        products = products.order_by('production_year')
    elif sort_by == 'name+':
        products = products.order_by('name')
    elif sort_by == 'name-':
        products = products.order_by('-name')
    elif sort_by == 'price-':
        products = products.order_by('-price')
    elif sort_by == 'price+':
        products = products.order_by('price')

    # Здесь должен быть код для отображения страницы с товарами,
    # с учетом сортировки
    return render(request, 'main/catalog/catalog.html', {'categories': categories, 'products': products})

def category(request, cat_id):
    cats = Category.objects.all()
    category = Category.objects.get(pk=cat_id)
    products = Product.objects.filter(category=category)

    # Получение параметра сортировки из GET-запроса
    sort_by = request.GET.get('sort_by')

    # Сортировка товаров в зависимости от параметра сортировки
    if sort_by == 'newest':
        products = products.order_by('-production_year')
    elif sort_by == 'oldest':
        products = products.order_by('production_year')
    elif sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == 'price-':
        products = products.order_by('-price')
    elif sort_by == 'price+':
        products = products.order_by('price')
    else:
        # Если параметр сортировки не указан или некорректен, выводим товары без сортировки
        pass

    return render(request, 'main/catalog/catalog.html', {'category': category, 'products': products, 'cats': cats})

def product(request, product_id):
    product = Product.objects.get(pk=product_id)
    return render(request, 'main/product/product.html', {'product': product})

@login_required
def cart(request):
    # Получаем все товары в корзине текущего пользователя
    cart_items = Cart.objects.filter(client=request.user)

    # Вычисляем общую стоимость всех товаров в корзине
    total_cost = sum(item.item.price * item.quantity for item in cart_items)

    return render(request, 'main/cart/cart.html', {'cart_items': cart_items, 'total_cost': total_cost})

@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(pk=product_id)
    # Сохраняем товар в корзину с указанием текущего пользователя
    cart_item, created = Cart.objects.get_or_create(client=request.user, item=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = Cart.objects.get(id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

from django.db import transaction

@login_required
def order(request):
    if request.method == 'POST':
        user = request.user
        cart_items = Cart.objects.filter(client=user)

        # Проверяем, что в корзине есть товары
        if cart_items:
            # Начинаем транзакцию
            with transaction.atomic():
                try:
                    # Создаем новый заказ для текущего пользователя со статусом "New"
                    order = Order.objects.create(user=user, status='New')

                    # Добавляем товары из корзины в заказ
                    for cart_item in cart_items:
                        OrderItem.objects.create(order=order, product=cart_item.item, quantity=cart_item.quantity)

                        # Уменьшаем количество товара на складе
                        product = cart_item.item
                        product.quantity -= cart_item.quantity
                        product.save()

                    # Очищаем корзину текущего пользователя
                    cart_items.delete()

                    messages.success(request, 'Заказ успешно оформлен.')
                    return redirect('order_detail')

                except Exception as e:
                    # Если произошла ошибка, откатываем транзакцию и выводим сообщение об ошибке
                    transaction.rollback()
                    messages.error(request, f'Ошибка при оформлении заказа: {str(e)}')
                    return redirect('cart')

        else:
            messages.error(request, 'Ваша корзина пуста.')
            return redirect('cart')

    else:
        cart_items = Cart.objects.filter(client=request.user)
        total_cost = sum(item.item.price * item.quantity for item in cart_items)
        return render(request, 'main/order/order_menu.html', {'cart_items': cart_items, 'total_cost': total_cost})

@login_required
def order_add(request, product_id):
    if request.method == 'POST':
        user = request.user
        product = Product.objects.get(pk=product_id)

        # Проверяем доступное количество товара перед добавлением в заказ
        if product.quantity > 0:
            # Получаем или создаем заказ для текущего пользователя
            order, created = Order.objects.get_or_create(user=user, status='New')

            # Если товар уже есть в заказе, увеличиваем количество
            order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
            if not created:
                # Проверяем, что количество товара в заказе не превышает доступное количество
                if order_item.quantity < product.quantity:
                    order_item.quantity += 1
                    order_item.save()
                    messages.success(request, f'Количество товара {product.name} в заказе увеличено на 1.')
                else:
                    messages.error(request, f'Количество товара {product.name} в заказе превышает доступное количество.')
            else:
                messages.success(request, f'Товар {product.name} добавлен в заказ.')

            return redirect('cart')
        else:
            messages.error(request, 'Товара нет в наличии.')
            return redirect('product', product_id=product_id)
    else:
        return redirect('product', product_id=product_id)

@login_required
def order_detail(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        action = request.POST.get('action')
        admin_message = request.POST.get('admin_message')

        try:
            order = Order.objects.get(pk=order_id)

            if action == 'approve':
                order.status = 'Confirmed'
                messages.success(request, 'Заявка успешно одобрена.')
            elif action == 'reject':
                order.status = 'Closed'
                messages.success(request, 'Заявка успешно отклонена.')

            if admin_message:
                order.user_message = admin_message  # Исправлено здесь, должно быть order.user_message

            order.save()

        except Order.DoesNotExist:
            messages.error(request, 'Заказ не найден.')

        return HttpResponseRedirect(reverse('order_detail'))

    else:
        orders = Order.objects.filter(user=request.user)
        return render(request, 'main/order/order_detail.html', {'orders': orders})

def order_menu(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'main/order/order_menu.html', {'orders': orders})


def about(request):
    return render(request, 'main/about.html')

def wherefind(request):
    return render(request, 'main/wherefind.html')

class Register(View):
    template_name = 'registration/register.html'

    def get(self, request):
        context = {
            'form': UserCreationForm()
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request,user)
            return redirect('home')
        context = {
            'form': form
        }
        return render(request,self.template_name,context)