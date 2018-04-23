# -*- coding: utf-8 -*-
import logging
from datetime import datetime, time
from dateutil.relativedelta import relativedelta

from openerp import fields, models, api, _
from openerp.exceptions import Warning as UserError

from ..services.currency_getter import CurrencyGetterFactoryTHB
import openerp.addons.currency_rate_update.\
    model.currency_rate_update as currency_rate_update

from openerp.api import Environment
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)

_intervalTypes = {
    'days': lambda interval: relativedelta(days=interval),
    'weeks': lambda interval: relativedelta(days=7 * interval),
    'months': lambda interval: relativedelta(months=interval),
}


THB_BOT_supported_currency_array = [
    'USD', 'GBP', 'EUR', 'JPY', 'HKD', 'MYR', 'SGD', 'BND', 'PHP',
    'IDR', 'INR', 'CHF', 'AUD', 'NZD', 'CAD', 'SEK', 'DKK', 'NOK',
    'CNY', 'LKR', 'IQD', 'BHD', 'OMR', 'JOD', 'QAR', 'MVR', 'NPR',
    'PGK', 'ILS', 'HUF', 'PKR', 'MXN', 'ZAR', 'MMK', 'KRW', 'TWD',
    'KWD', 'SAR', 'AED', 'BDT', 'CZK', 'KHR', 'KES', 'LAK', 'RUB',
    'VND', 'EGP', 'PLN',
]

currency_rate_update.supported_currecies['THB_getter'] =\
    THB_BOT_supported_currency_array


class CurrencyRateUpdateService(models.Model):
    """Class keep services and currencies that
    have to be updated"""
    _inherit = "currency.rate.update.service"

    service = fields.Selection(
        selection_add=([
            ('THB_getter', 'Bank of Thailand: Daily Foreign Exchange Rates')
        ])
    )

    # Using TH exchange rate, webservice show other currency as bigger rate
    def init(self, cr):
        env = Environment(cr, SUPERUSER_ID, {})
        env['res.currency'].search([]).write({'type': 'bigger'})

    @api.one
    def refresh_currency(self):
        """Refresh the currencies rates !!for all companies now"""
        _logger.info(
            'Starting to refresh currencies with service %s (company: %s)',
            self.service, self.company_id.name)

        curr_obj = self.env['res.currency']
        rate_obj = self.env['res.currency.rate']
        company = self.company_id
        # The multi company currency can be set or no so we handle
        # The two case
        if company.auto_currency_up:
            main_currency = curr_obj.search(
                [('base', '=', True), ('company_id', '=', company.id)],
                limit=1)
            if not main_currency:
                main_currency = curr_obj.search(
                    [('base', '=', True)], limit=1)
            if main_currency.name != 'THB':
                return super(CurrencyRateUpdateService,
                             self).refresh_currency()
            if not main_currency:
                raise UserError(_('There is no base currency set!'))
            if main_currency.rate != 1:
                raise UserError(_('Base currency rate should be 1.00!'))
            note = self.note or ''
            try:
                # We initalize the class that will handle the request
                # and return a dict of rate
                factory = CurrencyGetterFactoryTHB()
                getter = factory.register(self.service)
                curr_to_fetch = map(lambda x: x.name,
                                    self.currency_to_update)
                res, log_info = getter.get_updated_currency(
                    curr_to_fetch,
                    main_currency.name,
                    self.max_delta_days
                )
                rate_name = \
                    fields.Datetime.to_string(datetime.utcnow().replace(
                        hour=0, minute=0, second=0, microsecond=0))
                for curr in self.currency_to_update:
                    if curr.id == main_currency.id:
                        continue
                    do_create = True
                    for rate in curr.rate_ids:
                        if rate.name == rate_name:
                            rate.rate = res[curr.name]
                            do_create = False
                            break
                    if do_create:
                        vals = {
                            'currency_id': curr.id,
                            'rate_input': res[curr.name],  # with Currency Ext
                            'name': rate_name
                        }
                        rate_obj.create(vals)
                        _logger.info(
                            'Updated currency %s via service %s',
                            curr.name, self.service)

                # Show the most recent note at the top
                msg = '%s \n%s currency updated. %s' % (
                    log_info or '',
                    fields.Datetime.to_string(datetime.today()),
                    note
                )
                self.write({'note': msg})
            except Exception as exc:
                error_msg = '\n%s ERROR : %s %s' % (
                    fields.Datetime.to_string(datetime.today()),
                    repr(exc),
                    note
                )
                _logger.error(repr(exc))
                self.write({'note': error_msg})
            if self._context.get('cron', False):
                midnight = time(0, 0)
                next_run = (datetime.combine(
                            fields.Date.from_string(self.next_run),
                            midnight) +
                            _intervalTypes[str(self.interval_type)]
                            (self.interval_number)).date()
                self.next_run = next_run
