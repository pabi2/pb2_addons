from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class XLSXReportChequeReport(models.TransientModel):
    _name = 'xlsx.report.cheque.register'
    _inherit = 'xlsx.report'

    # Search Criteria
    cheque_lot_ids = fields.Many2many(
        'cheque.lot',
        string='Cheque Lot(s)',
    )
    number_from = fields.Char(
        string='From Cheque Number',
    )
    number_to = fields.Char(
        string='To Cheque Number',
    )
    status = fields.Selection(
        [('active', 'Active'),
         ('inactive', 'Inactive')],
        string='Status',
    )
    # Report Result
    results = fields.Many2many(
        'cheque.register',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['cheque.register']
        dom = []
        if self.cheque_lot_ids:
            dom += [('cheque_lot_id', 'in', self.cheque_lot_ids.ids)]
        if self.number_from:
            dom += [('number', '>=', self.number_from)]
        if self.number_to:
            dom += [('number', '<=', self.number_to)]
        if self.status:
            dom += [('cheque_lot_id.state', '=', self.status)]
        if not dom:
            raise ValidationError(
                _('Please input criteria to limit resulting data set!'))
        self.results = Result.search(dom)
