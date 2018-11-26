========================================
Sale Shipment Cost and DUA cost Scenario
========================================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import config, Model, Wizard
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> today = datetime.date.today()

Create database::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Install module::

    >>> Module = Model.get('ir.module')
    >>> module, = Module.find([('name', '=', 'sale_shipment_dua')])
    >>> module.click('install')
    >>> Wizard('ir.module.install_upgrade').execute('upgrade')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Reload the context::

    >>> User = Model.get('res.user')
    >>> Group = Model.get('res.group')

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']

Create sale user::

    >>> sale_user = User()
    >>> sale_user.name = 'Sale'
    >>> sale_user.login = 'sale'
    >>> sale_user.main_company = company
    >>> sale_group, = Group.find([('name', '=', 'Sales')])
    >>> sale_user.groups.append(sale_group)
    >>> sale_user.save()

Create customer::

    >>> Party = Model.get('party.party')
    >>> customer = Party(name='Customer')
    >>> customer.save()

Create category::

    >>> ProductCategory = Model.get('product.category')
    >>> category = ProductCategory(name='Category')
    >>> category.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> template = ProductTemplate()
    >>> template.name = 'product'
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.purchasable = True
    >>> template.salable = True
    >>> template.list_price = Decimal('20')
    >>> template.cost_price = Decimal('8')
    >>> template.cost_price_method = 'fixed'
    >>> template.account_expense = expense
    >>> template.account_revenue = revenue
    >>> template.save()
    >>> product, = template.products

Create carrier product::

    >>> carrier_template = ProductTemplate()
    >>> carrier_template.name = 'carrier product'
    >>> carrier_template.category = category
    >>> carrier_template.default_uom = unit
    >>> carrier_template.type = 'service'
    >>> carrier_template.salable = True
    >>> carrier_template.delivery_time = 0
    >>> carrier_template.list_price = Decimal('3')
    >>> carrier_template.cost_price = Decimal(0)
    >>> carrier_template.account_revenue = revenue
    >>> carrier_template.save()
    >>> carrier_product, = carrier_template.products
    >>> carrier_product.save()

Create carrier DUA product::

    >>> carrier_dua_template = ProductTemplate()
    >>> carrier_dua_template.name = 'DUA carrier product'
    >>> carrier_dua_template.category = category
    >>> carrier_dua_template.default_uom = unit
    >>> carrier_dua_template.type = 'service'
    >>> carrier_dua_template.salable = True
    >>> carrier_dua_template.delivery_time = 0
    >>> carrier_dua_template.list_price = Decimal('3')
    >>> carrier_dua_template.cost_price = Decimal(0)
    >>> carrier_dua_template.account_revenue = revenue
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

    >>> config.user = sale_user.id
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
    >>> sale_copy = sale.duplicate()
    >>> sale_copy[0].click('quote')
    >>> sale_copy[0].total_amount == sale.total_amount
    True
