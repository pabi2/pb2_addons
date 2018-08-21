# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, except_orm


class AccountModel(models.Model):
    _inherit = 'account.model'

    special_type = fields.Selection(
        [('invoice_plan', 'Purchase Invoice Plan'),
         ('invoice_plan_fin_lease', 'Purchase Invoice Plan (Fin Lease)')],
        string='Special Type',
        help="With this selection, journal entrires will be created based "
        "on due/draft purchase invoice plan."
    )
    accrual_account_id = fields.Many2one(
        'account.account',
        string='Accrual Account',
        domain=[('type', '!=', 'view')]
    )
    debit_account_id = fields.Many2one(
        'account.account',
        string='Debit Account',
        domain=[('user_type.report_type', 'in', ('asset', 'liability'))],
    )
    credit_account_id = fields.Many2one(
        'account.account',
        string='Credit Account',
        domain=[('user_type.report_type', 'in', ('asset', 'liability'))],
    )
    fin_debit_account_id = fields.Many2one(
        'account.account',
        string='Fin. Debit Account',
        domain=[('user_type.report_type', 'in', ('asset', 'liability'))],
    )
    fin_credit_account_id = fields.Many2one(
        'account.account',
        string='Fin. Credit Account',
        domain=[('user_type.report_type', 'in', ('asset', 'liability'))],
    )

    @api.onchange('special_type')
    def _onchange_special_type(self):
        if self.special_type:
            self.lines_id = []
            self.lines_id = False

    @api.model
    def _prepare_move_line(self, model):
        if model.special_type == 'invoice_plan':  # Case invoice plan
            return self._prepare_move_line_by_invoice_plan(model)
        elif model.special_type == 'invoice_plan_fin_lease':
            return self._prepare_move_line_by_invoice_plan_fin_lease(model)
        else:
            return super(AccountModel, self)._prepare_move_line(model)

    @api.model
    def _prepare_move_line_by_invoice_plan_fin_lease(self, model):
        Period = self.env['account.period']
        Purchase = self.env['purchase.order']
        move_lines = []
        context = self._context.copy()
        date = context.get('date', fields.Date.context_today(self))
        ctx = context.copy()
        period = Period.with_context(ctx).find(date)
        ctx.update({
            'company_id': model.company_id.id,
            'journal_id': model.journal_id.id,
            'period_id': period.id
        })
        purchases = Purchase.search([
            ('order_type', '=', 'purchase_order'),
            ('date_contract_start', '<=', date),
            ('state', '=', 'approved'),
            ('is_fin_lease', '=', True),
        ])
        for purchase in purchases:
            debit_account = model.debit_account_id
            credit_account = model.credit_account_id
            if not debit_account or not credit_account:
                raise except_orm(
                    _('No Account Configured!'),
                    _("Model '%s' has no dr/cr account code defined!") %
                    (model.name,))
            # Currency
            amount_currency = False
            amount = 0.0
            currency_id = False
            po_currency = purchase.currency_id
            company_currency = self.env.user.company_id.currency_id
            if company_currency != po_currency:
                amount_currency = purchase.amount_untaxed
                amount = po_currency.compute(amount_currency,
                                             company_currency)
                currency_id = po_currency.id
            else:
                amount = purchase.amount_untaxed
            # Debit
            val = {
                'journal_id': model.journal_id.id,
                'period_id': period.id,
                'analytic_account_id': False,
                'name': '%s' % (purchase.name,),
                'quantity': False,
                'amount_currency': amount_currency,
                'currency_id': currency_id,
                'debit': amount,
                'credit': False,
                'account_id': debit_account.id,
                'partner_id': purchase.partner_id.id,
                'date': date,
                'date_maturity': date,
            }
            move_lines.append((0, 0, val))
            # Credit Accrual Account
            val2 = val.copy()
            val2.update({
                'analytic_account_id': False,
                'debit': False,
                'credit': amount,
                'account_id': credit_account.id,
                'amount_currency': -amount_currency,
            })
            move_lines.append((0, 0, val2))
        return move_lines

    @api.model
    def _prepare_move_line_by_invoice_plan(self, model):
        Period = self.env['account.period']
        InvoicePlan = self.env['purchase.invoice.plan']
        move_lines = []
        context = self._context.copy()
        date = context.get('date', fields.Date.context_today(self))
        ctx = context.copy()
        period = Period.with_context(ctx).find(date)
        ctx.update({
            'company_id': model.company_id.id,
            'journal_id': model.journal_id.id,
            'period_id': period.id
        })
        invoice_plans = InvoicePlan.search([
            ('ref_invoice_id', '!=', False),
            ('state', '=', 'draft'),
            ('date_invoice', '<', date),
            ('order_id.state', '=', 'approved'),
            ('order_id.order_type', '=', 'purchase_order'),
            ('order_id.is_fin_lease', '=', False),  # For non-fin-lease
        ])
        for line in invoice_plans:
            if line.installment == 0:
                continue
            po_line = line.order_line_id
            analytic_account_id = False
            if po_line.account_analytic_id:
                # kittiu: Can't check, because in pabi, we will have JN
                # if not model.journal_id.analytic_journal_id:
                #     raise except_orm(
                #         _('No Analytic Journal!'),
                #         _("You have to define an analytic journal on the "
                #           "'%s' journal!") % (model.journal_id.name,))
                analytic_account_id = po_line.account_analytic_id.id
            product = po_line.product_id
            account = product.property_account_expense or \
                product.categ_id.property_account_expense_categ or False
            if not account:
                raise except_orm(
                    _('No Product Account!'),
                    _("%s's line product %s, has no account code defined!") %
                    (po_line.order_id.name, product.name,))
            # Currency
            amount_currency = False
            amount = 0.0
            currency_id = False
            po_currency = po_line.order_id.currency_id
            company_currency = self.env.user.company_id.currency_id
            if company_currency != po_currency:
                amount_currency = line.invoice_amount
                amount = po_currency.compute(line.invoice_amount,
                                             company_currency)
                currency_id = po_currency.id
            else:
                amount = line.invoice_amount
            # Debit
            val = {
                'journal_id': model.journal_id.id,
                'period_id': period.id,
                'analytic_account_id': analytic_account_id,
                'name': '%s, #%s' % (line.order_id.name, line.installment),
                'quantity': False,
                'amount_currency': amount_currency,
                'currency_id': currency_id,
                'debit': amount,
                'credit': False,
                'account_id': account.id,
                'partner_id': line.order_id.partner_id.id,
                'date': date,
                'date_maturity': date,
            }
            move_lines.append((0, 0, val))
            # Credit Accrual Account
            val2 = val.copy()
            val2.update({
                'analytic_account_id': False,
                'debit': False,
                'credit': amount,
                'account_id': model.accrual_account_id.id,
                'amount_currency': -amount_currency,
            })
            move_lines.append((0, 0, val2))
        return move_lines


class AccountSubscription(models.Model):
    _inherit = 'account.subscription'

    special_type = fields.Selection(
        [('invoice_plan', 'Purchase Invoice Plan'),
         ('invoice_plan_fin_lease', 'Purchase Invoice Plan (Fin Lease)')],
        string='Special Type',
        related='model_id.special_type',
        help="With this selection, journal entrires will be created based "
        "on due/draft purchase invoice plan."
    )

    @api.multi
    def _validate_model_invoice_plan_type(self, vals):
        if vals.get('model_id', False) or vals.get('type', False):
            for rec in self:
                if rec.model_id.special_type in ('invoice_plan',
                                                 'invoice_plan_fin_lease') \
                        and rec.type != 'standard':
                    raise ValidationError(
                        _('Model "%s" is using invoice plan,\n'
                          'only valid type is "Standard"') %
                        (rec.model_id.name, ))

    @api.multi
    def write(self, vals):
        res = super(AccountSubscription, self).write(vals)
        self._validate_model_invoice_plan_type(vals)
        return res

    @api.model
    def create(self, vals):
        rec = super(AccountSubscription, self).create(vals)
        rec._validate_model_invoice_plan_type(vals)
        return rec
