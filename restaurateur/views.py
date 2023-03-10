from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from foodcartapp.models import Product, Restaurant, Order
from locations.geo import calculate_distance, add_locations_with_coordinates
from locations.models import Location


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.exclude(status='CLIENT').order_by('status')\
        .prefetch_related('executing_restaurant').with_prices()
    restaurants = Restaurant.objects.all()
    stored_locations = Location.objects.all()

    addresses_lon_lat = add_locations_with_coordinates(
        orders,
        restaurants,
        stored_locations=stored_locations,
    )

    for order in orders:

        order_items = order.order_items.all()

        order_items_in_restaurants = {}
        for order_item in order_items:
            order_items_in_restaurants[order_item.product] = [
                item.restaurant for item in
                order_item.product.menu_items.all()
            ]

        restaurants_with_order_items = []
        for bunch in order_items_in_restaurants.values():
            for restaurant in bunch:
                if restaurant not in restaurants_with_order_items:
                    restaurants_with_order_items.append(restaurant)

        if not order.executing_restaurant:
            capable_restaurants = []
            for restaurant in restaurants_with_order_items:
                if all(restaurant in restaurants for restaurants
                        in order_items_in_restaurants.values()):
                    restaurant_coordinates = (
                        addresses_lon_lat.get(restaurant.address)['lon'],
                        addresses_lon_lat.get(restaurant.address)['lat'],
                    )
                    order_coordinates = (
                        addresses_lon_lat.get(order.address)['lon'],
                        addresses_lon_lat.get(order.address)['lat'],
                    )
                    distance_to_order = calculate_distance(
                        restaurant_coordinates,
                        order_coordinates,
                    )
                    capable_restaurants.append(
                        (restaurant.name, round(distance_to_order, 3))
                    )
            order.capable_restaurants = [
                {restaurant[0]: restaurant[1]} for restaurant
                in sorted(
                    capable_restaurants,
                    key=lambda restaurant: restaurant[1]
                )
            ]
            order.restaurants_text = 'Может быть приготовлен ресторанами:'
        else:
            order.restaurants_text = 'Готовится в ресторане:'

    return render(request, template_name='order_items.html', context={
        'orders': orders,
    })
