# -*- coding: utf-8 -*-
from datetime import datetime
from openerp import models, fields, api
from openerp.addons import jasper_reports


class Account_Vat_Report(models.Model):
    _inherit ='account.vat.report'

    @api.multi
    def print_report(self):
        date = self.calendar_period_id.period_id.date_start
        datetime_object = datetime.strptime(date, '%Y-%m-%d')
        data = {'parameters': {}}
        report_name = self.print_format == 'excel' and 'vat_report_xls' or \
            'vat_report_pdf'
        Report = self.env['purchase.vat.report']
        ids = Report.search([])._ids
        data['parameters']['ids'] = ids
        data['parameters']['period_id'] = self.calendar_period_id.period_id.id
        data['parameters']['tax_code_id'] = self.tax_code_id.id
        data['parameters']['tax_id'] = self.tax_id.id
        data['parameters']['company_id'] = self.company_id.id
        data['parameters']['calandar_pariod_id'] = self.calendar_period_id.id
        data['parameters']['company_name'] = self.company_id.name
        data['parameters']['tax_type'] = self.tax_id.type_tax_use
        data['parameters']['month'] = datetime_object.month
        data['parameters']['year'] = datetime_object.year
        data['parameters']['company_vat'] = self.company_id.vat
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
        }
        return res
