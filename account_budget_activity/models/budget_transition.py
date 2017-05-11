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
    purchase_request_line_id = fields.Many2one(
        'purchase.request.line',
        string='Purchase Request Line',
        index=True,
    )
    purchase_line_id = fields.Many2one(
        'purchase.order.line',
        string='Purchase Order Line',
        index=True,
    )
    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Sales Order Line',
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
        help="True, when the end document is cancelled, "
        "if it has been forwarded, do regain budget commitment."
    )

    @api.multi
    def return_budget_commitment(self, trigger_model, to_sources):
        for source in to_sources:
            for tran in self:
                if source in tran and tran[source]:
                    ctx = {'diff_qty': tran.quantity}
                    tran[source].with_context(ctx).\
                        _create_analytic_line(reverse=False)

    @api.multi
    def regain_budget_commitment(self, trigger_model, to_sources):
        for source in to_sources:
            for tran in self:
                if source in tran and tran[source] and tran.forward:  # Fwd
                    ctx = {'diff_qty': tran.quantity}
                    tran[source].with_context(ctx).\
                        _create_analytic_line(reverse=True)  # True

    @api.multi
    def write(self, vals):
        """ Target Document, write forward/backward, return / regain budget """
        trigger_models = ['account.invoice',
                          'purchase.order']
        trigger_model = self._context.get('trigger', False)
        if trigger_model not in trigger_models:
            raise ValidationError(_('Wrong budget transition trigger!'))
        is_forward = 'forward' in vals and vals.get('forward', False)
        is_backward = 'backward' in vals and vals.get('backward', False)
        # For each type of model,
        to_sources = []  # source document to return or regain
        if trigger_model == 'account.invoice':
            to_sources = ['expense_line_id',
                          'purchase_line_id',
                          'sale_line_id']
        elif trigger_model == 'purchase.order':
            to_sources = ['purchase_request_line_id']
        # Start
        if is_forward:
            self.return_budget_commitment(trigger_model, to_sources)
        elif is_backward:
            self.regain_budget_commitment(trigger_model, to_sources)

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

    # Create budget transition log, when link between doc is created
    @api.model
    def create_trans_expense_to_invoice(self, line):
        return self.create_budget_transition(
            line, 'invoice_line_ids', 'unit_quantity',
            'quantity', 'expense_line_id', 'invoice_line_id')

    @api.model
    def create_trans_pr_to_purchase(self, line):
        return self.create_budget_transition(
            line, 'purchase_lines', 'product_qty',
            'product_qty', 'purchase_request_line_id', 'purchase_line_id')

    @api.model
    def create_trans_purchase_to_invoice(self, line):
        return self.create_budget_transition(
            line, 'invoice_lines', 'product_qty',
            'quantity', 'purchase_line_id', 'invoice_line_id')

    @api.model
    def create_trans_sale_to_invoice(self, line):
        return self.create_budget_transition(
            line, 'invoice_lines', 'product_uom_qty',
            'quantity', 'sale_line_id', 'invoice_line_id')

    # Return / Regain Commitment
    @api.model
    def do_forward(self, model, objects, obj_line_field):
        self.do_transit(model, objects, obj_line_field, 'forward')

    @api.model
    def do_backward(self, model, objects, obj_line_field):
        self.do_transit(model, objects, obj_line_field, 'backward')

    @api.model
    def do_transit(self, model, objects, obj_line_field, direction):
        target_model_fields = {'account.invoice': 'invoice_line_id',
                               'purchase.order': 'purchase_line_id'}
        trans_target_field = target_model_fields.get(model, False)
        if not trans_target_field:
            raise ValidationError(_('Wrong model for budget transition!'))
        line_ids = []
        for obj in objects:
            line_ids += obj[obj_line_field].ids
        trans = self.search([
            (trans_target_field, 'in', line_ids), (direction, '=', False)])
        trans.with_context(trigger=model).write({direction: True})


class HRExpenseLine(models.Model):
    """ Source document, when line's link created, so do budget transition """
    _inherit = 'hr.expense.line'

    @api.multi
    @api.constrains('invoice_line_ids')
    def _trigger_invoice_line_ids(self):
        BudgetTrans = self.env['budget.transition']
        for expense_line in self:
            BudgetTrans.create_trans_expense_to_invoice(expense_line)


class PurchaseRequestLine(models.Model):
    """ Source document, when line's link created, so do budget transition """
    _inherit = 'purchase.request.line'

    @api.multi
    @api.constrains('purchase_lines')
    def _trigger_purchase_lines(self):
        BudgetTrans = self.env['budget.transition']
        for pr_line in self:
            BudgetTrans.create_trans_pr_to_purchase(pr_line)


class PurchaseOrderLine(models.Model):
    """ Source document, when line's link created, so do budget transition """
    _inherit = 'purchase.order.line'

    @api.multi
    @api.constrains('invoice_lines')
    def _trigger_purchase_lines(self):
        BudgetTrans = self.env['budget.transition']
        for po_line in self:
            BudgetTrans.create_trans_purchase_to_invoice(po_line)


class SaleOrderLine(models.Model):
    """ Source document, when line's link created, so do budget transition """
    _inherit = 'sale.order.line'

    @api.multi
    @api.constrains('invoice_lines')
    def _trigger_purchase_lines(self):
        BudgetTrans = self.env['budget.transition']
        for so_line in self:
            BudgetTrans.create_trans_sale_to_invoice(so_line)


class PurchaseOrder(models.Model):
    """ As target document, stamp forward / backward to budget_transition """
    _inherit = 'purchase.order'

    @api.multi
    def write(self, vals):
        BudgetTrans = self.env['budget.transition']
        if 'state' in vals:
            purchases = self
            # PO Confirmed, It is time to return commitment to PR
            if vals['state'] == 'confirmed':
                BudgetTrans.do_forward(self._name, purchases, 'order_line')
            # PO Cancelled, It is time to regain commitment
            if vals['state'] == 'cancel':
                BudgetTrans.do_backward(self._name, self, 'order_line')
        return super(PurchaseOrder, self).write(vals)


class AccountInvoice(models.Model):
    """ As target document, stamp forward / backward to budget_transition """
    _inherit = 'account.invoice'

    @api.multi
    def write(self, vals):
        BudgetTrans = self.env['budget.transition']
        if 'state' in vals:
            invoices = self
            # Invoice Validated, It is time to return commitment
            if vals['state'] == 'open':
                BudgetTrans.do_forward(self._name, invoices, 'invoice_line')
            # Invoice Cancelled, It is time to regain commitment
            if vals['state'] == 'cancel':
                BudgetTrans.do_backward(self._name, self, 'invoice_line')
        return super(AccountInvoice, self).write(vals)
