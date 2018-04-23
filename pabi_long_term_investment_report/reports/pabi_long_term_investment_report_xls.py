# -*- coding: utf-8 -*
import xlwt
from datetime import datetime
from .pabi_long_term_investment_report import PabiLongTermInvestmentReport
from openerp.addons.report_xls.report_xls import report_xls
from openerp.tools.translate import _

# HEADER
HEADER_FIELDS = ['company', 'account_detail', 'date_current']
HEADER_CELL_NUMBER = [10, 10, 10]
HEADER_CELL_WIDTH = [5, 0, 0]

# HEADER PARTNER
HEADER_PARTNER_FIELDS = ['partner_name', 'percent_invest']
HEADER_PARTNER_CELL_NUMBER = [4, 9]
HEADER_PARTNER_CELL_WIDTH = [0, 0]

# COLUMN HEADER, LINE AND FOOT
C_HEADER_LINE_FOOT_FIELDS = [
    'name', 'date_approve', 'description', 'total_captial', 'total_share',
    'nstda_share', 'price_unit', 'total_amount', 'invoice_number',
    'date_invoice', 'invoice_desc', 'amount_invoice', 'ref_payment']
C_HEADER_LINE_FOOT_CELL_NUMBER = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
C_HEADER_LINE_FOOT_CELL_WIDTH = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

_column_sizes = [('name', 20), ('date_approve', 20), ('description', 20),
                 ('total_captial', 25), ('total_share', 25),
                 ('nstda_share', 20), ('price_unit', 20), ('total_amount', 20),
                 ('invoice_number', 20), ('date_invoice', 20),
                 ('invoice_desc', 20), ('amount_invoice', 20),
                 ('ref_payment', 40), ]


class PabiLongTermInvestmentReportXLS(report_xls):
    column_sizes = [x[1] for x in _column_sizes]

    def _get_spec_data(self, field_list, cell_number_list, cell_width_list,
                       type_list, description_list, cell_style_list=None):
        specs = []
        for field in field_list:
            index = field_list.index(field)
            cell_style = (cell_style_list is not None) \
                and cell_style_list[index] or None
            specs += [(field, cell_number_list[index],
                       cell_width_list[index], type_list[index],
                       _(description_list[index]), None, cell_style)]
        return specs

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        # Set Locale
        # locale.setlocale(locale.LC_TIME, 'th_TH.utf8')  # server may not have

        ws = wb.add_sheet(_p.report_name[:31])
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        # Header
        head_type = ['text', 'text', 'text']
        print_date = _p.date_print and \
            datetime.strptime(_p.date_print, '%Y-%m-%d') or datetime.today()

        head_des = [
            'สำนักงานพัฒนาวิทยาศาสตร์และเทคโนโลยีแห่งชาติ',
            'รายละเอียด เลขที่บัญชี %s ชื่อบัญชี %s'
            % (str(_p.account.code), _p.account.name.encode('utf-8')),
            'ณ วันที่ %s' % (print_date.strftime('%d/%m/%Y'))
        ]

        head_specs = self._get_spec_data(HEADER_FIELDS, HEADER_CELL_NUMBER,
                                         HEADER_CELL_WIDTH, head_type,
                                         head_des)
        head_cell_style = xlwt.easyxf(_xs['bold'] + _xs['center'])
        for head in head_specs:
            row_data = self.xls_row_template([head], [head[0]])
            row_pos = self.xls_write_row(
                ws, row_pos, row_data, row_style=head_cell_style)

        # Get partner_id
        Partner = self.pool.get('res.partner')
        partner_ids = sorted(list(set([line['partner_id']
                                       for line in _p['investment_lines']])))
        for partner in Partner.browse(self.cr, self.uid, partner_ids):
            # write empty row to define column sizes
            c_sizes = self.column_sizes
            c_specs = [('empty%s' % i, 1, c_sizes[i], 'text', None)
                       for i in range(0, len(c_sizes))]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(
                ws, row_pos, row_data, set_column_size=True)

            # Head partner
            head_partner_type = ['text', 'text']
            head_partner_desc = [
                '%s %s' % (partner.search_key, partner.name),
                'สวทช ถือหุ้นร้อยละ %s'
                % str("{:.2f}".format(partner.percent_invest))]
            head_partner_specs = self._get_spec_data(
                HEADER_PARTNER_FIELDS, HEADER_PARTNER_CELL_NUMBER,
                HEADER_PARTNER_CELL_WIDTH, head_partner_type,
                head_partner_desc)
            head_partner_cell_style = xlwt.easyxf(_xs['bold'] +
                                                  _xs['fill_blue'])
            row_data = self.xls_row_template(
                head_partner_specs, [x[0] for x in head_partner_specs])
            row_pos = self.xls_write_row(
                ws, row_pos, row_data, row_style=head_partner_cell_style)

            # Column Header
            c_hdr_type = ['text', 'text', 'text', 'text', 'text', 'text',
                          'text', 'text', 'text', 'text', 'text', 'text',
                          'text']
            c_hdr_des = ['อนุมัติโดยกวทช. ครั้งที่', 'วันที่อนุมัติ', 'รายการ',
                         'ทุนจดทะเบียน (ล้านบาท)', 'ทุนจดทะเบียน (จำนวนหุ้น)',
                         'จำนวนหุ้น (สวทช.)', 'ราคา/หุ้น', 'ยอดรวม',
                         'เลขที่เอกสารใบตั้งหนี้', 'วันที่ตั้งหนี้',
                         'รายละเอียด', 'ยอดเงิน', 'อ้างถึงการจ่าย']
            cell_format = _xs['bold'] + _xs['borders_all']
            c_hdr_cell_style = xlwt.easyxf(cell_format + _xs['fill'])
            c_hdr_cell_style = [c_hdr_cell_style for c_hdr in c_hdr_des]
            c_hdr_specs = self._get_spec_data(
                C_HEADER_LINE_FOOT_FIELDS, C_HEADER_LINE_FOOT_CELL_NUMBER,
                C_HEADER_LINE_FOOT_CELL_WIDTH, c_hdr_type, c_hdr_des,
                c_hdr_cell_style)
            row_data = self.xls_row_template(c_hdr_specs,
                                             [x[0] for x in c_hdr_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data)

            # DETAIL LINE
            investment_lines = [line for line in _p['investment_lines']
                                if line['partner_id'] == partner.id]
            investment_lines = sorted(investment_lines,
                                      key=lambda k: k['investment_id'])
            c_line_cell_style_decimal = xlwt.easyxf(
                _xs['borders_all'] + _xs['right'],
                num_format_str=report_xls.decimal_format)
            investment_tmp_ids = 0
            sum_total_capital, sum_total_share, sum_nstda_share, \
                sum_price_subtotal, sum_amount_invoice = 0, 0, 0, 0, 0
            for line in investment_lines:
                ref_payments = self.pool.get('account.move.line') \
                    .browse(self.cr, self.uid, line.get('move_line_id')) \
                    .invoice.payment_ids.mapped('ref')
                ref_payments = ', '.join(ref_payments)
                c_line_type = ['text', 'text', 'text', 'number', 'number',
                               'number', 'number', 'number', 'text', 'text',
                               'text', 'number', 'text']
                c_line_des = [
                    line.get('name', None),
                    datetime.strptime(
                        line.get('date_approve'), '%Y-%m-%d')
                    .strftime('%d/%m/%Y'),
                    line.get('description', None),
                    line.get('total_capital', 0.0),
                    line.get('total_share', 0.0),
                    line.get('nstda_share', 0.0),
                    line.get('price_unit', 0.0),
                    line.get('price_subtotal', 0.0),
                    line.get('invoice_number', None),
                    datetime.strptime(line.get('date_approve'), '%Y-%m-%d').
                    strftime('%d/%m/%Y') or None,
                    line.get('invoice_desc', None),
                    line.get('amount_invoice', 0.0),
                    ref_payments
                ]
                c_line_style = [
                    None, None, None, c_line_cell_style_decimal,
                    c_line_cell_style_decimal, c_line_cell_style_decimal,
                    c_line_cell_style_decimal, c_line_cell_style_decimal,
                    None, None, None, c_line_cell_style_decimal, None]

                # Not duplicate value for same investment
                if investment_tmp_ids == line['investment_id']:
                    for i in range(8):
                        c_line_type[i] = 'text'
                        c_line_des[i] = None
                        c_line_style[i] = None
                else:
                    sum_total_capital += line.get('total_capital', 0.0)
                    sum_total_share += line.get('total_share', 0.0)
                    sum_nstda_share += line.get('nstda_share', 0.0)
                    sum_price_subtotal += line.get('price_subtotal', 0.0)
                sum_amount_invoice += line.get('amount_invoice', 0.0)

                c_line_specs = self._get_spec_data(
                    C_HEADER_LINE_FOOT_FIELDS, C_HEADER_LINE_FOOT_CELL_NUMBER,
                    C_HEADER_LINE_FOOT_CELL_WIDTH, c_line_type, c_line_des,
                    c_line_style
                )
                row_data = self.xls_row_template(c_line_specs,
                                                 [x[0] for x in c_line_specs])
                row_pos = self.xls_write_row(ws, row_pos, row_data)
                investment_tmp_ids = line['investment_id']

            # FOOTER
            c_ftr_cell_style_decimal = xlwt.easyxf(
                _xs['bold'] + _xs['borders_all'] + _xs['right'] + _xs['fill'],
                num_format_str=report_xls.decimal_format)
            c_ftr_cell_style = xlwt.easyxf(
                _xs['bold'] + _xs['fill'] + _xs['borders_all'])
            c_foot_type = [
                'text', 'text', 'text', 'number', 'number', 'number', 'text',
                'number', 'text', 'text', 'text', 'number', 'text']
            c_foot_des = [
                None, None, None, sum_total_capital, sum_total_share,
                sum_nstda_share, None, sum_price_subtotal, None, None, None,
                sum_amount_invoice, None]
            c_foot_style = [
                c_ftr_cell_style, c_ftr_cell_style, c_ftr_cell_style,
                c_ftr_cell_style_decimal, c_ftr_cell_style_decimal,
                c_ftr_cell_style_decimal, c_ftr_cell_style,
                c_ftr_cell_style_decimal, c_ftr_cell_style, c_ftr_cell_style,
                c_ftr_cell_style, c_ftr_cell_style_decimal, c_ftr_cell_style]
            c_foot_specs = self._get_spec_data(
                C_HEADER_LINE_FOOT_FIELDS, C_HEADER_LINE_FOOT_CELL_NUMBER,
                C_HEADER_LINE_FOOT_CELL_WIDTH, c_foot_type, c_foot_des,
                c_foot_style
            )
            row_data = self.xls_row_template(c_foot_specs,
                                             [x[0] for x in c_foot_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data)


PabiLongTermInvestmentReportXLS(
    'report.pabi_long_term_investment_report_xls',
    'account.account',
    parser=PabiLongTermInvestmentReport)
