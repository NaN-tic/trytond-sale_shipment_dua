========================================
Sale Shipment Cost and DUA cost Scenario
========================================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import config, Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> today = datetime.date.today()

Install sale_shipment_dua::

    >>> config = activate_modules('sale_shipment_dua')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']

Create tax::

    >>> tax = create_tax(Decimal('.10'))
    >>> tax.save()

Create customer::

    >>> Party = Model.get('party.party')
    >>> customer = Party(name='Customer')
    >>> customer.save()

Create account categories::

    >>> ProductCategory = Model.get('product.category')
    >>> account_category = ProductCategory(name="Account Category")
    >>> account_category.accounting = True
    >>> account_category.account_expense = expense
    >>> account_category.account_revenue = revenue
    >>> account_category.save()

    >>> account_category_tax, = account_category.duplicate()
    >>> account_category_tax.customer_taxes.append(tax)
    >>> account_category_tax.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> template = ProductTemplate()
    >>> template.name = 'product'
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.salable = True
    >>> template.list_price = Decimal('20')
    >>> template.account_category = account_category_tax
    >>> template.save()
    >>> product, = template.products

Create carrier product::

    >>> carrier_template = ProductTemplate()
    >>> carrier_template.name = 'carrier product'
    >>> carrier_template.default_uom = unit
    >>> carrier_template.type = 'service'
    >>> carrier_template.salable = True
    >>> carrier_template.list_price = Decimal('3')
    >>> carrier_template.account_category = account_category_tax
    >>> carrier_template.save()
    >>> carrier_product, = carrier_template.products
    >>> carrier_product.save()

Create carrier DUA product::

    >>> carrier_dua_template = ProductTemplate()
    >>> carrier_dua_template.name = 'DUA carrier product'
    >>> carrier_dua_template.default_uom = unit
    >>> carrier_dua_template.type = 'service'
    >>> carrier_dua_template.salable = True
    >>> carrier_dua_template.list_price = Decimal('3')
    >>> carrier_dua_template.account_category = account_category_tax
    >>> carrier_dua_template.save()
    >>> carrier_dua_product, = carrier_dua_template.products
    >>> carrier_dua_product.save()

Create carrier::

    >>> Carrier = Model.get('carrier')
    >>> carrier = Carrier()
    >>> party = Party(name='Carrier')
    >>> party.save()
    >>> carrier.party = party
    >>> carrier.carrier_product = carrier_product
    >>> carrier.save()

Create carrier with non cost product::

    >>> Carrier = Model.get('carrier')
    >>> carrier_non_cost = Carrier()
    >>> party = Party(name='Carrier Non Cost')
    >>> party.save()
    >>> carrier_non_cost.party = party
    >>> carrier_non_cost.carrier_product = carrier_product
    >>> carrier_non_cost.save()

Create carrier with dua product::

    >>> Carrier = Model.get('carrier')
    >>> carrier_dua_cost = Carrier()
    >>> party = Party(name='Carrier Dua')
    >>> party.save()
    >>> carrier_dua_cost.party = party
    >>> carrier_dua_cost.carrier_product = carrier_product
    >>> carrier_dua_cost.dua = True
    >>> carrier_dua_cost.dua_product = carrier_dua_product
    >>> carrier_dua_cost.save()

Create carrier with dua product and dua price::

    >>> Carrier = Model.get('carrier')
    >>> carrier_dua_cost_price = Carrier()
    >>> party = Party(name='Carrier Dua Price')
    >>> party.save()
    >>> carrier_dua_cost_price.party = party
    >>> carrier_dua_cost_price.carrier_product = carrier_product
    >>> carrier_dua_cost_price.dua = True
    >>> carrier_dua_cost_price.dua_product = carrier_dua_product
    >>> carrier_dua_cost_price.dua_price = Decimal('30')
    >>> carrier_dua_cost_price.save()

Create payment term::

    >>> payment_term = create_payment_term()
    >>> payment_term.save()

Sale products with cost on shipment::

    >>> Sale = Model.get('sale.sale')
    >>> sale = Sale()
    >>> sale.party = customer
    >>> sale.carrier = carrier
    >>> sale.payment_term = payment_term
    >>> sale.invoice_method = 'shipment'
    >>> sale.shipment_cost_method = 'shipment'
    >>> sale_line = sale.lines.new()
    >>> sale_line.product = product
    >>> sale_line.quantity = 5.0
    >>> sale.click('quote')
    >>> cost_line, = [x for x in sale.lines if x.product == carrier_product]
    >>> cost_line.amount
    Decimal('3.00')

Sale products with dua cost on carrier::

    >>> sale = Sale()
    >>> sale.party = customer
    >>> sale.carrier = carrier_dua_cost
    >>> sale.payment_term = payment_term
    >>> sale.invoice_method = 'shipment'
    >>> sale.shipment_cost_method = 'shipment'
    >>> sale_line = sale.lines.new()
    >>> sale_line.product = product
    >>> sale_line.quantity = 5.0
    >>> sale.click('quote')
    >>> cost_line, = [x for x in sale.lines if x.product == carrier_product]
    >>> cost_line.amount
    Decimal('3.00')
    >>> dua_line, = [x for x in sale.lines if x.product == carrier_dua_product]
    >>> dua_line.amount
    Decimal('3.00')

Sale products with dua cost and dua price on carrier::

    >>> sale = Sale()
    >>> sale.party = customer
    >>> sale.carrier = carrier_dua_cost_price
    >>> sale.payment_term = payment_term
    >>> sale.invoice_method = 'shipment'
    >>> sale.shipment_cost_method = 'shipment'
    >>> sale_line = sale.lines.new()
    >>> sale_line.product = product
    >>> sale_line.quantity = 5.0
    >>> sale.click('quote')
    >>> cost_line, = [x for x in sale.lines if x.product == carrier_product]
    >>> cost_line.amount
    Decimal('3.00')
    >>> dua_line, = [x for x in sale.lines if x.product == carrier_dua_product]
    >>> dua_line.amount
    Decimal('30.00')

Duplicate sale::

    >>> sale_copy, = sale.duplicate()
    >>> sale_copy.click('quote')
    >>> sale_copy.total_amount == sale.total_amount
    True
