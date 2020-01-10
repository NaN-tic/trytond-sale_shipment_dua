# This file is part sale_shipment_dua module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval

__all__ = ['Sale', 'SaleLine']


class Sale(metaclass=PoolMeta):
    __name__ = 'sale.sale'

    def set_shipment_cost(self):
        removed = super(Sale, self).set_shipment_cost()

        if self.carrier and self.carrier.dua:
            self.set_dua_cost()
        return removed

    def set_dua_cost(self):
        cost = self.carrier.dua_price or self.carrier.dua_product.list_price
        cost_line = self.get_dua_cost_line(cost)
        lines = list(self.lines or [])
        for line in lines:
            if line.type != 'line' or not getattr(line, 'dua_cost', False):
                continue
            if cost_line and line.dua_cost == cost:
                cost_line = None
            else:
                lines.remove(line)
        if cost_line:
            lines.append(cost_line)
        self.lines = lines

    def get_dua_cost_line(self, cost):
        SaleLine = Pool().get('sale.line')

        sequence = None
        if self.lines:
            last_line = self.lines[-1]
            if last_line.sequence is not None:
                sequence = last_line.sequence + 1
        cost_line = SaleLine(
            sale=self,
            sequence=sequence,
            type='line',
            product=self.carrier.dua_product,
            quantity=1,
            unit=self.carrier.dua_product.sale_uom,
            dua_cost=cost,
            shipment_cost=None
            )
        cost_line.on_change_product()
        cost_line.unit_price = cost_line.amount = cost_line.gross_unit_price = cost
        return cost_line


class SaleLine(metaclass=PoolMeta):
    __name__ = 'sale.line'
    dua_cost = fields.Numeric('Dua Cost',
        digits=(16, Eval('_parent_sale', {}).get('currency_digits', 2)))
