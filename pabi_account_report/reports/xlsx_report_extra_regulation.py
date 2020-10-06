# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api
from openerp.exceptions import ValidationError

class XLSXReportExtraRegulation(models.TransientModel):
    _name = 'xlsx.report.extra.regulation'
    _inherit = 'xlsx.report'
    
    expense_id  = fields.Many2one(
        'hr.expense.expense',
        string='Expense ID',
    )    
    date_start = fields.Date(
        string="KV Posting Date Start"
    )
    date_end = fields.Date(
        string="KV Posting Date End"
    )
    results = fields.Many2many(
        'extra.reguation.line',
        compute='_compute_results',
        string='Extra Regulation Results',
    )

    @api.multi
    def _compute_results(self):
        """
        Solution
        1. Get data from cheque register
        2. Filter follow by criteria as we selected
        """
        self.ensure_one()
        Result = self.env['extra.reguation.line']
        dom = []
        if self.date_start:
            dom += [('date_invoice','>=',self.date_start)]
        if self.date_end:
            dom += [('date_invoice','<=',self.date_end)]
        # if self.date_cheque_received:
        #     dom += [('voucher_id.date_cheque_received', '=',
        #              self.date_cheque_received)]
        
        self.results = Result.search(dom)
