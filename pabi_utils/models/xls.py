# -*- coding: utf-8 -*-
import StringIO
import csv
import base64
import xlrd
import uuid
import re
import string
from xlrd.sheet import ctype_text
import unicodecsv
from datetime import datetime
from openerp import models, api, _
from openerp.exceptions import ValidationError, except_orm


class PABIUtilsXLS(models.AbstractModel):
    _name = 'pabi.utils.xls'
    _description = 'XLS Helper for PABI2 project'

    @api.model
    def pos2idx(self, pos):
        match = re.match(r"([a-z]+)([0-9]+)", pos, re.I)
        if not match:
            raise ValidationError(_('Position %s is not valid') % (pos, ))
        col, row = match.groups()
        col_num = 0
        for c in col:
            if c in string.ascii_letters:
                col_num = col_num * 26 + (ord(c.upper()) - ord('A')) + 1
        return (int(row) - 1, col_num - 1)

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
    def _add_id_column(self, file_txt):
        i = 0
        txt_lines = []
        for line in file_txt.split('\n'):
            if line and i == 0:
                line = '"id",' + line
            elif line:
                line = '%s.%s' % ('xls', uuid.uuid4()) + ',' + line
            txt_lines.append(line)
            i += 1
        file_txt = '\n'.join(txt_lines)
        return file_txt

    # @api.model
    # def _xldate_to_datetime(self, xldate):
    #     tempDate = datetime(1900, 1, 1)
    #     deltaDays = timedelta(days=int(xldate) - 2)
    #     xldate = (tempDate + deltaDays)
    #     return xldate.strftime("%Y-%m-%d")

    @api.model
    def import_xls(self, model, file, header_map=None,
                   extra_columns=None, auto_id=False,
                   force_id=False):
        # 1) Convert form XLS to CSV
        header_fields, file_txt = self.xls_to_csv(
            model, file, header_map=header_map,
            extra_columns=extra_columns, auto_id=auto_id,
            force_id=force_id)
        # 2) Do the import
        xls_ids = self.import_csv(model, header_fields, file_txt)
        return xls_ids

    @api.model
    def _get_field_type(self, model, field):
        """ Get 2 field type """
        try:
            record = self.env[model].new()
            for f in field.split('/'):
                field_type = record._fields[f].type
                if field_type in ('one2many', 'many2many'):
                    record = record[f]
                else:
                    return field_type
        except Exception:
            raise ValidationError(
                _('Invalid delaration, %s has no valid field type') % field)

    @api.model
    def _get_field_types(self, model, fields):
        """ Get multiple field type """
        field_types = {}
        for field in fields:
            field_type = self._get_field_type(model, field)
            field_types[field] = field_type
        return field_types

    @api.model
    def xls_to_csv(self, model, file,
                   header_map=None, extra_columns=None,
                   auto_id=False, force_id=False):
        """ This function will convert a simple (header+line) XLS file to
            simple CSV file (header+line) and the header columns
        To map user column with database column
        - header_map = {'Name': 'name', 'Document', 'doc_id', }
        If there is additional fixed column value
        - extra_columns = [('name', 'ABC'), ('id', 10), ]
        If the import file have column id, we will use this column to create
            external id, and hence possible to return record id being created
        if auto_id=True, system will add id field with running number
        if force_id=True, system will use ID from the original excel
            force_id=False, system will replace ID with UUID
        Return:
            - csv ready for import to Odoo
              'ID', 'Asset', ...
              'external_id_1', 'ASSET-0001', ...
              'external_id_2', 'ASSET-0002', ...
            - headers, i.e,
              ['id', 'asset_id', ...]
        """
        try:
            decoded_data = base64.decodestring(file)
            wb = xlrd.open_workbook(file_contents=decoded_data)
        except xlrd.XLRDError:
            raise ValidationError(
                _('Invalid file format, only .xls or .xlsx file allowed!'))
        except Exception:
            raise
        st = wb.sheet_by_index(0)
        csv_file = StringIO.StringIO()
        csv_out = unicodecsv.writer(csv_file,
                                    encoding='utf-8',
                                    quoting=unicodecsv.QUOTE_ALL)
        _HEADER_FIELDS = []
        if st._cell_values:
            _HEADER_FIELDS = st._cell_values[0]
        # Map column name
        if header_map:
            _HEADER_FIELDS = [header_map.get(x.lower().strip(), False) and
                              header_map[x.lower()] or False
                              for x in _HEADER_FIELDS]
        id_index = -1  # -1 means no id
        for nrow in xrange(st.nrows):
            if nrow == 0:  # Header, find id field
                header_values = [x.lower().strip()
                                 for x in st.row_values(nrow)]
                if 'id' in header_values:
                    id_index = header_values.index('id')
            if nrow > 0:
                row_values = st.row_values(nrow)
                field_types = self._get_field_types(model, _HEADER_FIELDS)
                for index, val in enumerate(row_values):
                    # Get Odoo field type
                    field = _HEADER_FIELDS[index]
                    # If id field, do not specify field_type
                    field_type = field != 'id' and field_types[field] or False
                    if id_index == index and val and not force_id:
                        # UUID replace id
                        xml_id = '%s.%s' % ('xls', uuid.uuid4())
                        row_values[index] = xml_id
                    else:
                        cell = st.cell(nrow, index)
                        row_values[index] = \
                            self._get_cell_value(cell, field_type=field_type)
                csv_out.writerow(row_values)
            else:
                csv_out.writerow(st.row_values(nrow))
        csv_file.seek(0)
        file_txt = csv_file.read()
        csv_file.close()
        if not file_txt:
            raise ValidationError(_(str("File Not found.")))
        # Create xml_ids if not already assigned
        if id_index == -1:
            _HEADER_FIELDS.insert(0, 'id')
            if auto_id:
                file_txt = self._add_id_column(file_txt)
            else:
                xml_id = '%s.%s' % ('xls', uuid.uuid4())
                file_txt = self._add_column('id', xml_id, file_txt)
        # Add extra column
        if extra_columns:
            for column in extra_columns:
                _HEADER_FIELDS.insert(0, str(column[0]))
                file_txt = self._add_column(column[0], column[1], file_txt)
        return (_HEADER_FIELDS, file_txt)

    @api.model
    def _get_cell_value(self, cell, field_type=False):
        """ If Odoo's field type is known, convert to valid string for import,
        if not know, just get value  as is """
        value = False
        datemode = 0  # From book.datemode, but we fix it for simplicity
        if field_type in ['date', 'datetime']:
            ctype = ctype_text.get(cell.ctype, 'unknown type')
            if ctype == 'number':
                time_tuple = xlrd.xldate_as_tuple(cell.value, datemode)
                date = datetime(*time_tuple)
                if field_type == 'date':
                    value = date.strftime("%Y-%m-%d")
                elif field_type == 'datetime':
                    value = date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                value = cell.value
        elif field_type in ['integer', 'float']:
            value_str = str(cell.value).strip().replace(',', '')
            if len(value_str) == 0:
                value = ''
            elif value_str.replace('.', '', 1).isdigit():  # Is number
                if field_type == 'integer':
                    value = int(float(value_str))
                elif field_type == 'float':
                    value = float(value_str)
            else:  # Is string, no conversion
                value = value_str
        elif field_type in ['many2one']:
            # If number, change to string
            if isinstance(cell.value, (int, long, float, complex)):
                value = str(cell.value)
            else:
                value = cell.value
        else:
            value = cell.value
        # If string, cleanup
        if isinstance(value, str):
            value = value.encode('utf-8')
            if value[-2:] == '.0':
                value = value[:-2]
        # Except boolean, when no value, we should return as ''
        if field_type not in ['boolean']:
            if not value:
                value = ''
        return value

        # if type == 'empty' or type == 'text' \
        #     or type == 'bool' or type == 'error' \
        #         or type == 'blank':
        #     value = cell.value
        # elif type == 'number':
        #     if not cell.value:
        #         value = 0
        #     else:
        #         if not str(cell.value).isdigit():
        #             value = int(cell.value)
        #         else:
        #             value = cell.value
        # elif type == 'xldate':
        #     str_date = self._xldate_to_datetime(
        #         cell.value)
        #     value = str_date
        # else:
        #     value = cell.value
        # return value

    # @api.model
    # def _get_cell_value(self, cell):
    #     ctype = cell.ctype
    #     type = ctype_text.get(ctype, 'unknown type')
    #     value = False
    #     if type == 'empty' or type == 'text' \
    #         or type == 'bool' or type == 'error' \
    #             or type == 'blank':
    #         value = cell.value
    #     elif type == 'number':
    #         if not cell.value:
    #             value = 0
    #         else:
    #             if not str(cell.value).isdigit():
    #                 value = int(cell.value)
    #             else:
    #                 value = cell.value
    #     elif type == 'xldate':
    #         str_date = self._xldate_to_datetime(
    #             cell.value)
    #         value = str_date
    #     else:
    #         value = cell.value
    #     return value

    @api.model
    def import_csv(self, model, header_fields, csv_txt, csv_header=True):
        """
        The csv_txt loaded, must also have the header row
        - header_fields i.e, ['id', 'field1', 'field2']
        - csv_txt = normal csv with comma delimited
        - csv_header = True (default), if csv_txt contain header row
        """
        # get xml_ids
        f = StringIO.StringIO(csv_txt)
        rows = csv.reader(f, delimiter=',')
        id_index = -1
        xml_ids = []
        # for row in rows:  # Check the first row only
        #     head_row = [isinstance(x, basestring) and x.lower() or ''
        #                 for x in row]
        #     id_index = head_row.index('id')
        #     break
        head_row = [isinstance(x, basestring) and x.lower() or ''
                    for x in header_fields]
        id_index = head_row.index('id')
        if id_index >= 0:
            for idx, row in enumerate(rows):
                if csv_header and idx == 0:
                    continue
                if isinstance(row[id_index], basestring) and \
                        len(row[id_index].strip()) > 0:
                    xml_ids.append(row[id_index])
        # Do the import
        Import = self.env['base_import.import']
        imp = Import.create({
            'res_model': model,
            'file': csv_txt,
        })
        [errors] = imp.do(
            header_fields,
            {'headers': csv_header, 'separator': ',',
             'quoting': '"', 'encoding': 'utf-8'})
        if errors:
            if errors[0]['message'] == ("Unknown error during import: "
                                        "<type 'exceptions.TypeError'>: "
                                        "'bool' object is not iterable"):
                raise except_orm(_('Data not valid or no data to import!'), "")
            else:
                raise ValidationError(errors[0]['message'].encode('utf-8'))
        return xml_ids

    @api.model
    def get_external_id(self, record):
        ModelData = self.env['ir.model.data']
        xml_id = record.get_external_id([record.id])
        if not xml_id or (record.id in xml_id and xml_id[record.id] == ''):
            ModelData.create({'name': '%s_%s' % (record._table, record.id),
                              'module': 'pabi_utils',
                              'model': record._name,
                              'res_id': record.id, })
            xml_id = record.get_external_id([record.id])
        return xml_id[record.id]
