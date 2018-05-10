from openerp import models, fields, api


class XLSXReportPurchaseContract(models.TransientModel):
    _name = 'xlsx.report.purchase.contract'
    _inherit = 'xlsx.report'

    # Search Criteria
    date_report = fields.Date(
        string='Report Date',
        required=True,
    )
    # Report Result
    results = fields.Many2many(
        'purchase.contract',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        self.results = self.env['purchase.contract'].search(
            [('collateral_remand_date', '>=', self.date_report)])
