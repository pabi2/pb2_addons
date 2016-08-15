# -*- coding: utf-8 -*-
from openerp import api, models, _
from openerp.exceptions import Warning as UserError
from .account_activity import ActivityCommon


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _invoice_budget_check(self):
        AccountBudget = self.env['account.budget']
        for invoice in self:
            if invoice.type != 'in_invoice':
                continue
            # Get budget level type resources
            r = AccountBudget.get_fiscal_and_budget_level(invoice.date_invoice)
            fiscal_id = r['fiscal_id']
            budget_type = 'check_budget'
            if budget_type not in r:
                raise UserError(_('Budget level is not set!'))
            budget_level = r[budget_type]  # specify what to check
            # Find amount in this invoice to check against budget
            self._cr.execute("""
                select %(budget_level)s,
                    coalesce(sum(ail.price_subtotal / cr.rate), 0.0) amount
                from account_invoice_line ail
                join account_invoice ai on ai.id = ail.invoice_id
                -- to base currency
                JOIN res_currency_rate cr ON (cr.currency_id = ai.currency_id)
                    AND
                    cr.id IN (SELECT id
                      FROM res_currency_rate cr2
                      WHERE (cr2.currency_id = ai.currency_id)
                          AND ((ai.date_invoice IS NOT NULL
                                  AND cr2.name <= ai.date_invoice)
                        OR (ai.date_invoice IS NULL AND cr2.name <= NOW()))
                      ORDER BY name DESC LIMIT 1)
                --
                where ai.id = %(invoice_id)s
                group by %(budget_level)s
            """ % {'budget_level': budget_level,
                   'invoice_id': invoice.id}
            )
            # Check budget at this budgeting level
            for r in self._cr.dictfetchall():
                res = AccountBudget.check_budget(fiscal_id,
                                                 budget_type,
                                                 budget_level,
                                                 r[budget_level],
                                                 r['amount'])
                if not res['budget_ok']:
                    raise UserError(res['message'])
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


class AccountInvoiceLine(ActivityCommon, models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def name_get(self):
        result = []
        for line in self:
            result.append(
                (line.id,
                 "%s / %s" % (line.invoice_id.name or '-',
                              line.name or '-')))
        return result
