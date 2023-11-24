from flask import Blueprint,render_template
from bookstore import Book

books = Blueprint('books', __name__)

@books.route("/book/<int:book_id>")
def bookDetail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('bookDetail.html', title=book.name, post=book)
