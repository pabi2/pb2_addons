# -*- coding: utf-8 -*-
from ast import literal_eval
import base64
import xlrd
import xlwt
import string
import re
import itertools
import cStringIO
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


def get_line_max(line_field):
    """ i.e., line_field = line_ids[100], mas = 100 else 0 """
    if '[' in line_field and ']' in line_field:
        i = line_field.index('[')
        j = line_field.index(']')
        max_str = line_field[i + 1:j]
        try:
            if len(max_str) > 0:
                return (line_field[:i], int(max_str))
            else:
                return (line_field, False)
        except:
            return (line_field, False)


def get_sheet_by_name(book, name):
    """Get a sheet by name from xlrd Workbook, a strangely missing method.
    Returns None if no sheet with the given name is present.
    """
    try:
        for idx in itertools.count():
            sheet = book.sheet_by_index(idx)
            if sheet.name == name:
                return sheet
    except IndexError:
        raise ValidationError(_("'%s' sheet not found") % (name,))


class ImportXlsxTemplate(models.TransientModel):
    """ This wizard is used with the template (ir.attachment) to import
    xlsx template back to active record """
    _name = 'import.xlsx.template'

    import_file = fields.Binary(
        string='Import File (*.xlsx)',
        required=True,
    )
    template_id = fields.Many2one(
        'ir.attachment',
        string='Template',
        required=True,
        ondelete='set null',
        domain="[('res_model', '=', res_model)]",
    )
    res_id = fields.Integer(
        string='Resource ID',
        readonly=True,
        required=True,
    )
    res_model = fields.Char(
        string='Resource Model',
        readonly=True,
        required=True,
    )

    @api.model
    def default_get(self, fields):
        res_model = self._context.get('active_model', False)
        res_id = self._context.get('active_id', False)
        template = self.env['ir.attachment'].\
            search([('res_model', '=', res_model)])
        if not template:
            raise ValidationError(_('No template found!'))
        defaults = super(ImportXlsxTemplate, self).default_get(fields)
        if not template.datas:
            raise ValidationError(_('No file in %s') % (template.name,))
        defaults['template_id'] = len(template) == 1 and template.id or False
        defaults['res_id'] = res_id
        defaults['res_model'] = res_model
        return defaults

    @api.model
    def _delete_record_data(self, record, data_dict):
        """ Fill data from record with format in data_dict to workbook """
        if not record or not data_dict:
            return
        try:
            for sheet_name in data_dict:
                worksheet = data_dict[sheet_name]
                # HEAD
                for rc, field in worksheet.get('_HEAD_', {}).iteritems():
                    if field in record and record[field]:
                        record[field] = False  # Set to False
                # Line Items
                line_fields = filter(lambda l: l != '_HEAD_', worksheet)
                for line_field in line_fields:
                    line_field, max_row = get_line_max(line_field)
                    if line_field in record and record[line_field]:
                        record[line_field].unlink()  # Delete all lines
        except Exception, e:
            raise ValidationError(
                _('Error deleting data!\n%s') % e)

    @api.model
    def _get_line_vals(self, st, worksheet, line_field):
        """ Get values of this field from excel sheet """
        XLS = self.env['pabi.utils.xls']
        new_line_field, max_row = get_line_max(line_field)
        fields = [field for rc, field
                  in worksheet.get(line_field, {}).iteritems()]
        vals = dict([(field, []) for field in fields])
        for rc, field in worksheet.get(line_field, {}).iteritems():
            row, col = XLS.pos2idx(rc)
            for idx in range(row, st.nrows - 1):
                value = st.cell(idx, col).value
                vals[field].append(value)
                if max_row and (idx - row) >= max_row:
                    break
        return (new_line_field, vals)

    @api.model
    def _import_record_data(self, import_file, record, data_dict):
        """ Create temp simple excel, and prepare to convert to CSV to load """
        if not record or not data_dict:
            return
        try:
            XLS = self.env['pabi.utils.xls']
            decoded_data = base64.decodestring(import_file)
            wb = xlrd.open_workbook(file_contents=decoded_data)

            # Create output xls, begins with id column
            col_idx = 0  # Starting column
            out_wb = xlwt.Workbook()
            out_st = out_wb.add_sheet("Sheet 1")
            xml_id = XLS.get_external_id(record)
            out_st.write(0, 0, 'id')
            out_st.write(1, 0, xml_id)
            col_idx += 1

            for sheet_name in data_dict:  # For each Sheet
                worksheet = data_dict[sheet_name]
                st = get_sheet_by_name(wb, sheet_name)
                # HEAD(s)
                for rc, field in worksheet.get('_HEAD_', {}).iteritems():
                    row, col = XLS.pos2idx(rc)
                    value = XLS._get_cell_value(st.cell(row, col))
                    out_st.write(0, col_idx, field)  # Next Column
                    out_st.write(1, col_idx, value)  # Next Value
                    col_idx += 1
                # Line Items
                line_fields = filter(lambda l: l != '_HEAD_', worksheet)
                for line_field in line_fields:
                    line_field, vals = self._get_line_vals(st, worksheet,
                                                           line_field)
                    for field in vals:
                        # Columns, i.e., line_ids/field_id
                        out_st.write(0, col_idx, '%s/%s' % (line_field, field))
                        # Data
                        i = 1
                        for value in vals[field]:
                            out_st.write(i, col_idx, value)
                            i += 1
                        col_idx += 1
            content = cStringIO.StringIO()
            out_wb.save(content)
            content.seek(0)  # Set index to 0, and start reading
            xls_file = base64.encodestring(content.read())
            model = record._name
            XLS.import_xls(model, xls_file, header_map=False,
                           extra_columns=False, auto_id=False,
                           force_id=True)
        except xlrd.XLRDError:
            raise ValidationError(
                _('Invalid file format, only .xls or .xlsx file allowed!'))
        except Exception, e:
            raise ValidationError(
                _('Error importing data!\n%s') % e)

    @api.model
    def _import_template(self, import_file, template, res_model, res_id):
        """
        - Delete fields' data according to data_dict['__IMPORT__']
        - Import data from excel according to data_dict['__IMPORT__']
        """
        record = self.env[res_model].browse(res_id)
        data_dict = literal_eval(template.description.strip())
        if not data_dict.get('__IMPORT__'):
            raise ValidationError(
                _("No data_dict['__IMPORT__'] in template %s") % template.name)
        # Delete existing data first
        self._delete_record_data(record, data_dict['__IMPORT__'])
        # Fill up record with data from excel sheets
        self._import_record_data(import_file, record, data_dict['__IMPORT__'])
        return

    @api.multi
    def action_import(self):
        self.ensure_one()
        if not self.import_file:
            raise ValidationError(_('Please choose excel file to import!'))
        self._import_template(self.import_file, self.template_id,
                              self.res_model, self.res_id)
        return
