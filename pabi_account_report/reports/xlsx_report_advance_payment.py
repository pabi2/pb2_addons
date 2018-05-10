from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class XLSXReportAdvancePayment(models.TransientModel):
    _name = 'xlsx.report.advance.payment'
    _inherit = 'xlsx.report'

    # Search Criteria
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        default=lambda self:
            self.env['account.account']
            .search([('code', '=', '1106010007')], limit=1),
        readonly=True,
    )
    date_report = fields.Date(
        string='Report Date',
        required=True,
    )
    # Report Result
    results = fields.Many2many(
        'account.move.line',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _account_validate(self):
        self.ensure_one()
        account = self.env['account.account'] \
            .search([('code', '=', '1106010007'),
                     '|', ('active', '=', True), ('active', '=', False)],
                    limit=1)
        if not account:
            raise ValidationError(_('There is no account 1106010007, '
                                    'please create the new account'))
        elif not account.active:
            raise ValidationError(_('Please select active = True for account '
                                    '1106010007'))

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        self._account_validate()
        self.results = self.env['account.move.line'].search(
            [('account_id', '=', self.account_id.id),
             ('reconcile_id', '=', False)])
