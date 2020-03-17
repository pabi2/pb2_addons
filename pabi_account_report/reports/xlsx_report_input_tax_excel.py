# -*- coding: utf-8 -*-
import time
from openerp.addons.pabi_report_xlsx_helper.report.report_xlsx_abstract \
    import ReportXlsxAbstract
from openerp import _


class InputTaxXLSX(ReportXlsxAbstract):
    def _get_ws_params(self, wb, data, objects):
        objects_head_filters = {
            '01_filter_period': {
                'header': {
                    'value': _('Period')
                },
                'data': {
                    'value': objects.calendar_period_id.calendar_name
                },
            },
            '02_filter_taxbranch': {
                'header': {
                    'value': 'Taxbranch',
                },
                'data': {
                    'value': objects.taxbranch_id.name,
                },
            },
            '03_filter_runby': {
                'header': {
                    'value': 'Run By',
                },
                'data': {
                    'value': self.env.user.display_name,
                },
            },
            '04_filter_rundate': {
                'header': {
                    'value': 'Run Date',
                },
                'data': {
                    'value': time.strftime("%d/%m/%Y"),
                },
            },
        }
        objects_template = {
            '01_tax_sequence_display': {
                'header': {
                    'multi': [
                        {'value': _('')},
                        {'value': _('Item')}],
                },
                'data': {
                    'value': self._render('object.tax_sequence_display'),
                },
                'width': 18,
            },
            '02_date': {
                'header': {
                    'multi': [
                        {'value': _('Tax Invoice'), 'colspan': 2},
                        {'value': _('Date')}],
                },
                'data': {
                    'value': self._render('object.invoice_date'),
                    'type': 'datetime',
                },
                'width': 18,
            },
            '03_number': {
                'header': {
                    'multi': [
                        {'value': _('')},
                        {'value': _('Number')}],
                },
                'data': {
                    'value': self._render('object.invoice_number'),
                },
                'width': 18,
            },
            '04_vendor_name': {
                'header': {
                    'multi': [
                        {'value': _('')},
                        {'value': _('Vendor Name')}],
                },
                'data': {
                    'value': self._render('object.partner_id.name'),
                },
                'width': 18,
            },
            '05_tax_number': {
                'header': {
                    'multi': [
                        {'value': _('')},
                        {'value': _('Tax Number')}],
                },
                'data': {
                    'value': self._render('object.partner_id.vat'),
                },
                'width': 18,
            },
            '06_branch_number': {
                'header': {
                    'multi': [
                        {'value': _('')},
                        {'value': _('Branch Number')}],
                },
                'data': {
                    'value': self._render(
                        'object.partner_id.taxbranch == "00000" and\
                         "Head Office" or object.partner_id.taxbranch'),
                },
                'width': 18,
            },
            '07_base_amount': {
                'header': {
                    'multi': [
                        {'value': _('Value Added Tax'), 'colspan': 2},
                        {'value': _('Base Amount')}],
                },
                'data': {
                    'value': self._render('object.base'),
                    'type': 'number'
                },
                'width': 18,
            },
            '08_vat_amount': {
                'header': {
                    'multi': [
                        {'value': _('')},
                        {'value': _('VAT amount')}],
                },
                'data': {
                    'value': self._render('object.amount'),
                    'type': 'number'
                },
                'width': 18,
            },
            '09_document_number': {
                'header': {
                    'multi': [
                        {'value': _('')},
                        {'value': _('Document Number')}],
                },
                'data': {
                    'value': self._render('object.move_number'),
                },
                'width': 18,
            },
        }
        objects_footer = {
            '01_sum': {
                'header': {
                    'value': _('Total'),
                },
                'data': {
                    'multi': [{
                        'value': self._render(
                            'sum(objects.results.mapped("base"))'),
                        'col': 'G',
                        'type': 'number',
                        },
                        {
                        'value': self._render(
                            'sum(objects.results.mapped("amount"))'),
                        'col': 'H',
                        'type': 'number',
                        }],
                },
            },
        }
        ws_params = {
            'ws_name': 'Input Tax Report',  # Sheet name
            'generate_ws_method': '_common_report',
            'title': _('Input Tax Report - %s') % objects.company_id.name,
            'data_filters':
                [str(x) for x in sorted(objects_head_filters.keys())],
            'col_filters': objects_head_filters,
            'wanted_list': [str(x) for x in sorted(objects_template.keys())],
            'col_specs': objects_template,
            'data_footer': [str(x) for x in sorted(objects_footer.keys())],
            'col_footer': objects_footer,
        }
        return [ws_params]


InputTaxXLSX('report.report_input_tax_xlsx', 'xlsx.report.input.tax')
