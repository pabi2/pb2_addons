# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime
import time


class JasperReportCDReceivableFollowUp(models.TransientModel):
    _name = 'jasper.report.cd.receivable.follow.up'
    _inherit = 'report.account.common'

    filter = fields.Selection(
        readonly=True,
        default='filter_date',
    )
    date_report = fields.Date(
        string='Report Date',
        required=True,
        default=lambda self: fields.Date.context_today(self),
    )
    groupby = fields.Selection(
        [('groupby_borrower_partner', 'Customer CD'),
         ('groupby_partner', 'Customer (bank)')],
        string='Group By',
        default='groupby_borrower_partner',
        required=True,
    )
    borrower_partner_ids = fields.Many2many(
        'res.partner',
        'receivable_follow_borrower_partner_rel',
        'follow_id', 'partner_id',
        string='Customer CD',
        domain=[('customer', '=', True)],
    )
    partner_ids = fields.Many2many(
        'res.partner',
        'receivable_follow_partner_rel',
        'follow_id', 'partner_id',
        string='Customer (bank)',
        domain=[('customer', '=', True)],
    )

    @api.onchange('groupby')
    def _onchange_groupby(self):
        self.borrower_partner_ids = False
        self.partner_ids = False

    @api.multi
    def _get_report_name(self):
        self.ensure_one()
        report_name = "cd_receivable_follow_up_group_by_customer"
        if self.groupby == 'groupby_partner':
            report_name = "cd_receivable_follow_up_group_by_bank"
        return report_name

    @api.multi
    def _get_domain(self):
        self.ensure_one()
        dom = [('loan_agreement_id.state', 'in', ('bank_paid', 'done')),
               ('loan_agreement_id.sale_id.state', 'in', ('progress', 'done')),
               ('invoice_plan_id.ref_invoice_id.date_paid', '=', False),
               ('invoice_plan_id.ref_invoice_id.cancel_move_id', '=', False),
               ('invoice_plan_id.ref_invoice_id.date_due', '<=',
                self.date_report)]
        if self.borrower_partner_ids:
            dom += [('loan_agreement_id.borrower_partner_id', 'in',
                     self.borrower_partner_ids.ids)]
        if self.partner_ids:
            dom += [('loan_agreement_id.partner_id', 'in',
                     self.partner_ids.ids)]
        return dom

    @api.multi
    def _get_datas(self):
        self.ensure_one()
        data = {'parameters': {}}
        dom = self._get_domain()
        data['ids'] = \
            self.env['pabi.common.loan.agreement.report.view'].search(dom).ids
        date_report = datetime.strptime(self.date_report, '%Y-%m-%d')
        data['parameters']['date_report'] = date_report.strftime('%d/%m/%Y')
        data['parameters']['user'] = self.env.user.display_name
        data['parameters']['date_run'] = time.strftime('%d/%m/%Y')
        return data

    @api.multi
    def run_report(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.report.xml',
            'report_name': self._get_report_name(),
            'datas': self._get_datas(),
        }
