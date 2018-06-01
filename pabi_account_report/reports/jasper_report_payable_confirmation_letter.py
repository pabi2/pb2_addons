# -*- coding: utf-8 -*
import time
from datetime import datetime
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class JasperReportPayableConfirmationLetter(models.TransientModel):
    _name = 'payable.confirmation.letter'
    _inherit = 'report.account.common'

    fiscalyear_ids = fields.Many2many(
        default=False,
    )
    date_from = fields.Date(
        default=False,
    )
    date_to = fields.Date(
        default=False,
    )
    filter = fields.Selection(
        [('filter_date', 'Date')],
        string='Filter by',
        required=True,
        default='filter_date',
    )
    date_report = fields.Date(
        string='Report Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
    )
    account_ids = fields.Many2many(
        'account.account',
        'jasper_report_payable_confirmation_letter_account_rel',
        'report_id', 'account_id',
        string='Filter on accounts',
        help='''Only selected accounts will be printed.
                Leave empty to print all accounts.''',
    )
    partner_ids = fields.Many2many(
        'res.partner',
        'jasper_report_payable_confirmation_letter_partner_rel',
        'report_id', 'partner_id',
        string='Filter on partners',
        help='''Only selected partners will be printed.
                Leave empty to print all partners.''',
    )

    @api.multi
    def run_report(self):
        self.ensure_one()
        data = {'parameters': {}}
        report_name = 'payable_confirmation_letter'
        condition = "a.type = 'payable'"
        if self.account_ids:
            if len(self.account_ids) > 1:
                condition += \
                    " AND a.id IN %s" % (str(tuple(self.account_ids.ids)))
            else:
                condition += \
                    " AND a.id = %s" % (self.account_ids.id)
        if self.partner_ids:
            if len(self.partner_ids) > 1:
                condition += " AND l.partner_id IN %s" \
                    % (str(tuple(self.partner_ids.ids)))
            else:
                condition += " AND l.partner_id = %s" % (self.partner_ids.id)
        if self.date_report:
            condition += " AND l.date_created <= '%s' \
                          AND (l.reconcile_id IS NULL OR \
                          l.date_reconciled > '%s')" \
                          % (self.date_report, self.date_report)
        self._cr.execute("""
            SELECT l.id
            FROM account_move_line l
            LEFT JOIN account_account a ON l.account_id = a.id
            WHERE %s""" % (condition, ))
        move_line_ids = list(map(lambda l: l[0], self._cr.fetchall()))
        if not move_line_ids:
            raise ValidationError(_('No Data!'))
        data['parameters']['ids'] = move_line_ids
        data['parameters']['date_run'] = time.strftime('%d/%m/%Y')
        data['parameters']['date_report'] = \
            datetime.strptime(self.date_report, '%Y-%m-%d') \
            .strftime('%d/%m/%Y')
        data['parameters']['company_name'] = self.company_id.name
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
        }
        return res
