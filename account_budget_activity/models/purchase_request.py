# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
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

    @api.multi
    def button_approved(self):
        for request in self:
            for line in request.line_ids:
                Analytic = self.env['account.analytic.account']
                line.analytic_account_id = \
                    Analytic.create_matched_analytic(line)
        return super(PurchaseRequest, self).button_approved()

    @api.multi
    def write(self, vals):
        # Create analytic when approved by PRWeb and be come To Accept in PR
        if vals.get('state') in ['to_approve']:
            self.line_ids.filtered(lambda l:
                                   l.request_state not in ('to_approve',)).\
                _create_analytic_line(reverse=True)
        # Create negative amount for the remain product_qty - invoiced_qty
        if vals.get('state') in ['rejected']:
            self.line_ids.filtered(lambda l:
                                   l.request_state not in ('draft',
                                                           'rejected',)).\
                _create_analytic_line(reverse=False)
        return super(PurchaseRequest, self).write(vals)


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
    price_unit = fields.Float(
        string='Unit Price',
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
    # DO NOT DELETE, Pending decision on what to use.
    #     @api.model
    #     def _get_account_id_from_pr_line(self):
    #         account = self.activity_group_id.account_id
    #         # If not exist, use the default expense account
    #         if not account:
    #             prop = self.env['ir.property'].search(
    #                 [('name', '=', 'property_account_expense_categ')])
    #             account = prop.get_by_record(prop)
    #         return account and account.id or False

    @api.model
    def _price_subtotal(self, line_qty):
        return self.price_unit * line_qty

    @api.model
    def _prepare_analytic_line(self, reverse=False):
        # general_account_id = self._get_account_id_from_pr_line()
        general_journal = self.env['account.journal'].search(
            [('type', '=', 'purchase'),
             ('company_id', '=', self.company_id.id)], limit=1)
        if not general_journal:
            raise Warning(_('Define an accounting journal for purchase'))
        if not general_journal.is_budget_commit:
            return False
        if not general_journal.pr_commitment_analytic_journal_id or \
                not general_journal.pr_commitment_account_id:
            raise UserError(
                _("No analytic journal for PR commitment defined on the "
                  "accounting journal '%s'") % general_journal.name)

        # Use PR Commitment Account
        general_account_id = general_journal.pr_commitment_account_id.id

        line_qty = 0.0
        if 'diff_purchased_qty' in self._context:
            line_qty = self._context.get('diff_purchased_qty')
        else:
            line_qty = self.product_qty - self.purchased_qty
        if not line_qty:
            return False
        sign = reverse and -1 or 1
        return {
            'name': self.name,
            'product_id': False,
            'account_id': self.analytic_account_id.id,
            'unit_amount': line_qty,
            'product_uom_id': False,
            'amount': sign * self._price_subtotal(line_qty),
            'general_account_id': general_account_id,
            'journal_id': general_journal.pr_commitment_analytic_journal_id.id,
            'ref': self.request_id.name,
            'user_id': self._uid,
            'doc_ref': self.request_id.name,
            'doc_id': '%s,%s' % ('purchase.request', self.request_id.id),
        }

    @api.one
    def _create_analytic_line(self, reverse=False):
        vals = self._prepare_analytic_line(reverse=reverse)
        if vals:
            self.env['account.analytic.line'].create(vals)

    # When partial purchased_qty
    @api.multi
    @api.depends('purchased_qty')
    def _compute_temp_purchased_qty(self):
        # As purchased_qty increased, release the commitment
        for rec in self:
            # On compute filed of temp_purchased_qty, ORM is not working
            self._cr.execute("""
                select temp_purchased_qty
                from purchase_request_line where id = %s
            """, (rec.id,))
            temp_purchased_qty = self._cr.fetchone()[0] or 0.0
            diff_purchased_qty = rec.purchased_qty - temp_purchased_qty
            if rec.request_state not in ('draft', 'to_approve', 'rejected'):
                rec.with_context(diff_purchased_qty=diff_purchased_qty).\
                    _create_analytic_line(reverse=False)
            rec.temp_purchased_qty = rec.purchased_qty

    # ======================================================
