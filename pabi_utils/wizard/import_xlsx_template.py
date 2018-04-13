# -*- coding: utf-8 -*-
from ast import literal_eval
import base64
import xlrd
import xlwt
import itertools
import cStringIO
import time
from datetime import date, datetime as dt
from openerp.tools import float_compare
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, ValidationError, RedirectWarning
from openerp.tools.safe_eval import safe_eval as eval


def get_field_condition(field):
    """ i..e, 'field${value > 0 and value or False}' """
    if '${' in field and '}' in field:
        i = field.index('${')
        j = field.index('}', i)
        cond = field[i + 2:j]
        try:
            if len(cond) > 0:
                return (field.replace('${%s}' % cond, ''), cond)
        except:
            return (field, False)
    return (field, False)


def get_line_max(line_field):
    """ i.e., line_field = line_ids[100], max = 100 else 0 """
    if '[' in line_field and ']' in line_field:
        i = line_field.index('[')
        j = line_field.index(']', i)
        max_str = line_field[i + 1:j]
        try:
            if len(max_str) > 0:
                return (line_field[:i], int(max_str))
        except:
            return (line_field, False)
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
        domain="[('res_model', '=', res_model),"
        "('res_id', '=', False),('res_name', '=', False)]"
    )
    domain_template_ids = fields.Many2many(
        'ir.attachment',
        string='Domain Templates',
        help="template_id's domain. If False, no domain",
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
    datas = fields.Binary(
        string='Sample',
        related='template_id.datas',
        readonly=True,
    )
    datas_fname = fields.Char(
        string='Template Name',
        related='template_id.datas_fname',
        readonly=True,
    )

    @api.model
    def view_init(self, fields_list):
        """ This template only works on some context of active record """

        res_model = self._context.get('active_model', False)
        res_id = self._context.get('active_id', False)
        record = self.env[res_model].browse(res_id)
        messages = []
        valid = True
        # For all import, only allow import in draft state (for documents)
        import_states = self._context.get('template_import_states', [])
        if import_states:  # states specified in context, test this
            if 'state' in record and \
                    record['state'] not in import_states:
                messages.append(
                    _('Document must be in %s states!') % import_states)
                valid = False
        else:  # no specific state specified, test with draft
            if 'state' in record and 'draft' not in record['state']:  # not in
                messages.append(_('Document must be in draft state!'))
                valid = False
        # Context testing
        if self._context.get('template_context', False):
            template_context = self._context['template_context']
            for key, value in template_context.iteritems():
                if key not in record or \
                        (record._fields[key].type == 'many2one' and
                         record[key].id or record[key]) != value:
                    valid = False
                    messages.append(
                        _('This import action is not usable '
                          'in this document context!'))
                    break
        if not valid:
            raise ValidationError('\n'.join(messages))

    @api.model
    def get_eval_context(self, model=False, value=False):
        eval_context = {'float_compare': float_compare,
                        'time': time,
                        'datetime': dt,
                        'date': date,
                        'env': self.env,
                        'context': self._context,
                        'value': False,
                        'model': False,
                        }
        if model:
            eval_context.update({'model': self.env[model]})
        if value:
            eval_context.update({'value': value})
        return eval_context

    @api.model
    def default_get(self, fields):
        res_model = self._context.get('active_model', False)
        res_id = self._context.get('active_id', False)
        template_dom = [('res_model', '=', res_model),
                        ('parent_id', '!=', False)]
        template_fname = self._context.get('template_fname', False)
        if template_fname:  # Specific template
            template_dom.append(('datas_fname', '=', template_fname))
        templates = self.env['ir.attachment'].search(template_dom)
        if not templates:
            raise ValidationError(_('No template found!'))
        defaults = super(ImportXlsxTemplate, self).default_get(fields)
        for template in templates:
            if not template.datas:
                act = self.env.ref('document.action_document_directory_tree')
                raise RedirectWarning(
                    _('File "%s" not found in template, %s.') %
                    (template.datas_fname, template.name),
                    act.id, _('Set Templates'))
        defaults['template_id'] = len(templates) == 1 and template.id or False
        defaults['res_id'] = res_id
        defaults['res_model'] = res_model
        defaults['domain_template_ids'] = templates.ids
        return defaults

    @api.model
    def _delete_record_data(self, record, data_dict):
        """ Fill data from record with format in data_dict to workbook """
        if not record or not data_dict:
            return
        try:
            for sheet_name in data_dict:
                worksheet = data_dict[sheet_name]
                # kittiu: Don't del header value, it make requried field error
                # # HEAD
                # for rc, field in worksheet.get('_HEAD_', {}).iteritems():
                #     if field in record and record[field]:
                #         record[field] = False  # Set to False
                # --
                # Line Items
                line_fields = filter(lambda l: l != '_HEAD_', worksheet)
                for line_field in line_fields:
                    line_field, _ = get_line_max(line_field)
                    if line_field in record and record[line_field]:
                        record[line_field].unlink()  # Delete all lines
        except Exception, e:
            raise except_orm(_('Error deleting data!'), e)

    @api.model
    def _get_line_vals(self, st, worksheet, model, line_field):
        """ Get values of this field from excel sheet """
        XLS = self.env['pabi.utils.xls']
        new_line_field, max_row = get_line_max(line_field)
        vals = {}
        for rc, columns in worksheet.get(line_field, {}).iteritems():
            if not isinstance(columns, list):  # Ex. 'A1': ['field1', 'field2']
                columns = [columns]
            for field in columns:
                rc, key_eval_cond = get_field_condition(rc)
                x_field, val_eval_cond = get_field_condition(field)
                row, col = XLS.pos2idx(rc)
                out_field = '%s/%s' % (new_line_field, x_field)
                field_type = XLS._get_field_type(model, out_field)
                vals.update({out_field: []})
                # Case default value from an eval
                for idx in range(row, st.nrows):
                    if max_row and (idx - row) > (max_row - 1):
                        break
                    value = XLS._get_cell_value(st.cell(idx, col),
                                                field_type=field_type)
                    eval_context = self.get_eval_context(model=model,
                                                         value=value)
                    if key_eval_cond:
                        # str() will throw cordinal not in range error
                        # value = str(eval(key_eval_cond, eval_context))
                        value = eval(key_eval_cond, eval_context)
                    # Case Eval
                    if val_eval_cond:
                        # value = str(eval(val_eval_cond, eval_context))
                        value = eval(val_eval_cond, eval_context)
                    vals[out_field].append(value)
                # if all value in vals[out_field] == '', we don't need it
                if not filter(lambda x: x != '', vals[out_field]):
                    vals.pop(out_field)
        return vals

    @api.model
    def _import_record_data(self, import_file, record, data_dict):
        """ Create temp simple excel, and prepare to convert to CSV to load """
        if not record or not data_dict:
            return
        try:
            XLS = self.env['pabi.utils.xls']
            decoded_data = base64.decodestring(import_file)
            wb = xlrd.open_workbook(file_contents=decoded_data)
            model = record._name

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
                st = False
                if isinstance(sheet_name, str):
                    st = get_sheet_by_name(wb, sheet_name)
                elif isinstance(sheet_name, int):
                    st = wb.sheet_by_index(sheet_name - 1)
                if not st:
                    raise ValidationError(
                        _('Sheet %s not found!') % sheet_name)
                # HEAD(s)
                for rc, field in worksheet.get('_HEAD_', {}).iteritems():
                    rc, key_eval_cond = get_field_condition(rc)
                    field, val_eval_cond = get_field_condition(field)
                    row, col = XLS.pos2idx(rc)
                    field_type = XLS._get_field_type(model, field)
                    value = XLS._get_cell_value(st.cell(row, col),
                                                field_type=field_type)
                    eval_context = self.get_eval_context(model=model,
                                                         value=value)
                    if key_eval_cond:
                        value = str(eval(key_eval_cond, eval_context))
                    # Case Eval
                    if val_eval_cond:
                        value = str(eval(val_eval_cond, eval_context))
                    # --
                    out_st.write(0, col_idx, field)  # Next Column
                    out_st.write(1, col_idx, value)  # Next Value
                    col_idx += 1
                # Line Items
                line_fields = filter(lambda l: l != '_HEAD_', worksheet)
                for line_field in line_fields:
                    vals = self._get_line_vals(st, worksheet,
                                               model, line_field)
                    for field in vals:
                        # Columns, i.e., line_ids/field_id
                        out_st.write(0, col_idx, field)
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
            XLS.import_xls(model, xls_file, header_map=False,
                           extra_columns=False, auto_id=False,
                           force_id=True)
        except xlrd.XLRDError:
            raise ValidationError(
                _('Invalid file format, only .xls or .xlsx file allowed!'))
        except Exception, e:
            raise except_orm(_('Error importing data!'), e)

    @api.model
    def _post_import_operation(self, record, operations):
        """ Run python code after import """
        if not record or not operations:
            return
        try:
            if not isinstance(operations, list):
                operations = [operations]
            for operation in operations:
                if '${' in operation:
                    code = (operation.split('${'))[1].split('}')[0]
                    eval_context = {'object': record}
                    eval(code, eval_context)
        except Exception, e:
            raise except_orm(_('Post import operation error!'), e)

    @api.model
    def import_template(self, import_file, template, res_model, res_id):
        """
        - Delete fields' data according to data_dict['__IMPORT__']
        - Import data from excel according to data_dict['__IMPORT__']
        """
        self = self.sudo()
        record = self.env[res_model].browse(res_id)
        data_dict = literal_eval(template.description.strip())
        if not data_dict.get('__IMPORT__'):
            raise ValidationError(
                _("No data_dict['__IMPORT__'] in template %s") % template.name)
        # Delete existing data first
        self._delete_record_data(record, data_dict['__IMPORT__'])
        # Fill up record with data from excel sheets
        self._import_record_data(import_file, record, data_dict['__IMPORT__'])
        # Post Import Operation, i.e., cleanup some data
        if data_dict.get('__POST_IMPORT__', False):
            self._post_import_operation(record, data_dict['__POST_IMPORT__'])
        return

    @api.multi
    def action_import(self):
        self.ensure_one()
        if not self.import_file:
            raise ValidationError(_('Please choose excel file to import!'))
        self.import_template(self.import_file, self.template_id,
                             self.res_model, self.res_id)
        return
