# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from setuptools import find_packages, setup

setup(
    name="mrredirect",
    version="1.0",
    description="Redirect service for old MozReview URLs.",
    author="Mozilla",
    license="MPL 2.0",
    packages=find_packages(exclude=["docs", "tests"]),
    install_requires=[
        "Flask",
        "SQLAlchemy",
        "flask-sqlalchemy",
    ],
    extras_require={},
    entry_points={
        "console_scripts": [
            "mr-redirect-dev = mrredirect.app:development_server",
            "dbinit = mrredirect.dbinit:dbinit",
        ]
    },
)
