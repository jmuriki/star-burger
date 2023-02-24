import phonenumbers

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Product, Order, OrderItem


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def validate_number(number):
    try:
        parsed_number = phonenumbers.parse(number, "RU")
    except Exception:
        return False
    return phonenumbers.is_valid_number(parsed_number)


def make_report(msgs):
    report = {}
    for msg in msgs:
        for field, text in msg.items():
            if report.get(field):
                report[field] = f"{report[field]} {text}"
            else:
                report[field] = text
    return report


def check_order_fields(payload):
    product_ids = [
        product_id for product_id in Product.objects.all().values_list(
            'id',
            flat=True,
        )
    ]
    products_fields = ['product', 'quantity']
    client_fields = ['firstname', 'lastname', 'phonenumber', 'address']
    err_msgs = []
    try:
        if payload['products'] is None:
            err_msgs.append({'products': 'Это поле не может быть пустым.'})
        elif not isinstance(payload['products'], list):
            instance = type(payload['products'])
            text = f"Ожидался list со значениями, но был получен {instance}."
            err_msgs.append({'products': text})
        if isinstance(payload['products'], list) and payload['products']:
            for product in payload['products']:
                if product['product'] not in product_ids:
                    text = f"Недопустимый первичный ключ - {product['product']}."
                    err_msgs.append({'products': text})
                elif product['quantity'] < 1:
                    wrong_quantity_product = Product.objects.get(
                        id=product['product'],
                    )
                    text = f"Недопустимое количество товара \
                    '{wrong_quantity_product.name}' - {product['quantity']}"
                    err_msgs.append({'products': text})
        elif isinstance(payload['products'], list) and not payload['products']:
            err_msgs.append({'products': 'Этот список не может быть пустым.'})
        elif payload['products'] is not None and not payload['products']:
            err_msgs.append({'products': 'Это поле не может быть пустым.'})
        if not any(payload[field] for field in client_fields):
            err_msgs.append({
                ', '.join(client_fields): 'Эти поля не могут быть пустыми.'
            })
        else:
            for field in client_fields:
                if payload[field] is None:
                    err_msgs.append({field: 'Это поле не может быть пустым.'})
                elif not isinstance(payload[field], str):
                    err_msgs.append({field: 'Not a valid string.'})
                elif not payload[field]:
                    err_msgs.append({field: 'Это поле не может быть пустым.'})
                elif field == 'phonenumber' and \
                        not validate_number(payload['phonenumber']):
                    msg = {'phonenumber': 'Введен некорректный номер телефона.'}
                    err_msgs.append(msg)
    except KeyError:
        if not payload.get('products'):
            err_msgs.append({'products': 'Обязательное поле.'})
        else:
            for product in payload['products']:
                for field in products_fields:
                    if not product.get(field):
                        err_msgs.append({field: 'Обязательное поле.'})
        if all(payload.get(field) is None for field in client_fields):
            err_msgs.append({', '.join(client_fields): 'Обязательные поля.'})
        else:
            for field in client_fields:
                if not payload.get(field):
                    err_msgs.append({field: 'Обязательное поле.'})
    if err_msgs:
        report = make_report(err_msgs)
        return report
    return None


@api_view(['POST'])
def register_order(request):
    order_payload = request.data
    err_report = check_order_fields(order_payload)
    if err_report:
        return Response(err_report, status=status.HTTP_406_NOT_ACCEPTABLE)
    order = Order.objects.create(
        address=order_payload['address'],
        firstname=order_payload['firstname'],
        lastname=order_payload['lastname'],
        phonenumber=order_payload['phonenumber'],
    )
    for clause in order_payload['products']:
        product = Product.objects.get(id=clause['product'])
        OrderItem.objects.create(
            product=product,
            quantity=clause['quantity'],
            order=order,
        )
    return Response(order_payload)
