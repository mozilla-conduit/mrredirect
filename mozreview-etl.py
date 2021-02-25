# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""ETL for MozReview redirect data.

This script extracts data from a MozReview/Review Board database and creates
a new table that can be used in the mr-redirect service.

Steps:
1. Install the mysql-connector-python Python package.
2. Import the MozReview/Review Board database into a MySQL server.
3. Adjust the "Database name and credentials" below as appropriate.
4. Run the script.  It will take several minutes to complete.

After it finishes, you will see a summary of the process.  Note that
some failures are expected due to the presence of various corrupted
review requests over the years.  To use the resulting table, run
"mysqldump -u mozreview -p mozreview review_request >
review_request.sql", replacing the database and user name if needed.
As the production instance of mr-redirect runs on Heroku and uses a
PostGreSQL database, you will need to lightly edit the database dump
file (review_request.sql): Remove the DELETE, CREATE, LOCK, and UNLOCK
statements (and the comments if desired).  Then replace all backticks
(`) with double quotes (").  Then you shoudl be able to pipe the file
into psql.
"""

import json

import mysql.connector

# Database name and credentials.
DATABASE = "mozreview"
USER = "mozreview"
PASSWORD = "mozreview"


TABLES = {}
TABLES[
    "review_request"
] = """
CREATE TABLE review_request (
        id INTEGER NOT NULL,
        bug_id INTEGER,
        review_repo VARCHAR(128),
        commit_sha VARCHAR(40),
        PRIMARY KEY (id)
) ENGINE=InnoDB
"""

cnx = mysql.connector.connect(
    user=USER, password=PASSWORD, host="127.0.0.1", database=DATABASE
)
cursor = cnx.cursor()

for name, ddl in TABLES.items():
    print(f"Creating table {name}: ", end="")
    try:
        cursor.execute(ddl)
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("ok")

select_query = """
SELECT
    mozreview_commitdata.review_request_id,
    mozreview_commitdata.extra_data,
    scmtools_repository.name,
    reviews_reviewrequest.bugs_closed
FROM
    mozreview_commitdata
INNER JOIN
     reviews_reviewrequest
     ON mozreview_commitdata.review_request_id = reviews_reviewrequest.id
INNER JOIN
      scmtools_repository
      ON reviews_reviewrequest.repository_id = scmtools_repository.id
"""

cursor.execute(select_query)
success = 0
failure = 0
exists = 0

insert_query = """
INSERT INTO review_request
(id, bug_id, review_repo, commit_sha)
VALUES (%s, %s, %s, %s)
"""

for rr_id, extra_data_str, repo_name, bugs_closed in cursor.fetchall():
    try:
        bug_id = int(bugs_closed)
    except ValueError:
        print(f"review request {rr_id} has a bad bug ID: {bugs_closed}")
        continue

    extra_data = json.loads(extra_data_str)

    try:
        insert_data = (
            rr_id,
            bug_id,
            repo_name,
            extra_data.get("p2rb.commit_id"),
        )

        try:
            cursor.execute(insert_query, insert_data)
            cnx.commit()
        except mysql.connector.errors.IntegrityError as e:
            if e.errno == 1062:
                print(f"Review request {rr_id} already exists in table.")
                exists += 1
            else:
                raise
        print(f"Inserted data for review request {rr_id}.")
    except KeyError as e:
        print(f"review request {rr_id} is corrupt: missing key {e}")
        failure += 1
    else:
        success += 1

print(
    f"Operation completed with {success} review requests successfully "
    f"imported, {failure} failures, and {exists} previously added."
)

cursor.close()
cnx.close()
