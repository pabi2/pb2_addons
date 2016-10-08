# -*- coding: utf-8 -*-
from datetime import datetime
import xlwt
import cStringIO
import base64
from operator import itemgetter
from openerp import fields, models, api

from ..report import vat_report

title_style1_bold_left = \
    xlwt.easyxf('font: name Times New Roman,bold on, height 240')
title_style1_bold_right = \
    xlwt.easyxf('font: name Times New Roman,bold on, height 240')
title_style1_bold = \
    xlwt.easyxf('font: name Times New Roman,bold on, height 240')
title_style = \
    xlwt.easyxf('font: name Times New Roman,bold on, italic on, height 600')
title_style1 = xlwt.easyxf('font: name Times New Roman,bold off, height 240')
al = xlwt.Alignment()
al.horz = xlwt.Alignment.HORZ_CENTER
al.vert = xlwt.Alignment.VERT_CENTER
title_style.alignment = al
title_style1_bold.alignment = al
title_style1_bold_right.alignment.horz = xlwt.Alignment.HORZ_RIGHT
title_style1_bold_right.alignment.vert = xlwt.Alignment.VERT_CENTER
title_style1.alignment.vert = xlwt.Alignment.VERT_CENTER


class AccountVatReport(models.TransientModel):
    _name = 'account.vat.report'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id,
    )
    period_id = fields.Many2one(
        'account.period',
        string='Period',
        related='calendar_period_id.period_id',
    )
    calendar_period_id = fields.Many2one(
        'account.period.calendar',
        string='Calendar Period',
        required=True,
    )
    tax_id = fields.Many2one(
        'account.tax',
        string='Tax',
        required=True,
    )
    base_code_id = fields.Many2one(
        'account.tax.code',
        string='Base Code',
        required=True,
    )
    tax_code_id = fields.Many2one(
        'account.tax.code',
        string='Tax Code',
        required=True,
    )
    print_format = fields.Selection(
        [('pdf', 'PDF'),
         ('excel', 'Excel')],
        string='Print Format',
        default='pdf',
        required=True,
    )

    @api.onchange('tax_id')
    def onchange_tax(self):
        for wizard in self:
            wizard.base_code_id = wizard.tax_id.base_code_id.id
            wizard.tax_code_id = wizard.tax_id.tax_code_id.id

    @api.model
    def _get_parser_object(self):
        VatParser = vat_report.VatReportParser(
            self._cr, self._uid, 'account.vat.report', self._context
        )
        return VatParser

    @api.model
    def _prepare_header_data(self):
        month = datetime.strptime(self.period_id.date_start, '%Y-%m-%d').month
        header_list = [
            {'priority': 1, 'label': 'Month', 'value': month},
            {'priority': 3, 'label': 'Company', 'value': self.company_id.name},
            {'priority': 4, 'label': 'Tax ID', 'value': self.company_id.vat},
            {'priority': 2, 'label': 'Calendar Year',
             'value': self.period_id.fiscalyear_id.name},
        ]
        return header_list

    @api.model
    def _render_header(self, sheet, row):
        header_list = self._prepare_header_data()
        header_list = sorted(header_list, key=itemgetter('priority'))
        cell_cnt = 0
        for data in header_list:
            if cell_cnt == 0:
                sheet.write(row, 0, data['label'], title_style1_bold_left)
                sheet.write(row, 1, data['value'], title_style1)
                cell_cnt += 1
            elif cell_cnt == 1:
                sheet.write(row, 6, data['label'], title_style1_bold_left)
                sheet.write(row, 7, data['value'], title_style1)
                row += 1
                cell_cnt = 0
        return row + 1

    @api.model
    def _print_excel(self):
        tax = self.tax_id
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet(tax.name)
        sheet.row(0).height = 256*3

        header_text = False
        if tax.type_tax_use == 'sale':
            header_text = 'Sale Vat Report'
        if tax.type_tax_use == 'purchase':
            header_text = 'Purchase Vat Report'
        else:
            header_text = 'Sale/Purchase Vat Report'

        sheet.write_merge(0, 0, 0, 7, header_text, title_style)
        col = sheet.col(0)
        col.width = 256 * 18
        row = 2
        row = self._render_header(sheet, row)

        sheet.write_merge(row, row+1, 0, 0, "#", title_style1_bold)
        sheet.write_merge(row, row, 1, 2, "Tax Invoice", title_style1_bold)
        sheet.write(row+1, 1, 'Date', title_style1_bold)
        sheet.write(row+1, 2, 'No.', title_style1_bold)
        sheet.write_merge(row, row+1, 3, 3, "Customer/Supplier Name",
                          title_style1_bold)
        sheet.write_merge(row, row+1, 4, 4, "Tax ID", title_style1_bold)
        sheet.write_merge(row, row+1, 5, 5, "Branch ID", title_style1_bold)
        sheet.write_merge(row, row+1, 6, 6, "Base Amount", title_style1_bold)
        sheet.write_merge(row, row+1, 7, 7, "Tax Amount", title_style1_bold)

        row = row + 2
        VatParser = self._get_parser_object()
        lines = VatParser.get_lines(self)

        cell_count = 0
        col_width = 0
        tax_sequence = 1
        for line in lines:
            if line.get('tax_sequence', False):
                tax_sequence = line['tax_sequence']
            sheet.write(row, cell_count, tax_sequence, title_style1)
            col = sheet.col(cell_count)
            cell_count += 1
            if not line.get('tax_sequence', False):
                tax_sequence += 1

            sheet.write(row, cell_count, line['date'], title_style1)
            col = sheet.col(cell_count)
            if len(line['date']) > col_width:
                col_width = len(line['date'])
                col.width = 256 * (col_width + 5)
            cell_count += 1

            sheet.write(row, cell_count, line['number'], title_style1)
            col = sheet.col(cell_count)
            if len(line['number']) > col_width:
                col_width = len(line['number'])
                col.width = 256 * (col_width + 5)
            cell_count += 1

            sheet.write(row, cell_count, line['partner_name'], title_style1)
            col = sheet.col(cell_count)
            if len(line['partner_name']) > col_width:
                col_width = len(line['partner_name'])
                col.width = 256 * (col_width + 5)
            cell_count += 1

            tax_id = ''
            if line['tax_id']:
                tax_id = line['tax_id']
            sheet.write(row, cell_count, tax_id, title_style1)
            col = sheet.col(cell_count)
            if len(tax_id) > col_width:
                col_width = len(tax_id)
                col.width = 256 * (col_width + 5)
            cell_count += 1

            branch = ''
            if line.get('taxbranch', False):
                branch = line['taxbranch']
            sheet.write(row, cell_count, branch, title_style1)
            col = sheet.col(cell_count)
            if len(branch) > col_width:
                col_width = len(branch)
                col.width = 256 * (col_width + 5)
            cell_count += 1

            sheet.write(row, cell_count, line['base_amount'], title_style1)
            col = sheet.col(cell_count)
            col.width = 256 * 16
            cell_count += 1

            sheet.write(row, cell_count, line['tax_amount'], title_style1)
            col = sheet.col(cell_count)
            col.width = 256 * 16
            cell_count += 1

            cell_count = 0
            row += 1

        total_tax_amount = VatParser.get_tax_total()
        total_base_amount = VatParser.get_base_total()
        sheet.write_merge(row, row, 0, 5, 'Total', title_style1_bold_right)
        sheet.write(row, 6, total_base_amount, title_style1_bold_left)
        sheet.write(row, 7, total_tax_amount, title_style1_bold_left)

        stream = cStringIO.StringIO()
        workbook.save(stream)
        self.env.cr.execute(""" DELETE FROM vat_report_xls_output """)

        attach_id =\
            self.env['vat.report.xls.output'].create(
                {'name': self.tax_id.name + '.xls',
                 'xls_output': base64.encodestring(stream.getvalue())}
            )
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'vat.report.xls.output',
            'res_id': attach_id.id,
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    @api.multi
    def print_report(self):
        data = self.read([])[0]
        context = self._context.copy()
        context.update({'xls_export': True})
        if self.print_format == 'excel':
            return self._print_excel()
        return self.env['report'].get_action(
            self, 'l10n_th_vat_report.report_vat', data=data)
