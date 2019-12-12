"""
Middleware specific to ixprofile_client
"""
from __future__ import absolute_import, unicode_literals

from django.template.response import SimpleTemplateResponse
from django.utils.deprecation import MiddlewareMixin

from .exceptions import EmailNotUnique


class PrintEmailNotUniqueMessage(MiddlewareMixin):
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
