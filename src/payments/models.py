import json
import logging

import requests.exceptions
from django.conf import settings
from django.utils.translation import gettext as _
from djongo import models

from . import enums

logger = logging.getLogger(__name__)


class Payment(models.Model):
    """
    Represents a payment including request for payment and response of payment
    fields
    """
    # Generic fields
    _id = models.ObjectIdField()

    created_on = models.DateTimeField(auto_now_add=True)

    # Used when requesting payment form IPG
    order_id = models.CharField(max_length=50, unique=True, verbose_name=_('Order ID'))
    amount = models.PositiveBigIntegerField(verbose_name=_('Amount'))

    # Used to store response of IPG
    track_id = models.CharField(unique=True, max_length=50, verbose_name=_('Track ID'), blank=True, null=True)
    request_result_code = models.CharField(
        max_length=4,
        help_text=_('IPG result code in response to our payment request'),
        verbose_name=_('Request Result Code')
    )

    # Used to store result of the payment
    is_successful = models.BooleanField(blank=True, null=True, verbose_name=_('Is successful?'))
    payment_status_code = models.CharField(
        max_length=4,
        help_text=_('IPG payment result code in response to our payment attempt.'),
        verbose_name=_('Payment Status Code'),
        blank=True, null=True
    )

    # Used to store result of the payment verification
    is_verified = models.BooleanField(blank=True, null=True, verbose_name=_('Is verified?'))
    payed_amount = models.PositiveBigIntegerField(verbose_name=_('Verified Payed Amount'), blank=True, null=True)
    verification_status_code = models.CharField(
        max_length=4,
        help_text=_('IPG payment verification result code in response to our payment verification attempt.'),
        verbose_name=_('Payment Verification Status Code'),
        blank=True, null=True
    )
    ref_number = models.CharField(
        max_length=50,
        blank=True, null=True,
        verbose_name=_('Ref. Number')
    )

    objects = models.DjongoManager()

    class Meta:
        ordering = ('-created_on',)

    def __str__(self):
        return f'{self.order_id}'

    def is_successful_and_verified(self) -> bool:
        return all((self.is_successful, self.is_verified))

    def obtain_zibal_track_id(self) -> bool:
        """
        Obtains and stores trackId from Zibal API
        """
        try:
            response = requests.post(
                'https://gateway.zibal.ir/v1/request',
                json={
                    "merchant": "zibal",
                    "amount": self.amount,
                    "callbackUrl": f"{settings.BASE_URL}/payments/callback",
                    "orderId": self.order_id
                }
            )
            decoded_response = response.json()
        except json.JSONDecodeError as e:
            logger.error(f'Invalid response from Zibal API, {e}')
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f'Failed to obtain track_id from Zibal API, {e}')
            return False

        """
        Example of what zibal is supposed to respond with
        {
            "trackId": 15966442233311,
            "result": 100,
            "message": "success"
        }
        """
        try:
            self.track_id = decoded_response['trackId']
            self.request_result_code = decoded_response['result']
            self.save()
            logger.info(f'[Payment #{self.pk}] Successfully obtained track_id from Zibal API.')
            return True
        except KeyError as e:
            logger.error(f'Invalid response from Zibal API, {e}')
            return False

    def get_ipg_redirect_url(self) -> str:
        return f'https://gateway.zibal.ir/start/{self.track_id}'

    def update_from_callback_args(self, callback_dict: dict) -> None:
        self.is_successful = callback_dict['success']
        self.payment_status_code = callback_dict['status']
        self.payment_status_code = callback_dict['status']
        self.save()
        logger.info(f'[Payment #{self.pk}] Updated via callback args.')

    def verify(self) -> bool:
        try:
            response = requests.post(
                'https://gateway.zibal.ir/v1/verify',
                json={
                    "merchant": "zibal",
                    "trackId": self.track_id
                }
            )
            decoded_response = response.json()
        except json.JSONDecodeError as e:
            logger.error(f'Invalid response from Zibal API, {e}')
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f'Failed to obtain track_id from Zibal API, {e}')
            return False

        """
        What we'd expect
        {
            "paidAt": "2018-03-25T23:43:01.053000",
            "amount": 1600,
            "result": 100,
            "status": 1,
            "refNumber": 12312,
            "description": "Hello World!",
            "cardNumber": "62741****44",
            "orderId": "2211",
            "message" : "success"
        }
        """
        self.payed_amount = decoded_response.get('amount', None)
        self.verification_status_code = decoded_response.get('status', None)
        self.ref_number = decoded_response.get('refNumber', None)

        # Verification logic
        c1 = self.payed_amount == self.amount
        c2 = self.verification_status_code == enums.ZibalVerificationResultCode.SUCCESS

        if all((c1, c2)):
            self.is_verified = True
        else:
            self.is_verified = False
        self.save()

        return True
