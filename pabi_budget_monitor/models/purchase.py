# -*- coding: utf-8 -*-
from openerp import api, models, fields
from openerp.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def _purchase_budget_check(self):
        Budget = self.env['account.budget']
        for purchase in self:
            doc_date = purchase.date_order
            doc_lines = Budget.convert_lines_to_doc_lines(purchase.order_line)
            res = Budget.post_commit_budget_check(doc_date, doc_lines)
            if not res['budget_ok']:
                raise ValidationError(res['message'])
        return True

    @api.multi
    def wkf_confirm_order(self):
        res = super(PurchaseOrder, self).wkf_confirm_order()
        self._purchase_budget_check()
        return res

    budget_error = fields.Boolean(
        string='Budget Error',
        compute='_compute_budget_error',
        search='_search_budget_error',
        help="Show PO that invoice/picking do not return actual properly",
    )

    @api.model
    def _get_budget_error_sql(self):
        return """
            select purchase_id
            from (
                select purchase_id, amount_untaxed,
                    coalesce(po_commit, 0.0) po_commit,
                    coalesce(inv_actual, 0.0) inv_actual,
                    coalesce(stock_actual, 0.0) stock_actual
                from (
                    select id purchase_id, state, name, amount_untaxed,
                        -- PO commit
                        (select sum(-amount) from account_analytic_line aal
                         where aal.purchase_id = po.id) po_commit,
                        -- invoice actual
                        (select sum(-amount) from account_analytic_line aal
                         where aal.move_id in (
                            select aml.id from account_move_line aml
                            join account_move am on am.id = aml.move_id
                            join account_invoice av on
                                (av.move_id = am.id or
                                 av.cancel_move_id = am.id)
                            join purchase_order po2 on
                                po2.name = av.source_document
                            where po2.id = po.id)) inv_actual,
                        -- stock actual
                        (select sum(-amount) from account_analytic_line aal
                         where aal.move_id in (
                            select aml.id from account_move_line aml
                            join account_move am on am.id = aml.move_id
                            join stock_picking pick on
                                pick.name = am.document
                            join purchase_order po2 on
                                po2.name = pick.origin
                            where po2.id = po.id)) stock_actual

                        from purchase_order po where state not in
                            ('draft', 'cancel') and currency_id = 140
                            and order_type = 'purchase_order'
                        -- Not COD migration case case where its
                        -- invoice is paid without number
                        and po.id not in (
                            select purchase_id from purchase_invoice_rel
                            where invoice_id in (select id
                                from account_invoice where state != 'draft'
                                and number is null))
                ) a ) b
                where (inv_actual + po_commit + stock_actual)
                    != amount_untaxed
        """

    @api.multi
    def _compute_budget_error(self):
        if self.ids:
            sql = self._get_budget_error_sql()
            self._cr.execute(
                sql + " and purchase_id in %s", (tuple(self.ids),))
        purchase_ids = [row[0] for row in self._cr.fetchall()]
        for po in self:
            if po.id in purchase_ids:
                po.budget_error = True
            else:
                po.budget_error = False
        return True

    @api.model
    def _search_budget_error(self, operator, value):
        budget_error_po_ids = []
        if operator == '=' and value:
            self._cr.execute(self._get_budget_error_sql())
            budget_error_po_ids = [row[0] for row in self._cr.fetchall()]
        return [('id', 'in', budget_error_po_ids)]
