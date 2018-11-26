# This file is part sale_shipment_dua module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import carrier
from . import sale

def register():
    Pool.register(
        carrier.Carrier,
        sale.Sale,
        sale.SaleLine,
        module='sale_shipment_dua', type_='model')
