from django import forms


class ZibalCallBackForm(forms.Form):
    """
    Used to validate and parse zibal callback args
    """
    success = forms.BooleanField()
    status = forms.IntegerField()
    trackId = forms.IntegerField()
    orderId = forms.CharField(max_length=50)
