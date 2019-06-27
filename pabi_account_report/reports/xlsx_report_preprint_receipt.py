# -*- coding: utf-8 -*-
from openerp import models, fields, api
from EpsImagePlugin import field
from openerp import tools
from pychart.basecanvas import _compute_bounding_box
from openerp import pooler
from openpyxl.worksheet import related

REFERENCE_SELECT = [('account.voucher', 'Receipt'),
                    ('interface.account.entry', 'Account Interface'),
                    ('account.tax.detail', 'Adjustment'),
                    ]

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
    
class Accountmovepreprintview(models.Model):
    _name = 'account.move.preprint'    
    #_auto = False    
    
    move_id = fields.Many2one(
        'account.move',
        string='Document No',
    )
    name = fields.Char(
        string='Preprint Number',
        readonly=True,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
       
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
    move_id = fields.Many2many(
        'account.move',
        string='Document No',
        domain=[('doctype','in',['adjustment','receipt','interface_account'])]
    )
    results = fields.Many2many(
        'account.move',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )
    preprint_number = fields.Many2many(
        'account.move.preprint',
        string='Preprint Number',
    )
    
    @api.onchange('preprint_number')
    def create_data_preprint (self):
        self.env.cr.execute("SELECT COUNT(*) from account_move_preprint ")
        result=self.env.cr.fetchone()
        if result[0]==0:
            self.create_account_move_preprint()
        else:
            self.env.cr.execute(
                """
                select COUNT(*) from (SELECT m.id as move_id,pre.number_preprint as name,org.org_id as org_id
                    from account_move m
                    LEFT JOIN 
                        ( 
                        select c.move_id,c.number_preprint from
                        (select account_move.id as move_id,account_voucher.number_preprint as number_preprint
                        from account_move 
                        LEFT JOIN account_voucher on account_voucher.move_id = account_move."id"
                        UNION 
                        select account_move.id as move_id,interface_account_entry.preprint_number as number_preprint
                        from account_move 
                        LEFT JOIN interface_account_entry on interface_account_entry.move_id = account_move."id"
                        UNION 
                        select account_move.id as move_id,account_tax_detail.number_preprint as number_preprint
                        from account_move 
                        LEFT JOIN account_tax_detail on account_tax_detail.ref_move_id = account_move."id"
                        )as c
                        where c.number_preprint!=''
                        ) pre ON m.id = pre.move_id
                    LEFT JOIN 
                        (
                        SELECT DISTINCT m.id,m.name,l.org_id
                        from account_move m
                        LEFT JOIN account_move_line l ON l.move_id = m.id
                        where m.doctype in ('receipt','interface_account') and l.org_id != 0
                        ) org on org."id" = m."id"
                    where m.doctype in ('adjustment','receipt','interface_account') and pre.number_preprint!=''
                ) as count_update
                """
                )
            check = self.env.cr.fetchone()
            if result[0]!=check[0]:
                self.delete_account_move_preprint()
                self.create_account_move_preprint()
                
    def delete_account_move_preprint(self):
        self.env.cr.execute("DELETE FROM account_move_preprint")
        
        
    def create_account_move_preprint(self):
        self.env.cr.execute(
                """
                INSERT INTO account_move_preprint (
                     move_id,name,org_id)
                    (SELECT m.id as move_id,pre.number_preprint as name,org.org_id as org_id
                    from account_move m
                    LEFT JOIN 
                        ( 
                        select c.move_id,c.number_preprint from
                        (select account_move.id as move_id,account_voucher.number_preprint as number_preprint
                        from account_move 
                        LEFT JOIN account_voucher on account_voucher.move_id = account_move."id"
                        UNION 
                        select account_move.id as move_id,interface_account_entry.preprint_number as number_preprint
                        from account_move 
                        LEFT JOIN interface_account_entry on interface_account_entry.move_id = account_move."id"
                        UNION 
                        select account_move.id as move_id,account_tax_detail.number_preprint as number_preprint
                        from account_move 
                        LEFT JOIN account_tax_detail on account_tax_detail.ref_move_id = account_move."id"
                        )as c
                        where c.number_preprint!=''
                        ) pre ON m.id = pre.move_id
                    LEFT JOIN 
                        (
                        SELECT DISTINCT m.id,m.name,l.org_id
                        from account_move m
                        LEFT JOIN account_move_line l ON l.move_id = m.id
                        where m.doctype in ('receipt','interface_account') and l.org_id != 0
                        ) org on org."id" = m."id"
                    where m.doctype in ('adjustment','receipt','interface_account') and pre.number_preprint!=''
                    )
                """
        )    
                
    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['account.move']
        dom = []
        domain=[]
        if self.period_start_id:
            dom += [('date', '>=', self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('date', '<=', self.period_end_id.date_stop)]
        if self.date_start:
            dom += [('date', '>=', self.date_start)]
        if self.date_end:
            dom += [('date', '<=', self.date_end)]
        if self.postingdate_start:
            dom += [('date', '>=', self.postingdate_start)]
        if self.postingdate_end:
            dom += [('date', '<=', self.postingdate_end)]
        if self.move_id:
            domain += [('move_id', 'in', self.move_id.ids)]
        if self.org_ids:
            domain += [('org_id', 'in', self.org_ids.ids)]
        if self.preprint_number:
            domain += [('id', 'in', self.preprint_number.ids)]
        if domain:
            preprint=self.env['account.move.preprint'].search(domain)
            dom += [('id', 'in', [x.move_id.id for x in preprint])]
            
        self.results = Result.with_context(active=False).search(dom)