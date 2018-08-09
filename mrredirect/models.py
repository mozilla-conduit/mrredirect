# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from mrredirect.storage import db


class Review(db.Model):
    """Represents a MozReview review."""

    id = db.Column(db.Integer, primary_key=True)
    review_request_id = db.Column(db.Integer)
    bug_id = db.Column(db.Integer)
    bug_comment_id = db.Column(db.Integer)


class ReviewRequest(db.Model):
    """Represents a MozReview review request."""

    id = db.Column(db.Integer, primary_key=True)
    bug_id = db.Column(db.Integer)
    review_repo = db.Column(db.String(128))
    commit_sha = db.Column(db.String(40))
