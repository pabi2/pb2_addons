# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    late_delivery_work_acceptance_id = fields.Many2one(
        'purchase.work.acceptance',
        string='Late Delivery Acceptance',
        domain=[('total_fine', '>', 0.0), ('invoiced', '=', False)],
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="List Purchase Work Acceptance with total_fine > 0.0 "
        "and not already invoiced",
    )

    @api.model
    def _get_account_id_from_product(self, product, fpos):
        account_id = product.property_account_expense.id
        if not account_id:
            categ = product.categ_id
            account_id = categ.property_account_expense_categ.id
        if not account_id:
            raise ValidationError(
                _('Define an expense account for this '
                  'product: "%s" (id:%d).') %
                (product.name, product.id,))
        if fpos:
            account_id = fpos.map_account(account_id)
        return account_id

    @api.onchange('late_delivery_work_acceptance_id')
    def _onchange_late_delivery_work_acceptance_id(self):
        # This method is called from Customer invoice to charge penalty
        if self.late_delivery_work_acceptance_id:
            self.invoice_line = []
            acceptance = self.late_delivery_work_acceptance_id
            self.taxbranch_id = acceptance.order_id.taxbranch_id
            penalty_line = self.env['account.invoice.line'].new()
            amount_penalty = acceptance.total_fine_cal
            if acceptance.is_manual_fine:
                amount_penalty = acceptance.manual_fine
            company = self.env.user.company_id
            activity_group = company.delivery_penalty_activity_group_id
            activity = company.delivery_penalty_activity_id
            if not activity_group or not activity:
                raise ValidationError(_('No AG/A for late delivery has been '
                                        'set in Account Settings!'))
            sign = self.type in ('out_invoice', 'out_refund') and 1 or -1
            penalty_line.activity_group_id = activity_group
            penalty_line.activity_id = activity
            penalty_line.account_id = activity.account_id
            penalty_line.name = (u'%s WA เลขที่ %s' %
                                 (activity.account_id.name, acceptance.name,))
            penalty_line.quantity = 1.0
            penalty_line.price_unit = sign * amount_penalty
            # If chart field is required, try getting from the PO line
            if penalty_line.require_chartfield:
                purchase = self.late_delivery_work_acceptance_id.order_id
                lines = purchase.order_line.filtered('require_chartfield').\
                    sorted(lambda l: l.price_subtotal, reverse=True)
                if lines:
                    penalty_line.project_id = lines[0].project_id
                    penalty_line.section_id = lines[0].section_id
                    penalty_line.invest_asset_id = lines[0].invest_asset_id
                    penalty_line.invest_construction_phase_id = \
                        lines[0].invest_construction_phase_id
                    penalty_line.fund_id = lines[0].fund_id
                    penalty_line.cost_control_id = lines[0].cost_control_id
            self.invoice_line += penalty_line
