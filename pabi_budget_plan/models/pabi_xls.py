# -*- coding: utf-8 -*-
from openerp import models, api, _
import base64
from datetime import datetime
import xlrd
from openerp.exceptions import ValidationError
import unicodecsv
import os

RESTRICT_MODEL = ['budget.breakdown.line']
HEADER_FIELDS = ['ID', 'Policy Amount']


class PABIXls(models.AbstractModel):
    _inherit = 'pabi.xls'

    @api.model
    def xls_to_csv(self, model, file, header_map=None, extra_columns=None,
                   auto_id=False):
        """
        This function will convert from xls to csv of budget.breakdown.line
        by in the excel file consisted of two column is 'ID' and
        'Policy Amount'
        Return:
            - csv ready for import odoo
              'ID', 'Policy Amount'
              'budget_breakdown_line.1685', 0
            - headers, i.e,
              ['id', 'policy_amount']
        """
        if model not in RESTRICT_MODEL:
            return super(PABIXls, self).xls_to_csv(model, file,
                                                   header_map=header_map,
                                                   extra_columns=extra_columns,
                                                   auto_id=auto_id)

        # --
        # For XLS (temp)
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
                _('Invalid file format, only .xls or .xlsx file allowed'))
        except Exception:
            raise
        st = wb.sheet_by_index(0)

        # For CSV (temp)
        active_id = self._context.copy().get('active_id', False)
        breakdown = False
        if active_id:
            Breakdown = self.env['budget.breakdown']
            breakdown = Breakdown.browse(active_id)
        csv_file = open(ftemp + '.csv', 'wb')
        csv_out = unicodecsv.writer(csv_file,
                                    encoding='utf-8',
                                    quoting=unicodecsv.QUOTE_ALL)
        _HEADER_FIELDS = HEADER_FIELDS
        id_index, org_name, year, count = -1, False, False, 0
        header_values = []
        for nrow in xrange(st.nrows):
            row = list(filter(lambda x: x != '', st.row_values(nrow)))
            if not row:
                continue
            row_values = [0 for x in _HEADER_FIELDS]
            if len(header_values) == 0:
                header_values = [str(x).lower().strip() for x in row]
            if 'id' in header_values:
                id_index = header_values.index('id')
                header_indexs = [id_index,
                                 header_values.index('policy amount')]
                count = count + 1
                if count == 1:
                    csv_out.writerow(_HEADER_FIELDS)
                    continue
            elif id_index == -1:
                if breakdown and len(row) == 2:
                    if row[0].lower().strip() == 'org':
                        org_name = row[1].strip()
                    elif row[0].lower().strip() == 'fiscal year':
                        year = row[1].strip()
                    if org_name and year:
                        if org_name != breakdown.org_id.name_short or \
                           year != breakdown.fiscalyear_id.name:
                            raise ValidationError(
                                _("The file is invalid, "
                                  "please select a new file according to "
                                  "the current window"))
                header_values = []
                continue

            # budget.policy.line
            for index, val in enumerate(row):
                if index not in header_indexs:
                    continue
                if header_values[index] == 'id':
                    Line = self.env['budget.breakdown.line']
                    line = Line.browse(int(val))
                    xml_id = line.get_external_id([line.id]).get(int(val))
                    row_values[header_indexs.index(index)] = xml_id
                else:
                    row_values[header_indexs.index(index)] = val
            csv_out.writerow(row_values)
        csv_file.close()
        csv_file = open(ftemp + '.csv', 'r')
        file_txt = csv_file.read()
        csv_file.close()
        os.unlink(ftemp + '.xls')
        os.unlink(ftemp + '.csv')
        if not file_txt:
            raise ValidationError(_(str("File Not found.")))
        if header_map:
            _HEADER_FIELDS = [header_map.get(x.lower().strip(), False) and
                              header_map[x.lower()] or False
                              for x in _HEADER_FIELDS]
        return (_HEADER_FIELDS, file_txt)
