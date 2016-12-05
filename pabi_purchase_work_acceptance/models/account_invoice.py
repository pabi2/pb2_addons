# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    late_delivery_work_acceptance_id = fields.Many2one(
        'purchase.work.acceptance',
        string="Late Delivery Acceptance",
        domain=[('total_fine', '>', 0.0), ('invoiced', '=', False)],
        copy=False,
        help="List Purchase Work Acceptance which has a penalty amount"
    )

    # No longer need as we change ways doing domain
    # @api.multi
    # def onchange_partner_id(self, ttype, partner_id, date_invoice=False,
    #                         payment_term=False, partner_bank_id=False,
    #                         company_id=False):
    #     res = super(AccountInvoice, self).onchange_partner_id(
    #         ttype, partner_id, date_invoice=date_invoice,
    #         payment_term=payment_term, partner_bank_id=partner_bank_id,
    #         company_id=company_id)
    #     if not res:
    #         res = {}
    #     if 'value' not in res:
    #         res['value'] = {}
    #     if 'domain' not in res:
    #         res['domain'] = {}
    #
    #     res['value'].update({'late_delivery_work_acceptance_id': False})
    #     if not partner_id:
    #         domain = [('id', 'in', [])]
    #        res['domain'].update({'late_delivery_work_acceptance_id': domain})
    #     else:
    #         self._cr.execute("""
    #             select id from purchase_work_acceptance
    #             where partner_id = %s and total_fine > 0
    #             and state = 'done'
    #          and id not in (select distinct late_delivery_work_acceptance_id
    #                         from account_invoice where partner_id = %s
    #                         and late_delivery_work_acceptance_id is not null
    #                         and state in ('open', 'paid'))
    #             order by id
    #         """, (partner_id, partner_id,))
    #         invoice_ids = [x[0] for x in self._cr.fetchall()]
    #         domain = [('id', 'in', invoice_ids)]
    #        res['domain'].update({'late_delivery_work_acceptance_id': domain})
    #     return res

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
            penalty_line = self.env['account.invoice.line'].new()
            amount_penalty = acceptance.total_fine
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
