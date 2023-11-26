from flask import Blueprint, render_template, redirect, url_for, session
from bookstore.cart.forms import AddToCart
from bookstore.cart.utils import handle_cart

cart = Blueprint("cart", __name__)

@cart.route("/quick-add/<int:id>")
def quickAdd(id):
    if "cart" not in session:
        session["cart"] = []
    
    product = [prod for prod in session["cart"] if prod["id"] == int(id)]
    index = [index for index, prod in enumerate(session["cart"]) if prod["id"] == int(id)]
    print(product, index)
    
    if len(product) == 0:
        session["cart"].append({"id": id, "quantity": 1})
    else:
        print(session)
        session["cart"][index[0]]['quantity'] = product[0]['quantity'] + 1
    session.modified = True

    return redirect(url_for("main.home"))

@cart.route("/cart")
def cartDetail():
    if "cart" not in session:
        session["cart"] = []
    print("Please", session)
        
    products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()

    return render_template("cart.html", products=products, grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total)


@cart.route("/add-to-cart", methods=["POST"])
def addToCart():
    if "cart" not in session:
        session["cart"] = []

    form = AddToCart()

    if form.validate_on_submit():
        id = int(form.id.data)
        product = [prod for prod in session["cart"] if prod["id"] == int(id)]
        index = [index for index, prod in enumerate(session["cart"]) if prod["id"] == int(id)]
        print(product, index)
        
        if len(product) == 0:
            session["cart"].append({"id": id, "quantity": int(form.quantity.data)})
        else:
            print(session)
            session["cart"][index[0]]['quantity'] = product[0]['quantity'] + int(form.quantity.data)
        
        session.modified = True

    return redirect(url_for('books.bookDetail', book_id=id))

@cart.route("/remove-from-cart/<int:index>")
def removeFromCart(index):
    del session["cart"][int(index)]
    session.modified = True
    return redirect(url_for("cart.cartDetail"))