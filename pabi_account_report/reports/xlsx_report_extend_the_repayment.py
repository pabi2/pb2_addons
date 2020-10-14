# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools

  
class XLSXReportExtendTheRepayment(models.TransientModel):
    _name = 'xlsx.report.extend.the.repayment'
    _inherit = 'xlsx.report'
    
    partner_id = fields.Many2many(
        'res.partner',
        string='Partner',
    )    

    calendar_period_id = fields.Many2one(
        'account.period.calendar',
        string='Calendar Period',
        required=True,
        default=lambda self: self.env['account.period.calendar'].find(),
    )
          
#     results = fields.Many2many(
#         string='Results',
#         compute='_compute_results',
#         help="Use compute fields, so there is nothing store in database",
#     )
#      
#     @api.model
#     def _domain_to_where_str(self, domain):
#         """ Helper Function for better performance """
#         where_dom = [" %s %s %s " % (x[0], x[1], isinstance(x[2], basestring)
#                      and "'%s'" % x[2] or x[2]) for x in domain]
#         
#         where_str = 'and'.join(where_dom)
#         where_str = where_str.replace(',)',')')
#         return where_str
     
    @api.multi     
    def _compute_results(self):
        self.check_date()
        self.ensure_one()
        Result = self.env['issi.report.cgd.monthly.view']
        dom = []
        if self.partner_id:
            dom += [('partner_id', '=', self.partner_id.id)]
        if self.calendar_period_id.date_start:
            dom += [('date_start','>=',self.calendar_period_id.date_start)]
        if self.calendar_period_id.date_end:
            dom += [('date_end','<=',self.calendar_period_id.date_end)]                
        if dom ==[]:
            raise ValidationError('Please fill in information')
        where_str = self._domain_to_where_str(dom) 
        self._cr.execute("""
            select row_number() over (order by source_document, invoice_date ) as id, *
            from issi_report_cgd_monthly 
            where %s          
            """% (where_str))
          
        sla_receipt = self._cr.dictfetchall()
        for line in sla_receipt:
            self.results += Result.new(line)  
        
class ExtendTheRepayment(models.Model):
    _name = 'extend.the.repayment.view'
        
    org_code = fields.Char(
        string='',
        readonly=True,
    )
    month_old_due = fields.Date(
        string='',
        readonly=True,
    )    
    pabi_doc = fields.Char(
        string='',
        readonly=True,    
    )
    mysale_doc = fields.Char(
        string='',
        readonly=True,    
    )
    partner = fields.Char(
        string='',
        readonly=True,        
    )
    display_name2 = fields.Char(
        string='',
        readonly=True,
    )
    category_name = fields.Char(
        string='',
        readonly=True,
    )
    activity_list = fields.Char(
        string='',
        readonly=True,
    )
    date_document = fields.Date(
        string='',
        readonly=True,
    )
    date_old_due = fields.Date(
        string='',
        readonly=True,
    )
    date_due = fields.Date(
        string='',
        readonly=True,
    )
    daydiff1 = fields.Integer(
        string='',
        readonly=True,
    )
    daydiff2 = fields.Integer(
        string='',
        readonly=True,
    )
    reason = fields.Char(
        string='',
        readonly=True,
    )
    def _get_sql_view(self):
        sql_view = """Select cast(org.id || '000' as varchar) as org_code ,
            DATE_PART('month', due.date_old_due) as month_old_due, am.document as pabi_doc,am.ref as mySale_Doc,
            cus.search_key as parther, cus.display_name2, cat.name as category_name, sub1.atv_list as activity_list,am.date_document,
            due.date_old_due,due.date_due,(due.date_due - due.date_old_due) as dayDiff1,
            (due.date_due - am.date_document) as dayDiff2, due.reason
            from account_move am
            
            left join account_move_line ml on (ml.move_id = am.id)
            left join res_org org on (org.id = ml.org_id)
            left join res_partner cus on (cus.id = am.partner_id)
            left join res_partner_category cat on (cat.id = cus.category_id)
            left join account_activity atv on (atv.id = ml.activity_id)
            left join account_move_due_history due on (due.move_id = am.id)
            left join
            (
            SELECT move_id, string_agg(atv_b.name, ', ') AS atv_list
            FROM account_move_line ml_b
            left join account_activity atv_b on (atv_b.id = ml_b.activity_id)
            GROUP BY ml_b.move_id
            ) AS sub1
            ON sub1.move_id = am.id
            where
            --am.document = 'IA20034742' and
            --DATE_PART('month', due.date_old_due) = ?เดือน and
            ml.activity_id is not null and due.id = (select max(id) from account_move_due_history where move_id = am.id)
            group by org.id, cus.search_key,cus.display_name2,cat.name,am.document,am.ref,ml.move_id,am.date_document,due.date_old_due,due.date_due,due.reason, sub1.move_id,sub1.atv_list    
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))