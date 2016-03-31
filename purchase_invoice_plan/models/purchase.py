# -*- coding: utf-8 -*-
import time

from openerp import models, fields, api, _
from openerp.exceptions import except_orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    invoice_method = fields.Selection(
        selection_add=[('invoice_plan', 'Invoice Plan')],
    )
    invoice_plan_ids = fields.One2many(
        'purchase.invoice.plan',
        'order_id',
        string='Invoice Plan',
        copy=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    invoice_plan_wd_ids = fields.One2many(
        'purchase.invoice.plan',
        'order_id',
        string='Invoice Plan with Advance',
        copy=True,
    )
    use_advance = fields.Boolean(
        string='Advance on 1st Invoice',
        readonly=True,
    )
    use_deposit = fields.Boolean(
        string='Deposit on 1st Invoice',
        readonly=True,
    )
    invoice_mode = fields.Selection(
        [('change_price', 'As 1 Job (change price)'),
         ('change_quantity', 'As Units (change quantity)')],
        string='Invoice Mode',
        requied=True,
        readonly=True,
    )

    @api.model
    def _calculate_subtotal(self, vals):
        if vals.get('invoice_plan_ids', False) or \
                vals.get('invoice_plan_wd_ids', False):
            plan_ids = self.invoice_plan_ids or self.invoice_plan_wd_ids
            old_installment = 0
            subtotal = 0.0
            index_list = []  # Keep the subtotal line index
            i = 0
            for line in plan_ids:
                if line.installment > old_installment:  # Start new installment
                    if len(index_list) > 0:
                        del index_list[-1]  # Remove last index
                    subtotal = 0.0
                index_list.append(i)
                if line.installment == 0:
                    line.subtotal = 0.0
                else:
                    subtotal += line.invoice_amount
                    line.subtotal = subtotal
                old_installment = line.installment
                i += 1
            if len(index_list) > 0:
                del index_list[-1]
            # Now, delete subtotal  not in the index_list
            for i in index_list:
                self.invoice_plan_ids[i].subtotal = 0.0

    @api.model
    def _validate_invoice_plan(self, vals):
        if vals.get('invoice_plan_ids', False):
            for line in vals.get('invoice_plan_ids'):
                # Deleting (2) line that is not being cancelled
                plan = self.env['purchase.invoice.plan'].browse(line[1])
                if line[0] == 2:  # Deletion
                    plan = self.env['purchase.invoice.plan'].browse(line[1])
                    if plan.state and plan.state != 'cancel':
                        raise except_orm(
                            _('Delete Error!'),
                            _("You are trying deleting line(s) "
                              "that has not been cancelled!\n"
                              "Please discard change and try again!"))

    # Don't know why, but can't use v8 API !!, so revert to v7
    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        order_id = super(PurchaseOrder, self).\
            copy(cr, uid, id, default, context)
        order = self.browse(cr, uid, order_id)
        for invoice_plan in order.invoice_plan_ids:
            copy_to_line_id = invoice_plan.order_line_id and \
                invoice_plan.order_line_id.copy_to_line_id.id
            self.pool.get('purchase.invoice.plan').write(
                cr, uid, [invoice_plan.id],
                {'order_line_id': copy_to_line_id}, context)
        return order_id

    @api.multi
    def write(self, vals):
        for purchase in self:
            purchase._validate_invoice_plan(vals)
        res = super(PurchaseOrder, self).write(vals)
        for purchase in self:
            purchase._calculate_subtotal(vals)
        self.env['purchase.invoice.plan']._validate_installment_date(
            self.invoice_plan_ids)
        return res

    @api.one
    def _check_invoice_plan(self):
        if self.invoice_method == 'invoice_plan':
            obj_precision = self.env['decimal.precision']
            prec = obj_precision.precision_get('Account')
            for order_line in self.order_line:
                subtotal = order_line.price_subtotal
                invoice_lines = self.env['purchase.invoice.plan'].search(
                    [('order_line_id', '=', order_line.id)])
                total_amount = 0.0
                for line in invoice_lines:
                    total_amount += line.invoice_amount
                    # Validate percent
                    if round(line.invoice_percent/100 * subtotal, prec) != \
                            round(line.invoice_amount, prec):
                        raise except_orm(
                            _('Invoice Plan Percent Mismatch!'),
                            _("%s on installment %s")
                            % (order_line.name, line.installment))
                if round(total_amount, prec) != round(subtotal, prec):
                    raise except_orm(
                        _('Invoice Plan Amount Mismatch!'),
                        _("%s, plan amount %d not equal to line amount %d!")
                        % (order_line.name, total_amount, subtotal))
        return True

    @api.multi
    def _create_deposit_invoice(self, percent, amount,
                                date_invoice=False, blines=False):
        for order in self:
            if amount:
                filter_values = {'date_invoice': date_invoice}
                if blines.is_advance_installment:
                    advance_label = 'Advance'
                    filter_values.update({'is_deposit': True, })
                elif blines.is_deposit_installment:
                    advance_label = 'Deposit'
                    filter_values.update({'is_deposit_invoice': True, })

                prop = self.env['ir.property'].get(
                    'property_account_deposit_customer', 'res.partner')
                prop_id = prop and prop.id or False
                account_id = self.env[
                    'account.fiscal.position'].map_account(prop_id)
                name = _("%s of %s %%") % (advance_label, percent)
                # create the invoice
                inv_line_values = {
                    'name': name,
                    'origin': order.name,
                    'user_id': self.env.user.id,
                    'account_id': account_id,
                    'price_unit': amount,
                    'quantity': 1.0,
                    'discount': False,
                    'uos_id': False,
                    'product_id': False,
                    'invoice_line_tax_id': [
                        (6, 0, [x.id for x in order.order_line[0].taxes_id])],
                }
                inv_values = self._prepare_invoice(order, inv_line_values)
                inv_values.update(filter_values)
                # Chainging from [6, 0, ...] to [0, 0, ...]
                inv_values['invoice_line'] = [
                    (0, 0, inv_values['invoice_line'][0][2])]
                invoice = self.env['account.invoice'].create(inv_values)
                # compute the invoice
                invoice.button_compute(set_total=True)
                # Link this new invoice to related purchase order
                order.write({'invoice_ids': [(4, invoice.id)]})

                if date_invoice:
                    data = invoice.onchange_payment_term_date_invoice(
                        order.payment_term_id.id, date_invoice)
                else:
                    data = invoice.onchange_payment_term_date_invoice(
                        order.payment_term_id.id,
                        time.strftime(DEFAULT_SERVER_DATE_FORMAT))
                if data.get('value', False):
                    invoice.write(data['value'])
                return invoice
        return False

    @api.multi
    def action_invoice_create(self):
        self._check_invoice_plan()
        invoice_ids = []
        # Case use_invoice_plan, create multiple invoice by installment
        for order in self:
            if order.invoice_method == 'invoice_plan':
                plan_obj = self.env['purchase.invoice.plan']
                installments = list(set([plan.installment
                                         for plan in order.invoice_plan_ids]))
                last_installment = max(installments)
                for installment in installments:
                    # Getting invoice plan for each installment
                    plan_lines = plan_obj.search(
                        [('installment', '=', installment),
                         ('order_id', '=', order.id)])
                    if plan_lines:
                        for blines in plan_lines:
                            if installment == 0:
                                if blines.is_advance_installment:
                                    inv_id = self._create_deposit_invoice(
                                        blines.deposit_percent,
                                        blines.deposit_amount,
                                        blines.date_invoice,
                                        blines)
                                elif blines.is_deposit_installment:
                                    inv_id = self._create_deposit_invoice(
                                        blines.deposit_percent,
                                        blines.deposit_amount,
                                        blines.date_invoice,
                                        blines)

                                blines.write({'ref_invoice_id': inv_id.id})
                                invoice_ids.append(inv_id)
                                inv_id.write({
                                    'date_invoice': blines.date_invoice
                                })
                            else:
                                percent_dict = {}
                                date_invoice = (blines and
                                                blines[0].date_invoice or
                                                False)
                                for b in blines:
                                    percent_dict.update(
                                        {b.order_line_id: b.invoice_percent})
                                order = order.with_context(
                                    installment=installment,
                                    invoice_plan_percent=percent_dict,
                                    date_invoice=date_invoice)
                                inv_id = super(PurchaseOrder, order).\
                                    action_invoice_create()
                                invoice_ids.append(inv_id)
                                blines.write({'ref_invoice_id': inv_id})
                                invoice = self.env['account.invoice'].\
                                    browse(inv_id)
                                invoice.write({'date_invoice': date_invoice})

                                for line in invoice.invoice_line:
                                    # Remove line with negative price line
                                    if line.price_unit < 0:
                                        line.unlink()
                                for advance in order.invoice_ids:
                                    if advance.state != 'cancel' and \
                                            advance.is_deposit:
                                        for preline in advance.invoice_line:
                                            ratio = (order.amount_untaxed and
                                                     (invoice.amount_untaxed /
                                                      order.amount_untaxed) or
                                                     1.0)
                                            inv_line = preline.copy(
                                                {'invoice_id': inv_id,
                                                 'price_unit': -1 *
                                                    preline.price_unit})
                                            inv_line.quantity = \
                                                inv_line.quantity * ratio
                                invoice.button_compute()
                                if installment == last_installment:
                                    for deposit in order.invoice_ids:
                                        if deposit.state != 'cancel' and \
                                                deposit.is_deposit_invoice:
                                            for dline in deposit.invoice_line:
                                                inv_line = dline.copy(
                                                    {'invoice_id': inv_id,
                                                     'price_unit': -1 *
                                                        dline.price_unit})
                                invoice.button_compute()
            else:
                inv_id = super(PurchaseOrder, order).action_invoice_create()
        return inv_id

    @api.model
    def _prepare_inv_line(self, account_id, order_line):
        # Call super
        res = super(PurchaseOrder, self).\
            _prepare_inv_line(account_id, order_line)
        # For invoice plan
        invoice_plan_percent = self._context.get('invoice_plan_percent', False)
        if invoice_plan_percent:
            if order_line in invoice_plan_percent:
                if order_line.order_id.invoice_mode == 'change_quantity':
                    res.update({'quantity': (res.get('quantity') or 0.0) *
                                (order_line and
                                invoice_plan_percent[order_line] or 0.0) /
                                100})
                elif order_line.order_id.invoice_mode == 'change_price':
                    res.update({'price_unit': (res.get('price_unit') or 0.0) *
                                (res.get('quantity') or 0.0) *
                                (order_line and
                                invoice_plan_percent[order_line] or 0.0) /
                                100,
                                'quantity': 1.0})
            else:
                return False
        # From invoice_percentage,
        line_percent = self._context.get('line_percent', False)
        if line_percent:
            res.update({'quantity': ((res.get('quantity') or 0.0) *
                                     (line_percent / 100))})
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    invoice_plan_ids = fields.One2many(
        'purchase.invoice.plan',
        'order_line_id',
        string='Invoice Plan',
        readonly=True,
    )
    copy_from_line_id = fields.Many2one(
        'purchase.order.line',
        string="Copied from",
        readonly=True,
    )
    copy_to_line_id = fields.Many2one(
        'purchase.order.line',
        string="Last copied to",
        readonly=True,
    )

    def copy_data(self, cr, uid, id, default=None, context=None):
        default = dict(default or {})
        default.update({'copy_from_line_id': id, 'copy_to_line_id': False})
        return super(PurchaseOrderLine, self).\
            copy_data(cr, uid, id, default, context=context)

    @api.model
    def create(self, vals):
        new_line = super(PurchaseOrderLine, self).create(vals)
        if new_line.copy_from_line_id:
            old_line = self.browse(new_line.copy_from_line_id.id)
            old_line.copy_to_line_id = new_line.id
        return new_line

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
