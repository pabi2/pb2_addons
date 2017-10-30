# -*- coding: utf-8 -*-
import itertools
import base64
import cStringIO
import string
import re
from xlrd import open_workbook
from xlwt import Formula
from xlutils.filter import process, XLRDReader, XLWTWriter
import openpyxl

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


def _get_cell(sheet, col, row):
    """ HACK: Extract the internal xlwt cell representation. """
    row = sheet._Worksheet__rows.get(row)
    if not row:
        return None
    cell = row._Row__cells.get(col)
    return cell


def set_cell(sheet, row, col, value=None, formula=None):
    """ Change cell value without changing formatting. """
    prev_cell = _get_cell(sheet, col, row)
    if value:
        sheet.write(row, col, value)
    if formula:
        sheet.write(row, col, Formula(formula))
    if prev_cell:
        new_cell = _get_cell(sheet, col, row)
        if new_cell:
            new_cell.xf_idx = prev_cell.xf_idx


def copy2(wb):
    w = XLWTWriter()
    process(XLRDReader(wb, 'unknown.xls'), w)
    return w.output[0][1], w.style_list


def pos2idx(pos):
    match = re.match(r"([a-z]+)([0-9]+)", pos, re.I)
    if not match:
        raise ValidationError(_('Position %s is not valid') % (pos, ))
    col, row = match.groups()
    col_num = 0
    for c in col:
        if c in string.ascii_letters:
            col_num = col_num * 26 + (ord(c.upper()) - ord('A')) + 1
    return (int(row) - 1, col_num - 1)


def get_sheet_by_name(book, name):
    """Get a sheet by name from xlwt.Workbook, a strangely missing method.
    Returns None if no sheet with the given name is present.
    """
    try:
        for idx in itertools.count():
            sheet = book.get_sheet(idx)
            if sheet.name == name:
                return sheet
    except IndexError:
        raise ValidationError(_("'%s' sheet not found") % (name,))


class BudgetPlanExportXls(models.TransientModel):
    _name = 'budget.plan.export.xls'

    name = fields.Char(
        string='File Name',
        readonly=True,
    )
    data = fields.Binary(
        string='File',
        readonly=True,
    )
    template_id = fields.Many2one(
        'ir.attachment',
        string='Template',
        required=True,
        ondelete='set null',
        readonly=True,
    )
    res_id = fields.Integer(
        string='Resource ID',
        readonly=True,
        required=True,
    )
    model = fields.Char(
        string='Model',
        readonly=True,
        required=True,
    )
    state = fields.Selection(
        [('choose', 'choose'),
         ('get', 'get')],
        default='choose',
    )

    @api.model
    def default_get(self, fields):
        TEMPLATE = {
            'budget.plan.unit': 'pabi_budget_plan.unit_base_template',
        }
        active_model = self._context.get('active_model', False)
        active_id = self._context.get('active_id', False)
        if active_model not in TEMPLATE:
            raise ValidationError(_('No import template found!'))
        defaults = super(BudgetPlanExportXls, self).default_get(fields)
        template = self.env.ref(TEMPLATE[active_model])
        if not template.datas:
            raise ValidationError(_('No file in %s') % (template.name,))
        defaults['template_id'] = template.id
        defaults['res_id'] = active_id
        defaults['model'] = active_model
        return defaults

    @api.model
    def _get_value(self, record, field):
        for f in field.split('.'):
            record = record[f]
        return record

    @api.model
    def _prepare_import_template(self, model, res_id, template):
        rd = open_workbook(formatting_info=True,
                           file_contents=base64.decodestring(template.datas))
        wb, wb_style = copy2(rd)  # Create workbook from template
        # worksheets = {
        #     <sheet>: {
        #         'HEAD': {<field>: <position x,y>,
        #                  <field>: <position x,y>},
        #         'LINES': {<field>: <start position x, y>,
        #                   <field>: <start position x, y>}
        #     }
        # }
        record = self.env[model].browse(res_id)
        worksheets = {
            'Expense': {
                'HEAD': {
                    'B1': 'fiscalyear_id.name',
                    'B2': 'org_id.name_short',
                    'B3': 'section_id.code',
                },
                'LINES': {
                },
            }
        }

        for st_name in worksheets:
            st = get_sheet_by_name(wb, st_name)
            worksheet = worksheets[st_name]
            # Write HEAD
            for pos, field in worksheet.get('HEAD', {}).iteritems():
                row, col = pos2idx(pos)
                value = self._get_value(record, field)
                set_cell(st, row, col, value=value)
            set_cell(st, 9, 8, formula='A10+A11')
            # Write LINES
        # st = wb.get_sheet(0)
        # x = u'กกกกกกก'
        # st.write(0, 0, x)

        # Set active worksheet = 2
        wb.active_sheet = 0

        # Return file
        content = cStringIO.StringIO()
        wb.save(content)
        content.seek(0)  # Set index to 0, and start reading
        res = base64.encodestring(content.read())

        # Setting data validation by openpyxl
        f = open('/tmp/test.xlsx', 'w')
        f.write(res)
        f.close()

        wb2 = openpyxl.load_workbook(filename='/tmp/test.xlsx')
        content2 = cStringIO.StringIO()
        wb2.save(content2)
        content2.seek(0)  # Set index to 0, and start reading
        res = base64.encodestring(content2.read())

        return res

    @api.multi
    def act_getfile(self):
        self.ensure_one()

        out_file = self._prepare_import_template(self.model,
                                                 self.res_id,
                                                 self.template_id)
        out_name = 'MyUnitBase.xls'

        self.write({'state': 'get', 'data': out_file, 'name': out_name})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'budget.plan.export.xls',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
