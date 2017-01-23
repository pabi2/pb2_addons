# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class PrintPartnerDunningLetter(models.TransientModel):
    _name = 'print.partner.dunning.letter'

    report_type = fields.Selection(
        [('7', '#1 Overdue 7 Days'),
         ('14', '#2 Overdue 14 Days'),
         ('19', '#3 Overdue 19 Days')],
        string='Report Type',
        required=True,
    )
    lang = fields.Selection(
        [('th_TH', 'Thai'),
         ('en_US', 'English')],
        string='Language',
        default='th_TH',
    )
    date_run = fields.Date(
        string='Report Run Date',
        default=lambda self: self._context.get('date_run', False),
        # Try to pass the context here, but only works in Form Views
        # will fix later. For now, user will have to choose the date_run
    )

    # @api.model
    # def default_get(self, field_list):
    #     print self._context
    #     res = super(PrintPartnerDunningLetter, self).default_get(field_list)
    #     active_ids = self._context.get('active_ids')
    #     model = self._context.get('active_model')
    #     dunnings = self.env[model].browse(active_ids)
    #     # Check Days Overdue, whether all records has same value
    #     days_overdue = dunnings.mapped('days_overdue')
    #     if len(days_overdue) == 1:
    #         if days_overdue[0] in (7, 14, 19):
    #             res['report_type'] = str(days_overdue[0])
    #     return res

    @api.multi
    def action_print_dunning_letter(self):
        data = {'parameters': {}}
        report_name = False
        if self.report_type == '7':
            if self.lang == 'en_US':
                report_name = 'pabi_customer_dunning_letter_1st_en'
            else:
                report_name = 'pabi_customer_dunning_letter_1st'
        elif self.report_type == '14':
            if self.lang == 'en_US':
                report_name = 'pabi_customer_dunning_letter_2nd_en'
            else:
                report_name = 'pabi_customer_dunning_letter_2nd'
        elif self.report_type == '19':
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
        data['parameters']['signature_dunning'] = \
            company.signature_dunning
        data['parameters']['signature_litigation'] = \
            company.signature_litigation
        data['parameters']['account_dept_contact'] = \
            company.account_dept_contact

        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
            'context': {'lang': self.lang},
        }
        return res
