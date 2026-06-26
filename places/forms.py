from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = [
            "name",
            "email",
            "country",
            "suggested_location",
            "message",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Your name",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Your email address (optional)",
            }),
            "country": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Your country (optional)",
            }),
            "suggested_location": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Suggested location in Hiroshima (optional)",
            }),
            "message": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 6,
                "placeholder": "Please write your message or suggestion here.",
            }),
        }

        labels = {
            "name": "Name",
            "email": "Email",
            "country": "Country",
            "suggested_location": "Suggested Location",
            "message": "Message",
        }