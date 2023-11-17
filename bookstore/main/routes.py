from flask import render_template, request, Blueprint

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
