# -*- coding: utf-8 -*-
import time
import decimal
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, ValidationError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, \
    float_compare, float_round as round


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    invoice_method = fields.Selection(
        selection_add=[('invoice_plan', 'Invoice Plan')],
    )
    use_invoice_plan = fields.Boolean(
        string='Use Invoice Plan',
        default=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
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
    plan_invoice_created = fields.Boolean(
        string='Invoice Created',
        compute='_compute_plan_invoice_created',
        help="Compute whether number of invoices "
        "(not cancelled invoices) are created as planned",
    )
    total_invoice_amount = fields.Float(
        compute='_compute_plan_invoice_created',
        string='Invoice Amount',
    )
    num_installment = fields.Integer(
        string='Number of Installment',
        default=0,
    )

    @api.multi
    def _compute_plan_invoice_created(self):
        for rec in self:
            if not rec.invoice_ids or not rec.use_invoice_plan:
                rec.plan_invoice_created = False
            else:
                total_invoice_amt = 0
                num_valid_invoices = 0
                for i in rec.invoice_ids:
                    if i.state not in ('cancel'):
                        num_valid_invoices += 1
                    if i.state in ('open', 'paid'):
                        total_invoice_amt += i.amount_untaxed
                plan_invoice = len(list(set([i.installment for i in
                                             rec.invoice_plan_ids])))
                print '----------> %s' % num_valid_invoices
                print '--------> %s' % plan_invoice
                rec.plan_invoice_created = num_valid_invoices >= plan_invoice
                print '--------> %s' % rec.plan_invoice_created
                rec.total_invoice_amount = total_invoice_amt
        return True

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

    @api.onchange('invoice_method')
    def _onchange_invoice_method(self):
        self.use_invoice_plan = self.invoice_method == 'invoice_plan'

    @api.onchange('use_invoice_plan')
    def _onchange_use_invoice_plan(self):
        if self.use_invoice_plan:
            self.invoice_method = 'invoice_plan'
        else:
            default_invoice_method = self.env['ir.values'].get_default(
                'purchase.order', 'invoice_method')
            self.invoice_method = default_invoice_method or 'order'

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

    @api.multi
    def _check_invoice_plan(self):
        self.ensure_one()
        if self.invoice_method == 'invoice_plan':
            # self._check_invoice_mode()
            # kittiu: problem with decimal, so we dicide to test with 0
            # obj_precision = self.env['decimal.precision']
            # prec = obj_precision.precision_get('Account')
            prec = 0
            # --
            for order_line in self.order_line:
                subtotal = order_line.price_subtotal
                invoice_lines = self.env['purchase.invoice.plan'].search(
                    [('order_line_id', '=', order_line.id)])
                total_amount = 0.0
                for line in invoice_lines:
                    total_amount += line.invoice_amount
                    # Validate percent
                    if round(line.invoice_percent / 100 * subtotal, prec) != \
                            round(line.invoice_amount, prec):
                        raise except_orm(
                            _('Invoice Plan Percent Mismatch!'),
                            _("%s on installment %s")
                            % (order_line.name, line.installment))
                if round(total_amount, prec) != round(subtotal, prec):
                    raise except_orm(
                        _('Invoice Plan Amount Mismatch!'),
                        _("%s, plan amount %s not equal to line amount %s!")
                        % (order_line.name,
                           '{:,.2f}'.format(total_amount),
                           '{:,.2f}'.format(subtotal)))
        return True

    @api.model
    def _prepare_deposit_invoice_line(self, name, order, amount):
        company = self.env.user.company_id
        account_id = company.account_deposit_supplier.id
        return {
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

    @api.multi
    def _create_deposit_invoice(self, percent, amount,
                                date_invoice=False, blines=False):
        for order in self:
            if amount:
                filter_values = {'date_invoice': date_invoice}
                if blines.is_advance_installment:
                    advance_label = _('Advance')
                    filter_values.update({'is_advance': True, })
                elif blines.is_deposit_installment:
                    advance_label = _('Deposit')
                    filter_values.update({'is_deposit': True, })
                name = _("%s of %s %%") % (advance_label, percent)
                # create the invoice
                inv_line_values = \
                    self._prepare_deposit_invoice_line(name, order, amount)
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
                return invoice.id
        return False

    @api.model
    def compute_advance_payment_line(self, inv_id):
        invoice = self.env['account.invoice'].browse(inv_id)
        order = self
        for advance in order.invoice_ids:
            if advance.state != 'cancel' and \
                    advance.is_advance:
                for preline in advance.invoice_line:
                    ratio = (order.amount_untaxed and
                             (invoice.amount_untaxed /
                              order.amount_untaxed) or 1.0)
                    inv_line = preline.copy(
                        {'invoice_id': inv_id,
                         'price_unit': -preline.price_unit * ratio})
                    inv_line.quantity = 1.0
        invoice.button_compute()
        return True

    @api.model
    def compute_deposit_line(self, inv_id):
        invoice = self.env['account.invoice'].browse(inv_id)
        order = self
        for deposit in order.invoice_ids:
            if deposit.state != 'cancel' and \
                    deposit.is_deposit:
                for dline in deposit.invoice_line:
                    dline.copy({'invoice_id': inv_id,
                                'price_unit': -1 *
                                dline.price_unit})
        invoice.button_compute()
        return True

    @api.multi
    def wkf_approve_order(self):
        self._check_invoice_plan()
        return super(PurchaseOrder, self).wkf_approve_order()

    # @api.multi
    # def _check_invoice_mode(self):
    #     # Removed as it conflict between asset must use 1 job, but sometime
    #     # we PO asset > 1 qty
    #     # --
    #     # for order in self:
    #     #     if order.invoice_method == 'invoice_plan':
    #     #         if order.invoice_mode == 'change_price':
    #     #             for order_line in order.order_line:
    #     #                 if order_line.product_qty != 1:
    #     #                     raise ValidationError(
    #     #                         _('For invoice plan mode "As 1 Job", '
    #     #                           'all line quantity must equal to 1'))
    #     return True

    @api.multi
    def action_invoice_create(self):
        self._check_invoice_plan()
        if self.plan_invoice_created:
            raise ValidationError(_('Create more invoices not allowed!'))
        invoice_ids = []
        inv_id = False
        # Case use_invoice_plan, create multiple invoice by installment
        for order in self:
            first_time_invoice_plan = not order.invoice_ids and True or False
            if order.invoice_method == 'invoice_plan':
                plan_obj = self.env['purchase.invoice.plan']
                installments = list(set([plan.installment
                                         for plan in order.invoice_plan_ids]))
                if not installments:
                    raise ValidationError(_('No invoice plan installments!'))
                last_installment = max(installments)
                for installment in installments:
                    # Getting invoice plan for each installment
                    blines = plan_obj.search(
                        [('installment', '=', installment),
                         ('order_id', '=', order.id),
                         ('state', 'in', [False, 'cancel'])])
                    if blines:
                        if installment == 0:
                            if blines.is_advance_installment or \
                                    blines.is_deposit_installment:
                                inv_id = self._create_deposit_invoice(
                                    blines.deposit_percent,
                                    blines.deposit_amount,
                                    blines.date_invoice,
                                    blines)
                                invoice_ids.append(inv_id)
                            blines.write({'ref_invoice_id': inv_id})
                            invoice = self.env['account.invoice'].\
                                browse(inv_id)
                            invoice.write({
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
                            order.compute_advance_payment_line(inv_id)
                            if installment == last_installment:
                                order.compute_deposit_line(inv_id)
            else:
                inv_id = super(PurchaseOrder, order).action_invoice_create()
                invoice_ids.append(inv_id)
            order._action_invoice_create_hook(invoice_ids)  # Special Hook
            order.with_context(first_time=first_time_invoice_plan).\
                _validate_invoice_balance(invoice_ids)  # Special Hook
        return inv_id

    @api.model
    def _validate_invoice_balance(self, invoice_ids):
        # Hook
        # Check total amount PO must equal to Invoice
        if self._context.get('first_time', False) and len(invoice_ids) > 0:
            self._cr.execute("""
                select coalesce(sum(amount_untaxed), 0.0)
                from account_invoice where id in %s
            """, (tuple(invoice_ids), ))
            invoice_untaxed = self._cr.fetchone()[0]
            prec = self.env['decimal.precision'].precision_get('Account')
            if float_compare(invoice_untaxed, self.amount_untaxed,
                             precision_digits=prec) != 0:
                raise except_orm(
                    _('Amount Mismatch!'),
                    _('Total invoice amount, %s, not equal to purchase '
                      'order amount, %s.\nThis may be caused by quantity '
                      'rounding from invoice plan to invoice line.') %
                    ('{:,.2f}'.format(invoice_untaxed),
                     '{:,.2f}'.format(self.amount_untaxed)))
        return

    @api.model
    def _action_invoice_create_hook(self, invoice_ids):
        # Hook
        return

    @api.model
    def _prepare_inv_line(self, account_id, order_line):
        # Call super
        res = super(PurchaseOrder, self).\
            _prepare_inv_line(account_id, order_line)
        # For invoice plan
        invoice_plan_percent = self._context.get('invoice_plan_percent', False)
        if invoice_plan_percent:
            if order_line in invoice_plan_percent:
                line_percent = invoice_plan_percent.get(order_line, 0.0)
                if order_line.order_id.invoice_mode == 'change_quantity':
                    quantity = res.get('quantity', 0.0) * line_percent / 100
                    d = decimal.Decimal(str(quantity))
                    if d.as_tuple().exponent < -2:
                        raise ValidationError(
                            _('Too many decimal places in percent will cause '
                              'rounding error in invoice quantity, i.e., %s.'
                              '\nPlease reduce to maximum 2 decimal places') %
                            quantity)
                    res.update({'quantity': quantity})
                elif order_line.order_id.invoice_mode == 'change_price':
                    price_unit = res.get('price_unit', 0.0) * \
                        res.get('quantity', 0.0) * line_percent / 100
                    res.update({'price_unit': price_unit,
                                'quantity': 1.0})
                    # d = decimal.Decimal(str(price_unit))
                    # if d.as_tuple().exponent < -2:
                    #     raise ValidationError(
                    #        _('Too many decimal places in percent will cause '
                    #         'rounding error in invoice unit price, i.e., %s.'
                    #          '\nPlease reduce to maximum 2 decimal places') %
                    #         price_unit)
            else:
                return {}
        return res

    @api.multi
    def action_cancel_draft_invoices(self):
        assert len(self) == 1, \
            'This option should only be used for a single id at a time.'
        # Get all unpaid invoice
        for invoice in self.invoice_ids:
            if invoice.state in ('draft',):
                invoice.signal_workflow('invoice_cancel')
        return True


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
