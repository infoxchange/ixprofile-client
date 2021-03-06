"""
Forms for editing the users backed by the profile server.
"""
from django import forms
from django.contrib.auth.models import User

from ixprofile_client import webservice

# Forms are new style classes


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


class UserCreationForm(UserFormBase):
    """
    User creation form.
    """

    def clean_email(self):
        """
        Validate that the email is not already registered
        """
        # pylint:disable=no-member
        email = self.cleaned_data['email']
        users = User.objects.filter(email__iexact=email)

        if users.exists():
            raise forms.ValidationError(
                "Email is already registered to user %(username)s",
                params={'username': users.first().get_full_name()}
            )

        return email

    def save(self, commit=True):
        """
        Create the user, registering them on the profile server.
        """
        user = super(UserCreationForm, self).save(commit=False)
        webservice.profile_server.connect(user, commit=False)
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
            webservice.profile_server.subscribe(user)
        else:
            webservice.profile_server.unsubscribe(user)
        if commit:
            user.save()
        return user
