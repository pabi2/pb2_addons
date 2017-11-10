# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class BudgetTransition(models.Model):
    _name = 'budget.transition'
    _description = 'Keep track of budget transition from one model to another'
    _order = 'id desc'

    id = fields.Integer(
        string='ID',
    )
    expense_line_id = fields.Many2one(
        'hr.expense.line',
        string='Expense Line',
        index=True,
    )
    expense_id = fields.Many2one(
        'hr.expense.expense',
        string='Expense',
        related='expense_line_id.expense_id',
        store=True,
    )
    purchase_request_line_id = fields.Many2one(
        'purchase.request.line',
        string='Purchase Request Line',
        index=True,
    )
    purchase_request_id = fields.Many2one(
        'purchase.request',
        string='Purchase Request',
        related='purchase_request_line_id.request_id',
        store=True,
    )
    purchase_line_id = fields.Many2one(
        'purchase.order.line',
        string='Purchase Order Line',
        index=True,
    )
    purchase_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        related='purchase_line_id.order_id',
        store=True,
    )
    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Sales Order Line',
        index=True,
    )
    sale_id = fields.Many2one(
        'sale.order',
        string='Sales Order',
        related='sale_line_id.order_id',
        store=True,
    )
    invoice_line_id = fields.Many2one(
        'account.invoice.line',
        string='Invoice Line',
        index=True,
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
        related='invoice_line_id.invoice_id',
        store=True,
    )
    stock_move_id = fields.Many2one(
        'stock.move',
        string='Stock Move',
        index=True,
    )
    picking_id = fields.Many2one(
        'stock.picking',
        string='Picking',
        related='stock_move_id.picking_id',
        store=True,
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
    source = fields.Char(
        string='Source',
        compute='_compute_source_target',
    )
    target = fields.Char(
        string='Target',
        compute='_compute_source_target',
    )

    @api.multi
    def _compute_source_target(self):
        for rec in self:
            source = 'source'
            target = 'target'
            # if rec.backward:
            #     source = 'target'
            #     target = 'source'
            # PR -> PO
            if rec.purchase_request_line_id and rec.purchase_line_id:
                rec[source] = '%s, %s' % \
                    (rec.purchase_request_id.name,
                     rec.purchase_request_line_id.name_get()[0][1])
                rec[target] = '%s, %s' % \
                    (rec.purchase_id.name,
                     rec.purchase_line_id.name_get()[0][1])
            # PO -> Invoice
            if rec.purchase_line_id and rec.invoice_line_id:
                rec[source] = '%s, %s' % \
                    (rec.purchase_id.name,
                     rec.purchase_line_id.name_get()[0][1])
                rec[target] = '%s, %s' % \
                    (rec.invoice_id.number,
                     rec.invoice_line_id.name_get()[0][1])
            # PO -> Picking
            if rec.purchase_line_id and rec.stock_move_id:
                rec[source] = '%s, %s' % \
                    (rec.purchase_id.name,
                     rec.purchase_line_id.name_get()[0][1])
                rec[target] = '%s, %s' % \
                    (rec.picking_id.name,
                     rec.stock_move_id.name_get()[0][1])
            # Picking -> invoice
            if rec.invoice_line_id and rec.stock_move_id:
                rec[source] = '%s, %s' % \
                    (rec.invoice_id.number,
                     rec.invoice_line_id.name_get()[0][1])
                rec[target] = '%s, %s' % \
                    (rec.picking_id.name,
                     rec.stock_move_id.name_get()[0][1])
            # EXP -> Invoice
            if rec.expense_line_id and rec.invoice_line_id:
                rec[source] = '%s, %s' % \
                    (rec.expense_id.number,
                     rec.expense_line_id.name_get()[0][1])
                rec[target] = '%s, %s' % \
                    (rec.invoice_id.number,
                     rec.invoice_line_id.name_get()[0][1])
        if not rec.source:
            rec.source = _('N/A')
        if not rec.target:
            rec.target = _('N/A')

    @api.model
    def _get_qty(self, line):
        qty_fields = ['quantity', 'product_uom_qty',
                      'product_qty', 'unit_quantity']
        for field in qty_fields:
            if field in line:
                return line[field]

    @api.multi
    def return_budget_commitment(self, to_sources):
        for source in to_sources:
            for tran in self:
                if source in tran and tran[source]:
                    quantity = self._get_qty(tran[source])  # use samller qty
                    if quantity > tran.quantity:
                        quantity = tran.quantity
                    ctx = {'diff_qty': quantity}
                    tran[source].with_context(ctx).\
                        _create_analytic_line(reverse=False)

    @api.multi
    def regain_budget_commitment(self, to_sources):
        for source in to_sources:
            for tran in self:
                if source in tran and tran[source] and tran.forward:  # Fwd
                    quantity = self._get_qty(tran[source])  # use samller qty
                    if quantity > tran.quantity:
                        quantity = tran.quantity
                    ctx = {'diff_qty': quantity}
                    tran[source].with_context(ctx).\
                        _create_analytic_line(reverse=True)  # True

    @api.multi
    def write(self, vals):
        """ Target Document, write forward/backward, return/regain budget """
        trigger_models = {'account.invoice': ['expense_line_id',
                                              'purchase_line_id',
                                              'sale_line_id'],
                          'purchase.order': ['purchase_request_line_id'],
                          'stock.move': ['purchase_line_id'],
                          }
        model = self._context.get('trigger', False)
        if model not in trigger_models:
            raise ValidationError(_('Wrong budget transition trigger!'))
        is_forward = 'forward' in vals and vals.get('forward', False)
        is_backward = 'backward' in vals and vals.get('backward', False)
        # For each type of model,
        to_sources = trigger_models[model]  # source document to return/regain
        # Start
        if is_forward:
            self.return_budget_commitment(to_sources)
        elif is_backward:
            self.regain_budget_commitment(to_sources)

        return super(BudgetTransition, self).write(vals)

    @api.model
    def _create_trans_by_target_lines(self, source_line, target_lines,
                                      source_qty_field, target_qty_field,
                                      trans_source_field, trans_target_field):
        trans_ids = []
        # Do not add, if exists. We value the first entry to be correct.
        existing_trans = self.search([
            (trans_source_field, '=', source_line.id),
            (trans_target_field, 'in', target_lines.ids)])
        # TODO: existing_trans can be > 1 for case create invoice plan
        # Also make it run faster
        for target_line in target_lines:
            if existing_trans[trans_source_field] == source_line and \
                    existing_trans[trans_target_field] == target_line:
                continue
            trans_dict = {
                trans_source_field: source_line.id,
                trans_target_field: target_line.id,
                'quantity': target_line[target_qty_field],
            }
            trans = self.create(trans_dict)
            trans_ids.append(trans.id)
        return trans_ids

    @api.model
    def _create_budget_transition(self, source_line, field_name,
                                  source_qty_field, target_qty_field,
                                  trans_source_field, trans_target_field):
        trans_ids = []
        if field_name in source_line and source_line[field_name]:
            target_lines = source_line[field_name]
            trans_ids = self._create_trans_by_target_lines(
                source_line, target_lines,
                source_qty_field, target_qty_field,
                trans_source_field, trans_target_field)
        return trans_ids

    # Create budget transition log, when link between doc is created
    @api.model
    def create_trans_expense_to_invoice(self, line):
        return self._create_budget_transition(
            line, 'invoice_line_ids', 'unit_quantity',
            'quantity', 'expense_line_id', 'invoice_line_id')

    @api.model
    def create_trans_pr_to_purchase(self, line):
        return self._create_budget_transition(
            line, 'purchase_lines', 'product_qty',
            'product_qty', 'purchase_request_line_id', 'purchase_line_id')

    @api.model
    def create_trans_purchase_to_invoice(self, line):
        return self._create_budget_transition(
            line, 'invoice_lines', 'product_qty',
            'quantity', 'purchase_line_id', 'invoice_line_id')

    # TODO: Why this one can't use create_budget_transition???
    @api.model
    def create_trans_purchase_to_picking(self, moves):
        trans_ids = []
        purchase_lines = moves.mapped('purchase_line_id')
        for line in purchase_lines:
            grp_moves = moves.filtered(lambda l: l.purchase_line_id == line)
            trans_ids += self._create_trans_by_target_lines(
                line, grp_moves, 'product_qty', 'product_uom_qty',
                'purchase_line_id', 'stock_move_id')
        return trans_ids

    @api.model
    def create_trans_sale_to_invoice(self, line):
        return self._create_budget_transition(
            line, 'invoice_lines', 'product_uom_qty',
            'quantity', 'sale_line_id', 'invoice_line_id')

    # TODO: from sale to picking. Cannot find field from sale that link to move
    # def create_trans_sale_to_picking(self, line):

    # Return / Regain Commitment
    @api.model
    def do_forward(self, model, objects, obj_line_field=False):
        self.sudo().do_transit('forward', model, objects, obj_line_field)

    @api.model
    def do_backward(self, model, objects, obj_line_field=False):
        self.sudo().do_transit('backward', model, objects, obj_line_field)

    @api.model
    def do_transit(self, direction, model, objects, obj_line_field=False):
        target_model_fields = {'account.invoice': 'invoice_line_id',
                               'purchase.order': 'purchase_line_id',
                               'stock.move': 'stock_move_id'}
        trans_target_field = target_model_fields.get(model, False)
        if not trans_target_field:
            raise ValidationError(_('Wrong model for budget transition!'))
        line_ids = []
        if obj_line_field:
            for obj in objects:
                line_ids += obj[obj_line_field].ids
        else:
            line_ids = objects.ids
        trans = self.search([
            (trans_target_field, 'in', line_ids), (direction, '=', False)])
        trans.with_context(trigger=model).write({direction: True})


class HRExpenseLine(models.Model):
    """ Source document, when line's link created, so do budget transition """
    _inherit = 'hr.expense.line'

    # TODO:
    # @api.multi
    # @api.constrains('invoice_line_ids')
    # def _trigger_invoice_line_ids(self):
    #     BudgetTrans = self.env['budget.transition'].sudo()
    #     for expense_line in self:
    #         BudgetTrans.create_trans_expense_to_invoice(expense_line)


class PurchaseRequestLine(models.Model):
    """ Source document, when line's link created, so do budget transition """
    _inherit = 'purchase.request.line'

    # TODO: purchase_lines (direct from pr_line to po_line is not available)
    # We do not install the module purchase_request_to_rfq
    # @api.multi
    # @api.constrains('purchase_lines')
    # def _trigger_purchase_lines(self):
    #     BudgetTrans = self.env['budget.transition'].sudo()
    #     for pr_line in self:
    #         BudgetTrans.create_trans_pr_to_purchase(pr_line)


class PurchaseOrderLine(models.Model):
    """ Source document, when line's link created, so do budget transition """
    _inherit = 'purchase.order.line'

    # TODO: Error on case purchase invoice plan
    # @api.multi
    # @api.constrains('invoice_lines')
    # def _trigger_purchase_lines(self):
    #     """ PO -> INV """
    #     BudgetTrans = self.env['budget.transition'].sudo()
    #     for po_line in self:
    #         product = po_line.product_id
    #         if product.type != 'service' and product.valuation == 'realtime':
    #             continue  # Skip case real time stockable
    #         BudgetTrans.create_trans_purchase_to_invoice(po_line)


class StockMove(models.Model):
    """ For real time stock, transition created and actual when it is moved """
    _inherit = 'stock.move'

    # TODO:
    # @api.multi
    # @api.constrains('state')
    # def _trigger_stock_moves(self):
    #     """ PO -> Stock Move, create transaction as it is tansferred """
    #     BudgetTrans = self.env['budget.transition'].sudo()
    #     # For done moves, create transition and return budget
    #     moves = self.filtered(lambda l: l.state == 'done' and
    #                           l.product_id.valuation == 'real_time')
    #     BudgetTrans.create_trans_purchase_to_picking(moves)
    #     BudgetTrans.do_forward(self._name, moves)


class SaleOrderLine(models.Model):
    """ Source document, when line's link created, so do budget transition """
    _inherit = 'sale.order.line'

    # TODO:
    # @api.multi
    # @api.constrains('invoice_lines')
    # def _trigger_sale_lines(self):
    #     BudgetTrans = self.env['budget.transition'].sudo()
    #     for so_line in self:
    #         BudgetTrans.create_trans_sale_to_invoice(so_line)


class PurchaseOrder(models.Model):
    """ As target document, stamp forward / backward to budget_transition """
    _inherit = 'purchase.order'

    @api.multi
    def write(self, vals):
        BudgetTrans = self.env['budget.transition'].sudo()
        if 'state' in vals:
            purchases = self
            # PO Confirmed, It is time to return commitment to PR
            if vals['state'] == 'confirmed':
                BudgetTrans.do_forward(self._name, purchases, 'order_line')
            # PO Cancelled, It is time to regain commitment
            if vals['state'] == 'cancel':
                BudgetTrans.do_backward(self._name, purchases, 'order_line')
        return super(PurchaseOrder, self).write(vals)


class AccountInvoice(models.Model):
    """ As target document, stamp forward / backward to budget_transition """
    _inherit = 'account.invoice'

    @api.multi
    def write(self, vals):
        BudgetTrans = self.env['budget.transition'].sudo()
        if 'state' in vals:
            invoices = self
            # Invoice Validated, It is time to return commitment
            if vals['state'] == 'open':
                BudgetTrans.do_forward(self._name, invoices, 'invoice_line')
            # Invoice Cancelled, It is time to regain commitment
            if vals['state'] == 'cancel':
                BudgetTrans.do_backward(self._name, invoices, 'invoice_line')
        return super(AccountInvoice, self).write(vals)
