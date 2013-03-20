"""
Forms for editing the users backed by the profile server.
"""
from django import forms
from django.contrib.auth.models import User

from ixprofile_client.models import hash_email
from ixprofile_client.webservice import UserWebService


# pylint:disable=E1002,W0232
# ModelForm is a new style class
class UserFormBase(forms.ModelForm):
    """
    A form for creating or editing users with hashed email as username and a
    disabled password.
    """

    # pylint:disable=W0232,R0903
    # Meta doesn't need __init__ or other methods
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

    def save(self, commit=True):
        """
        Save the user, setting the username to a hash of email.
        """
        user = super(UserFormBase, self).save(commit=False)
        user.username = hash_email(user.email)
        if commit:
            user.save()
        return user


# pylint:disable=E1002,W0232
# ModelForm is a new style class
class UserCreationForm(UserFormBase):
    """
    User creation form.
    """

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
        help_text="Enter the same password as above, for verification."
    )

    def clean_password2(self):
        """
        Verify that the entered passwords match.
        """
        # pylint:disable=E1101
        # form has cleaned_data
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                "The two password fields didn't match.")
        return password2

    def save(self, commit=True):
        """
        Create the user, registering them on the profile server.
        """
        user = super(UserCreationForm, self).save(commit=False)
        if user.username == "":
            raise Exception("Why no username?!")
        user.set_password(None)
        user_ws = UserWebService()
        details = user_ws.details(user.email)
        if details is None:
            # pylint:disable=E1101
            # form has cleaned_data
            password = self.cleaned_data['password1']
            user_ws.register(user, password)
        else:
            user.first_name = details['first_name']
            user.last_name = details['last_name']
        if commit:
            user.save()
        return user


# pylint:disable=E1002,W0232
# ModelForm is a new style class
# pylint:disable=R0903
# Too few public methods - part of the API
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
