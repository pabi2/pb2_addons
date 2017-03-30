# -*- coding: utf-8 -*-
import time
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError, except_orm


class AccountModel(models.Model):
    _inherit = 'account.model'

    use_purchase_invoice_plan = fields.Boolean(
        string='Use Purchase Invoice Plan',
        default=False,
        help="With this selection, journal entrires will be created based "
        "on due/draft purchase invoice plan."
    )
    accrual_account_id = fields.Many2one(
        'account.account',
        string='Accrual Account',
    )

    @api.onchange('use_purchase_invoice_plan')
    def _onchange_use_purchase_invoice_plan(self):
        if self.use_purchase_invoice_plan:
            self.lines_id = []
            self.lines_id = False

    @api.multi
    def generate(self, data=None):
        move_ids = []
        # For recurring by invoice plan, it require different way
        inv_models = self.filtered('use_purchase_invoice_plan')
        move_ids += inv_models._generate_by_inovice_plan(data)
        # Normal models
        models = self - inv_models
        move_ids += super(AccountModel, models).generate(data)
        return move_ids

    @api.multi
    def _generate_by_inovice_plan(self, data=None):
        """ Gnerate Journal Entries based on Purchase invoice Plan data """
        if data is None:
            data = {}
        move_ids = []
        AccountMove = self.env['account.move']
        context = self._context.copy()
        if data.get('date', False):
            context.update({'date': data['date']})
        for model in self:
            # Move
            move_dict = self.with_context(context)._prepare_move(model)
            move = AccountMove.create(move_dict)
            move_ids.append(move.id)
            # Lines
            move_lines = self.with_context(
                context)._prepare_move_line_by_invoice_plan(model)
            move.write({'line_id': move_lines})
        return move_ids

    @api.model
    def _prepare_move_line_by_invoice_plan(self, model):
        Period = self.env['account.period']
        InvoicePlan = self.env['purchase.invoice.plan']
        move_lines = []
        context = self._context.copy()
        date = context.get('date', False)
        ctx = context.copy()
        period = Period.with_context(ctx).find(date)
        ctx.update({
            'company_id': model.company_id.id,
            'journal_id': model.journal_id.id,
            'period_id': period.id
        })
        invoice_plans = InvoicePlan.search([('ref_invoice_id', '!=', False),
                                            ('state', '=', 'draft'),
                                            ('date_invoice', '<', date)])
        for line in invoice_plans:
            if line.installment == 0:
                continue
            po_line = line.order_line_id
            analytic_account_id = False
            if po_line.account_analytic_id:
                if not model.journal_id.analytic_journal_id:
                    raise except_orm(
                        _('No Analytic Journal!'),
                        _("You have to define an analytic journal on the "
                          "'%s' journal!") % (model.journal_id.name,))
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
                po_currency = po_currency.with_context(
                    date=date or fields.Date.context_today(self))
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
                'date': context.get('date', fields.Date.context_today(self)),
                'date_maturity': context.get('date', time.strftime('%Y-%m-%d'))
            }
            move_lines.append((0, 0, val))
            # Credit Accrual Account
            val2 = val.copy()
            val2.update({
                'analytic_account_id': False,
                'debit': False,
                'credit': line.invoice_amount,
                'account_id': model.accrual_account_id.id,
                'amount_currency': -amount_currency,
            })
            move_lines.append((0, 0, val2))
        return move_lines


class AccountSubscription(models.Model):
    _inherit = 'account.subscription'

    @api.multi
    def _validate_model_invoice_plan_type(self, vals):
        if vals.get('model_id', False) or vals.get('type', False):
            for rec in self:
                if rec.model_id.use_purchase_invoice_plan and \
                        rec.type != 'standard':
                    raise UserError(
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
