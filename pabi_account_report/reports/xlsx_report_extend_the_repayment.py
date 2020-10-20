# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools
import datetime
  
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
    results = fields.Many2many(
        'extend.the.repayment.view',
        string='Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['extend.the.repayment.view']
#         dom = []
#         if self.calendar_period_id.date_start:
#             dom += [('date_document','>=',self.calendar_period_id.date_start)]
#         if self.calendar_period_id.date_stop:
#             dom += [('date_document','<=',self.calendar_period_id.date_stop)]
#         if self.partner_id:
#             dom += [('partner_id','in',self.partner_id.ids)]
        self._cr.execute("""
            Select cast(org.id || '000' as varchar) as org_code ,
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
            ml.activity_id is not null and due.id = (select max(id) from account_move_due_history where move_id = am.id)
            and am.date_document between '%s' and '%s'
            and am.partner_id in %s
            group by org.id, cus.search_key,
            cus.display_name2, cat.name,am.document,
            am.ref,ml.move_id,am.date_document,
            due.date_old_due,due.date_due,
            due.reason, sub1.move_id,sub1.atv_list
        """ % (self.calendar_period_id.date_start,
               self.calendar_period_id.date_stop,
               tuple(self.partner_id.ids)))
        results = self._cr.dictfetchall()
        self.results = [Result.new(line).id for line in results]
    
class ExtendTheRepayment(models.Model):
    _name = 'extend.the.repayment.view'
        
    org_code = fields.Char(
        string='Org Code',
        readonly=True,
    )
    month_old_due = fields.Float(
        string='Month Old Due',
        readonly=True,
    )    
    pabi_doc = fields.Char(
        string='Pabi Doc.',
        readonly=True,    
    )
    mysale_doc = fields.Char(
        string='Mysale Doc',
        readonly=True,    
    )
    partner = fields.Many2many(
        'res.partner',
        string='Partner',
        readonly=True,        
    )
    display_name2 = fields.Char(
        string='Display Name',
        readonly=True,
    )
    category_name = fields.Char(
        string='Category Name',
        readonly=True,
    )
    activity_list = fields.Char(
        string='Activity List',
        readonly=True,
    )
    date_document = fields.Date(
        string='Date Document',
        readonly=True,
    )
    date_old_due = fields.Date(
        string='Date Old Due',
        readonly=True,
    )
    date_due = fields.Date(
        string='Date Due',
        readonly=True,
    )
    daydiff1 = fields.Integer(
        string='Day Difference 1',
        readonly=True,
    )
    daydiff2 = fields.Integer(
        string='Day Difference 2',
        readonly=True,
    )
    reason = fields.Char(
        string='Reason',
        readonly=True,
    )