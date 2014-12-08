"""
Middleware specific to ixprofile_client
"""

from ixprofile_client.exceptions import EmailNotUnique
from django.template.response import SimpleTemplateResponse


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
        If you wish to do something other than display this message,
        you can catch EmailNotUnique before process_exception() is
        invoked.
        """
        if isinstance(exception, EmailNotUnique):
            return SimpleTemplateResponse('email_not_unique.html')
