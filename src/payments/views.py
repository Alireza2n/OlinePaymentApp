from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext as _
from . import models, utils, forms


def checkout_view(request):
    cxt = {}

    return render(request, template_name='payments/checkout.html', context=cxt)


def prepare_payment_view(request):
    cxt = {}
    # Get trackId from Ziba
    payment_obj = models.Payment.objects.create(
        amount=10000,
        order_id=utils.generate_a_random_string()
    )
    payment_obj.obtain_zibal_track_id()
    cxt.update({
        'object': payment_obj
    })
    return render(request, template_name='payments/prepare.html', context=cxt)


def payment_callback_view(request):
    cxt = {}
    template_name = 'payments/callback.html'
    form = forms.ZibalCallBackForm(data=request.GET)

    # What if args are not valid?
    if not form.is_valid():
        cxt.update({
            'error': _('Invalid callback args.')
        })
        return render(request, template_name, context=cxt)

    # Get payment obj via order_id
    payment_obj = get_object_or_404(models.Payment, order_id=form.cleaned_data['orderId'])
    payment_obj.update_from_callback_args(form.cleaned_data)
    payment_obj.verify()

    cxt.update({
        'object': payment_obj
    })
    return render(request, template_name, context=cxt)
