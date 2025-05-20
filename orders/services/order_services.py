import uuid
from typing import List

from django.db import transaction
from django.utils.timezone import now

from common.services import model_update
from orders.models import Order
from orders.services.order_item_services import order_item_create
from orders.utils import calculate_order_amount
from users.models import User


@transaction.atomic
def order_create_process(*, amount: int,
                         coupon_id: uuid = None,
                         customer_contact: str = None,
                         customer_id: str = None,
                         delivery_fee: int,
                         delivery_time: str = None,
                         discount: str = None,
                         paid_total: str = None,
                         payment_gateway: str = None,
                         products: str = None,
                         sales_tax: list = None,
                         total: str = None,
                         use_wallet_points: bool,
                         ) -> Order:
    order = order_create(amount=amount,
                         coupon_id=coupon_id,
                         customer_contact=customer_contact,
                         customer_id=customer_id,
                         delivery_fee=delivery_fee,
                         delivery_time=delivery_time,
                         discount=discount,
                         paid_total=paid_total,
                         payment_gateway=payment_gateway,
                         sales_tax=sales_tax,
                         total=total,
                         # use_wallet_points=use_wallet_points,
                         )

    for product in products:
        # batch = batch_get(batch_id=product.get('batch_id'))
        # product = product_get(product_id=product.get('product_id'))
        order_item_create(
            # item_name=product.get('item_name'),
            # batch_number=batch.batch_number,
            quantity=product.get('order_quantity'),
            price=product.get('unit_price'),
            cost=product.get('unit_price'),
            sale_price=product.get('unit_price'),
            # percentage_discount=order_item.percentage_discount,
            # percentage_discount_amount=order_item.percentage_discount_amount,
            # flat_discount_amount=order_item.flat_discount_amount,
            # sale_price_discount_amount=order_item.sale_price_discount_amount,
            # item_value=product.get('item_value'),
            order_id=order.id,
            product_id=product.get('product_id'),
        )

    return order


@transaction.atomic
def shop_order_create_process(*, products: list = None,
                              customer: User,
                              ) -> Order:
    amount = calculate_order_amount(products)
    order = order_create(amount=amount,
                         # coupon_id=coupon_id,
                         # customer_contact=customer,
                         customer_id=customer.id,
                         # delivery_fee=delivery_fee,
                         # delivery_time=delivery_time,
                         # discount=discount,
                         # paid_total=paid_total,
                         # payment_gateway=payment_gateway,
                         # sales_tax=sales_tax,
                         total=amount,
                         # use_wallet_points=use_wallet_points,
                         )

    for product in products:
        # batch = batch_get(batch_id=product.get('batch_id'))
        # product = product_get(product_id=product.get('product_id'))
        order_item_create(
            # item_name=product.get('item_name'),
            # batch_number=batch.batch_number,
            quantity=product.get('order_quantity'),
            price=product.get('unit_price'),
            cost=product.get('unit_price'),
            sale_price=product.get('unit_price'),
            # percentage_discount=order_item.percentage_discount,
            # percentage_discount_amount=order_item.percentage_discount_amount,
            # flat_discount_amount=order_item.flat_discount_amount,
            # sale_price_discount_amount=order_item.sale_price_discount_amount,
            # item_value=product.get('item_value'),
            order_id=order.id,
            product_id=product.get('product_id'),
        )

    return order


@transaction.atomic
def order_create(*, amount: int,
                 coupon_id: uuid = None,
                 customer_contact: str = None,
                 customer_id: str = None,
                 delivery_fee: int,
                 delivery_time: str = None,
                 discount: str = None,
                 paid_total: str = None,
                 payment_gateway: str = None,
                 products: str = None,
                 sales_tax: str = None,
                 total: str = None,
                 # use_wallet_points: bool,
                 ) -> Order:
    """Creates an order with a unique tracking number."""

    def generate_tracking_number():
        return f"ORD-{now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"

    tracking_number = generate_tracking_number()
    order = Order.objects.create(amount=amount,
                                 tracking_number=tracking_number,
                                 coupon_id=coupon_id,
                                 customer_contact=customer_contact,
                                 customer_id=customer_id,
                                 delivery_fee=delivery_fee,
                                 delivery_time=delivery_time,
                                 discount=discount,
                                 paid_total=paid_total,
                                 payment_gateway=payment_gateway,
                                 sales_tax=sales_tax,
                                 total=total,
                                 # use_wallet_points=use_wallet_points,
                                 )

    return order


@transaction.atomic
def order_update(*, order: Order, data) -> Order:
    non_side_effect_fields: List[str] = [
        "order_status",
    ]

    author, has_updated = model_update(instance=order, fields=non_side_effect_fields, data=data)

    return author
