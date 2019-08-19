from decimal import Decimal

from oscar.apps.shipping import methods
from oscar.core import prices


class Standard(methods.FixedPrice):
    code = 'standard'
    name = 'پست'
    charge_incl_tax = Decimal('50000.00')
    charge_excl_tax =  Decimal('50000.00')


class Express(methods.FixedPrice):
    code = 'express'
    name = 'پست پیشتاز'
    charge_incl_tax = Decimal('100000.00')
    charge_excl_tax = Decimal('100000.00')
