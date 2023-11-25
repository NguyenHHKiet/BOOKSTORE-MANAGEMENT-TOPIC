from flask import render_template, request, Blueprint, flash, jsonify, make_response, redirect, url_for
from bookstore import utils
from bookstore import Book

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Book.query.order_by(Book.id.desc()).paginate(page=page, per_page=5)
    return render_template("home.html", posts=posts)

@main.route("/about")
def about():
    return render_template("about.html", title='About')

@main.route("/import", methods=["POST"])
def import_book():
    # get data file from form
    excel = request.files['excel']
    # handle new data
    utils.import_book(excel=excel)
    response = make_response()
    response.status_code = 200
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