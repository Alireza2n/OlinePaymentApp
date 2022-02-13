from django.db import models
from django.utils.translation import gettext as _


class ZibalVerificationResultCode(models.IntegerChoices):
    SUCCESS = 1, _('Success')
