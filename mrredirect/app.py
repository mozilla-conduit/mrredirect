# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import os
from pathlib import Path

from flask import Flask, abort, redirect, render_template
from flask_talisman import Talisman

from mrredirect.models import Review, ReviewRequest
from mrredirect.storage import db

REDIRECT_CODE = 302
HG_URL = "https://hg.mozilla.org/mozreview/"
BMO_URL = "https://bugzilla.mozilla.org/"

app = Flask(__name__)
Talisman(app)

DB_FILE = Path(__file__).resolve().parent.parent / "mrredirect.sqlite"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_FILE}"
print(app.config["SQLALCHEMY_DATABASE_URI"])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/r/<int:review_request_id>/diff/", defaults={"diff_id": 1})
@app.route("/r/<int:review_request_id>/diff/<int:diff_id>/")
def review_request_diff(review_request_id, diff_id):
    """Redirect diffs to the review-repo archive.

    'diff_id' is not actually used, as it is difficult to determine commits
    for anything but the latest diff.  We capture it anyway as it is
    (arguably) better to redirect old diffs to the most recent commit than to
    not redirect them at all.
    """
    review_request = ReviewRequest.query.get(review_request_id)

    if not review_request:
        abort(404)

    if not review_request.commit_sha:
        return render_template(
            "squashed.html", bmo_url=BMO_URL, bug_id=review_request.bug_id
        )

    return redirect(
        f"{HG_URL}{review_request.review_repo}/rev/" f"{review_request.commit_sha}",
        code=REDIRECT_CODE,
    )


@app.route("/r/<int:review_request_id>/")
def review_request(review_request_id):
    """Redirect review requests and reviews to Bugzilla.

    The database has a mapping of review requests to bugs and
    reviews to specific bug comments.  However, like bug comments, reviews
    are identified in the URL by a fragment, which does not get sent to the
    server.  To avoid repeated server calls, we put review -> comment mapping
    into a template and use JavaScript to redirect.
    """
    review_request = ReviewRequest.query.get(review_request_id)

    if not review_request:
        abort(404)

    reviews = Review.query.filter_by(review_request_id=review_request_id).all()

    review_comments = [(r.id, r.bug_comment_id) for r in reviews]
    return render_template(
        "review_redirect.html",
        bmo_url=BMO_URL,
        bug_id=review_request.bug_id,
        review_comments=review_comments,
    )


def development_server():
    app.run(host="0.0.0.0", port=8888)
