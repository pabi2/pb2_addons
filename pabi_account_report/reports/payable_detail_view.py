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
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
        readonly=True,
    )
    purchase_id = fields.Many2one(
        'purchase.order',
        string='Purchase',
        readonly=True,
    )
    voucher_id = fields.Many2one(
        'account.voucher',
        string='Voucher',
        readonly=True,
    )
    tax_id = fields.Many2one(
        'account.voucher.tax',
        string='Tax',
        readonly=True,
    )
    export_id = fields.Many2one(
        'payment.export',
        string='Export',
        readonly=True,
    )
    account_invoice_move_id = fields.Many2one(
        'account.move',
        string='Account Invoice Move',
        readonly=True,
    )
    account_invoice_move_line_id = fields.Many2one(
        'account.move.line',
        string='Account Invoice Move Line',
        readonly=True,
    )
    account_voucher_move_id = fields.Many2one(
        'account.move',
        string='Account Voucher Move',
        readonly=True,
    )
    account_voucher_move_line_id = fields.Many2one(
        'account.move.line',
        string='Account Voucher Move Line',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY avml.id) AS id,
                   inv.id AS invoice_id,
                   po.id AS purchase_id,
                   av.id AS voucher_id,
                   tax.id AS tax_id,
                   pel.export_id,
                   invml.move_id AS account_invoice_move_id,
                   invml.id AS account_invoice_move_line_id,
                   avml.move_id AS account_voucher_move_id,
                   avml.id AS account_voucher_move_line_id
            FROM (SELECT *
                  FROM account_move_line
                  WHERE doctype = 'payment') avml
            LEFT JOIN (SELECT l.*, m.date AS date_move, m.name AS move_name
                       FROM account_move_line l
                       LEFT JOIN account_move m ON l.move_id = m.id
                       WHERE l.doctype IN ('in_invoice', 'in_refund',
                                           'in_invoice_debitnote')) invml
                ON avml.reconcile_partial_id = invml.reconcile_partial_id
                OR avml.reconcile_id = invml.reconcile_id
            LEFT JOIN account_invoice inv ON invml.move_id = inv.move_id
            LEFT JOIN purchase_invoice_rel rel ON inv.id = rel.invoice_id
            LEFT JOIN purchase_order po ON rel.purchase_id = po.id
            LEFT JOIN account_voucher av ON avml.move_id = av.move_id
            LEFT JOIN payment_export_line pel ON av.id = pel.voucher_id
            LEFT JOIN account_voucher_tax tax ON inv.id = tax.invoice_id
                AND tax.voucher_id = av.id AND tax.tax_code_type = 'wht'
            WHERE avml.reconcile_partial_id IS NOT NULL OR
                  avml.reconcile_id IS NOT NULL
            ORDER BY invml.partner_id, invml.date_move, invml.move_name
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))
