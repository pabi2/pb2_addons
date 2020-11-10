# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools


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
        default=lambda self: self.env['account.period.calendar'].find(),
    )
    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Taxbranch',
        required=True,
    )
    tax = fields.Selection(
        [('OX', 'OX')],
        string='Tax',
        default='OX',
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
        where_str = ""
        if self.calendar_period_id:
            where_str += " AND am.period_id = %s" % str(self.calendar_period_id.id)
        if self.taxbranch_id:
            where_str += " AND rtb.id = %s" % str(self.taxbranch_id.id)
        if self.tax:
            where_str += " AND at.description = '%s'" % self.tax

        self._cr.execute("""
            ((SELECT inv.move_id, inv.taxbranch_id, inv.date_invoice,
                STRING_AGG(DISTINCT atd.invoice_number, ', ') as number_preprint,
                inv.partner_id, SUM(atd.base) AS amount_untaxed, inv.amount_tax,
                inv.source_document_id, inv.number, NULL AS document_origin,
                inv.validate_user_id
            FROM account_invoice inv
                LEFT JOIN account_invoice_line invl on invl.invoice_id = inv.id
                LEFT JOIN account_invoice_line_tax ailt on ailt.invoice_line_id = invl.id
                LEFT JOIN account_tax at on at.id = ailt.tax_id
                LEFT JOIN account_move am on am.id = inv.move_id
                LEFT JOIN res_taxbranch rtb on rtb.id = inv.taxbranch_id
                LEFT JOIN account_tax_detail atd on atd.ref_move_id = am.id
            WHERE inv.type IN ('out_invoice', 'out_refund')
                AND inv.state NOT IN ('draft', 'cancel')
                %s
            GROUP BY inv.move_id, inv.taxbranch_id, inv.date_invoice,
                inv.partner_id, inv.amount_untaxed, inv.amount_tax, inv.source_document_id,
                inv.number, inv.validate_user_id
            )
            UNION ALL
            (SELECT iae.move_id, iael.taxbranch_id,
                iael.date AS date_invoice,
                STRING_AGG(DISTINCT atd.invoice_number, ', ') AS number_preprint,
                iael.partner_id, SUM(atd.base) AS amount_untaxed,
                (SELECT ABS(SUM(credit) - SUM(debit))
                FROM interface_account_entry_line
                WHERE tax_id IS NOT NULL AND interface_id = iae.id
                GROUP BY interface_id) AS amount_tax,
                NULL AS source_document_id, iae.number,
                iae.name AS document_origin, iae.validate_user_id
            FROM interface_account_entry iae
            LEFT JOIN interface_account_entry_line iael
            ON iae.id = iael.interface_id
            LEFT JOIN account_move am on am.id = iae.move_id
            LEFT JOIN account_tax at on at.id = iael.tax_id
            LEFT JOIN res_taxbranch rtb on rtb.id = iael.taxbranch_id
            LEFT JOIN account_tax_detail atd on atd.ref_move_id = am.id
            WHERE iae.type = 'invoice' AND iae.state = 'done'
                %s
            GROUP BY iae.id, iael.taxbranch_id, iael.date, iael.tax_id,
                iael.partner_id))
        """  % (where_str, where_str))

        line_ids = self._cr.dictfetchall()
        self.results = [Result.new(line).id for line in line_ids]


class TaxExemptionlView(models.AbstractModel):
    _name = 'tax.exemption.view'
    #_auto = False

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
