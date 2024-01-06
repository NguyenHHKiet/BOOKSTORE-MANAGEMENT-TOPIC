import datetime
import math

from bookstore.books.utils import *
from flask import Blueprint,render_template,request, jsonify
from flask_login import login_required

from bookstore import Book, app
from bookstore.cart.forms import AddToCart
from bookstore.cart.utils import handle_cart
from bookstore.users.routes import login

books = Blueprint('books', __name__)

@books.route("/book/<int:book_id>")
def bookDetail(book_id):
    # products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()
    book = Book.query.get_or_404(book_id)

    form = AddToCart()
    comments = get_comment(page=request.args.get('page', 1), bookID=book_id)

    return render_template('bookDetail.html', title=book.name, post=book, form=form,
                           comments=comments, pages=math.ceil(get_count_comment(book_id) / app.config['COMMENT_SIZE']))


@books.route('/api/comments', methods=['post'])
@login_required
def add_comment():
    data = request.json
    content = data.get('content')
    book_id = data.get('book_id')

    try:
        c= add_comment_into_db(content=content, book_id=book_id)

        return jsonify({
            'status': 201,
            'comment':{
                'id':c.id,
                'content':c.content,
                'created_date':str(c.created_date),
                'user':{
                    'username':current_user.username,
                    'avatar': current_user.image_file
                }
            }
        })
    except:
        return {'status':404, 'err_msg':'chuong trinh loi'}

@books.route('/api/book/<int:book_id>/comments', methods=['get'])
def get_comments(book_id):
    page = request.args.get('page',1)
    comments = get_comment(page=int(page), bookID=book_id)
    results=[]
    for c in comments:
        results.append({
            'id':c.id,
            'content':c.content,
            'created_date': str(c.created_date),
            'user': {
                'id':c.user.id,
                'username': c.user.username,
                'avatar': c.user.image_file
            }
        })
    return jsonify(results)