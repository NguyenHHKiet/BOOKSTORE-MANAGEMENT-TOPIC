from flask import Blueprint,render_template
from bookstore import Book
from bookstore.cart.forms import AddToCart
from bookstore.cart.utils import handle_cart

books = Blueprint('books', __name__)

@books.route("/book/<int:book_id>")
def bookDetail(book_id):
    products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()
    book = Book.query.get_or_404(book_id)
    
    form = AddToCart()
    
    return render_template('bookDetail.html', title=book.name, post=book, form=form, quantity_total=quantity_total)
