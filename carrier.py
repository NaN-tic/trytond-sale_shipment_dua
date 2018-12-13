# This file is part sale_shipment_dua module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.model import fields
from trytond.pyson import Eval
from trytond.modules.product import price_digits

__all__ = ['Carrier']


class Carrier(metaclass=PoolMeta):
    __name__ = 'carrier'
    dua = fields.Boolean('DUA')
    dua_product = fields.Many2One('product.product', 'DUA Product',
        domain=[
            ('salable', '=', True),
            ('type', '=', 'service'),
        ], states={
            'invisible': ~Eval('dua', False),
            'required': Eval('dua', False),
            },
        depends=['dua'])
    dua_price = fields.Numeric('DUA Price', digits=price_digits,
        states={
            'invisible': ~Eval('dua', False),
            },
        depends=['dua'])
