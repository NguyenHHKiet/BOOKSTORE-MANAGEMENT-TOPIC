
from flask import render_template, request, Blueprint, flash, jsonify, make_response
from bookstore import utils
main = Blueprint('main', __name__)

posts =[
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First Post Comment',
        'date_posted': 'April 20, 2018'
    }, 
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second Post Comment',
        'date_posted': 'April 21, 2018'
    }
]

@main.route("/")
@main.route("/home")
def home():
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
