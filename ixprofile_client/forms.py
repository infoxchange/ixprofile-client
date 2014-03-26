"""
Forms for editing the users backed by the profile server.
"""
from django import forms
from django.contrib.auth.models import User

from ixprofile_client.webservice import UserWebService

# pylint:disable=super-on-old-class
# Forms are new style classes


class UserFormBase(forms.ModelForm):
    """
    A form for creating or editing users with hashed email as username and a
    disabled password.
    """

    def __init__(self, *args, **kwargs):
        super(UserFormBase, self).__init__(*args, **kwargs)
        self.user_ws = UserWebService()

    class Meta(object):
        """
        Meta options for the user form.
        """
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
        )


class UserCreationForm(UserFormBase):
    """
    User creation form.
    """

    def save(self, commit=True):
        """
        Create the user, registering them on the profile server.
        """
        user = super(UserCreationForm, self).save(commit=False)
        self.user_ws.connect(user, commit=False)
        if commit:
            user.save()
        return user


class UserChangeForm(UserFormBase):
    """
    User edit form.
    """

    is_active = forms.BooleanField(required=False)

    def save(self, commit=True):
        """
        Save the user, subscribing or unsubscribing them from the applicaion
        on the profile server as needed.
        """
        user = super(UserChangeForm, self).save(commit=False)
        if user.is_active:
            self.user_ws.subscribe(user)
        else:
            self.user_ws.unsubscribe(user)
        if commit:
            user.save()
        return user
