# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields
from openerp.addons.l10n_th_account.models.res_partner \
    import INCOME_TAX_FORM


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    pnd_form_line = fields.One2many(
        'report.pnd.form',
        'voucher_id',
        string='PND Form Lines',
        readonly=True,
    )


class ReportPNDForm(models.Model):
    _name = 'report.pnd.form'
    _description = 'PND Forms'
    _auto = False

    voucher_id = fields.Many2one(
        'account.voucher',
        string='Voucher',
    )
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
    tax_percent = fields.Float(
        string='Tax Percent',
    )
    wht_cert_income_type = fields.Char(
        string='Type of Income',
    )
    wht_cert_income_desc = fields.Char(
        string='Income Description',
    )
    base = fields.Float(
        string='Base',
    )
    tax = fields.Float(
        string='Tax',
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            select min(avt.id) id, avt.voucher_id,
                av.income_tax_form, av.wht_period_id, av.partner_id,
                av.date_value, at.amount * 100 as tax_percent,
                avt.wht_cert_income_type, avt.wht_cert_income_desc,
                -sum(avt.base) as base, -sum(avt.amount) as tax
            from account_voucher av join account_voucher_tax avt
                on avt.voucher_id = av.id and tax_code_type = 'wht'
            join account_tax at on at.id = avt.tax_id
            where av.wht_sequence > 0
            group by av.wht_period_id, av.income_tax_form, avt.voucher_id,
                av.partner_id, av.date_value, avt.wht_cert_income_type,
                avt.wht_cert_income_desc, at.amount
        )""" % (self._table, ))
