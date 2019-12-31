# -*- coding: utf-8 -*-
# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from types import CodeType
from openerp.addons.pabi_report_xlsx_helper.report.report_xlsx_abstract \
    import ReportXlsxAbstract
from openerp import _


class MISReportInstanceXlsx(ReportXlsxAbstract):

    def _write_header(self, ws, row_pos, ws_params, width,
                      render_space=None, default_format=None):
        pos = 0
        # first column is null
        for val in range(2):
            ws.write_string(row_pos+val, pos, '', default_format)
        pos += 1
        for col in ws_params:
            ws.set_column(pos, pos, width)
            colspan = 1
            cell_value = col.get('name')
            cell_value_date = col.get('date')
            cell_format = default_format
            cell_type = 'string'
            args_pos = [row_pos, pos]
            args_data = [cell_value]
            if cell_format:
                if isinstance(cell_format, CodeType):
                    cell_format = self._eval(cell_format, render_space)
                args_data.append(cell_format)
            ws_method = getattr(ws, 'write_%s' % cell_type)
            args = args_pos + args_data
            ws_method(*args)
            # loop create header date
            row = row_pos + 1
            args_pos = [row, pos]
            args_data = [cell_value_date]
            if cell_format:
                if isinstance(cell_format, CodeType):
                    cell_format = self._eval(cell_format, render_space)
                args_data.append(cell_format)
            args = args_pos + args_data
            ws_method(*args)
            pos += colspan
        return row + 1

    def _get_ws_params(self, wb, data, mis_report):
        mis_template = {
            'kpi': {
                'data': {
                    'value': self._render('kpi_name'),
                },
                'width': 60,
            },
        }
        ws_params = {
            'ws_name': '%s' % mis_report.name,
            'generate_ws_method': '_mis_builder_report',
            'title': _('%s - %s') % (
                mis_report.name, mis_report.company_id.name),
            'wanted_list': [str(x) for x in sorted(mis_template.keys())],
            'col_specs': mis_template,
        }
        return [ws_params]

    def _mis_builder_report(self, workbook, ws, ws_params, data, mis_report):
        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_header(self.xls_headers['standard'])
        ws.set_footer(self.xls_footers['standard'])
        # Set font name
        font_name = 'Arial'
        workbook.formats[0].set_font_name(font_name)

        self._set_column_width(ws, ws_params)

        row_pos = 0
        row_pos = self._write_ws_title(ws, row_pos, ws_params)
        # get all data
        data_dict = mis_report.compute()
        # Column Headers
        width = 25
        row_pos = self._write_header(
            ws, row_pos, data_dict['header'][0]['cols'],
            width, default_format=self.format_theader_yellow_amount_right)
        # freeze header and left
        ws.freeze_panes(row_pos, 1)
        for line in data_dict['content']:
            style = ''
            if 'text-indent' in line.get('default_style'):
                len_indent = line.get('default_style').split(':')[1].strip()
                # indent < 100 px
                if len(len_indent) <= 4:
                    format_css = self.format_indent_1
                else:
                    format_css = self.format_indent_2
            if 'font-weight' in line.get('default_style'):
                style = line.get('default_style').split(':')[1].strip()
                format_css = workbook.add_format(
                    {'align': 'left', u'{}'.format(style): True,
                     'font_name': font_name})
            row_pos = self._write_line(
                ws, row_pos, ws_params, col_specs_section='data',
                render_space={
                    'kpi_name': line['kpi_name'],
                },
                default_format=format_css)
            col = 0
            for value in line['cols']:
                col += 1
                # style
                num_format_str = '#,##0'
                if value.get('dp'):
                    num_format_str += '.'
                    num_format_str += '0' * int(value['dp'])
                if value.get('prefix'):
                    num_format_str = '"%s" %s' % \
                        (value['prefix'], num_format_str)
                if value.get('suffix'):
                    num_format_str += ' "%s"' % value['suffix']
                self.format_amount_mis_right = workbook.add_format(
                    {'align': 'right', 'num_format': num_format_str,
                     'font_name': font_name})
                if style:
                    self.format_amount_mis_right = workbook.add_format(
                        {'align': 'right', 'num_format': num_format_str,
                         u'{}'.format(style): True, 'font_name': font_name})

                if value.get('val'):
                    val = value['val']
                    if value.get('is_percentage'):
                        val = val / 0.01
                    ws.write(row_pos-1, col, val, self.format_amount_mis_right)
                else:
                    ws.write(row_pos-1, col, value['val_r'],
                             self.format_amount_mis_right)


MISReportInstanceXlsx('report.mis_report_instance_xlsx', 'mis.report.instance')
