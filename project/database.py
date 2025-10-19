# =============================================================================
#                        Project Oasis - Database
#
# This file initializes the SQLAlchemy database object.
# By keeping it separate, we can import this `db` object into our models
# and our main app without creating circular import errors.
#
# =============================================================================

from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy instance. This object will be the primary way we
# interact with the database.
db = SQLAlchemy()