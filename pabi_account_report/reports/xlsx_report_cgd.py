# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api
from openerp.exceptions import ValidationError


class XLSXReportCGD(models.TransientModel):
    _name = 'xlsx.report.cgd'
    _inherit = 'xlsx.report'
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner ID',
        )
    
    reference_date_start = fields.Date(
        string = 'Reference Date Start',
        )
    reference_date_end = fields.Date(
        string = 'Reference Date End',
        )
          
    results = fields.Many2many(
        'issi.report.cgd.monthly.view',
        string='Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )
    @api.multi
    def chack_date(self):
        if reference_date_end > reference_date_start:
            raise ValidationError('Date Start more then Date End')
     
    @api.multi
    def _compute_results(self):
        """
        Solution
        1. Get from account bank receipt
        2. Check state is done
        """
        self.ensure_one()
        Result = self.env['issi.report.cgd.monthly.view']
        dom = []
        if self.user_ids:
            dom += [(' partner_id', '=', self.partner_id)]
        if self.reference_date_start:
            dom += [('invoice_date','>=',self.reference_date_start)]
        if self.reference_date_start:
            dom += [('invoice_date','<=',self.reference_date_end)]                
         
        self._cr.execute("""
            select row_number() over (order by source_document, invoice_date ) as id, *
            from issi_report_cgd_monthly 
            where %s          
            """% (dom))
         
        sla_receipt = self._cr.dictfetchall()
         
        for line in sla_receipt:
            self.results += Result.new(line) 
        
class ISSIReportCGDMonthly(models.AbstractModel):
    _name = 'issi.report.cgd.monthly.view'
    
    
    
    partner_taxid = fields.Char(
        string ='Partner TaxID',
        )
    partner_name = fields.Char(
        string ='Partner name',
        )
    name = fields.Char(
        straing = 'Name',
        )
    base = fields.Float(
        string = 'Base',
        )
    invoice_date = fields.Date(
        string = 'Invoice Date',
        )
    partner_invoice_number = fields.Char(
        string = 'Partner Invoice Number',
        )
    txtreason = fields.Char(
        string = 'TXT Reason',
        )
    source_document = fields.Char(
        string = 'Source Document',
        )
    partner_id = fields.Integer(
        string = 'Partner ID',
        )
    invoice_number = fields.Char(
        string = 'Invoice Number',
        )
    is_small_amount = fields.Char(
        string = 'Is Small Amount',
        )
    pay_dtl2 = fields.Char(
        string = 'Pay DTL2',
        )
    is_reason = fields.Char(
        string = 'Is Reason',
        )