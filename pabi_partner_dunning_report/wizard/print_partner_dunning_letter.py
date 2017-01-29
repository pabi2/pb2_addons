# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class PrintPartnerDunningLetter(models.TransientModel):
    _name = 'print.partner.dunning.letter'

    report_type = fields.Selection(
        [('l1', '#1 Overdue 7 Days'),
         ('l2', '#2 Overdue 14 Days'),
         ('l3', '#3 Overdue 19 Days')],
        string='Report Type',
        required=True,
    )
    lang = fields.Selection(
        [('th_TH', 'Thai'),
         ('en_US', 'English')],
        string='Language',
        default='th_TH',
        required=True,
    )
    date_run = fields.Date(
        string='Report Run Date',
        default=lambda self: self._context.get('date_run', False),
        required=True,
        # Try to pass the context here, but only works in Form Views
        # will fix later. For now, user will have to choose the date_run
    )

    @api.multi
    def action_print_dunning_letter(self):
        data = {'parameters': {}}
        report_name = False
        if self.report_type == 'l1':
            if self.lang == 'en_US':
                report_name = 'pabi_customer_dunning_letter_1st_en'
            else:
                report_name = 'pabi_customer_dunning_letter_1st'
        elif self.report_type == 'l2':
            if self.lang == 'en_US':
                report_name = 'pabi_customer_dunning_letter_2nd_en'
            else:
                report_name = 'pabi_customer_dunning_letter_2nd'
        elif self.report_type == 'l3':
            report_name = 'pabi_customer_dunning_letter_3rd'
        # For ORM, we search for ids, and only pass ids to parser and jasper
        if not report_name:
            raise UserError(_('No report template found!'))
        active_ids = self._context.get('active_ids', [])
        model = self._context.get('active_model')
        dunnings = self.env[model].browse(active_ids)
        # Log Print History
        dunnings._create_print_history(self.report_type)
        # Print
        company = self.env.user.company_id
        data['parameters']['ids'] = active_ids
        data['parameters']['date_run'] = self.date_run
        data['parameters']['litigation_contact'] = \
            company.litigation_contact
        data['parameters']['signature_dunning'] = \
            company.signature_dunning
        data['parameters']['signature_litigation'] = \
            company.signature_litigation
        data['parameters']['account_dept_contact'] = \
            company.account_dept_contact
        # EN
        data['parameters']['litigation_contact_en'] = \
            company.litigation_contact_en
        data['parameters']['signature_dunning_en'] = \
            company.signature_dunning_en
        data['parameters']['signature_litigation_en'] = \
            company.signature_litigation_en
        data['parameters']['account_dept_contact_en'] = \
            company.account_dept_contact_en
        print data['parameters']
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
            'context': {'lang': self.lang},
        }
        return res
