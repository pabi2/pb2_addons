# -*- coding: utf-8 -*
from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class PabiLongTermInvestmentReportWizard(models.TransientModel):
    _name = 'pabi.long.term.investment.report.wizard'

    account_id = fields.Many2one(
        'account.account',
        string='Account Name',
        required=True,
        readonly=True,
        default=lambda self:
            self.env.user.company_id.longterm_invest_account_id,
        help="Please specific account name in menu \
              Settings > Configuration > Accounting \
              (Section Long Term Investment)"
    )
    date_print = fields.Date(
        string='Print Date',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        domain=[('supplier', '=', True)],
    )

    @api.multi
    def xls_export(self):
        return self.check_report()

    @api.multi
    def check_report(self):
        context = self._context.copy()
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(
            ['account_id',  'date_print',  'partner_id'])[0]
        for field in ['account_id', 'date_print', 'partner_id']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        return self.print_report(data)

    @api.multi
    def print_report(self, data):
        context = self._context.copy()
        if context.get('xls_export', False):
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'pabi_long_term_investment_report_xls',
                'datas': data,
            }
        raise except_orm(_('Error !'), _('The report has not yet.'))
