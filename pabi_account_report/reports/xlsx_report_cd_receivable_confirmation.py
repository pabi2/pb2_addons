# -*- coding: utf-8 -*-
from openerp import models, fields, api


class XLSXReportCDReceivableConfirmation(models.TransientModel):
    _name = 'xlsx.report.cd.receivable.confirmation'
    _inherit = 'report.account.common'

    borrower_partner_ids = fields.Many2many(
        'res.partner',
        'confirmation_borrower_partner_rel',
        'confirmation_id', 'partner_id',
        string='Customer CD',
        domain=[('customer', '=', True)],
    )
    partner_ids = fields.Many2many(
        'res.partner',
        'confirmation_partner_rel',
        'confirmation_id', 'partner_id',
        string='Customer (bank)',
        domain=[('customer', '=', True)],
    )
    results = fields.Many2many(
        'loan.customer.agreement',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['loan.customer.agreement']
        dom = [('state', 'in', ['bank_paid']),
               ('sale_id.state', 'in', ['progress'])]
        if self.borrower_partner_ids:
            dom += [('borrower_partner_id', 'in',
                     self.borrower_partner_ids.ids)]
        if self.partner_ids:
            dom += [('partner_id', 'in', self.partner_ids.ids)]
        self.results = Result.search(dom).sorted(
            lambda l: l.borrower_partner_id.search_key)
