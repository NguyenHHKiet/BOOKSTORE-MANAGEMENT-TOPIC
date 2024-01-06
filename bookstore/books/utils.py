import datetime

from bookstore import db, app
from bookstore.models import Comment
from flask_login import current_user

def add_comment_into_db(content, book_id):
    c = Comment(content=content, book_id=book_id, user=current_user, created_date=datetime.datetime.now())
    db.session.add(c)
    db.session.commit()
    return c

def get_comment(page=1, bookID=None):

    page = int(page)
    page_size = app.config['COMMENT_SIZE']
    start = (page - 1)*page_size

    return Comment.query.filter(Comment.book_id.__eq__(bookID)).order_by(-Comment.id).slice(start, start+page_size).all()


def get_count_comment(bookID):
    return Comment.query.filter(Comment.book_id.__eq__(bookID)).count()

