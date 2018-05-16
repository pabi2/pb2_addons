# -*- coding: utf-8 -*
from openerp import models, fields
from openerp import tools


class SLAPurchaseView(models.Model):
    _name = 'sla.purchase.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    voucher_id = fields.Many2one(
        'account.voucher',
        readonly=True,
    )
    count_invoice = fields.Integer(
        string='Count Invoice',
        readonly=True,
    )
    export_name = fields.Char(
        string='Export Name',
        readonly=True,
    )
    date_due = fields.Date(
        string='Date Due',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY av.id) AS id,
                   av.id AS voucher_id, COUNT(inv.id) AS count_invoice,
                   STRING_AGG(exp.name, ', ' ORDER BY exp.name) AS export_name,
                   MIN(inv.date_due) AS date_due
            FROM account_move_line l
            LEFT JOIN account_invoice inv ON l.move_id = inv.move_id
            LEFT JOIN account_move_reconcile r ON l.reconcile_id = r.id
                OR l.reconcile_partial_id = r.id
            LEFT JOIN (SELECT * FROM account_move_line
                       WHERE doctype = 'payment') l2 ON
                r.id = l2.reconcile_id OR r.id = l2.reconcile_partial_id
            LEFT JOIN account_voucher av ON l2.move_id = av.move_id
            LEFT JOIN payment_export_line exp_line ON
                av.id = exp_line.voucher_id
            LEFT JOIN payment_export exp ON exp_line.export_id = exp.id
            WHERE l.doctype IN ('in_invoice', 'in_refund') AND
                l.account_id = inv.account_id AND
                    SPLIT_PART(inv.source_document_id, ',', 1)
                        = 'purchase.order' AND av.id IS NOT NULL AND
                    av.state = 'posted'
            GROUP BY av.id
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))
