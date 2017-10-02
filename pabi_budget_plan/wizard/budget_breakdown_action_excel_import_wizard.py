# -*- coding: utf-8 -*-
import xlrd
import xlwt
import base64
import cStringIO
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

IMPORT_ACTION = {
    'budget_breakdown_line': {
        'model': 'budget.breakdown.line',
        'header_map': {
            'id': 'id',
            'policy amount': 'policy_amount'
        },
        'extra_columns': [],
    }
}


class BudgetBreakdownActionExcelImportWizard(models.TransientModel):
    _name = 'budget.breakdown.action.excel.import.wizard'

    import_file = fields.Binary(
        string='Import File (*.xls)',
        required=True,
    )

    @api.model
    def _prepare_xls_file(self, import_file):
        """ Transform to excle with only 2 volumn, ID and Policy Amount """
        active_id = self._context.get('active_id')
        line_ids = self.env['budget.breakdown'].browse(active_id).line_ids.ids

        content = base64.decodestring(import_file)
        rb = xlrd.open_workbook(file_contents=content)
        st = rb.sheet_by_index(0)
        # Reading from I11 and J11
        row1, col1 = self.env['pabi.utils.xls'].pos2idx('J11')  # External ID
        row2, col2 = self.env['pabi.utils.xls'].pos2idx('I11')  # Policy Amount
        out_rows = []
        for row in range(row1, st.nrows):
            row_vals = st.row_values(row)
            id = int(row_vals[col1])
            policy_amount = row_vals[col2]
            if id not in line_ids:
                raise ValidationError(_('Invalid import file, please use the '
                                        'one exported from this window!'))
            out_rows.append(('budget_breakdown_line.%s' % id, policy_amount))

        # Create output xls file
        wb = xlwt.Workbook()
        st = wb.add_sheet("budget_breakdown")
        # Write column header
        st.write(0, 0, 'ID')
        st.write(0, 1, 'Policy Amount')
        i = 1
        # line line
        for row in out_rows:
            st.write(i, 0, row[0])
            st.write(i, 1, row[1])
            i += 1
        content = cStringIO.StringIO()
        wb.save(content)
        content.seek(0)  # Set index to 0, and start reading
        res = base64.encodestring(content.read())
        return res

    @api.multi
    def action_import_xls(self):
        self.ensure_one()
        if not self.import_file:
            raise ValidationError(_('Please choose excel file to import!'))
        import_action = 'budget_breakdown_line'
        model = IMPORT_ACTION[import_action]['model']
        header_map = IMPORT_ACTION[import_action].get('header_map', False)
        extra_columns = IMPORT_ACTION[import_action].get('extra_columns',
                                                         False)
        xls_file = self._prepare_xls_file(self.import_file)
        return self.env['pabi.utils.xls'].\
            import_xls(model, xls_file, header_map=header_map,
                       extra_columns=extra_columns, auto_id=False,
                       force_id=True)
