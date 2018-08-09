A simple service to redirect old MozReview links.

To install locally, create and activate a virtualenv, then run `pip
install -r requirements.txt` and then `pip install -e .`.

Set the environment variable `DATABASE_URL` to a valid SQLAlchemy
database URL, e.g., `file:////<path>/mrdirect.sqlite`.  You will also
likely want to set `FLASK_ENV` to `development` or the app will
attempt to redirect you to an https local URL.

Create the database by running `python mrdirect/dbinit.py`.  Run
`mr-redirect-dev` for a local development server.
