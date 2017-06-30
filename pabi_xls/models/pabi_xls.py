# -*- coding: utf-8 -*-
import base64
import os
import xlrd
from xlrd.sheet import ctype_text
import unicodecsv
from datetime import datetime, timedelta
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class PABIXls(models.AbstractModel):
    _name = 'pabi.xls'
    _description = 'XLS Helper for PABI2 project'

    @api.model
    def _add_column(self, column_name, column_value, file_txt):
        i = 0
        txt_lines = []
        for line in file_txt.split('\n'):
            if line and i == 0:
                line = '"' + str(column_name) + '",' + line
            elif line:
                line = '"' + str(column_value) + '",' + line
            txt_lines.append(line)
            i += 1
        file_txt = '\n'.join(txt_lines)
        return file_txt

    @api.model
    def xldate_to_datetime(self, xldate):
        tempDate = datetime(1900, 1, 1)
        deltaDays = timedelta(days=int(xldate) - 2)
        xldate = (tempDate + deltaDays)
        return xldate.strftime("%Y-%m-%d")

    @api.model
    def import_xls(self, model, file, extra_columns=None, column_map=None):
        """
        If there is additional fixed column value
        - add_col_val = [('name', 'ABC'), ('id', 10), ]
        To map user column with database column
        - column_map = {'Name': 'name', 'Document', 'doc_id', }
        """
        decoded_data = base64.decodestring(file)
        ftemp = 'temp' + datetime.utcnow().strftime('%H%M%S%f')[:-3]
        f = open(ftemp + '.xls', 'wb+')
        f.write(decoded_data)
        f.seek(0)
        f.close()
        wb = xlrd.open_workbook(f.name)
        st = wb.sheet_by_index(0)
        csv_file = open(ftemp + '.csv', 'wb')
        csv_out = unicodecsv.writer(csv_file,
                                    encoding='utf-8',
                                    quoting=unicodecsv.QUOTE_ALL)
        if st._cell_values:
            _HEADER_FIELDS = st._cell_values[0]
        for nrow in xrange(st.nrows):
            if nrow > 0:
                row_values = st.row_values(nrow)
                for index, val in enumerate(row_values):
                    ctype = st.cell(nrow, index).ctype
                    type = ctype_text.get(ctype, 'unknown type')
                    if type == 'empty' or type == 'text' \
                        or type == 'bool' or type == 'error' \
                            or type == 'blank':
                        row_values[index] = st.cell(nrow, index).value
                    elif type == 'number':
                        if not val:
                            row_values[index] = 0
                        else:
                            if not str(val).isdigit():
                                row_values[index] = int(val)
                            else:
                                row_values[index] = val
                    elif type == 'xldate':
                        str_date = self.xldate_to_datetime(
                            st.cell(nrow, index).value)
                        row_values[index] = str_date
                    else:
                        row_values[index] = st.cell(nrow, index).value
                csv_out.writerow(row_values)
            else:
                csv_out.writerow(st.row_values(nrow))
        csv_file.close()
        csv_file = open(ftemp + '.csv', 'r')
        file_txt = csv_file.read()
        csv_file.close()
        os.unlink(ftemp + '.xls')
        os.unlink(ftemp + '.csv')
        if not file_txt:
            raise ValidationError(_(str("File Not found.")))
        # Add extra column
        if extra_columns:
            for column in extra_columns:
                _HEADER_FIELDS.insert(0, str(column[0]))
                file_txt = self._add_column(column[0], column[1], file_txt)
        # Map column name
        if column_map:
            _HEADER_FIELDS = [column_map.get(x, False) and column_map[x] or x
                              for x in _HEADER_FIELDS]
        Import = self.env['base_import.import']
        imp = Import.create({
            'res_model': model,
            'file': file_txt,
        })
        [errors] = imp.do(
            _HEADER_FIELDS,
            {'headers': True, 'separator': ',',
             'quoting': '"', 'encoding': 'utf-8'})
        if errors:
            raise ValidationError(_(str(errors[0]['message'])))
        return file

    # Original
    # @api.multi
    # def action_import_csv(self):
    #     _TEMPLATE_FIELDS = ['statement_id/.id',
    #                         'document',
    #                         'cheque_number',
    #                         'description',
    #                         'debit', 'credit',
    #                         'date_value',
    #                         'batch_code']
    #     for rec in self:
    #         rec.import_ids.unlink()
    #         rec.import_error = False
    #         if not rec.import_file:
    #             continue
    #         Import = self.env['base_import.import']
    #         file_txt = base64.decodestring(rec.import_file)
    #         file_txt = self._add_statement_id_column(rec.id, file_txt)
    #         imp = Import.create({
    #             'res_model': 'pabi.bank.statement.import',
    #             'file': file_txt,
    #         })
    #         [errors] = imp.do(
    #             _TEMPLATE_FIELDS,
    #             {'headers': True, 'separator': ',',
    #              'quoting': '"', 'encoding': 'utf-8'})
    #         if errors:
    #             rec.import_error = str(errors)
