"""
Django command to wait for the database to be available
"""
from typing import Any

import time

from psycopg import OperationalError as PsycopgError

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to wait for database"""

    def handle(self, *args: Any, **options: Any) -> str | None:
        """Entrypoint for command."""
        self.stdout.write("Waiting for database connection...")
        db_up = False

        while db_up is False:
            try:
                self.check(databases=("default",))
                db_up = True
            except (PsycopgError, OperationalError):
                self.stderr.write(self.style.ERROR(
                    "Database unavailable, waiting for 1 second..."
                ))
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Database available!"))
