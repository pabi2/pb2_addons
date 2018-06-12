# -*- coding: utf-8 -*
from openerp import models, fields, api, tools


class XLSXReportCDReceivableConfirmation(models.TransientModel):
    _name = 'xlsx.report.cd.receivable.confirmation'
    _inherit = 'report.account.common'

    filter = fields.Selection(
        default='filter_date',
        readonly=True,
    )
    date_report = fields.Date(
        string='Report Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Customers',
        domain=[('customer', '=', True)],
    )
    bank_ids = fields.Many2many(
        'res.bank',
        string='Banks',
    )
    results = fields.Many2many(
        'cd.receivable.confirmation.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['cd.receivable.confirmation.view']
        dom = []
        if self.partner_ids:
            dom += [('loan_agreement_id.borrower_partner_id', 'in',
                     self.partner_ids.ids)]
        if self.bank_ids:
            dom += [('loan_agreement_id.bank_id.bank', 'in',
                     self.bank_ids.ids)]
        # Check for history view
        dom += [('loan_agreement_id.state', '=', 'bank_paid'),
                ('loan_agreement_id.supplier_invoice_id.date_paid', '<=',
                 self.date_report),
                '|', ('invoice_id.date_paid', '=', False),
                ('invoice_id.date_paid', '>', self.date_report),
                '|', ('invoice_id.cancel_move_id', '=', False),
                ('invoice_id.cancel_move_id.create_date', '>',
                 self.date_report)
                ]
        self.results = Result.search(dom)


class CDReceivableConfirmationView(models.Model):
    _name = 'cd.receivable.confirmation.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    loan_agreement_id = fields.Many2one(
        'loan.customer.agreement',
        string='Loan Agreement',
        reaonly=True,
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY lca.id, inv.id) AS id,
                   lca.id AS loan_agreement_id,
                   inv.id AS invoice_id
            FROM loan_customer_agreement lca
            LEFT JOIN sale_order so ON lca.sale_id = so.id
            LEFT JOIN sale_invoice_plan sip ON so.id = sip.order_id
            LEFT JOIN account_invoice inv ON sip.ref_invoice_id = inv.id
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))
