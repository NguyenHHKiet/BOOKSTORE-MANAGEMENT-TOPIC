import math

from flask import render_template, request, Blueprint, flash, jsonify, make_response, redirect, url_for, session
from bookstore import utils, app, dao
from bookstore.models import Book
from bookstore.cart.utils import handle_cart
from flask_security import current_user
main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    cate_id = request.args.get('cate_id')
    page = request.args.get('page', 1, type=int)
    num = Book.query.filter(Book.enable.__eq__(True)).count()
    numCate = None
    if cate_id:
        num_cate_book = Book.query.filter(Book.category_id.__eq__(cate_id)).count()
        numCate = math.ceil(num_cate_book / app.config['PAGE_SIZE'])
    # if "cart" not in session:
    #     session["cart"] = []
    # products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()


    posts=dao.load_book(cate_id, page)
    if current_user.is_authenticated:
        if "cart" in session:
            products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()
            return render_template("home.html", numCate=numCate, cate_id=cate_id, posts=posts,
                                   pages=math.ceil(num / app.config['PAGE_SIZE']), quantity_total=quantity_total)

    return render_template("home.html", numCate=numCate, cate_id=cate_id,
                                   pages=math.ceil(num / app.config['PAGE_SIZE']), posts=posts)


@app.context_processor
def common_response():
    return {
        'categories': dao.load_cate()}


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
    num = Book.query.filter(Book.name.contains(data)).count()

    res = dao.load_book(kw=data, page=page)
    
    if not data or num==0:
        flash('Book not found!!', 'warning')
        return redirect(url_for('main.home'))
    num=math.ceil(num/app.config['PAGE_SIZE'])

    return render_template("home.html", posts=res, num=num, kw=data)


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