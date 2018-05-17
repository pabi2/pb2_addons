from openerp import models, fields, api


class XLSXReportSLAEmployee(models.TransientModel):
    _name = 'xlsx.report.sla.employee'
    _inherit = 'xlsx.report'

    # Search Criteria
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
    user_ids = fields.Many2many(
        'res.users',
        'xlsx_report_sla_employee_users',
        'report_id', 'user_id',
        string='Responsible By',
    )
    category_id = fields.Many2one(
        'res.partner.category',
        string='Supplier Category',
    )
    # Report Result
    results = fields.Many2many(
        'sla.employee.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['sla.employee.view']
        dom = []
        if self.start_period_id:
            dom += [('voucher_id.period_id.date_start', '>=',
                     self.start_period_id.date_start)]
        if self.end_period_id:
            dom += [('voucher_id.period_id.date_start', '<=',
                     self.end_period_id.date_start)]
        if self.user_ids:
            dom += [('voucher_id.create_uid', 'in', self.user_ids.ids)]
        if self.category_id:
            dom += [('voucher_id.partner_id.category_id', '=',
                     self.category_id.id)]
        self.results = Result.search(dom)
