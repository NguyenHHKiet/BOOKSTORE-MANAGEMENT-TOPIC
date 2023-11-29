# Python Flask Tutorial

Flask is a very lightweight Python Web Framework, easily helping beginners learn Python to create small websites.

![image](https://github.com/NguyenHHKiet/BOOKSTORE-MANAGEMENT-TOPIC/assets/52524133/4bdebee6-66e3-40e2-bc59-f188b1e8cf92)
[Flask-Security](https://flask-security-too.readthedocs.io/en/stable/index.html) allows you to quickly add common security mechanisms to your Flask application.
Many of these features are made possible by integrating various Flask extensions and libraries. They include:

<ul>
    <li>Flask-Login</li>
    <li>Flask-Mailman</li>
    <li>Flask-Principal</li>
    <li>Flask-WTF</li>
    <li>itsdangerous</li>
    <li>passlib</li>
    <li>QRCode</li>
    <li>webauthn</li>
    <li>authlib</li>
</ul>

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install flask
```

## Usage

```python
# Create an environment
> python -m venv .venv
> .venv\Scripts\activate

# setup file, setup debug rerender, and flask run or python fileName.py
> set FLASK_APP=run.py
# Debugger is active!
> set FLASK_DEBUG=1
> python -m flask run
# or
> python run.py

# to open the interpreter
python
>>> import flask
>>> exit()

```

## License

1. Activate virtual env (.venv\Scripts\activate)

2. Go to your project root directory

3. Get all the packages along with dependencies in requirements.txt

```bash
pip freeze > requirements.txt
```

4. You don't have to worry about anything else apart from making sure next person installs the requirements recursively by following command

```bash
pip install -r requirements.txt
```
