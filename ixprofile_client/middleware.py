"""
Middleware specific to ixprofile_client
"""

from ixprofile_client.exceptions import EmailNotUnique
from django.conf import settings
from django.http import HttpResponse


class PrintEmailNotUniqueMessage(object):
    """
    Middleware class which prints a message if
    EmailNotUnique is raised and
    bubbles up from the application.
    """
    def process_exception(self, request, exception):
        """
        Prints the message for the EmailNotUnique Error.
        Return HttpResponse prevents any other middleware in
        the chain from running.
        """
        if isinstance(exception, EmailNotUnique) and not settings.DEBUG:
            return HttpResponse('Could not log in. There is more than account '
                                'with this email address! Please contact '
                                'Infoxchange to resolve this issue.'
                                )