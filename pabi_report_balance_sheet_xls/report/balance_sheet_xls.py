# -*- coding: utf-8 -*-
from datetime import datetime
import xlwt
from openerp.addons.account.report.common_report_header \
    import common_report_header
from openerp.addons.report_xls.report_xls import report_xls
from openerp.report import report_sxw
from openerp import pooler
from openerp.tools.translate import _


class BalanceSheetParser(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context=None):
        super(BalanceSheetParser, self).__init__(cr, uid, name,
                                                 context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr

        footer_date_time = self.formatLang(str(datetime.today()),
                                           date_time=True)

        self.localcontext.update({
            'cr': cr,
            'uid': uid,
            'get_lines': self.get_lines,
            'get_fiscalyear': self._get_fiscalyear,
            'get_account': self._get_account,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_filter': self._get_filter,
            'get_start_date': self._get_start_date,
            'get_end_date': self._get_end_date,
            'get_target_move': self._get_target_move,
            'additional_args': [
                ('--header-font-name', 'Helvetica'),
                ('--footer-font-name', 'Helvetica'),
                ('--header-font-size', '10'),
                ('--footer-font-size', '6'),
                ('--header-spacing', '2'),
                ('--footer-left', footer_date_time),
                ('--footer-right', ' '.join((_('Page'), '[page]', _('of'),
                                             '[topage]'))),
                ('--footer-line',),
            ]
        })

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
            new_ids = \
                'chart_account_id' in data['form'] and \
                [data['form']['chart_account_id']] or []
            objects = self.pool.get('account.account').browse(
                self.cr, self.uid, new_ids)
        self.localcontext.update({
            'report_name':
                _(data['form']['account_report_id'][1].encode('utf-8'))})
        return super(BalanceSheetParser, self).set_context(
            objects, data, new_ids, report_type=report_type)

    def get_lines(self, data):
        lines = []
        account_obj = self.pool.get('account.account')
        currency_obj = self.pool.get('res.currency')
        report_obj = self.pool.get('account.financial.report')
        data = data['form']
        cr, uid = self.cr, self.uid
        ids2 = report_obj._get_children_by_order(
                cr, uid, [data['account_report_id'][0]],
                context=data['used_context'])
        for report in report_obj.browse(cr, uid, ids2,
                                        context=data['used_context']):
            vals = {
                'name': report.name,
                'balance': report.balance * report.sign or 0.0,
                'type': 'report',
                'level': bool(report.style_overwrite) and
                        report.style_overwrite or report.level,
                'account_type': report.type == 'sum' and 'view' or False,
            }
            if data['debit_credit']:
                vals['debit'] = report.debit
                vals['credit'] = report.credit
            if data['enable_filter']:
                vals['balance_cmp'] = report_obj.browse(
                    cr, uid, report.id,
                    context=data['comparison_context']).balance * report.sign \
                    or 0.0
            lines.append(vals)
            account_ids = []
            if report.display_detail == 'no_detail':
                continue
            if report.type == 'accounts' and report.account_ids:
                account_ids = account_obj._get_children_and_consol(
                    cr, uid, [x.id for x in report.account_ids])
            elif report.type == 'account_type' and report.account_type_ids:
                account_ids = account_obj.search(
                    cr, uid, [('user_type', 'in', [x.id for x in
                                                   report.account_type_ids])])
            if account_ids:
                for account in account_obj.browse(
                   cr, uid, account_ids, context=data['used_context']):
                    if report.display_detail == 'detail_flat' and \
                      account.type == 'view':
                        continue
                    flag = False
                    vals = {
                        'name': account.code + ' ' + account.name,
                        'balance': account.balance != 0 and
                        account.balance * report.sign or account.balance,
                        'type': 'account',
                        'level':
                            report.display_detail == 'detail_with_hierarchy'
                            and min(account.level + 1, 6) or 6,
                        'account_type': account.type,
                    }
                    if data['debit_credit']:
                        vals['debit'] = account.debit
                        vals['credit'] = account.credit
                    if not currency_obj.is_zero(
                      cr, uid, account.company_id.currency_id,
                      vals['balance']):
                        flag = True
                    if data['enable_filter']:
                        vals['balance_cmp'] = account_obj.browse(
                            cr, uid, account.id,
                            context=data['comparison_context']).balance * \
                                report.sign or 0.0
                        if not currency_obj.is_zero(
                          cr, uid, account.company_id.currency_id,
                          vals['balance_cmp']):
                            flag = True
                    if flag:
                        lines.append(vals)
        return lines


class BalanceSheetXLS(report_xls):
    column_sizes = [12, 60, 17, 17, 17]

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        # Get data
        lines = _p.get_lines(data)
        fiscalyear = _p.get_fiscalyear(data)
        account = _p.get_account(data)
        start_period = _p.get_start_period(data)
        end_period = _p.get_end_period(data)
        filter = _p.get_filter(data)
        start_date = _p.get_start_date(data)
        end_date = _p.get_end_date(data)
        target_move = _p.get_target_move(data)

        # --
        ws = wb.add_sheet(_p.report_name[:31])
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        # Title
        cell_style = xlwt.easyxf(_xs['xls_title'])
        report_name = ' - '.join([_p.report_name.upper(),
                                 _p.company.partner_id.name,
                                 _p.company.currency_id.name])
        c_specs = [
            ('report_name', 1, 0, 'text', report_name),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style)

        # write empty row to define column sizes
        c_sizes = self.column_sizes
        c_specs = [('empty%s' % i, 1, c_sizes[i], 'text', None)
                   for i in range(0, len(c_sizes))]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, set_column_size=True)

        # Header Table
        cell_format = _xs['bold'] + _xs['fill_blue'] + _xs['borders_all']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
        c_specs = [
            ('coa', 1, 0, 'text', _('Chart of Account'),
                None, cell_style_center),
            ('fy', 1, 0, 'text', _('Fiscal Year')),
            ('df', 1, 0, 'text', filter == 'filter_date' and _('Dates Filter')
                or _('Periods Filter')),
            ('tm', 2, 0, 'text', _('Target Moves'), None, cell_style_center),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style)

        cell_format = _xs['borders_all'] + _xs['wrap'] + _xs['top']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
        c_specs = [
            ('coa', 1, 0, 'text', account, None, cell_style_center),
            ('fy', 1, 0, 'text', fiscalyear if fiscalyear else '-'),
        ]
        df = _('From') + ': '
        if data['form']['filter'] == 'filter_date':
            df += start_date if start_date else u''
        else:
            df += \
                start_period if start_period else u''
        df += ' ' + _('\nTo') + ': '
        if data['form']['filter'] == 'filter_date':
            df += end_date if end_date else u''
        else:
            df += end_period if end_period else u''
        c_specs += [
            ('df', 1, 0, 'text', df),
            ('tm', 2, 0, 'text', target_move, None, cell_style_center),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style)

        c_specs = [('empty%s' % i, 1, c_sizes[i], 'text', None)
                   for i in range(0, len(c_sizes))]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, set_column_size=True)

        if data['form']['enable_filter']:
            cell_format_ct = _xs['bold'] + \
                _xs['fill_blue'] + _xs['borders_all']
            cell_style_ct = xlwt.easyxf(cell_format_ct)
            c_specs = [('ct', 5, 0, 'text', _('Comparisons'))]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(
                ws, row_pos, row_data, row_style=cell_style_ct)
            cell_style_center = xlwt.easyxf(cell_format)
            c_specs = [
                ('c', 3, 0, 'text',
                 _('Comparison') + ' (' + data['form']['label_filter'] + ')')
            ]
            fiscalyear_cmp = ''
            if data['form']['fiscalyear_id_cmp']:
                fiscalyear_cmp = \
                    _('Fiscal Year') + ': ' + \
                    data['form']['fiscalyear_id_cmp'][1]
            c_specs += [('fc', 1, 0, 'text', fiscalyear_cmp)]
            if data['form']['filter_cmp'] == 'filter_date':
                c_specs += [('f', 1, 0, 'text', _('Dates Filter') + ': ' +
                             _p.formatLang(data['form']['date_from_cmp'],
                             date=True) + ' - ' +
                             _p.formatLang(data['form']['date_to_cmp'],
                             date=True))]
            elif data['form']['filter_cmp'] == 'filter_period':
                c_specs += [('f', 1, 0, 'text', _('Periods Filter') + ': ' +
                             data['form']['period_from_cmp'][1] + ' - ' +
                             data['form']['period_to_cmp'][1])]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(
                ws, row_pos, row_data, row_style=cell_style_center)

            c_specs = [('empty%s' % i, 1, c_sizes[i], 'text', None)
                       for i in range(0, len(c_sizes))]
            row_data = self.xls_row_template(
                c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(
                ws, row_pos, row_data, set_column_size=True)

        cell_format = _xs['bold'] + _xs['fill_blue'] + \
            _xs['borders_all'] + _xs['wrap'] + _xs['top']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_right = xlwt.easyxf(cell_format + _xs['right'])
        cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
        account_span = 1
        if not data['form']['debit_credit']:
            if not data['form']['enable_filter']:
                account_span = 3
            else:
                account_span = 2
        c_specs = [
            ('account_code', 1, 0, 'text', _('Code')),
            ('account_name', account_span, 0, 'text', _('Account')),
        ]
        if data['form']['debit_credit'] == 1:
            c_specs += [
                ('debit', 1, 0, 'text', _('Debit'), None, cell_style_right),
                ('credit', 1, 0, 'text', _('Credit'), None, cell_style_right),
            ]
        c_specs += [
            ('balance', 1, 0, 'text', _('Balance'), None, cell_style_right),
        ]
        if data['form']['enable_filter'] == 1 and not \
           data['form']['debit_credit']:
            c_specs += [
                ('label_filter', 1, 0, 'text', _(data['form']['label_filter']),
                    None, cell_style_right)
            ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style)

        for line in lines:
            cell_format = _xs['borders_all'] + _xs['wrap'] + _xs['top']
            cell_style = xlwt.easyxf(cell_format)
            cell_style_decimal = xlwt.easyxf(
                cell_format, num_format_str=report_xls.decimal_format)
            cell_style_bold = xlwt.easyxf(cell_format + _xs['bold'])
            c_specs = []
            if line['level'] != 0:
                cell_style_detail = cell_style
                cell_style_decimal_detail = cell_style_decimal
                if line['level'] <= 3:
                    cell_style_detail = cell_style_bold
                    cell_style_decimal_detail = xlwt.easyxf(
                        cell_format + _xs['bold'],
                        num_format_str=report_xls.decimal_format)
                account_code = line.get('name', None)
                account_name = None
                if len(line['name'].split(' ')) > 1:
                    account_code = line['name'].split(' ')[0]
                    account_name = line['name'].split(' ')[1]
                c_specs += [
                    ('account_code', 1, 0, 'text', account_code,
                        None, cell_style_detail),
                    ('account_name', account_span, 0, 'text', account_name,
                        None, cell_style_detail),
                ]
                if data['form']['debit_credit'] == 1:
                    c_specs += [
                        ('debit', 1, 0, 'number', line.get('debit', None),
                            None, cell_style_decimal_detail),
                        ('credit', 1, 0, 'number', line.get('credit', None),
                            None, cell_style_decimal_detail),
                    ]
                c_specs += [
                    ('balance', 1, 0, 'number', line.get('balance', None),
                        None, cell_style_decimal_detail),
                ]
                if data['form']['enable_filter'] == 1 and not \
                   data['form']['debit_credit']:
                    c_specs += [
                        ('balance_cmp', 1, 0, 'number',
                            line.get('balance_cmp', None), None,
                            cell_style_decimal_detail)
                    ]
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data, row_style=cell_style)


BalanceSheetXLS('report.account.account_report_balance_sheet_xls',
                'account.account',
                parser=BalanceSheetParser)
