"""
Exceptions raised when interacting with the profile server
"""


class ProfileServerException(Exception):
    """
    Base exception for all profile server errors
    """

    def __init__(self, response=None):
        super(ProfileServerFailure, self).__init__()
        self.response = response
        try:
            self.json = self.response.json()
        except (AttributeError, ValueError):
            pass

    def __str__(self):
        """
        String representation of the exception
        """
        return self.__unicode__()

    def __unicode__(self):
        """
        Unicode representation of the exception
        """
        try:
            return "Profile server failure: %d %s." % (
                self.response.status_code, self.response.reason)
        except (AttributeError, KeyError):
            return "Profile server failure: %s." % self.response


class EmailNotUnique(ProfileServerException):
    """
    An email used in an interaction with the profile server is not unique
    """
    def __init__(self, response, email):
        super(EmailNotUnique, self).__init__(response)
        self.email = email

    def __str__(self):
        """
        String representation of the exception
        """
        return self.__unicode__()

    def __unicode__(self):
        """
        Unicode representation of the exception
        """
        return ("Email %s is not unique on the profile server. "
                "Consider installing the "
                "PrintEmailNotUniqueMessage Middleware." % self.email
                )

    def __repr__(self):
        """
        Unique representation of the exception
        """
        return "EmailNotUnique('%s')" % self.email


ProfileServerFailure = ProfileServerException
