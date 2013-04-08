"""
Forms for editing the users backed by the profile server.
"""
from django import forms
from django.contrib.auth.models import User

from ixprofile_client.webservice import UserWebService


# pylint:disable=E1002
# ModelForm is a new style class
class UserFormBase(forms.ModelForm):
    """
    A form for creating or editing users with hashed email as username and a
    disabled password.
    """

    class Meta:
        """
        Meta options for the user form.
        """
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
        )


# pylint:disable=E1002
# ModelForm is a new style class
class UserCreationForm(UserFormBase):
    """
    User creation form.
    """

    def save(self, commit=True):
        """
        Create the user, registering them on the profile server.
        """
        user = super(UserCreationForm, self).save(commit=False)
        user_ws = UserWebService()
        user_ws.connect(user, commit=False)
        if commit:
            user.save()
        return user


# pylint:disable=E1002
# ModelForm is a new style class
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
        user_ws = UserWebService()
        if user.is_active:
            user_ws.subscribe(user)
        else:
            user_ws.unsubscribe(user)
        if commit:
            user.save()
        return user
