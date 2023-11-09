# Python Flask Tutorial

Flask is a very lightweight Python Web Framework, easily helping beginners learn Python to create small websites.

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
