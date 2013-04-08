"""
Exceptions raised when interacting with the profile server.
"""


class ProfileServerException(Exception):
    """
    Base exception for all profile server errors.
    """
    pass


class EmailNotUnique(ProfileServerException):
    """
    An email used in an interaction with the profile server is not unique.
    """
    def __init__(self, email):
        super(EmailNotUnique, self).__init__()
        self.email = email

    def __str__(self):
        "String representation of the exception."
        return self.__unicode__()

    def __unicode__(self):
        "Unicode representation of the exception."
        return "Email %s is not unique on the profile server." % self.email

    def __repr__(self):
        "Unique representation of the exception."
        return "EmailNotUnique('%s')" % self.email
