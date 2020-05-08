# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openpyxl.worksheet import related


class HRExpense(models.Model):
    _inherit = 'hr.expense.expense'
 
    message_mail = fields.One2many(
        'hr.email.enhance',
        'expense_id',
        string='Message',
        readonly=True,
    )
    
class PABIEmailEnhance(models.Model):
    _name = 'hr.email.enhance'
    
    expense_id = fields.Many2one(
        'hr.expense.expense',
        string='Document'
    )
    mail_id = fields.Many2one(
        'mail.mail',
        string='Email',
    )
    subject = fields.Char(
        string='Subject',
        related='mail_id.mail_message_id.subject'
    )
    body_html = fields.Text(
        string='Body',
        related='mail_id.body_html',
    )
    recipient_ids = fields.Many2many(
        'res.partner', 
        string='To (Partners)',
        related='mail_id.recipient_ids'
    )
    state = fields.Selection([
            ('outgoing', 'Outgoing'),
            ('sent', 'Sent'),
            ('received', 'Received'),
            ('exception', 'Delivery Failed'),
            ('cancel', 'Cancelled'),
        ], 'Status', 
        readonly=True,
        copy=False,
        related='mail_id.state',
    )
    

class mail_mail(models.Model):
    _inherit = 'mail.mail'
    
    
    recipient_ids = fields.Many2many(
        'res.partner',
        string="To Employee",
        readonly=True,
    )
#     email_cc = fields.Char(
#         string='Cc',  
#     )
    
    @api.model
    def default_get(self, fields):
#         list_ids = []
        email_res_partner = ''
        res = super(mail_mail, self).default_get(fields)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        hr_expenes_doc = self.env['hr.expense.expense'].search([('id', '=', active_id)])
        hr_employee_code = hr_expenes_doc.employee_id.employee_code
        hr_employee_work_mail = hr_expenes_doc.employee_id.work_email
        if hr_expenes_doc.user_id.partner_id.email :
            email_res_partner = hr_expenes_doc.user_id.partner_id.email
        res_partner = self.env['res.partner'].search([('search_key', '=', hr_employee_code)])
        res_partner_prepare = hr_expenes_doc.user_id.partner_id
#         list_ids.append(res_partner.id)
#         res['recipient_ids'] = list_ids
        res['email_to'] = hr_employee_work_mail
        if res_partner != res_partner_prepare :
            res['email_cc'] = email_res_partner
        else:
            res['email_cc'] = ''
        return res
    
    def create(self, cr, uid, values, context=None):
        values['model'] = context.get('active_model')
        values['res_id'] = context.get('active_id')
        res = super(mail_mail, self).create(cr, uid, values, context=context)
        self.pool.get('hr.email.enhance').create(cr, uid,{'mail_id': res , 'expense_id': context.get('active_id')})
        return res
        
    