from bookstore import db
from bookstore.models import Configuration, ImportTicket, Book, Category, Author

def get_configuration():
    return Configuration.query.first()

def save_ticket(ticket):
    db.session.add(ticket)
    db.session.commit()

def get_book_by_name(name):
    return Book.query.filter_by(name=name).first()

def save_book(book):
    db.session.add(book)
    db.session.commit()

def get_category_by_name(name):
    return Category.query.filter_by(name=name).first()

def save_category(category):
    db.session.add(category)
    db.session.commit()

def get_author_by_name(name):
    return Author.query.filter_by(name=name).first()

def save_author(author):
    db.session.add(author)
    db.session.commit()

def save_ticket_details(ticket_details):
    db.session.add(ticket_details)
    db.session.commit()
