# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp import tools

class AccountTaxReportOutTax(models.Model):
    _name = 'account.tax.report.outtax'
    #_inherit = 'account.tax.detail'
    _description = 'Account OutTax Report (pdf/xls)'
    _auto = False

    move_id = fields.Many2one(
        'account.move',
        string='Move',
        readonly=True,
    )
    doc_type = fields.Selection(
        [('sale', 'Sales'),
         ('purchase', 'Purchase')],
        string='Type',
    )
    period_id = fields.Many2one(
        'account.period',
        string='Period',
    )
    move_number = fields.Char(
        string='JE Number',
        size=500,
    )
    move_ref = fields.Char(
        string='JE Ref.',
        size=500,
        help="Original Document",
    )
    year = fields.Char(
        string='Year',
        size=4,
    )
    month = fields.Char(
        string='Month',
        size=100,
    )
    report_period_id = fields.Many2one(
        'account.period',
        string='Reporting Period',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    partner_name = fields.Char(
        string='Partner Name',
        size=500,
    )
    partner_title = fields.Char(
        string='Partner Title',
        size=500,
    )
    tax_id = fields.Many2one(
        'account.tax',
        string='Tax',
    )
    invoice_date = fields.Date(
        string='Invoice Date',
    )
    invoice_number = fields.Char(
        string='Invoice Number',
        size=20,
    )
    base = fields.Float(
        string='Base',
    )
    amount = fields.Float(
        string='Tax',
    )
    number_preprint = fields.Char(
        string='Preprint Number',
        size=500,
    )
    validate_user_id = fields.Many2one(
        'res.users',
        related='move_id.validate_user_id',
        string='Validated By',
    )
    def _select(self):
        res = """
            doc_type, ROW_NUMBER() OVER(ORDER BY invoice_number, am.name) AS id, atd.period_id, am.name as move_number, am.ref as move_ref, am.id as move_id, 
            to_char(ap.date_start, 'YYYY') as "year", to_char(ap.date_start, 'MM') as "month", report_period_id, tax_id, invoice_date, invoice_number, atd.partner_id,
            atd.taxbranch_id,atd.invoice_tax_id,atd.voucher_tax_id,atd.number_preprint,
            case when cancel is true then ''
                else rp.name end as partner_name,
            case when cancel is true then ''
                else rpt.name end as partner_title,
            case when cancel is true then ''
                else rp.vat end as vat,
            case when cancel is true then ''
                else rp.taxbranch end as taxbranch,
            case when cancel is true then 0.0
                else sum(base_company) end as base,
            case when cancel is true then 0.0
                else sum(amount_company) end as amount 
        """
        return res

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            select %s
            from account_tax_detail atd
            left outer join res_partner rp on rp.id = atd.partner_id
            left outer join res_partner_title rpt on rp.title = rpt.id
            left outer join account_period ap on atd.period_id = ap.id
            left outer join account_move am on am.id = atd.ref_move_id
            where report_period_id is not null
            group by invoice_number, atd.partner_id,doc_type,atd.period_id, am.name, am.ref,report_period_id, tax_id, invoice_date, rp.name,rp.vat,rp.taxbranch,rpt.name,cancel, am.id,
                  ap.date_start,atd.taxbranch_id,atd.invoice_tax_id,atd.voucher_tax_id,atd.number_preprint
            order by year, month
        )""" % (self._table, self._select(), )
        )
class XLSXReportOutputTax(models.TransientModel):
    _name = 'xlsx.report.output.tax'
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
        [('o0', 'O0'),
         ('o7', 'O7')],
        string='Tax',
    )
    results = fields.Many2many(
        'account.tax.report.outtax',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        """
        Solution
        1. Get from account.tax.report.outtax
        2. Check document type is sale (doc_type = sale)
        """
        self.ensure_one()
        model = 'account.tax.report.outtax'
        where = "doc_type = 'sale' \
                 and (move_id is not null or invoice_tax_id is not null or \
                 voucher_tax_id is not null)"
        if self.calendar_period_id:
            where += " and report_period_id = %s" \
                % (str(self.calendar_period_id.id))
        if self.taxbranch_id:
            where += " and taxbranch_id = %s" % (str(self.taxbranch_id.id))
        if self.tax == 'o7':
            where += " and tax in ('O7', 'OI7')"
        if self.tax == 'o0':
            where += " and tax = 'O0'"
        self._cr.execute("""
            select id from %s where %s""" % (model.replace('.', '_'), where))
        report_ids = map(lambda l: l[0], self._cr.fetchall())
        # --
        Result = self.env[model]
        dom = [('id', '=', 0)]
        if report_ids:
            dom = [('id', 'in', report_ids)]
        self.results = Result.search(dom, order='number_preprint')
