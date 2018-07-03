# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools


class TaxExemptionlView(models.Model):
    _name = 'tax.exemption.view'
    _auto = False

    date_invoice = fields.Date(
        string='Posting Date',
        readonly=True,
    )
    number_preprint = fields.Char(
        string='Number',
        readonly=True
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner ID',
        readonly=True,
    )
    amount_untaxed = fields.Float(
        string='Subtotal',
        readonly=True,
    )
    number = fields.Char(
        string='Document Number',
        readonly=True
    )
    document_origin = fields.Char(
        string='Document Origin',
        readonly=True
    )
    validate_user_id = fields.Many2one(
        'res.users',
        string='User ID',
        readonly=True,
    )
    move_id = fields.Many2one(
        'account.move',
        string='Move ID',
        readonly=True,
    )
    taxbranch_id = fields.Integer(
        string='Tax Branch',
        readonly=True
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT id, id AS invoice_id,
                NULL AS interface_id, date_invoice, number_preprint,
                        partner_id, amount_untaxed, source_document_id, number,
                NULL AS document_origin, validate_user_id,
                        move_id, taxbranch_id
            FROM account_invoice
            WHERE type IN ('out_invoice', 'out_refund')
                AND state NOT IN ('draft','cancel')
                AND id NOT IN
                (SELECT DISTINCT invoice_id FROM account_invoice_tax)
            UNION
            SELECT invf.id, NULL AS invoice_id, invf.id AS interface_id,
                invf_line.date AS date_invoice,
                invf.preprint_number AS number_perprint,
                invf_line.partner_id, sum(debit) AS amount_untaxed,
                NULL AS source_document_id, invf.number,
                invf.name AS document_origin, invf.validate_user_id,
                invf.move_id, invf_line.taxbranch_id
            FROM interface_account_entry invf
            INNER JOIN interface_account_entry_line invf_line
                ON invf.id = invf_line.interface_id
            WHERE invf.type = 'invoice' AND invf.state = 'done'
                AND invf.id NOT IN
                (SELECT DISTINCT invoice_id FROM account_invoice_tax)
            GROUP BY invf.id, invf_line.date, invf.preprint_number,
                invf_line.partner_id, invf.move_id, invf_line.taxbranch_id
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
        self.ensure_one()
        Result = self.env['tax.exemption.view']
        dom = []
        if self.calendar_period_id:
            dom += [('move_id.period_id', '=', self.calendar_period_id.id)]
        if self.taxbranch_id:
            dom += [('taxbranch_id', '=', self.taxbranch_id.id)]
        self.results = Result.search(dom)
