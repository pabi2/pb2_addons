# -*- coding: utf-8 -*-
import base64
import os
import xlrd
import uuid
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
    def import_xls(self, model, file, header_map=None, extra_columns=None):
        """
        To map user column with database column
        - header_map = {'Name': 'name', 'Document', 'doc_id', }
        If there is additional fixed column value
        - extra_columns = [('name', 'ABC'), ('id', 10), ]
        If the import file have column id, we will use this column to create
        external id, and hence possible to return record id being created
        """
        decoded_data = base64.decodestring(file)
        ftemp = 'temp' + datetime.utcnow().strftime('%H%M%S%f')[:-3]
        f = open(ftemp + '.xls', 'wb+')
        f.write(decoded_data)
        f.seek(0)
        f.close()
        try:
            wb = xlrd.open_workbook(f.name)
        except xlrd.XLRDError:
            raise ValidationError(
                _('Invalid file format, only .xls or .xlsx file allowed!'))
        except Exception:
            raise
        st = wb.sheet_by_index(0)
        csv_file = open(ftemp + '.csv', 'wb')
        csv_out = unicodecsv.writer(csv_file,
                                    encoding='utf-8',
                                    quoting=unicodecsv.QUOTE_ALL)
        if st._cell_values:
            _HEADER_FIELDS = st._cell_values[0]
        id_index = -1  # -1 means no id
        xml_ids = []
        for nrow in xrange(st.nrows):
            if nrow == 0:  # Header, find id field
                header_values = [x.lower().strip()
                                 for x in st.row_values(nrow)]
                if 'id' in header_values:
                    id_index = header_values.index('id')
            if nrow > 0:
                row_values = st.row_values(nrow)
                for index, val in enumerate(row_values):
                    ctype = st.cell(nrow, index).ctype
                    type = ctype_text.get(ctype, 'unknown type')
                    if id_index == index and val:
                        # UUID replace id
                        xml_id = '%s.%s' % ('pabi_xls', uuid.uuid4())
                        row_values[index] = xml_id
                        xml_ids.append(xml_id)
                    elif type == 'empty' or type == 'text' \
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
        # Create xml_ids if not already assigned
        if id_index == -1:
            _HEADER_FIELDS.insert(0, 'id')
            xml_id = '%s.%s' % ('pabi_xls', uuid.uuid4())
            file_txt = self._add_column('id', xml_id, file_txt)
            xml_ids.append(xml_id)
        # Map column name
        if header_map:
            _HEADER_FIELDS = [header_map.get(x.lower().strip(), False) and
                              header_map[x.lower()] or False
                              for x in _HEADER_FIELDS]
        # Add extra column
        if extra_columns:
            for column in extra_columns:
                _HEADER_FIELDS.insert(0, str(column[0]))
                file_txt = self._add_column(column[0], column[1], file_txt)
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
        return list(set(xml_ids))
