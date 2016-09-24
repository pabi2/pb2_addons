# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields
from openerp.addons.l10n_th_account.models.res_partner \
    import INCOME_TAX_FORM


class ReportPNDForm(models.Model):
    _name = 'report.pnd.form'
    _description = 'PND Forms'
    _auto = False

    income_tax_form = fields.Selection(
        INCOME_TAX_FORM,
        string='Income Tax Form',
    )
    wht_period_id = fields.Many2one(
        'account.period',
        string='Period',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
    )
    date_value = fields.Date(
        string='Value Date',
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            select id, income_tax_form, wht_period_id,
                partner_id, date_value
            from account_voucher
            where wht_sequence > 0
        )""" % (self._table, ))
