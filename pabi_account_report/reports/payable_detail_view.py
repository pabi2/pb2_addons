# -*- coding: utf-8 -*
from openerp import models, fields
from openerp import tools


class PayableDetailView(models.Model):
    _name = 'payable.detail.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    move_line_id = fields.Many2one(
        'account.move.line',
        string='Move Line',
        readonly=True,
    )
    voucher_id = fields.Many2one(
        'account.voucher',
        string='Voucher',
        readonly=True,
    )
    export_id = fields.Many2one(
        'payment.export',
        string='Export',
        readonly=True,
    )
    purchase_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        readonly=True,
    )
    tax_id = fields.Many2one(
        'account.voucher.tax',
        string='Tax',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY av.id) AS id,
                l.id AS move_line_id, av.id AS voucher_id, exp_line.export_id,
                po.id AS purchase_id, tax.id AS tax_id
            FROM account_move_line l
            LEFT JOIN account_invoice inv ON l.move_id = inv.move_id
            LEFT JOIN purchase_invoice_rel rel ON inv.id = rel.invoice_id
            LEFT JOIN purchase_order po ON rel.purchase_id = po.id
            LEFT JOIN account_move_reconcile r ON l.reconcile_id = r.id
                OR l.reconcile_partial_id = r.id
            LEFT JOIN (SELECT * FROM account_move_line
                       WHERE doctype = 'payment') l2 ON
                r.id = l2.reconcile_id OR r.id = l2.reconcile_partial_id
            LEFT JOIN account_voucher av ON l2.move_id = av.move_id
            LEFT JOIN (SELECT * FROM payment_export_line l3
                       LEFT JOIN payment_export exp ON l3.export_id = exp.id
                       WHERE exp.state = 'done') exp_line ON
                av.id = exp_line.voucher_id
            LEFT JOIN account_voucher_tax tax ON inv.id = tax.invoice_id
                AND tax.voucher_id = av.id AND tax.tax_code_type = 'wht'
            WHERE l.doctype IN ('in_invoice', 'in_refund', 'adjustment') AND
                l.account_id = inv.account_id
            ORDER BY l.partner_id
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))
