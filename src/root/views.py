from django.shortcuts import redirect


def redirect_to_checkout(request):
    return redirect('payments:checkout')
