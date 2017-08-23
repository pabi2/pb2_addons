# -*- coding: utf-8 -*-
import StringIO
import csv
import base64
import os
import xlrd
import uuid
from xlrd.sheet import ctype_text
import unicodecsv
from datetime import datetime, timedelta
from openerp import models, api, _
from openerp.exceptions import ValidationError

HEADER_BUDGET_BREAKDOWN = [
    'ID', 'Name', 'Org', 'Fiscal Year', 'Revision', 'Planned Overall',
    'Budget Policy', 'Diff Amount', 'Section', 'Planned Amount', 'Consumed',
    'Rolling', 'Last Policy Amount', 'Policy Amount'
]


class PABIXls(models.AbstractModel):
    _inherit = 'pabi.xls'

    @api.model
    def xls_to_csv(self, model, file, header_map=None, extra_columns=None):
        context = self._context.copy()
        if context.get('active_model', False) not in ['budget.breakdown']:
            return super(PABIXls, self).xls_to_csv(
                model, file, header_map=header_map,
                extra_columns=extra_columns)

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

        _HEADER_FIELDS = []
        if st._cell_values:
            _HEADER_FIELDS = HEADER_BUDGET_BREAKDOWN

        csv_data = []
        csv_data.append(_HEADER_FIELDS)

        xml_id = 30
        csv_row_values = ['' for header in HEADER_BUDGET_BREAKDOWN]
        csv_row_values[HEADER_BUDGET_BREAKDOWN.index('ID')] = xml_id

        detail_header = []
        for nrow in xrange(st.nrows):
            row_values = list(filter(lambda x: x != '', st.row_values(nrow)))
            if len(row_values) == 0:
                continue
            elif len(row_values) == 1:
                csv_row_values[HEADER_BUDGET_BREAKDOWN.index('Name')] = \
                    row_values[0]
                continue
            elif len(row_values) == 2:
                csv_row_values[HEADER_BUDGET_BREAKDOWN.index(row_values[0])] \
                     = row_values[1]
                continue
            elif len(row_values) == 6 and len(detail_header) == 0:
                detail_header = row_values
                continue
            for index, val in enumerate(row_values):
                if index == 0:
                    continue
                csv_row_values[HEADER_BUDGET_BREAKDOWN.index(
                    detail_header[index])] = val
            csv_data.append(csv_row_values)
            csv_row_values = ['' for header in HEADER_BUDGET_BREAKDOWN]
        csv_out.writerows(csv_data)
        csv_file.close()
        csv_file = open(ftemp + '.csv', 'r')
        file_txt = csv_file.read()
        csv_file.close()
        os.unlink(ftemp + '.xls')
        os.unlink(ftemp + '.csv')
        if not file_txt:
            raise ValidationError(_(str("File Not found.")))
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
        return (_HEADER_FIELDS, file_txt)
