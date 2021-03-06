from django import forms
from .models import Contact


class MessageForm(forms.ModelForm):

    class Meta:
        model = Contact
        fields = ('message_email', 'message_author',
                  'order_number', 'message_body',)

    message_email = forms.EmailField(label='Your contact email')
    message_author = forms.CharField(label='Name')
    order_number = forms.CharField(label='Order Number (if applicable)',
                                   required=False)
    message_body = forms.CharField(label='How can we help you?',
                                   required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
