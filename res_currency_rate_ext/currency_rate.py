# -*- coding: utf-8 -*-
import time
from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class ResCurrency(models.Model):
    _inherit = "res.currency"

    @api.one
    def _current_rate_input(self):
        self.rate_input = self._get_current_rate_input()[0]

    @api.one
    def _current_rate_input_silent(self):
        self.rate_input_silent = \
            self._get_current_rate_input(raise_on_no_rate=False)[0]

    @api.one
    def _get_current_rate_input(self, raise_on_no_rate=True):
        date = self._context.get('date') or time.strftime('%Y-%m-%d')
        self._cr.execute('SELECT rate_input FROM res_currency_rate '
                         'WHERE currency_id = %s '
                         'AND name <= %s '
                         'ORDER BY name desc LIMIT 1',
                         (self.id, date))
        if self._cr.rowcount:
            return self._cr.fetchone()[0]
        elif not raise_on_no_rate:
            return 0
        else:
            raise except_orm(
                _('Error!'),
                _("No currency rate associated for currency '%s' "
                  "for the given period" % (self.name)))
        return False

    type = fields.Selection([
        ('smaller', 'Smaller than base currency'),
        ('bigger', 'Bigger than base currency'), ],
        string='Type',
        default='smaller',
        required=True,
    )
    rate = fields.Float(
        digis=(12, 12),
    )
    rate_silent = fields.Float(
        digis=(12, 12),
    )
    rate_input = fields.Float(
        string='Current Rate',
        digits=(12, 6),
        compute='_current_rate_input',
    )
    rate_input_silent = fields.Float(
        string='Current Rate',
        digits=(12, 6),
        compute='_current_rate_input_silent',
    )

    @api.onchange('base')
    def _onchange_base(self):
        if self.base:
            self.type = 'bigger'


class ResCurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    def init(self, cr):
        cr.execute('update res_currency_rate set rate_input = rate '
                   'where rate_input is null')

    @api.one
    @api.depends('currency_id.type', 'rate_input')
    def _compute_rate(self):
        if not self.rate_input:
            raise except_orm(
                _('Configuration Error!'),
                _("Rate cannot be zero!"))
        if self.currency_id.type == 'smaller':
            self.rate = self.rate_input
        else:
            self.rate = 1 / self.rate_input

    rate = fields.Float(
        string='Rate',
        digits=(12, 12),
        compute='_compute_rate',
        store=True,
        help='The rate of the currency to the currency of rate 1',
    )
    rate_input = fields.Float(
        string='Rate',
        digits=(12, 6),
        default=1.0,
        help='The rate of the currency to the currency of rate 1. '
        'This value will be used together with Type',
    )
