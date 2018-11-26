# This file is part sale_shipment_dua module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import unittest
import doctest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase
from trytond.tests.test_tryton import doctest_setup, doctest_teardown


class SaleShipmentDuaTestCase(ModuleTestCase):
    'Test Sale Shipment Dua module'
    module = 'sale_shipment_dua'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            SaleShipmentDuaTestCase))
    suite.addTests(doctest.DocFileSuite('scenario_sale_shipment_dua.rst',
            setUp=doctest_setup, tearDown=doctest_teardown, encoding='utf-8',
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE))
    return suite
