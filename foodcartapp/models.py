import requests

from django.db import models
from django.db.models import F, Prefetch
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField

from locations.models import Location
from locations.geo import fetch_coordinates, calculate_distance


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def extra(self):

        restaurants = Restaurant.objects.all()

        menu_items = RestaurantMenuItem.objects.filter(availability=True)\
            .prefetch_related(Prefetch('restaurant', restaurants))

        products = Product.objects.prefetch_related(
            Prefetch(
                'menu_items',
                menu_items
            )
        )

        order_items = OrderItem.objects.prefetch_related(
            Prefetch(
                'product',
                products
            )
        ).annotate(subtotal=F('price') * F('quantity'))

        orders = self.exclude(status='CT').order_by('status').prefetch_related(
            Prefetch(
                'order_items',
                order_items
            )
        ).prefetch_related('executing_restaurant')

        locations = Location.objects.all()

        loc_lon_lat = {}

        for location in locations:
            loc_lon_lat[location.address] = {
                'lon': location.lon,
                'lat': location.lat,
            }

        for restaurant in restaurants:
            if not any(restaurant.address == location
                    for location in loc_lon_lat.keys()):
                try:
                    lon, lat = fetch_coordinates(restaurant.address)
                    Location.objects.create(
                        address=restaurant.address,
                        lon=lon,
                        lat=lat,
                    )
                except requests.exceptions.HTTPError:
                    lon, lat = 0, 0
                loc_lon_lat[restaurant.address] = {
                    'lon': lon,
                    'lat': lat,
                }

        for order in orders:
            if not any(order.address == location
                    for location in loc_lon_lat.keys()):
                try:
                    lon, lat = fetch_coordinates(order.address)
                    Location.objects.create(
                        address=order.address,
                        lon=lon,
                        lat=lat,
                    )
                except requests.exceptions.HTTPError:
                    lon, lat = 0, 0
                loc_lon_lat[order.address] = {
                    'lon': lon,
                    'lat': lat,
                }

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
                restaurants_suitable_for_order = []
                for restaurant in restaurants_with_order_items:
                    if all(restaurant in restaurants for restaurants
                            in order_items_in_restaurants.values()):
                        restaurant_coordinates = (
                            loc_lon_lat.get(restaurant.address)['lon'],
                            loc_lon_lat.get(restaurant.address)['lat'],
                        )
                        order_coordinates = (
                            loc_lon_lat.get(order.address)['lon'],
                            loc_lon_lat.get(order.address)['lat'],
                        )
                        distance_to_order = calculate_distance(
                            restaurant_coordinates,
                            order_coordinates,
                        )
                        restaurants_suitable_for_order.append(
                            (restaurant, round(distance_to_order, 3))
                        )
                order.restaurants = [
                    {restaurant[0]: restaurant[1]} for restaurant
                    in sorted(
                        restaurants_suitable_for_order,
                        key=lambda r: r[1]
                    )
                ]
                order.restaurants_text = 'Может быть приготовлен ресторанами:'
            else:
                order.restaurants_text = 'Готовится в ресторане:'

            subtotals = [item.subtotal for item in order_items]
            total = sum(subtotals)
            order.total = total
        return orders


class OrderItem(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name='товар',
        related_name='order_items',
        on_delete=models.CASCADE,
    )
    quantity = models.IntegerField(
        verbose_name='количество',
    )
    price = models.DecimalField(
        verbose_name='цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    order = models.ForeignKey(
        'Order',
        verbose_name='заказ',
        related_name='order_items',
        on_delete=models.CASCADE,
    )


class Order(models.Model):

    STATUS_CHOISES = [
        ('MANAGER', 'Согласование'),
        ('RESTAURANT', 'Готовится'),
        ('COURIER', 'В пути'),
        ('CLIENT', 'Доставлен'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('NONE', 'Не выбран'),
        ('CASH', 'Наличные'),
        ('CARD', 'Карта'),
        ('ONLINE', 'На сайте')
    ]

    status = models.CharField(
        verbose_name='статус',
        max_length=10,
        choices=STATUS_CHOISES,
        default='MANAGER',
        db_index=True,
    )
    executing_restaurant = models.ForeignKey(
        Restaurant,
        related_name='orders',
        verbose_name="испоняющий ресторан",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    payment = models.CharField(
        verbose_name='способ оплаты',
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
        default='NONE',
        db_index=True,
    )
    address = models.CharField(
        max_length=200,
        verbose_name='адрес',
    )
    firstname = models.CharField(
        max_length=200,
        verbose_name='имя',
    )
    lastname = models.CharField(
        max_length=200,
        verbose_name='фамилия',
    )
    phonenumber = PhoneNumberField(
        verbose_name='номер телефона',
        db_index=True,
    )
    comment = models.TextField(
        verbose_name='комментарий к заказу',
        max_length=500,
        blank=True,
    )
    registered_at = models.DateTimeField(
        verbose_name='принят',
        auto_now_add=True,
        db_index=True,
    )
    called_at = models.DateTimeField(
        verbose_name='время звонка',
        db_index=True,
        null=True,
        blank=True,
    )
    delivered_at = models.DateTimeField(
        verbose_name='время доставки',
        db_index=True,
        null=True,
        blank=True,
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f"№ {self.id} - {self.firstname} {self.lastname}, {self.address}"
