import os
import pandas
from flask import current_app

from bookstore import dao
from bookstore.models import ImportTicket, Category, Author, Book, ImportDetails


def import_book(excel):
    # save file
    file_path = os.path.join(current_app.root_path, 'static/data_import', excel.filename)
    excel.save(file_path)
    # read data
    data = pandas.read_excel(excel)
    # handle new book data
    # save ticket
    ticket = ImportTicket()
    dao.save_ticket(ticket=ticket)
    # get bookstore configuration
    configuration = dao.get_configuration()
    for index, row in data.iterrows():
        name = str(row['Name']).strip()
        category = str(row['Category']).strip()
        author = str(row['Author']).strip()
        quantity = int(row['Quantity'])
        # check the quantity is valid or not
        if quantity < configuration.min_import_quantity:
            continue
        # query book from database if not exist then create
        db_book = dao.get_book_by_name(name=name)
        if not db_book:
            db_category = dao.get_category_by_name(name=category)
            if not db_category:
                db_category = Category(name=category)
                dao.save_category(db_category)
            db_author = dao.get_author_by_name(name=author)
            if not db_author:
                db_author = Author(name=author)
                dao.save_author(db_author)
            db_book = Book(name=name, author=db_author, category=db_category, available_quantity=quantity)
            dao.save_book(book=db_book)
        else:
            # check in stock quantity
            if db_book.available_quantity > configuration.min_stock_quantity:
                continue
            else:
                db_book.available_quantity += quantity
                dao.save_book(book=db_book)
        # save ticket details
        ticket_details = ImportDetails(quantity=quantity, book=db_book, import_ticket=ticket)
        dao.save_ticket_details(ticket_details=ticket_details)