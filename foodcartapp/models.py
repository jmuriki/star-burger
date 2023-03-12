from django.db import models
from django.db.models import F, Prefetch
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField

from locations.geo import calculate_distance, add_locations_with_coordinates
from locations.models import Location


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


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)

    def with_menu_items(self):
        return self.prefetch_related(Prefetch(
                'menu_items',
                RestaurantMenuItem.objects.available_in()
            )
        )


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


class RestaurantMenuItemQuerySet(models.QuerySet):
    def available_in(self):
        return self.filter(availability=True)\
            .prefetch_related('restaurant')


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

    objects = RestaurantMenuItemQuerySet.as_manager()

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderItemQuerySet(models.QuerySet):
    def with_products(self):
        return self.prefetch_related(Prefetch(
                'product',
                Product.objects.with_menu_items()
            )
        )

    def subtotal(self):
        return self.annotate(subtotal=F('price') * F('quantity'))


class OrderItem(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name='товар',
        related_name='order_items',
        on_delete=models.CASCADE,
    )
    quantity = models.IntegerField(
        verbose_name='количество',
        validators=[MinValueValidator(1)]
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

    objects = OrderItemQuerySet.as_manager()

    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказа'

    def __str__(self):
        return self.product.name


class OrderQuerySet(models.QuerySet):
    def actual_status(self):
        return self.exclude(status='CLIENT').order_by('status')


    def with_prices(self):
        orders = self.prefetch_related(
            Prefetch(
                'order_items',
                OrderItem.objects.with_products().subtotal()
            )
        )
        for order in orders:
            subtotals = [item.subtotal for item in order.order_items.all()]
            order.total = sum(subtotals)
        return orders


    def with_capable_restaurants(self):
        orders = self
        restaurants = Restaurant.objects.all()
        stored_locations = Location.objects.all()

        addresses_lon_lat = add_locations_with_coordinates(
            orders,
            restaurants,
            stored_locations=stored_locations,
        )

        for order in orders:
            order_items = order.order_items.all()
            """For every order item collecting all capable restaurants"""
            order_items_with_capable_restaurants = {}
            for order_item in order_items:
                order_items_with_capable_restaurants[order_item.product] = [
                    item.restaurant for item in
                    order_item.product.menu_items.all()
                ]

            """Collecting distinct restaurants with any order item available"""
            restaurants_with_any_item = []
            for bunch in order_items_with_capable_restaurants.values():
                for restaurant in bunch:
                    if restaurant not in restaurants_with_any_item:
                        restaurants_with_any_item.append(restaurant)

            if not order.executing_restaurant:
                """Choosing restaurant with only all order items available"""
                capable_restaurants = []
                for restaurant_with_item in restaurants_with_any_item:
                    if all(restaurant_with_item in restaurants for restaurants
                            in order_items_with_capable_restaurants.values()):
                        restaurant_coordinates = (
                            addresses_lon_lat.get(restaurant_with_item.address)['lon'],
                            addresses_lon_lat.get(restaurant_with_item.address)['lat'],
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
                            (
                                restaurant_with_item.name,
                                round(distance_to_order, 3)
                            )
                        )
                order.capable_restaurants = [
                    {restaurant[0]: restaurant[1]} for restaurant
                    in sorted(
                        capable_restaurants,
                        key=lambda restaurant: restaurant[1]
                    )
                ]
        return orders


class Order(models.Model):

    STATUS_CHOISES = [
        ('0 - MANAGER', 'Согласование'),
        ('1 - RESTAURANT', 'Готовится'),
        ('2 - COURIER', 'В пути'),
        ('3 - CLIENT', 'Доставлен'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('NONE', 'Не выбран'),
        ('CASH', 'Наличные'),
        ('CARD', 'Карта'),
        ('ONLINE', 'На сайте')
    ]

    status = models.CharField(
        verbose_name='статус',
        max_length=14,
        choices=STATUS_CHOISES,
        default='0 - MANAGER',
        db_index=True,
    )
    executing_restaurant = models.ForeignKey(
        Restaurant,
        related_name='orders',
        verbose_name="исполняющий ресторан",
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
