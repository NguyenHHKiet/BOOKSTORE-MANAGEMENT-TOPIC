from flask import session
from bookstore import Book

def handle_cart():
    products = []
    grand_total = 0
    index = 0
    quantity_total = 0
    print(session['cart'])
    for item in session['cart']:
        product = Book.query.filter_by(id=item['id']).first()

        quantity = int(item['quantity'])
        total = quantity * product.unit_price
        grand_total += total

        quantity_total += quantity

        products.append({'id': product.id, 'name': product.name, 'unit_price':  product.unit_price,
                        'image_src': product.image_src, 'quantity': quantity, 'total': total, 'index': index})
        index += 1

    grand_total_plus_shipping = grand_total + 1000

    return products, grand_total, grand_total_plus_shipping, quantity_total
