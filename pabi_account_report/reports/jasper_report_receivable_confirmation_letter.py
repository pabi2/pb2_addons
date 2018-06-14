# -*- coding: utf-8 -*
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from datetime import datetime
import time


class JasperReportReceivableConfirmationLetter(models.TransientModel):
    _name = 'receivable.confirmation.letter'
    _inherit = 'report.account.common'

    fiscalyear_start_id = fields.Many2one(
        default=False,
    )
    fiscalyear_end_id = fields.Many2one(
        default=False,
    )
    filter = fields.Selection(
        readonly=True,
        default='filter_date',
    )
    date_report = fields.Date(
        string='Report Date',
        required=True,
        default=lambda self: fields.Date.context_today(self),
    )
    account_ids = fields.Many2many(
        'account.account',
        string='Accounts',
        domain=[('type', '=', 'receivable')],
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Customers',
        domain=[('customer', '=', True)],
    )

    @api.multi
    def _get_report_name(self):
        self.ensure_one()
        report_name = "receivable_confirmation_letter"
        return report_name

    @api.multi
    def _get_sql_condition(self):
        self.ensure_one()
        condition = "a.type = 'receivable'"
        if self.account_ids:
            if len(self.account_ids) > 1:
                condition += \
                    " AND a.id IN %s" % (str(tuple(self.account_ids.ids)), )
            else:
                condition += "AND a.id = %s" % (self.account_ids.id, )
        if self.partner_ids:
            if len(self.partner_ids) > 1:
                condition += " AND l.partner_id IN %s" \
                    % (str(tuple(self.partner_ids.ids)), )
            else:
                condition += " AND l.partner_id = %s" % (self.partner_ids.id, )
        # Check for History View
        condition += " AND l.date_created <= '%s' \
                      AND (l.reconcile_id IS NULL OR \
                      l.date_reconciled > '%s')" \
                      % (self.date_report, self.date_report, )
        return condition

    @api.multi
    def _get_move_line_ids(self):
        self.ensure_one()
        self._cr.execute("""
            SELECT l.id
            FROM account_move_line l
            LEFT JOIN account_account a ON l.account_id = a.id
            WHERE %s""" % (self._get_sql_condition(), ))
        move_line_ids = list(map(lambda l: l[0], self._cr.fetchall()))
        # If not found data
        if not move_line_ids:
            raise ValidationError(_('No Data!'))
        return move_line_ids

    @api.multi
    def _get_datas(self):
        self.ensure_one()
        data = {'parameters': {}}
        data['parameters']['ids'] = self._get_move_line_ids()
        date_report = datetime.strptime(self.date_report, '%Y-%m-%d')
        data['parameters']['date_report'] = date_report.strftime('%d/%m/%Y')
        data['parameters']['date_run'] = time.strftime('%d/%m/%Y')
        data['parameters']['company_name'] = \
            self.company_id.with_context(lang="th_TH").display_name
        return data

    @api.multi
    def run_report(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.report.xml',
            'report_name': self._get_report_name(),
            'datas': self._get_datas(),
        }
