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
    
    def create(self, cr, uid, values, context=None):
        values['model'] = context.get('active_model')
        values['res_id'] = context.get('active_id')
        res = super(mail_mail, self).create(cr, uid, values, context=context)
        self.pool.get('hr.email.enhance').create(cr, uid,{'mail_id': res , 'expense_id': context.get('active_id')})
        return res
        
    