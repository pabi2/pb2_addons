# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp.exceptions import except_orm, Warning


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _invoice_budget_check(self):
        AccountBudget = self.env['account.budget']
        for invoice in self:
            if invoice.type != 'in_invoice':
                continue
            # Get fiscal year and budget level for this group
            fiscal_id, budgeting_level = AccountBudget.\
                get_fiscal_and_budgeting_level(invoice.date_invoice)
            # Find amount in this invoice to check against budget
            self._cr.execute("""
                select %(budgeting_level)s,
                coalesce(sum(price_subtotal), 0.0) amount
                from account_invoice_line where invoice_id = %(invoice_id)s
                group by %(budgeting_level)s
            """ % {'budgeting_level': budgeting_level,
                   'invoice_id': invoice.id}
            )
            # Check budget at this budgeting level
            for r in self._cr.dictfetchall():
                res = AccountBudget.check_budget(r['amount'],
                                                 r[budgeting_level],
                                                 fiscal_id,
                                                 budgeting_level)
                if not res['budget_ok']:
                    raise Warning(res['message'])
        return True

    @api.multi
    def action_date_assign(self):
        self._invoice_budget_check()
        return super(AccountInvoice, self).action_date_assign()

    @api.multi
    def action_move_create(self):
        for inv in self:
            for line in inv.invoice_line:
                Analytic = self.env['account.analytic.account']
                line.account_analytic_id = \
                    Analytic.create_matched_analytic(line)
        res = super(AccountInvoice, self).action_move_create()
        return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        required=False,
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        required=False,
    )

    @api.onchange('activity_id')
    def _onchange_activity_id(self):
        self.product_id = False
        self.activity_group_id = self.activity_id.activity_group_id
        self.account_id = self.activity_id.account_id or \
            self.activity_id.activity_group_id.account_id

    @api.multi
    def product_id_change(
            self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False,
            currency_id=False, company_id=None):
        res = super(AccountInvoiceLine, self).product_id_change(
            product, uom_id, qty=qty, name=name, type=type,
            partner_id=partner_id, fposition_id=fposition_id,
            price_unit=price_unit, currency_id=currency_id,
            company_id=company_id)
        res['value'].update({'activity_group_id': False,
                             'activity_id': False, })
        return res
