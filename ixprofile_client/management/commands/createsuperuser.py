"""
A management command to create a user with a given email.
"""

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from ixprofile_client.webservice import UserWebService

from optparse import make_option


class Command(BaseCommand):
    """
    The command to create a superuser with a given email.
    """

    option_list = BaseCommand.option_list + (
        make_option('--email', default=None,
                    help='Specifies the email for the superuser.'),
        make_option('--noinput',
                    action='store_false',
                    dest='interactive',
                    default=True,
                    help='Tells Django to NOT prompt the user for input of ' +
                         'any kind. You must use --email with --noinput.'),
    )

    def handle(self, *args, **options):
        interactive = options.get('interactive')
        email = options.get('email')
        verbosity = int(options.get('verbosity', 1))

        if interactive and not email:
            email = raw_input("Email: ")
        if not email:
            raise CommandError("No email given.")

        user = User()
        user.email = email
        user.set_password(None)
        user.is_superuser = True

        user_ws = UserWebService()
        user_ws.connect(user)

        if verbosity >= 1:
            self.stdout.write("Superuser created successfully.")
