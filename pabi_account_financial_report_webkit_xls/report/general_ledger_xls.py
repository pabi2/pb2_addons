# -*- coding: utf-8 -*-
import xlwt
from datetime import datetime
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell
from openerp.addons.pabi_account_financial_report_webkit \
    .report.general_ledger import GeneralLedgerWebkit
from openerp.tools.translate import _
# import logging
# _logger = logging.getLogger(__name__)

_column_sizes = [
    ('charge_type', 10),
    ('document_date', 14),
    ('posting_date', 7),
    ('period', 12),
    ('fiscal_year', 7),
    ('budget', 20),
    ('fund', 20),
    ('costcenter', 20),
    ('taxbranch', 50),
    ('move', 20),
    ('doctype', 20),
    ('doc_journel', 12),
    ('activity_group', 20),
    ('activity', 20),
    ('account_code', 12),
    ('partner', 30),
    ('reference', 30),
    ('description', 45),
    ('header_description', 45),
    ('counterpart', 30),
    ('debit', 15),
    ('credit', 15),
    ('cumul_bal', 15),
    ('curr_bal', 15),
    ('curr_code', 7),
    ('source_document', 30),
    ('reconcile_id', 15),
    ('partial_id', 15),
    ('program_code', 10),
    ('program_name', 10),
    ('section_program', 10),
    ('job_g_code', 10),
    ('job_g_name', 10),
    ('job_code', 10),
    ('job_name', 10),
    ('m_plan_code', 10),
    ('m_plan_name', 10),
    ('mission', 20),
    ('posted_by', 30),
    ('due_date', 12),
    ('value_date', 12),
    ('preprint_number', 7),
]


class general_ledger_xls(report_xls):
    # column_sizes = [x[1] for x in _column_sizes]
    column_sizes = dict(_column_sizes)

    def generate_xls_report(self, _p, _xs, data, objects, wb):

        ws = wb.add_sheet(_p.report_name[:31])
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        # cf. account_report_general_ledger.mako
        initial_balance_text = {'initial_balance': _('Computed'),
                                'opening_balance': _('Opening Entries'),
                                False: _('No')}

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
        c_sizes = []
        if _p.amount_currency(data):
            tmp = self.column_sizes.copy()
            del(tmp['curr_bal'])
            del(tmp['curr_code'])
            c_sizes = [x[1] for x in tmp]
        # --
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
            ('coa', 2, 0, 'text', _('Chart of Account')),
            ('fy', 1, 0, 'text', _('Fiscal Year')),
            ('df', 3, 0, 'text', _p.filter_form(data) ==
             'filter_date' and _('Dates Filter') or _('Periods Filter')),
            ('af', 1, 0, 'text', _('Accounts Filter')),
            ('tm', 2, 0, 'text', _('Target Moves')),
            ('ib', 2, 0, 'text', _('Initial Balance')),

        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style_center)

        cell_format = _xs['borders_all']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
        c_specs = [
            ('coa', 2, 0, 'text', _p.chart_account.name),
            ('fy', 1, 0, 'text', _p.fiscalyear.name if _p.fiscalyear else '-'),
        ]
        df = _('From') + ': '
        if _p.filter_form(data) == 'filter_date':
            df += _p.start_date if _p.start_date else u''
        else:
            df += _p.start_period.name if _p.start_period else u''
        df += ' ' + _('To') + ': '
        if _p.filter_form(data) == 'filter_date':
            df += _p.stop_date if _p.stop_date else u''
        else:
            df += _p.stop_period.name if _p.stop_period else u''
        c_specs += [
            ('df', 3, 0, 'text', df),
            ('af', 1, 0, 'text', _p.accounts(data) and ', '.join(
                [account.code for account in _p.accounts(data)]) or _('All')),
            ('tm', 2, 0, 'text', _p.display_target_move(data)),
            ('ib', 2, 0, 'text', initial_balance_text[
             _p.initial_balance_mode]),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style_center)
        ws.set_horz_split_pos(row_pos)
        row_pos += 1

        # Column Title Row
        cell_format = _xs['bold']
        c_title_cell_style = xlwt.easyxf(cell_format)

        # Column Header Row
        cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        c_hdr_cell_style = xlwt.easyxf(cell_format)
        c_hdr_cell_style_right = xlwt.easyxf(cell_format + _xs['right'])
        c_hdr_cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
        c_hdr_cell_style_decimal = xlwt.easyxf(
            cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)

        # Column Initial Balance Row
        cell_format = _xs['italic'] + _xs['borders_all']
        c_init_cell_style = xlwt.easyxf(cell_format)
        c_init_cell_style_decimal = xlwt.easyxf(
            cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)

        c_specs = [
            ('charge_type', 1, 0, 'text', _('Charge Type'), None,
                c_hdr_cell_style),
            ('document_date', 1, 0, 'text', _('Document Date'), None,
                c_hdr_cell_style),
            ('posting_date', 1, 0, 'text', _('Posting Date'), None,
                c_hdr_cell_style),
            ('period', 1, 0, 'text', _('Period'), None, c_hdr_cell_style),
            ('fiscal_year', 1, 0, 'text', _('Fiscal Year'), None,
                c_hdr_cell_style),
            ('budget', 1, 0, 'text', _('Budget'), None, c_hdr_cell_style),
            ('fund', 1, 0, 'text', _('Fund'), None, c_hdr_cell_style),
            ('costcenter', 1, 0, 'text', _('Costcenter'), None,
                c_hdr_cell_style),
            ('taxbranch', 1, 0, 'text', _('Tax Branch'), None,
                c_hdr_cell_style),
            ('move', 1, 0, 'text', _('Entry'), None, c_hdr_cell_style),
            ('doctype', 1, 0, 'text', _('DocType'), None, c_hdr_cell_style),
            ('doc_journel', 1, 0, 'text', _('Doc Journal'), None,
                c_hdr_cell_style),
            ('activity_group', 1, 0, 'text', _('Activity Group'), None,
                c_hdr_cell_style),
            ('activity', 1, 0, 'text', _('Activity'), None,
                c_hdr_cell_style),
            ('account_code', 1, 0, 'text',
             _('Account'), None, c_hdr_cell_style),
            ('partner', 1, 0, 'text', _('Partner'), None, c_hdr_cell_style),
            ('reference', 1, 0, 'text', _('Reference'), None,
                c_hdr_cell_style),
            ('description', 1, 0, 'text', _('Description'), None,
                c_hdr_cell_style),
            ('header_description', 1, 0, 'text', _('Header Description'), None,
                c_hdr_cell_style),
            ('counterpart', 1, 0, 'text',
             _('Counterpart'), None, c_hdr_cell_style),
            ('debit', 1, 0, 'text', _('Debit'), None, c_hdr_cell_style_right),
            ('credit', 1, 0, 'text', _('Credit'),
             None, c_hdr_cell_style_right),
            ('cumul_bal', 1, 0, 'text', _('Cumul. Bal.'),
             None, c_hdr_cell_style_right),
        ]
        if _p.amount_currency(data):
            c_specs += [
                ('curr_bal', 1, 0, 'text', _('Curr. Bal.'),
                 None, c_hdr_cell_style_right),
                ('curr_code', 1, 0, 'text', _('Curr.'),
                 None, c_hdr_cell_style_center),
            ]
        c_specs += [
            # PABI2
            ('source_document', 1, 0, 'text', _('Source Doc.'),
                None, c_hdr_cell_style),
            ('reconcile_id', 1, 0, 'text', _('Rec.ID'),
                None, c_hdr_cell_style),
            ('partial_id', 1, 0, 'text', _('Part.ID'),
                None, c_hdr_cell_style),
            ('program_code', 1, 0, 'text', _('Program Code'),
                None, c_hdr_cell_style),
            ('program_name', 1, 0, 'text', _('Program Name'),
                None, c_hdr_cell_style),
            ('section_program', 1, 0, 'text', _('Section Program'),
                None, c_hdr_cell_style),
            ('job_g_code', 1, 0, 'text', _('Job Order Group Code'),
                None, c_hdr_cell_style),
            ('job_g_name', 1, 0, 'text', _('Job Order Group Name'),
                None, c_hdr_cell_style),
            ('job_code', 1, 0, 'text', _('Job Order Code'),
                None, c_hdr_cell_style),
            ('job_name', 1, 0, 'text', _('Job Order Name'),
                None, c_hdr_cell_style),
            ('m_plan_code', 1, 0, 'text', _('Master Plan Code'),
                None, c_hdr_cell_style),
            ('m_plan_name', 1, 0, 'text', _('Master Plan Name'),
                None, c_hdr_cell_style),
            ('mission', 1, 0, 'text', _('Mission'),
                None, c_hdr_cell_style),
            ('posted_by', 1, 0, 'text', _('Posted By'),
                None, c_hdr_cell_style),
            ('due_date', 1, 0, 'text', _('Due Date'),
                None, c_hdr_cell_style),
            ('value_date', 1, 0, 'text', _('Value Date'),
                None, c_hdr_cell_style),
            ('preprint_number', 1, 0, 'text', _('Preprint Number'),
                None, c_hdr_cell_style),
            # --
        ]
        c_hdr_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])

        # cell styles for ledger lines
        ll_cell_format = _xs['borders_all']
        ll_cell_style = xlwt.easyxf(ll_cell_format)
        ll_cell_style_center = xlwt.easyxf(ll_cell_format + _xs['center'])
        ll_cell_style_date = xlwt.easyxf(
            ll_cell_format + _xs['left'],
            num_format_str=report_xls.date_format)
        ll_cell_style_decimal = xlwt.easyxf(
            ll_cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)

        cnt = 0
        for account in objects:

            display_initial_balance = _p['init_balance'][account.id] and \
                (_p['init_balance'][account.id].get(
                    'debit', 0.0) != 0.0 or
                    _p['init_balance'][account.id].get('credit', 0.0) != 0.0)
            display_ledger_lines = _p['ledger_lines'][account.id]

            if _p.display_account_raw(data) == 'all' or \
                    (display_ledger_lines or display_initial_balance):
                # TO DO : replace cumul amounts by xls formulas
                cnt += 1
                cumul_debit = 0.0
                cumul_credit = 0.0
                cumul_balance = 0.0
                cumul_balance_curr = 0.0
                c_specs = [
                    ('acc_title', 11, 0, 'text',
                     ' - '.join([account.code, account.name])),
                ]
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data, c_title_cell_style)
                row_pos = self.xls_write_row(ws, row_pos, c_hdr_data)
                row_start = row_pos

                if display_initial_balance:
                    init_balance = _p['init_balance'][account.id]
                    cumul_debit = init_balance.get('debit') or 0.0
                    cumul_credit = init_balance.get('credit') or 0.0
                    cumul_balance = init_balance.get('init_balance') or 0.0
                    cumul_balance_curr = init_balance.get(
                        'init_balance_currency') or 0.0
                    c_specs = [('empty%s' % x, 1, 0, 'text', None)
                               for x in range(14)]
                    c_specs += [
                        ('init_bal', 1, 0, 'text', _('Initial Balance')),
                        ('counterpart', 1, 0, 'text', None),
                        ('debit', 1, 0, 'number', cumul_debit,
                         None, c_init_cell_style_decimal),
                        ('credit', 1, 0, 'number', cumul_credit,
                         None, c_init_cell_style_decimal),
                        ('cumul_bal', 1, 0, 'number', cumul_balance,
                         None, c_init_cell_style_decimal),
                    ]
                    if _p.amount_currency(data):
                        c_specs += [
                            ('curr_bal', 1, 0, 'number', cumul_balance_curr,
                             None, c_init_cell_style_decimal),
                            ('curr_code', 1, 0, 'text', None),
                        ]
                    row_data = self.xls_row_template(
                        c_specs, [x[0] for x in c_specs])
                    row_pos = self.xls_write_row(
                        ws, row_pos, row_data, c_init_cell_style)

                for line in _p['ledger_lines'][account.id]:

                    cumul_debit += line.get('debit') or 0.0
                    cumul_credit += line.get('credit') or 0.0
                    cumul_balance_curr += line.get('amount_currency') or 0.0
                    cumul_balance += line.get('balance') or 0.0
                    label_elements = [line.get('lname') or '']
                    if line.get('invoice_number'):
                        label_elements.append(
                            "(%s)" % (line['invoice_number'],))
                    label = ' '.join(label_elements)
                    c_specs = [('charge_type', 1, 0, 'text',
                                line.get('charge_type') or '')]

                    if line.get('document_date'):
                        c_specs += [
                            ('document_date', 1, 0, 'date', datetime.strptime(
                                line['document_date'], '%Y-%m-%d'), None,
                                ll_cell_style_date),
                        ]
                    else:
                        c_specs += [
                            ('document_date', 1, 0, 'text', None),
                        ]

                    if line.get('ldate'):
                        c_specs += [
                            ('posting_date', 1, 0, 'date', datetime.strptime(
                                line['ldate'], '%Y-%m-%d'), None,
                             ll_cell_style_date),
                        ]
                    else:
                        c_specs += [
                            ('posting_date', 1, 0, 'text', None),
                        ]
                    c_specs += [
                        ('period', 1, 0, 'text',
                         line.get('period_code') or ''),
                        ('fiscal_year', 1, 0, 'text', _p.fiscalyear.name),
                        ('budget', 1, 0, 'text',
                         line.get('budget_name') or ''),
                        ('fund', 1, 0, 'text', line.get('fund_name') or ''),
                        ('costcenter', 1, 0, 'text',
                         line.get('costcenter_name') or ''),
                        ('taxbranch', 1, 0, 'text',
                         line.get('taxbranch_name') or ''),
                        ('move', 1, 0, 'text', line.get('move_name') or ''),
                        ('doctype', 1, 0, 'text', line.get('doctype') or ''),
                        ('doc_journel', 1, 0, 'text',
                         line.get('journal') or ''),
                        ('activity_group', 1, 0, 'text',
                         line.get('activity_group_name') or ''),
                        ('activity', 1, 0, 'text',
                         line.get('activity_name') or ''),
                        ('account_code', 1, 0, 'text', account.code),
                        ('partner', 1, 0, 'text',
                         line.get('partner_name') or ''),
                        ('reference', 1, 0, 'text', line.get('lref') or ''),
                        ('description', 1, 0, 'text', label),
                        ('header_description', 1, 0, 'text',
                         line.get('hname') or ''),
                        ('counterpart', 1, 0, 'text',
                         line.get('counterparts') or ''),
                        ('debit', 1, 0, 'number', line.get('debit', 0.0),
                         None, ll_cell_style_decimal),
                        ('credit', 1, 0, 'number', line.get('credit', 0.0),
                         None, ll_cell_style_decimal),
                        ('cumul_bal', 1, 0, 'number', cumul_balance,
                         None, ll_cell_style_decimal),
                    ]
                    if _p.amount_currency(data):
                        c_specs += [
                            ('curr_bal', 1, 0, 'number', line.get(
                                'amount_currency') or 0.0, None,
                             ll_cell_style_decimal),
                            ('curr_code', 1, 0, 'text', line.get(
                                'currency_code') or '', None,
                             ll_cell_style_center),
                        ]
                    c_specs += [
                        # PABI2
                        ('source_document', 1, 0, 'text',
                            line.get('source_document') or ''),
                        ('reconcile_id', 1, 0, 'text',
                            line.get('reconcile_id') or ''),
                        ('partial_id', 1, 0, 'text',
                            line.get('partial_id') or ''),
                        ('program_code', 1, 0, 'text',
                            line.get('program_code') or ''),
                        ('program_name', 1, 0, 'text',
                            line.get('program_name') or ''),
                        ('section_program', 1, 0, 'text',
                            line.get('section_program') or ''),
                        ('job_g_code', 1, 0, 'text',
                            line.get('job_order_group_code') or ''),
                        ('job_g_name', 1, 0, 'text',
                            line.get('job_order_group_name') or ''),
                        ('job_code', 1, 0, 'text',
                            line.get('job_order_code') or ''),
                        ('job_name', 1, 0, 'text',
                            line.get('job_order_name') or ''),
                        ('m_plan_code', 1, 0, 'text',
                            line.get('master_code') or ''),
                        ('m_plan_name', 1, 0, 'text',
                            line.get('master_name') or ''),
                        ('mission', 1, 0, 'text',
                            line.get('mission') or ''),
                        ('posted_by', 1, 0, 'text',
                            line.get('posted_by') or ''),
                        ('due_date', 1, 0, 'text',
                            line.get('due_date') or ''),
                        ('value_date', 1, 0, 'text',
                            line.get('value_date') or ''),
                        ('preprint_number', 1, 0, 'text',
                            line.get('preprint') or ''),
                        # --
                    ]
                    row_data = self.xls_row_template(
                        c_specs, [x[0] for x in c_specs])
                    row_pos = self.xls_write_row(
                        ws, row_pos, row_data, ll_cell_style)

                debit_start = rowcol_to_cell(row_start, 20)
                debit_end = rowcol_to_cell(row_pos - 1, 20)
                debit_formula = 'SUM(' + debit_start + ':' + debit_end + ')'
                credit_start = rowcol_to_cell(row_start, 21)
                credit_end = rowcol_to_cell(row_pos - 1, 21)
                credit_formula = 'SUM(' + credit_start + ':' + credit_end + ')'
                balance_debit = rowcol_to_cell(row_pos, 20)
                balance_credit = rowcol_to_cell(row_pos, 21)
                balance_formula = balance_debit + '-' + balance_credit
                c_specs = [
                    ('acc_title', 19, 0, 'text',
                     ' - '.join([account.code, account.name])),
                    ('cum_bal', 1, 0, 'text',
                     _('Cumulated Balance on Account'),
                     None, c_hdr_cell_style_right),
                    ('debit', 1, 0, 'number', None,
                     debit_formula, c_hdr_cell_style_decimal),
                    ('credit', 1, 0, 'number', None,
                     credit_formula, c_hdr_cell_style_decimal),
                    ('balance', 1, 0, 'number', None,
                     balance_formula, c_hdr_cell_style_decimal),
                ]
                if _p.amount_currency(data):
                    if account.currency_id:
                        c_specs += [('curr_bal', 1, 0, 'number',
                                     cumul_balance_curr, None,
                                     c_hdr_cell_style_decimal)]
                    else:
                        c_specs += [('curr_bal', 1, 0, 'text', None)]
                    c_specs += [('curr_code', 1, 0, 'text', None)]
                c_specs += [
                    ('created_by', 1, 0, 'text', None),
                    ('source_document', 1, 0, 'text', None),
                    ('reconcile_id', 1, 0, 'text', None),
                    ('partial_id', 1, 0, 'text', None),
                ]
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data, c_hdr_cell_style)
                row_pos += 1


general_ledger_xls('report.account.account_report_general_ledger_xls',
                   'account.account',
                   parser=GeneralLedgerWebkit)
