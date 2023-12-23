import os
from bookstore import app, build_sample_db

# It Allows You to Execute Code When the File Runs as a Script
if __name__ == '__main__':
    
    # Build a sample db on the fly, if one does not exist yet.
    # app_dir = os.path.realpath(os.path.dirname(__file__))
    # database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    # if not os.path.exists(database_path):
    with app.app_context():
        build_sample_db()

    # Start app
    app.run(debug=True)  