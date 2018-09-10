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
    active = fields.Boolean(
        string='Active',
        default=True,
        readonly=True,
    )
    expense_line_id = fields.Many2one(
        'hr.expense.line',
        string='Expense Line',
        index=True,
        ondelete='cascade',
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
        ondelete='cascade',
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
        ondelete='cascade',
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
        ondelete='cascade',
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
        ondelete='cascade',
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
        ondelete='cascade',
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
    amount = fields.Float(
        string='Amount',
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
    source_model = fields.Selection(
        [('purchase.request.line', 'Purchase Request Line'),
         ('purchase.order.line', 'Purchase Order Line'),
         ('sale.order.line', 'Sales Order Line'),
         ('hr.expense.line', 'Expense Line'), ],
        string='Source Model',
        readonly=True,
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
                     rec.purchase_request_line_id.display_name)
                rec[target] = '%s, %s' % \
                    (rec.purchase_id.name,
                     rec.purchase_line_id.display_name)
            # SO -> Invoice
            if rec.sale_line_id and rec.invoice_line_id:
                rec[source] = '%s, %s' % \
                    (rec.sale_id.name,
                     rec.sale_line_id.display_name)
                rec[target] = '%s, %s' % \
                    (rec.invoice_id.number,
                     rec.invoice_line_id.display_name)
            # PO -> Invoice
            if rec.purchase_line_id and rec.invoice_line_id:
                rec[source] = '%s, %s' % \
                    (rec.purchase_id.name,
                     rec.purchase_line_id.display_name)
                rec[target] = '%s, %s' % \
                    (rec.invoice_id.number,
                     rec.invoice_line_id.display_name)
            # SO -> Picking
            if rec.sale_line_id and rec.stock_move_id:
                rec[source] = '%s, %s' % \
                    (rec.sale_id.name,
                     rec.sale_line_id.display_name)
                rec[target] = '%s, %s' % \
                    (rec.picking_id.name,
                     rec.stock_move_id.display_name)
            # PO -> Picking
            if rec.purchase_line_id and rec.stock_move_id:
                rec[source] = '%s, %s' % \
                    (rec.purchase_id.name,
                     rec.purchase_line_id.display_name)
                rec[target] = '%s, %s' % \
                    (rec.picking_id.name,
                     rec.stock_move_id.display_name)
            # EXP -> Invoice
            if rec.expense_line_id and rec.invoice_line_id:
                rec[source] = '%s, %s' % \
                    (rec.expense_id.number,
                     rec.expense_line_id.display_name)
                rec[target] = '%s, %s' % \
                    (rec.invoice_id.number,
                     rec.invoice_line_id.display_name)
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
                    ctx = {}
                    if tran.quantity:
                        quantity = self._get_qty(tran[source])
                        if quantity > tran.quantity:
                            quantity = tran.quantity
                        ctx = {'diff_qty': quantity}
                    if tran.amount:
                        ctx = {'diff_amount': tran.amount}
                    tran[source].with_context(ctx).\
                        _create_analytic_line(reverse=False)

    @api.multi
    def regain_budget_commitment(self, to_sources):
        for source in to_sources:
            for tran in self:
                if source in tran and tran[source] and tran.forward:  # Fwd
                    ctx = {}
                    if tran.quantity:
                        quantity = self._get_qty(tran[source])
                        if quantity > tran.quantity:
                            quantity = tran.quantity
                        ctx = {'diff_qty': quantity}
                    if tran.amount:
                        ctx = {'diff_amount': tran.amount}
                    tran[source].with_context(ctx).\
                        _create_analytic_line(reverse=True)  # True

    @api.multi
    def write(self, vals):
        """ Target Document, write forward/backward, return/regain budget """
        trigger_models = {'account.invoice': ['expense_line_id',
                                              'purchase_line_id',
                                              'sale_line_id'],
                          'purchase.order': ['purchase_request_line_id'],
                          'stock.move': ['purchase_line_id',
                                         'sale_line_id'],
                          }

        if self._context.get('trigger', False):
            model = self._context.get('trigger', False)
            if model not in trigger_models:
                raise ValidationError(_('Wrong budget transition trigger!'))
            if 'forward' in vals:
                if vals.get('forward', False):
                    self.return_budget_commitment(trigger_models[model])
                else:
                    self.regain_budget_commitment(trigger_models[model])
            if 'backward' in vals:
                if vals.get('backward', False):
                    self.regain_budget_commitment(trigger_models[model])
                else:
                    self.return_budget_commitment(trigger_models[model])

        return super(BudgetTransition, self).write(vals)

    @api.model
    def _create_trans_by_target_lines_quantity(
            self, source_line, target_lines, target_field, trans_source_field,
            trans_target_field, reverse=False):
        """ target_field_type = 'quantity' """
        return self._create_trans_by_target_lines(
            source_line, target_lines, target_field, trans_source_field,
            trans_target_field, target_field_type='quantity', reverse=reverse)

    @api.model
    def _create_trans_by_target_lines_amount(
            self, source_line, target_lines, target_field, trans_source_field,
            trans_target_field, reverse=False):
        """ target_field_type = 'amount' """
        return self._create_trans_by_target_lines(
            source_line, target_lines, target_field, trans_source_field,
            trans_target_field, target_field_type='amount', reverse=reverse)

    @api.model
    def _create_trans_by_target_lines(
            self, source_line, target_lines, target_field, trans_source_field,
            trans_target_field, target_field_type='quantity', reverse=False):
        trans_ids = []
        # If trans already exist (same source id and target id), skip it.
        existing_trans = source_line.budget_transition_ids.filtered('active')
        # Prepare existing trans dictionary. We use it to skip.
        existing_dicts = []
        for existing_tran in existing_trans:
            existing_dicts.append({
                trans_source_field: existing_tran[trans_source_field].id,
                trans_target_field: existing_tran[trans_target_field].id,
            })
        for target_line in target_lines:
            # Check if new trans dict already exists
            todo = True
            trans_dict = {
                trans_source_field: source_line.id,
                trans_target_field: target_line.id,
            }
            for existing_dict in existing_dicts:
                if existing_dict == trans_dict:
                    todo = False
                    break
            if todo:
                number = target_line[target_field]
                # Quantity or Amount
                trans_dict[target_field_type] = reverse and -number or number
                # Source Model
                trans_dict['source_model'] = source_line._name
                trans = self.create(trans_dict)
                trans_ids.append(trans.id)
        return trans_ids

    # Create budget transition log, when link between doc is created
    @api.model
    def create_trans_expense_to_invoice(self, line):
        if line and line.invoice_line_ids:
            # For expense use "Amount" instead of "Quantity"
            # Because, quantity is always equal to 1, so we can ignore it.
            self._create_trans_by_target_lines_amount(
                line, line.invoice_line_ids,
                'price_subtotal', 'expense_line_id', 'invoice_line_id')

    @api.model
    def create_trans_pr_to_purchase(self, line):
        if line and line.purchase_lines:
            self._create_trans_by_target_lines_quantity(
                line, line.purchase_lines,
                'product_qty', 'purchase_request_line_id', 'purchase_line_id')

    @api.model
    def create_trans_purchase_to_invoice(self, po_line):
        if po_line and po_line.invoice_lines:
            # Use invoice plan + invoice_mode = 'change_price', use amount
            if po_line.order_id.use_invoice_plan and \
                    po_line.order_id.invoice_mode == 'change_price':
                self._create_trans_by_target_lines_amount(
                    po_line, po_line.invoice_lines,
                    'price_subtotal', 'purchase_line_id', 'invoice_line_id')
            else:  # Other case, use quantity
                self._create_trans_by_target_lines_quantity(
                    po_line, po_line.invoice_lines,
                    'quantity', 'purchase_line_id', 'invoice_line_id')

    @api.model
    def create_trans_purchase_to_picking(self, po_line, moves, reverse=False):
        if po_line and moves:
            self._create_trans_by_target_lines_quantity(
                po_line, moves,
                'product_uom_qty', 'purchase_line_id', 'stock_move_id',
                reverse=reverse)

    @api.model
    def create_trans_sale_to_invoice(self, so_line):
        if so_line and so_line.invoice_lines:
            self._create_trans_by_target_lines_quantity(
                so_line, so_line.invoice_lines,
                'quantity', 'sale_line_id', 'invoice_line_id',
                reverse=True)  # For sales

    @api.model
    def create_trans_sale_to_picking(self, so_line, moves, reverse=False):
        reverse = not reverse  # For sales
        if so_line and moves:
            self._create_trans_by_target_lines_quantity(
                so_line, moves,
                'product_uom_qty', 'sale_line_id', 'stock_move_id',
                reverse=reverse)

    # Return / Regain Commitment
    @api.model
    def do_forward(self, model, objects, obj_line_field=False):
        self.sudo().do_transit('forward', model, objects, obj_line_field)

    @api.model
    def undo_forward(self, model, objects, obj_line_field=False):
        self.sudo().do_transit('forward', model, objects, obj_line_field,
                               undo=True)

    @api.model
    def do_backward(self, model, objects, obj_line_field=False):
        self.sudo().do_transit('backward', model, objects, obj_line_field)

    @api.model
    def undo_backward(self, model, objects, obj_line_field=False):
        self.sudo().do_transit('backward', model, objects, obj_line_field,
                               undo=True)

    @api.model
    def do_transit(self, direction, model, objects, obj_line_field=False,
                   undo=False):
        target_model_fields = {'account.invoice': 'invoice_line_id',
                               'sale.order': 'sale_line_id',
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
        if not undo:  # Normal case
            trans = self.search([
                (trans_target_field, 'in', line_ids), (direction, '=', False)])
            trans.with_context(trigger=model).write({direction: True})
        else:
            trans = self.search([
                (trans_target_field, 'in', line_ids), (direction, '=', True)])
            trans.with_context(trigger=model).write({direction: False})


class HRExpenseLine(models.Model):
    """ Source document, when line's link created, so do budget transition """
    _inherit = 'hr.expense.line'

    @api.multi
    @api.constrains('invoice_line_ids')
    def _trigger_expense_invoice_lines(self):
        """ EXP -> INV """
        BudgetTrans = self.env['budget.transition'].sudo()
        for expense_line in self:
            BudgetTrans.create_trans_expense_to_invoice(expense_line)


class PurchaseRequestLine(models.Model):
    """ Source document, when line's link created, so do budget transition """
    _inherit = 'purchase.request.line'

    @api.multi
    @api.constrains('purchase_lines')
    def _trigger_purchase_lines(self):
        BudgetTrans = self.env['budget.transition'].sudo()
        for pr_line in self:
            BudgetTrans.create_trans_pr_to_purchase(pr_line)


class PurchaseOrderLine(models.Model):
    """ Source document, when line's link created, so do budget transition """
    _inherit = 'purchase.order.line'

    @api.multi
    @api.constrains('invoice_lines')
    def _trigger_purchase_invoice_lines(self):
        """ PO -> INV """
        BudgetTrans = self.env['budget.transition'].sudo()
        for po_line in self:
            product = po_line.product_id
            if product.type == 'service' or product.valuation != 'real_time':
                BudgetTrans.create_trans_purchase_to_invoice(po_line)


class StockMove(models.Model):
    """ For real time stock, transition created and actual when it is moved """
    _inherit = 'stock.move'

    @api.multi
    @api.constrains('state')
    def _trigger_stock_moves(self):
        """ SO/PO -> Stock Move, create transaction as it is tansferred """
        BudgetTrans = self.env['budget.transition'].sudo()
        # For done moves, create transition and return budget same time
        # Peformance Tuning
        moves = self.filtered(lambda l: l.state == 'done' and
                              l.product_id.valuation == 'real_time')
        # Following is very slow... not necessary serach will be fast
        # moves = self.search([('id', 'in', self.ids), ('state', '=', 'done'),
        #                      ('product_id.valuation', '=', 'real_time')])
        if not moves:
            return
        for move in moves:
            reverse = move.picking_type_id.code == 'outgoing'
            if move.purchase_line_id:
                BudgetTrans.create_trans_purchase_to_picking(
                    move.purchase_line_id, moves, reverse=reverse)
            if move.sale_line_id:
                BudgetTrans.create_trans_sale_to_picking(
                    move.sale_line_id, moves, reverse=reverse)
        # Do Forward immediately
        BudgetTrans.do_forward(self._name, moves)


class SaleOrderLine(models.Model):
    """ Source document, when line's link created, so do budget transition """
    _inherit = 'sale.order.line'

    @api.multi
    @api.constrains('invoice_lines')
    def _trigger_sale_invoice_lines(self):
        """ SO -> INV """
        BudgetTrans = self.env['budget.transition'].sudo()
        for so_line in self:
            product = so_line.product_id
            if product.type == 'service' or product.valuation != 'real_time':
                BudgetTrans.create_trans_sale_to_invoice(so_line)


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
            # PO Draft, reset both return and regain
            if vals['state'] == 'draft':
                BudgetTrans.undo_forward(self._name, purchases, 'order_line')
                BudgetTrans.undo_backward(self._name, purchases, 'order_line')
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
