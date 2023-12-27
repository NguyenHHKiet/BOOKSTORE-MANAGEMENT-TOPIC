from flask import render_template, request, Blueprint, flash, jsonify, make_response, redirect, url_for, session
from bookstore import utils
from bookstore.models import Book
from bookstore.cart.utils import handle_cart
from flask_security import current_user
main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():

    # if "cart" not in session:
    #     session["cart"] = []
    # products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()

    page = request.args.get('page', 1, type=int)
    posts = Book.query.order_by(Book.id.desc()).paginate(page=page, per_page=5)
    if current_user.is_authenticated:
        if "cart" in session:
            products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()
            return render_template("home.html", posts=posts, quantity_total=quantity_total)
    return render_template("home.html", posts= posts)

@main.route("/about")
def about():
    return render_template("about.html", title='About')

@main.route("/import", methods=["POST"])
def import_book():
    # get data file from form
    excel = request.files['excel']
    # handle new data
    response = make_response()

    try:
        utils.import_book(excel=excel)
        response.status_code = 200
    except:
        response.status_code= 400
    return response

@main.route("/search", methods=['GET', 'POST'])
def searchItems():
    data = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    res = Book.query.filter(Book.name.contains(data)).paginate(page=page, per_page=5)
    if not data or not res:
        flash('Book not found!!', 'warning')
        return redirect(url_for('main.home'))
    return render_template("home.html", posts=res)

@main.route("/statistic", methods=['GET'])
def statistic():
    month = int(request.args.get("month"))
    type = request.args.get("type")
    data = None
    if type == 'book':
        data = utils.statistic_book_by_month(month)
    if type == 'category':
        data = utils.statistic_category_by_month(month)
    if type == 'overall':
        data = utils.statistic_revenue()
    return data