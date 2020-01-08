# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api


class XLSXReportPabiEmployeeAdvanceReport(models.TransientModel):
    _name = 'xlsx.report.pabi.employee.advance.report'
    _inherit = 'xlsx.report'
    
    av_ids=fields.Many2one(
        'hr.expense.expense',
        string='Expense ID',
        
    )
    employee_codes = fields.Many2one(
        'hr.employee',
        string='Employee Code',
        
    )
    
    source_budget_names = fields.Many2one(
        'chartfield.view',
        string='Source Budget Name',
        
    )
    
    amounts =  fields.Selection(
        [(1, '==all=='),
         (2, 'not clear'),
        ],
        string='Status',
        default=1,
        require=True,
    )
    
    date_report = fields.Date(
            string='Report Date',
            default=lambda self: fields.Date.context_today(self),
            required=True,
    )
    
    
    results = fields.Many2many(
        'xlsx.report.pabi.employee.advance.report.results',
        string='Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )
    
    @api.model
    def create(self,values):
        return  super(XLSXReportPabiEmployeeAdvanceReport, self).create(values)
    
    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.pabi.employee.advance.report.results']
        dom = []
        employee_code_id =[]
        dom1=[]
        state = 0
        if  self.amounts == 2:
            if self.av_ids:
                    dom1+=[('av_id','=',self.av_ids.id)]
            if self.employee_codes:
                    dom1+=[('employee_code', '=', self.employee_codes.employee_code)]   
            if self.source_budget_names:
                    dom1+=[('source_budget', '=',self.source_budget_names.code)]
            search_dom1 = Result.search(dom1)
            numlen=len(search_dom1)                  
            for dom1_id in search_dom1 :
                if state == 0:
                    hrid=dom1_id.employee_code
                    name_amount =0.00
                if hrid == dom1_id.employee_code :
                    name_amount += dom1_id.amount                    
                else :
                    if name_amount != 0 :
                       employee_code_id.append(hrid) 
                    hrid=dom1_id.employee_code 
                    name_amount =dom1_id.amount
                state =state+1
                if state == numlen:
                    if name_amount != 0 :
                       employee_code_id.append(hrid)                           
            dom += [('employee_code', 'in', employee_code_id)]                   
####////////////////////////////////////////////////////////////////  //////////////////////////////////////////////                                       
        if self.amounts == 1:
            if self.employee_codes:
                    dom += [('employee_code', '=', self.employee_codes.employee_code)]
        if self.av_ids:
                dom += [('av_id', '=', self.av_ids.id)]           
        if self.source_budget_names:
                dom += [('source_budget', '=',self.source_budget_names.code)]                               
        self.results = Result.search(dom)    
class XLSXReportPabiEmployeeAdvanceReportResults(models.Model):
    _name = 'xlsx.report.pabi.employee.advance.report.results'
    _auto = False
    _description = 'Temp table as ORM holder'
    
    
    employee_code = fields.Char(
        string='Employee Code',
        
    )
    
    name_th=fields.Text(
        string='Employee Name',
       
    )
    
    av_doc=fields.Char(
        string='Advance Number',
        
    )
    
    av_id=fields.Many2one(
        'hr.expense.expense',
        string='Expense ID',
        
    )
    
    av_due_date_origin=fields.Date(
        string='Date Origin',
        
    )
    
    av_due_date_last=fields.Date(
        string='Date last',
        
    )
    
    description=fields.Char(
        string='Line Description',
        
    )
    
    supplier_invoice_number=fields.Char(
        string='Supplier Invoice Number',
        
    )
    
    source_doc=fields.Char(
        string='Source Doc.',
        
    )
    
    doc_date=fields.Date(
        string='Document Date',
        
    )
    
    posting_date=fields.Date(
        string='Posting Date',
        
    )
    
    due_date=fields.Date(
        string='Due Date',
        
    )
    
    period_name=fields.Char(
        string='Period',
        
    )
    
    organization=fields.Char(
        string='Org',
        
    )
    
    chart_view=fields.Char(
        string='Char view',
        
    )
    
    costcenter_code=fields.Char(
        string='Costcenter',
        
    )
    
    costcenter_name=fields.Char(
        string='Costcenter Name',
        
    )
    
    source_budget=fields.Char(
        string='Source Budget',
        
    )
    
    
    source_budget_name=fields.Text(
        string='Source Budget Name',
        
    )
    
    amount=fields.Float(
        string='Amount',
        
    )
    
    reconcile_ref=fields.Char(
        string='Rec.ID',
       
    )
    
    reconcile_id=fields.Integer(
        string='Reconcile Id',
        
    )
    
    reconcile_partial_id=fields.Integer(
        string='Part.ID',
        
    )
    
    reconcile_txt=fields.Text(
        string='Part.ID',
        
    )
    
    reccreate_date=fields.Date(
        string='Reccreate Date',
        
    )
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT 
            row_number() over (order by a.employee_code) as id,
            a.employee_code,
    a.name_th,
    a.av_doc,
    a.av_id,
    a.av_due_date_origin,
    a.av_due_date_last,
    a.description,
    a.supplier_invoice_number,
    a.source_doc,
    a.doc_date,
    a.posting_date,
    a.due_date,
    a.period_name,
    a.organization,
    a.chart_view,
    a.costcenter_code,
    a.costcenter_name,
    a.source_budget,
    a.source_budget_name,
    a.amount,
    a.reconcile_ref,
    a.reconcile_id,
    a.reconcile_partial_id,
    a.reconcile_txt,
    a.reccreate_date
   FROM ( SELECT hr.employee_code,
            hr.display_name_th AS name_th,
            av.number AS av_doc,
            av.id AS av_id,
                CASE
                    WHEN (av_his.date_due IS NOT NULL) THEN av_his.date_due
                    ELSE av.date_due
                END AS av_due_date_origin,
            av.date_due AS av_due_date_last,
            avline.name AS description,
            invav.number AS supplier_invoice_number,
            avsource.number AS source_doc,
            invav.date_document AS doc_date,
            invav.date_invoice AS posting_date,
            invav.date_due AS due_date,
            period.name AS period_name,
            org.name AS organization,
            avline.chart_view,
                CASE avline.chart_view
                    WHEN 'unit_base'::text THEN cctr.costcenter_code
                    WHEN 'project_base'::text THEN prj.costcenter_used
                    WHEN 'invest_asset'::text THEN invass.costcenter_used
                    WHEN 'invest_construction'::text THEN cons.costcenter_used
                    WHEN 'personnel'::text THEN pers.costcenter_used
                    ELSE ''::character varying
                END AS costcenter_code,
                CASE avline.chart_view
                    WHEN 'unit_base'::text THEN (cctr.costcenter_name)::character varying
                    WHEN 'project_base'::text THEN (prj.costcenter_name_used)::character varying
                    WHEN 'invest_asset'::text THEN (invass.costcenter_name_used)::character varying
                    WHEN 'invest_construction'::text THEN (cons.costcenter_name_used)::character varying
                    WHEN 'personnel'::text THEN (pers.costcenter_name_used)::character varying
                    ELSE ''::character varying
                END AS costcenter_name,
                CASE avline.chart_view
                    WHEN 'unit_base'::text THEN cctr.costcenter_code
                    WHEN 'project_base'::text THEN prj.source_budget
                    WHEN 'invest_asset'::text THEN invass.source_budget
                    WHEN 'invest_construction'::text THEN cons.source_budget
                    WHEN 'personnel'::text THEN pers.source_budget
                    ELSE ''::character varying
                END AS source_budget,
                CASE avline.chart_view
                    WHEN 'unit_base'::text THEN cctr.costcenter_name
                    WHEN 'project_base'::text THEN prj.source_budget_name
                    WHEN 'invest_asset'::text THEN invass.source_budget_name
                    WHEN 'invest_construction'::text THEN cons.source_budget_name
                    WHEN 'personnel'::text THEN pers.source_budget_name
                    ELSE ''::text
                END AS source_budget_name,
            invav.amount_total AS amount,
            ml.reconcile_ref,
            ml.reconcile_id,
            ml.reconcile_partial_id,
                CASE
                    WHEN (ml.reconcile_id IS NOT NULL) THEN 'full'::text
                    WHEN (ml.reconcile_partial_id IS NOT NULL) THEN 'partial'::text
                    ELSE ''::text
                END AS reconcile_txt,
            mr.create_date AS reccreate_date
           FROM ((((((((((((((hr_expense_expense av
             LEFT JOIN issi_hr_employee_view hr ON ((hr.id = av.employee_id)))
             LEFT JOIN hr_expense_line avline ON ((avline.expense_id = av.id)))
             LEFT JOIN account_invoice invav ON ((invav.id = av.invoice_id)))
             LEFT JOIN hr_expense_expense avsource ON (((avsource.id)::numeric = (NULLIF(regexp_replace((invav.source_document_id)::text, '\D'::text, ''::text, 'g'::text), ''::text))::numeric)))
             LEFT JOIN account_period period ON ((period.id = invav.period_id)))
             LEFT JOIN operating_unit org ON ((org.id = invav.operating_unit_id)))
             LEFT JOIN etl_issi_m_costcenter cctr ON ((avline.costcenter_id = cctr.costcenter_id)))
             LEFT JOIN issi_m_source_budget_view prj ON ((avline.project_id = prj.project_id)))
             LEFT JOIN issi_m_source_budget_view invass ON ((avline.invest_asset_id = invass.invest_asset_id)))
             LEFT JOIN issi_m_source_budget_view cons ON ((avline.invest_construction_id = cons.invest_construction_phase_id)))
             LEFT JOIN issi_m_source_budget_view pers ON ((avline.personnel_costcenter_id = pers.personnel_costcenter_id)))
             LEFT JOIN account_move_line ml ON ((ml.move_id = invav.move_id)))
             LEFT JOIN account_move_reconcile mr ON (((mr.name)::text = (ml.reconcile_ref)::text))
             LEFT JOIN hr_expense_advance_due_history av_his ON (((av.id = av_his.expense_id) AND (av_his.date_old_due IS NULL)))))
          WHERE ((av.is_employee_advance IS TRUE) AND (ml.account_id = 4964))
        UNION
         SELECT hr.employee_code,
            hr.display_name_th AS name_th,
            av.number AS av_doc,
            av.id AS av_id,
                CASE
                    WHEN (av_his.date_due IS NOT NULL) THEN av_his.date_due
                    ELSE av.date_due
                END AS av_due_date_origin,
            av.date_due AS av_due_date_last,
            avline.name AS description,
            inv.number AS supplier_invoice_number,
                CASE
                    WHEN (ex.number IS NULL) THEN av.number
                    ELSE ex.number
                END AS source_doc,
            inv.date_document AS doc_date,
            inv.date_invoice AS posting_date,
            inv.date_due AS due_date,
            period.name AS period_name,
            org.name AS organization,
            avline.chart_view,
                CASE avline.chart_view
                    WHEN 'unit_base'::text THEN cctr.costcenter_code
                    WHEN 'project_base'::text THEN prj.costcenter_used
                    WHEN 'invest_asset'::text THEN invass.costcenter_used
                    WHEN 'invest_construction'::text THEN cons.costcenter_used
                    WHEN 'personnel'::text THEN pers.costcenter_used
                    ELSE ''::character varying
                END AS costcenter_code,
                CASE avline.chart_view
                    WHEN 'unit_base'::text THEN (cctr.costcenter_name)::character varying
                    WHEN 'project_base'::text THEN (prj.costcenter_name_used)::character varying
                    WHEN 'invest_asset'::text THEN (invass.costcenter_name_used)::character varying
                    WHEN 'invest_construction'::text THEN (cons.costcenter_name_used)::character varying
                    WHEN 'personnel'::text THEN (pers.costcenter_name_used)::character varying
                    ELSE ''::character varying
                END AS costcenter_name,
                CASE avline.chart_view
                    WHEN 'unit_base'::text THEN cctr.costcenter_code
                    WHEN 'project_base'::text THEN prj.source_budget
                    WHEN 'invest_asset'::text THEN invass.source_budget
                    WHEN 'invest_construction'::text THEN cons.source_budget
                    WHEN 'personnel'::text THEN pers.source_budget
                    ELSE ''::character varying
                END AS source_budget,
                CASE avline.chart_view
                    WHEN 'unit_base'::text THEN cctr.costcenter_name
                    WHEN 'project_base'::text THEN prj.source_budget_name
                    WHEN 'invest_asset'::text THEN invass.source_budget_name
        WHEN 'invest_construction'::text THEN cons.source_budget_name
            WHEN 'personnel'::text THEN pers.source_budget_name
            ELSE ''::text
        END AS source_budget_name,
avclear.clearing_amount * -1 as amount,
ml.reconcile_ref,

     ml.reconcile_id,
            ml.reconcile_partial_id,
                CASE
                    WHEN (ml.reconcile_id IS NOT NULL) THEN 'full'::text
                    WHEN (ml.reconcile_partial_id IS NOT NULL) THEN 'partial'::text
                    ELSE ''::text
                END AS reconcile_txt,
            mr.create_date AS reccreate_date
    
 from hr_expense_clearing avclear
LEFT join hr_expense_expense av on av.id = avclear.advance_expense_id 
--------
LEFT join hr_expense_advance_due_history av_his on av.id = av_his.expense_id and av_his.date_old_due is null
LEFT JOIN issi_hr_employee_view hr ON ((hr.id = av.employee_id))
LEFT JOIN hr_expense_line avline ON ((avline.expense_id = av.id))
LEFT JOIN account_invoice inv on inv.id = avclear.invoice_id 
LEFT join hr_expense_expense ex on ex.id = avclear.expense_id 
left join operating_unit org on org.id = inv.operating_unit_id
left join account_period period on period.id = inv.Period_id
LEFT JOIN etl_issi_m_costcenter cctr ON ((avline.costcenter_id = cctr.costcenter_id))
LEFT JOIN issi_m_source_budget_view prj ON ((avline.project_id = prj.project_id))
LEFT JOIN issi_m_source_budget_view invass ON ((avline.invest_asset_id = invass.invest_asset_id))
LEFT JOIN issi_m_source_budget_view cons ON ((avline.invest_construction_id = cons.invest_construction_phase_id))
LEFT JOIN issi_m_source_budget_view pers ON ((avline.personnel_costcenter_id = pers.personnel_costcenter_id))
LEFT JOIN account_move_line ml on ml.move_id = inv.move_id
    LEFT JOIN account_move_reconcile mr ON (((mr.name)::text = (ml.reconcile_ref)::text))
where av.is_employee_advance is true --,001932'000272'
--and av.number = 'AV19001167' and hr.employee_code = '001932'  
and ml.account_id = 4964 --?1104010001 ?Թ??????ͧ????
) a
)""" % (self._table, ))