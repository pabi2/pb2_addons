# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp.exceptions import Warning as UserError


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    @api.multi
    def button_to_approve(self):
        for request in self:
            for line in request.line_ids:
                Analytic = self.env['account.analytic.account']
                line.analytic_account_id = \
                    Analytic.create_matched_analytic(line)
        return super(PurchaseRequest, self).button_to_approve()


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        compute='_compute_activity_group',
        store=True,
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
    )
    purchased_qty = fields.Float(
        string='Purchased Quantity',
        digits=(12, 6),
        compute='_compute_purchased_qty',
        store=True,
        help="This field calculate purchased quantity at line level. "
        "Will be used to calculate committed budget",
    )
    temp_purchased_qty = fields.Float(
        string='Temporary Purchased Quantity',
        digits=(12, 6),
        compute='_compute_temp_purchased_qty',
        store=True,
        copy=False,
        default=0.0,
        help="This field is used to keep the previous purchase qty, "
        "for calculate release commitment amount",
    )

    @api.multi
    @api.depends('requisition_lines.purchase_line_ids.order_id.state')
    def _compute_purchased_qty(self):
        Uom = self.env['product.uom']
        for request_line in self:
            purchased_qty = 0.0
            for reqisition_line in request_line.requisition_lines:
                for purchase_line in reqisition_line.purchase_line_ids:
                    if purchase_line.order_id.state in ['approved']:
                        # Purchased Qty in PO Line's UOM
                        purchased_qty += \
                            Uom._compute_qty(purchase_line.product_uom.id,
                                             purchase_line.product_qty,
                                             request_line.product_uom_id.id)
            request_line.purchased_qty = min(request_line.product_qty,
                                             purchased_qty)

    @api.one
    @api.depends('product_id', 'activity_id')
    def _compute_activity_group(self):
        if self.product_id and self.activity_id:
            self.product_id = self.activity_id = False
            self.name = False
        if self.product_id:
            account_id = self.product_id.property_account_expense.id or \
                self.product_id.categ_id.property_account_expense_categ.id
            activity_group = self.env['account.activity.group'].\
                search([('account_id', '=', account_id)])
            self.activity_group_id = activity_group
        elif self.activity_id:
            self.activity_group_id = self.activity_id.activity_group_id
            self.name = self.activity_id.name

    # ================= PR Commitment =====================

    @api.model
    def _price_subtotal(self, line_qty):
        line_price = self._calc_line_base_price(self)
        taxes = self.taxes_id.compute_all(line_price, line_qty,
                                          self.product_id,
                                          self.order_id.partner_id)
        cur = self.order_id.pricelist_id.currency_id
        return cur.round(taxes['total'])

    @api.model
    def _prepare_analytic_line(self, reverse=False):
        general_account_id = self.pool['purchase.order'].\
            _choose_account_from_po_line(self._cr, self._uid,
                                         self, self._context)
        general_journal = self.env['account.journal'].search(
            [('type', '=', 'purchase'),
             ('company_id', '=', self.company_id.id)], limit=1)
        if not general_journal:
            raise Warning(_('Define an accounting journal for purchase'))
        if not general_journal.pr_commitment_analytic_journal_id:
            raise UserError(
                _("No analytic journal for PR commitment defined on the "
                  "accounting journal '%s'") % general_journal.name)

        line_qty = 0.0
        if 'diff_purchased_qty' in self._context:
            line_qty = self._context.get('diff_purchased_qty')
        else:
            line_qty = self.product_qty - self.invoiced_qty
        if not line_qty:
            return False
        sign = reverse and -1 or 1
        return {
            'name': self.name,
            'product_id': self.product_id.id,
            'account_id': self.account_analytic_id.id,
            'unit_amount': line_qty,
            'product_uom_id': self.product_uom.id,
            'amount': sign * self._price_subtotal(line_qty),
            'general_account_id': general_account_id,
            'journal_id': general_journal.pr_commitment_analytic_journal_id.id,
            'ref': self.order_id.name,
            'user_id': self._uid,
            'doc_ref': self.order_id.name,
            'doc_id': '%s,%s' % ('purchase.order', self.order_id.id),
        }

    @api.one
    def _create_analytic_line(self, reverse=False):
        if self.account_analytic_id:
            vals = self._prepare_analytic_line(reverse=reverse)
            if vals:
                self.env['account.analytic.line'].create(vals)

    # When cancel or set done
    @api.multi
    def write(self, vals):
        # Create negative amount for the remain product_qty - invoiced_qty
        if vals.get('request_state') in ('approved'):
            self.filtered(lambda l: l.request_state not in ('approved',)).\
                _create_analytic_line(reverse=True)
        # Create negative amount for the remain product_qty - invoiced_qty
        if vals.get('request_state') in ('rejected'):
            self.filtered(lambda l: l.request_state not in ('draft',
                                                            'rejected',
                                                            'to_approve')).\
                _create_analytic_line(reverse=False)
        return super(PurchaseRequestLine, self).write(vals)

    # When partial purchased_qty
    @api.multi
    @api.depends('purchased_qty')
    def _compute_temp_purchased_qty(self):
        # As purchased_qty increased, release the commitment
        diff_purchased_qty = self.purchased_qty - self.temp_purchased_qty
        self.filtered(lambda l: l.request_state not in ('draft', 'to_approve',
                                                        'rejected')).\
            with_context(diff_purchased_qty=diff_purchased_qty).\
            _create_analytic_line(reverse=False)
        self.temp_purchased_qty = self.purchased_qty

    # ======================================================
