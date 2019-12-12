"""
A management command to create a user with a given email.
"""
# pylint:disable=redefined-builtin,unused-wildcard-import,wrong-import-position
from __future__ import absolute_import, unicode_literals
from future import standard_library
standard_library.install_aliases()
from future.builtins import *
# pylint:enable=redefined-builtin,unused-wildcard-import

# pylint:disable=redefined-builtin
from builtins import input
# pylint:enable=redefined-builtin

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ixprofile_client.webservice import UserWebService

from optparse import make_option
# pylint:enable=wrong-import-position


class Command(BaseCommand):
    """
    The command to create a superuser with a given email.
    """

    def add_arguments(self, parser):
        """
        Add the arguments for the command.
        """
        parser.add_argument('--email', default=None,
                            help='Specifies the email for the superuser.')
        parser.add_argument('--noinput', action='store_false',
                            dest='interactive',
                            help='Tells Django to NOT prompt the user for '
                                 'input of any kind. You must use --email with '
                                 '--noinput')

    def handle(self, *args, **options):
        interactive = options.get('interactive')
        email = options.get('email')
        verbosity = int(options.get('verbosity', 1))

        if interactive and not email:
            email = input("Email: ")
        if not email:
            raise CommandError("No email given.")

        with transaction.atomic():
            # pylint:disable=no-member
            user, created = User.objects.get_or_create(email=email)
            user.set_password(None)
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True

            user_ws = UserWebService()
            user_ws.connect(user)

            if verbosity >= 1:
                if created:
                    self.stdout.write("Superuser created successfully.")
                else:
                    self.stdout.write("Superuser flag added successfully.")
