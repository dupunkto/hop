from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

from models import db


MIGRATIONS = []


def run_migrations():
    for statement in MIGRATIONS:
        try:
            db.session.execute(text(statement))
            db.session.commit()
        except (OperationalError, ProgrammingError):
            db.session.rollback()
