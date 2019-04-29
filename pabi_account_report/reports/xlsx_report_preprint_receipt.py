# -*- coding: utf-8 -*-
from openerp import models, fields, api
from EpsImagePlugin import field

class AccountMove(models.Model):
    _inherit = 'account.move'

    preprint_number = fields.Char(
        string='Preprint Number',
        compute='_compute_preprint_number',
    )
    
    @api.multi
    def _compute_preprint_number(self):
        for move in self:
            if move.doctype == 'receipt':
                Fund = self.env['account.voucher'] 
                domain = ([('move_id', '=', move.id)])
                lines = Fund.search(domain)
                move.preprint_number = lines.number_preprint
            if move.doctype == 'interface_account': 
                Fund = self.env['interface.account.entry'] 
                domain = ([('move_id', '=', move.id)])
                lines = Fund.search(domain)
                move.preprint_number = lines.preprint_number
            if move.doctype == 'adjustment': 
                Fund = self.env['account.tax.detail'] 
                domain = ([('ref_move_id', '=', move.id),('amount', '=', 0)])
                lines = Fund.search(domain)
                move.preprint_number = lines.invoice_number
                
                
                
class XLSXReportGlProject(models.TransientModel):
    _name = 'xlsx.report.preprint.receipt'
    _inherit = 'report.account.common'

    postingdate_start = fields.Date(
        string='Start Posting Date',
    )
    postingdate_end = fields.Date(
        string='End Posting Date',
    )
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
    )
    move_id = fields.Many2one(
        'account.move',
        string='Document No',
    )
    results = fields.Many2many(
        'account.move',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
#         self.ensure_one()
#         Result = self.env['account.move.line']
#         dom = []
#         if self.org_ids:
#             dom += [('org_id', 'in', self.org_ids.ids)]
#         if self.period_start_id:
#             dom += [('date', '>=', self.period_start_id.date_start)]
#         if self.period_end_id:
#             dom += [('date', '<=', self.period_end_id.date_stop)]
#         if self.date_start:
#             dom += [('date', '>=', self.date_start)]
#         if self.date_end:
#             dom += [('date', '<=', self.date_end)]
#         if self.move_id :
#             dom += [('move_id', '=', self.move_id.id),('move_id.doctype','in',['receipt','interface_account'])]

        self.ensure_one()
        Result = self.env['account.move']
        dom = []
#         if self.org_ids:
#             dom += [('line_id.org_id', 'in', self.org_ids.ids)]
        if self.period_start_id:
            dom += [('date', '>=', self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('date', '<=', self.period_end_id.date_stop)]
        if self.date_start:
            dom += [('date', '>=', self.date_start)]
        if self.date_end:
            dom += [('date', '<=', self.date_end)]
        if self.move_id :
            dom += [('id', '=', self.move_id.id)]
        dom += [('preprint_number','!=',False)]
        test = Result.with_context(active=False).search(dom)

        for move in test:
            if move.doctype == 'receipt':
                Fund = self.env['account.voucher'] 
                domain = ([('move_id', '=', move.id)])
                lines = Fund.search(domain)
                move.preprint_number = lines.number_preprint
            if move.doctype == 'interface_account': 
                Fund = self.env['interface.account.entry'] 
                domain = ([('move_id', '=', move.id)])
                lines = Fund.search(domain)
                move.preprint_number = lines.preprint_number
            if move.doctype == 'adjustment': 
                Fund = self.env['account.tax.detail'] 
                domain = ([('ref_move_id', '=', move.id)])
                lines = Fund.search(domain)
                move.preprint_number = lines.invoice_number
        self.results = test
        print "self.results "
    