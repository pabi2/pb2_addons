# -*- coding: utf-8 -*-
import math
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    by_fiscalyear = fields.Boolean(
        string='By Fiscal Year',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    advance_rounding = fields.Boolean(
        string="Advance Rounding",
        readonly=True,
    )
    account_deposit_supplier = fields.Many2one(
        'account.account',
        string='Advance/Deposit Account',
        domain=lambda self:
        [('id', 'in', self.env.user.company_id.other_deposit_account_ids.ids)],
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="This account will be used as default for invoices created by "
        "invoice plan. You can change it."
    )

    @api.multi
    def wkf_confirm_order(self):
        for purchase in self:
            # For case invoice plan only, if By Fiscal Year is selected,
            if purchase.use_invoice_plan and purchase.by_fiscalyear:
                if False in [x.fiscalyear_id.id for x in purchase.order_line]:
                    raise ValidationError(_('Some lines missing Fiscal Year'))
            else:
                # all line must have fiscalyear_id
                lines = purchase.order_line.filtered(lambda l:
                                                     not l.fiscalyear_id)
                if lines:
                    Fiscal = self.env['account.fiscalyear']
                    lines.write({'fiscalyear_id': Fiscal.find()})
        return super(PurchaseOrder, self).wkf_confirm_order()

    # @api.constrains('use_invoice_plan', 'by_fiscalyear', 'order_line')
    # def _check_by_fiscalyear(self):
    #     for order in self:
    #         if not order.use_invoice_plan:
    #             continue
    #         count_order_line = len(order.order_line)
    #         count_fiscalyear_order_line = 0
    #         for line in order.order_line:
    #             if not line.fiscalyear_id:
    #                 continue
    #             count_fiscalyear_order_line += 1
    #         if order.by_fiscalyear and \
    #            count_order_line != count_fiscalyear_order_line:
    #             raise ValidationError(
    #                 _('All order line must specify fiscal year'))
    #         if not order.by_fiscalyear and count_fiscalyear_order_line:
    #             raise ValidationError(
    #                 _('All order line must not specify fiscal year'))

    @api.model
    def _action_invoice_create_hook(self, invoice_ids):
        # For Hook
        res = super(PurchaseOrder, self).\
            _action_invoice_create_hook(invoice_ids)
        if self.use_advance and self.advance_rounding and \
                self.invoice_method == 'invoice_plan':
            adv_invoice = self.env['account.invoice'].\
                search([('id', 'in', invoice_ids), ('is_advance', '=', True)])
            adv_amount = adv_invoice and \
                adv_invoice[0].invoice_line[0].price_unit or 0.0
            invoices = self.env['account.invoice'].\
                search([('id', 'in', invoice_ids), ('is_advance', '=', False)],
                       order='date_invoice')
            if invoices:
                total_invoices = len(invoices.ids)
                adv_accum = 0.0
                count = 1
                for invoice in invoices:
                    if count < total_invoices:
                        for line in invoice.invoice_line:
                            price_subtotal_frac, price_subtotal_whole =\
                                math.modf(line.price_subtotal)
                            if line.price_subtotal < 0:
                                if price_subtotal_frac:  # change
                                    line.price_unit = price_subtotal_whole
                                adv_accum += price_subtotal_whole
                    if count == total_invoices:
                        for line in invoice.invoice_line:
                            if line.price_subtotal < 0:
                                line.price_unit = -(adv_amount + adv_accum)
                    count += 1
        # For NSTDA only, date_document = date_invoice
        invoices = self.env['account.invoice'].browse(invoice_ids)
        for invoice in invoices:
            invoice.write({'date_document': invoice.date_invoice,
                           'date_invoice': False})
        return res

    @api.model
    def _create_invoice_line(self, inv_line_data, inv_lines, po_line):
        if not po_line.order_id.by_fiscalyear:
            return super(PurchaseOrder, self).\
                _create_invoice_line(inv_line_data, inv_lines, po_line)

        installment = self._context.get('installment', False)
        if installment:
            installment = \
                self.env['purchase.invoice.plan'].search(
                    [('installment', '=', installment),
                     ('order_id', '=', po_line.order_id.id),
                     ('state', 'in', [False, 'cancel'])]
                )
        if installment:
            fiscalyear = installment[0].fiscalyear_id
            if po_line.order_id.by_fiscalyear:
                if po_line.fiscalyear_id == fiscalyear:
                    inv_line_obj = self.env['account.invoice.line']
                    inv_line_id = inv_line_obj.create(inv_line_data).id
                    inv_lines.append(inv_line_id)
                    po_line.write({'invoice_lines': [(4, inv_line_id)]})
        return inv_lines

    @api.multi
    def _check_invoice_plan(self):
        res = super(PurchaseOrder, self)._check_invoice_plan()
        self.ensure_one()
        # Case Invoice Plan + Advance: all line must charge same budget
        # So that, advance line know which budget to use.
        if self.use_invoice_plan and (self.use_advance or self.use_deposit):
            if len(self.order_line.mapped('account_analytic_id')) != 1:
                raise ValidationError(
                    _('No mixing of costcenter when use Advance/Deposit!'))
        # Case Invoice Plan + Asset: all ine must be asset, and use Job base
        # So that, Picking qty will be equal to number of intsallment.
        if self.invoice_method == 'invoice_plan':
            assets = [x.product_id.asset or False for x in self.order_line]
            if True in assets:  # has some asset in line
                if len(list(set(assets))) != 1:
                    raise ValidationError(_('Invoice plan do not allow mixing '
                                            'asset and non-asset!'))
                # We can't use this as it conflict when po asset > 1 qty
                # if self.invoice_mode != 'change_price':
                #   raise ValidationError(_('Invoice Plan/Assets, please use '
                #                             'invoice mode "As 1 Job"'))
        return res

    @api.model
    def _prepare_deposit_invoice_line(self, name, order, amount):
        res = super(PurchaseOrder, self).\
            _prepare_deposit_invoice_line(name, order, amount)
        # Use manual deposit account.
        res.update({'account_id': order.account_deposit_supplier.id})
        if not res['account_id']:
            raise ValidationError(_('No advance/deposit account seleted!'))
        # --
        AnayticAccount = self.env['account.analytic.account']
        dimensions = AnayticAccount._analytic_dimensions()
        for d in dimensions:
            if d in ('product_id', 'activity_group_id',
                     'activity_id', 'activity_rpt_id'):
                continue  # Do not need to copy above dimension.
            res.update({d: order.order_line[0][d].id})
        return res

    @api.model
    def _prepare_order_line_move(self, order, order_line,
                                 picking_id, group_id):
        res = super(PurchaseOrder, self).\
            _prepare_order_line_move(order, order_line, picking_id, group_id)
        # If invoice plan + all assets + change_price -> qty = num_installment
        if order.use_invoice_plan and order_line.product_id.asset and \
                order.invoice_mode == 'change_price':
            num = order.num_installment
            for r in res:
                r.update({'product_uom_qty': r['product_uom_qty'] * num,
                          'product_uos_qty': r['product_uos_qty'] * num})
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
    )
    by_fiscalyear = fields.Boolean(
        related='order_id.by_fiscalyear',
        string='By Fiscal Year',
    )


class PurchaseInvoicePlan(models.Model):
    _inherit = 'purchase.invoice.plan'

    order_line_docline_seq = fields.Char(
        string='#',
        compute='_compute_results',
        readonly=True,
    )
    order_line_fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        compute='_compute_results',
        readonly=True,
    )
    order_line_budget_id = fields.Many2one(
        'chartfield.view',
        string='Budget',
        compute='_compute_results',
        readonly=True,
    )
    order_by_fiscalyear = fields.Boolean(
        string='By Fiscal Year',
        compute='_compute_results',
        readonly=True,
    )

        
    @api.multi
    def _compute_results(self):
        for line in self:
            line.order_by_fiscalyear = line.order_id.by_fiscalyear
            line.order_line_fiscalyear_id = line.order_line_id.fiscalyear_id
            line.order_line_docline_seq = line.order_line_id.docline_seq
            line.order_line_budget_id = line.order_line_id.chartfield_id
        
        
        
        
        
        
        
        
