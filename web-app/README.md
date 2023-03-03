## Screenshot
![screenshot](./static/images/Screenshot.png)



## Run the Web App

- cd to the current directory
  - `cd web-app`
- Create virtual environment
  - `python -m venv .venv`
- Activate virtual environment
  - windows: `.venv\Scripts\activate.bat`
  - mac: `source .venv/bin/activate`
- Install packages: `pip install -r requirements.txt`.
- define two environment variables from the command line:
  - on Mac, use the commands: `export FLASK_APP=app.py` and `export FLASK_ENV=development`.
  - on Windows, use `set FLASK_APP=app.py` and `set FLASK_ENV=development`.
- start flask with `flask run` - this will output an address at which the app is running locally, e.g. https://127.0.0.1:5000. Visit that address in a web browser.
