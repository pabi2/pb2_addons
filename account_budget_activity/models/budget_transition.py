# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class BudgetTransition(models.Model):
    _name = 'budget.transition'
    _description = 'Keep tranck of budget transition from one model to another'

    expense_line_id = fields.Many2one(
        'hr.expense.line',
        string='Expense Line',
        index=True,
    )
    invoice_line_id = fields.Many2one(
        'account.invoice.line',
        string='Invoice Line',
        index=True,
    )
    quantity = fields.Float(
        string='Quantity',
    )
    forward = fields.Boolean(
        string='Forward',
        default=False,
        help="True, when the end document trigger budget transition, "
        "it is time to return budget commitment."
    )
    backward = fields.Boolean(
        string='Backward',
        default=False,
        help="True, when the end document that forwarded, has been cancelled, "
        "it is time to regain budget commitment."
    )

    @api.multi
    def write(self, vals):
        if not self._context.get('trigger', False):
            raise ValidationError(
                _('Budget Transition without source document!'))
        # Case Forward
        if 'forward' in vals and vals.get('forward', False):
            # Invoice
            if self._context.get('trigger') == 'account.invoice':
                for tran in self:
                    # Return Expense Commitment
                    if tran.expense_line_id:
                        tran.expense_line_id.\
                            with_context(diff_invoiced_qty=tran.quantity).\
                            _create_analytic_line(reverse=False)
                    # Return PO Commitment
                    # TODO:
        # Case Backward
        if 'backward' in vals and vals.get('backward', False):
            # Invoice
            if self._context.get('trigger') == 'account.invoice':
                for tran in self:
                    # Return Expense Commitment
                    if tran.expense_line_id:
                        if tran.forward:  # Was forward before, else nothing
                            tran.expense_line_id.\
                                with_context(diff_invoiced_qty=tran.quantity).\
                                _create_analytic_line(reverse=True)
                    # Return PO Commitment
                    # TODO:

        return super(BudgetTransition, self).write(vals)

    @api.model
    def create_budget_transition(self, source_line, field_name,
                                 source_qty_field, target_qty_field,
                                 trans_source_field, trans_target_field):
        trans_ids = []
        if field_name in source_line and source_line[field_name]:
            target_lines = source_line[field_name]
            # Delete if exists
            self.search([
                (trans_source_field, '=', source_line.id),
                (trans_target_field, 'in', target_lines.ids)]).unlink()
            # Case 1 source_line - M target_line, use target qty
            # Case M source_line - 1 taret_line, use source qty
            multi = len(target_lines) > 1
            for target_line in target_lines:
                trans_dict = {
                    trans_source_field: source_line.id,
                    trans_target_field: target_line.id,
                    'quantity': (multi and target_line[target_qty_field] or
                                 source_line[source_qty_field]),
                }
                trans = self.create(trans_dict)
                trans_ids.append(trans.id)
        return trans_ids

    @api.model
    def create_trans_expense_to_invoice(self, expense_line):
        return self.create_budget_transition(
            expense_line, 'invoice_line_ids', 'unit_quantity',
            'quantity', 'expense_line_id', 'invoice_line_id')

# class HRExpenseExpense(models.Model):
#     _inherit = 'hr.expense.expense'

    # @api.multi
    # def _create_supplier_invoice_from_expense(self, merge_line=False):
    #     self.ensure_one()
    #     BudgetTrans = self.env['budget.transition']
    #     invoice = super(HRExpenseExpense, self).\
    #         _create_supplier_invoice_from_expense(merge_line=merge_line)
    #     expense = self
    #     # As invoice is created, log into budget.transition
    #     # When invoice_line is created
    #     # Case 1 expense_line to many invoice_line, use invoice_line qty
    #     # Case many expense_line to 1 invoice_line, use expense qty
    #     for expense_line in expense.line_ids:
    #         invoice_lines = expense_line.invoice_line_ids.\
    #             filtered(lambda l: l.invoice_id.state == 'draft')
    #         multi = len(invoice_lines) > 1
    #         for invoice_line in invoice_lines:
    #             trans_dict = {'expense_line_id': expense_line.id,
    #                           'invoice_line_id': invoice_line.id,
    #                           'quantity': (multi and invoice_line.quantity or
    #                                        expense_line.unit_quantity),
    #                           'forward': False,
    #                           'backward': False,
    #                           }
    #             BudgetTrans.create(trans_dict)
    #     return invoice


class HRExpenseLine(models.Model):
    _inherit = 'hr.expense.line'

    # @api.multi
    # def write(self, vals):
    #     res = super(HRExpenseLine, self).write(vals)
    #     # Prepare Budget Transition
    #     if 'invoice_line_ids' in vals and vals['invoice_line_ids']:
    #         BudgetTrans = self.env['budget.transition']
    #         for expense_line in self:
    #             BudgetTrans.create_trans_expense_to_invoice(expense_line)
    #     return res

    @api.multi
    @api.constrains('invoice_line_ids')
    def _trigger_invoice_line_ids(self):
        BudgetTrans = self.env['budget.transition']
        for expense_line in self:
            BudgetTrans.create_trans_expense_to_invoice(expense_line)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def write(self, vals):
        BudgetTrans = self.env['budget.transition']
        if 'state' in vals:
            # Invoice Validated, It is time to return commitment
            if vals['state'] == 'open':
                invoice_line_ids = []
                for invoice in self:
                    invoice_line_ids += invoice.invoice_line.ids
                trans = BudgetTrans.search([
                    ('invoice_line_id', 'in', invoice_line_ids),
                    ('forward', '=', False)])
                trans.with_context(trigger=self._name).write({'forward': True})

            # Invoice Cancelled, It is time to backward commitment
            if vals['state'] == 'cancel':
                invoice_line_ids = []
                for invoice in self:
                    invoice_line_ids += invoice.invoice_line.ids
                trans = BudgetTrans.search([
                    ('invoice_line_id', 'in', invoice_line_ids),
                    ('backward', '=', False)])
                trans.with_context(trigger=self._name).write({'backward': True})
        return super(AccountInvoice, self).write(vals)
