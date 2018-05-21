from openerp import models, fields, api


class XLSXReportPayableDetail(models.TransientModel):
    _name = 'xlsx.report.payable.detail'
    _inherit = 'xlsx.report'

    # Search Criteria
    account_ids = fields.Many2many(
        'account.account',
        'xlsx_report_partner_detail_account_rel',
        'report_id', 'account_id',
        string='Account(s)',
        domain=[('type', '=', 'payable')],
        required=True,
    )
    partner_ids = fields.Many2many(
        'res.partner',
        'xlsx_report_payable_detail_partner_rel',
        'report_id', 'partner_id',
        string='Supplier(s)',
        domain=[('supplier', '=', True)],
    )
    start_fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year From',
    )
    end_fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year To',
    )
    start_period_id = fields.Many2one(
        'account.period',
        string='Period From',
        domain=[('special', '=', False), ('state', '=', 'draft')],
    )
    end_period_id = fields.Many2one(
        'account.period',
        string='Period To',
        domain=[('special', '=', False), ('state', '=', 'draft')],
    )
    start_doc_posting_date = fields.Date(
        string='Document Posting Date From',
    )
    end_doc_posting_date = fields.Date(
        string='Document Posting Date To',
    )
    start_doc_date = fields.Date(
        string='Document Date From',
    )
    end_doc_date = fields.Date(
        string='Document Date To',
    )
    move_ids = fields.Many2many(
        'account.move',
        'xlsx_report_payable_detail_move_rel',
        'report', 'move_id',
        string='Document Number(s)',
        domain=[('state', '=', 'posted'),
                ('doctype', 'in', ['in_invoice', 'in_refund'])],
    )
    # Report Result
    results = fields.Many2many(
        'payable.detail.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['payable.detail.view']
        dom = [('move_line_id.account_id', 'in', self.account_ids.ids)]
        if self.partner_ids:
            dom += [('move_line_id.partner_id', 'in', self.partner_ids.ids)]
        if self.start_fiscalyear_id:
            dom += [('move_line_id.period_id.fiscalyear_id.date_start', '>=',
                     self.start_fiscalyear_id.date_start)]
        if self.end_fiscalyear_id:
            dom += [('move_line_id.period_id.fiscalyear_id.date_start', '<=',
                     self.end_fiscalyear_id.date_start)]
        if self.start_period_id:
            dom += [('move_line_id.period_id.date_start', '>=',
                     self.start_period_id.date_start)]
        if self.end_period_id:
            dom += [('move_line_id.period_id.date_start', '<=',
                     self.end_period_id.date_start)]
        if self.start_doc_posting_date:
            dom += [('move_line_id.move_id.date', '>=',
                     self.start_doc_posting_date)]
        if self.end_doc_posting_date:
            dom += [('move_line_id.move_id.date', '<=',
                     self.end_doc_posting_date)]
        if self.start_doc_date:
            dom += [('move_line_id.move_id.date_document', '>=',
                     self.start_doc_date)]
        if self.end_doc_date:
            dom += [('move_line_id.move_id.date_document', '<=',
                     self.end_doc_date)]
        if self.move_ids:
            dom += [('move_line_id.move_id', 'in', self.move_ids.ids)]
        self.results = Result.search(dom)
