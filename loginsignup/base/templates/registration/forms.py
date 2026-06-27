from  django import forms
class ContactForm(forms.Form):
    email = forms.EmailField(label = 'your email')
    