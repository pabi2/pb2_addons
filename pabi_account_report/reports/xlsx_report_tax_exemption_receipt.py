# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools


class TaxExemptionlView(models.Model):
    _name = 'tax.exemption.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    move_id = fields.Many2one(
        'account.move',
        string='Move',
        readonly=True,
    )
    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Tax Branch',
        readonly=True,
    )
    date_invoice = fields.Date(
        string='Posting Date',
        readonly=True,
    )
    number_preprint = fields.Char(
        string='Preprint Number',
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        readonly=True,
    )
    amount_untaxed = fields.Float(
        string='Subtotal',
        readonly=True,
    )
    amount_tax = fields.Float(
        string='Tax',
        readonly=True,
    )
    source_document_id = fields.Reference(
        [('purchase.order', 'Purchase'),
         ('sale.order', 'Sales'),
         ('hr.expense.expense', 'HR Expense')],
        string='Source Document Ref.',
        readonly=True,
    )
    number = fields.Char(
        string='Document Number',
        readonly=True,
    )
    document_origin = fields.Char(
        string='Document Origin',
        readonly=True,
    )
    validate_user_id = fields.Many2one(
        'res.users',
        string='Validated By',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY invoice.move_id) AS id, *
            FROM
                ((SELECT move_id, taxbranch_id, date_invoice, number_preprint,
                         partner_id, amount_untaxed, amount_tax,
                         source_document_id, number, NULL AS document_origin,
                         validate_user_id
                  FROM account_invoice
                  WHERE type IN ('out_invoice', 'out_refund')
                    AND state NOT IN ('draft', 'cancel'))
                 UNION ALL
                 (SELECT iae.move_id, iael.taxbranch_id,
                         iael.date AS date_invoice,
                         iae.preprint_number AS number_preprint,
                         iael.partner_id, SUM(iael.debit) AS amount_untaxed,
                         (SELECT SUM(amount)
                          FROM account_tax_detail
                          WHERE ref_move_id = iae.move_id
                          GROUP BY ref_move_id) AS amount_tax,
                         NULL AS source_document_id, iae.number,
                         iae.name AS document_origin, iae.validate_user_id
                  FROM interface_account_entry iae
                  LEFT JOIN interface_account_entry_line iael
                    ON iae.id = iael.interface_id
                  WHERE iae.type = 'invoice' AND iae.state = 'done'
                  GROUP BY iae.id, iael.taxbranch_id, iael.date,
                           iael.partner_id)) invoice
            WHERE invoice.move_id NOT IN
                (SELECT DISTINCT ref_move_id
                 FROM account_tax_detail
                 WHERE ref_move_id IS NOT NULL)
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


class XLSXReportTaxExemptionReceipt(models.TransientModel):
    _name = 'xlsx.report.tax.exemption.receipt'
    _inherit = 'report.account.common'

    filter = fields.Selection(
        readonly=True,
        default='filter_period',
    )
    calendar_period_id = fields.Many2one(
        'account.period.calendar',
        string='Calendar Period',
        required=True,
    )
    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Taxbranch',
        required=True,
    )
    results = fields.Many2many(
        'tax.exemption.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        """
        Solution
        1. Get from customer invoice, cutomer refund, invoice entries
           (exclude tax)
        """
        self.ensure_one()
        Result = self.env['tax.exemption.view']
        dom = []
        if self.calendar_period_id:
            dom += [('move_id.period_id', '=', self.calendar_period_id.id)]
        if self.taxbranch_id:
            dom += [('taxbranch_id', '=', self.taxbranch_id.id)]
        self.results = Result.search(dom)
