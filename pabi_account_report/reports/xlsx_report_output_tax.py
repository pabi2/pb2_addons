# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp import tools


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
    
    def _select(self):
        res = """
            am.id as move_id, atd.doc_type, atd.period_id
            , am.name as move_number, am.ref as move_ref
            , to_char(ap.date_start, 'YYYY') as "year"
            , to_char(ap.date_start, 'MM') as "month"
            , atd.report_period_id, atd.tax_id, atd.invoice_date
            , atd.invoice_number, atd.taxbranch_id, atd.number_preprint
            , atd.partner_id
            , case when atd.cancel is true then 0.0
                else sum(base_company) end as base
            , case when atd.cancel is true then 0.0
                else sum(amount_company) end as amount
        """
        return res

    @api.multi
    def _compute_results(self):
        """
        Solution
        1. Get from account.tax.report.outtax
        2. Check document type is sale (doc_type = sale)
        """
        self.ensure_one()
        dom = " and atd.doc_type = 'sale' "
        Result = self.env['account.tax.report.outtax']
        if self.calendar_period_id:
            dom += " and report_period_id = {} ".format(self.calendar_period_id.id)
        if self.taxbranch_id:
            dom += " and taxbranch_id = {} ".format(self.taxbranch_id.id)
        if self.tax == 'o7':
            dom += " and at.description in ('O7','OI7') "
        if self.tax == 'o0':
            dom += " and at.description in ('O0') "
        
        self._cr.execute("""
            select %s
            from account_tax_detail atd
                left outer join res_partner rp on rp.id = atd.partner_id
                left outer join res_partner_title rpt on rp.title = rpt.id
                left outer join account_period ap on atd.period_id = ap.id
                left outer join account_move am on am.id = atd.ref_move_id
                left outer join account_tax at on at.id = atd.tax_id
            where atd.report_period_id is not null
                and (am.id is not null or atd.invoice_tax_id is not null
                    or atd.voucher_tax_id is not null)
                %s
            group by atd.invoice_number, atd.partner_id, atd.doc_type
                , atd.period_id, am.name, am.ref,report_period_id, atd.tax_id
                , atd.invoice_date, rp.name, rp.vat, rp.taxbranch, rpt.name
                , atd.cancel, am.id, ap.date_start, atd.taxbranch_id
                , atd.invoice_tax_id, atd.voucher_tax_id, atd.number_preprint
            order by year, month, atd.number_preprint
        """ % (self._select(), dom))
        
        output_ids = self._cr.dictfetchall()
        self.results = [Result.new(line).id for line in output_ids]


class AccountTaxReportOutTax(models.AbstractModel):
    _name = 'account.tax.report.outtax'
    _description = 'Account OutTax Report (pdf/xls)'

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
    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Taxbranch',
    )
    number_preprint = fields.Char(
        string='Preprint Number',
        size=500,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    base = fields.Float(
        string='Base',
    )
    amount = fields.Float(
        string='Tax',
    )

    validate_user_id = fields.Many2one(
        'res.users',
        related='move_id.validate_user_id',
        string='Validated By',
    )
