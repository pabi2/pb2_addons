# -*- coding: utf-8 -*-
import time
from openerp.addons.pabi_report_xlsx_helper.report.report_xlsx_abstract \
    import ReportXlsxAbstract
from openerp import _, fields


class AdvanceStatusXLSX(ReportXlsxAbstract):
    def _get_ws_params(self, wb, data, objects):
        objects_head_filters = {
            '01_filter_report_date': {
                'header': {
                    'value': _('Report Date')
                },
                'data': {
                    'value': objects.date_report,
                    'type': 'datetime',
                },
            },
            '02_filter_employee': {
                'header': {
                    'value': 'Employee',
                },
                'data': {
                    'value': objects._get_filter_many2many(
                        objects.employee_ids, 'name'),
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
            '01_org': {
                'header': {
                    'value': _('Org')
                },
                'data': {
                    'value': self._render('object.operating_unit_id.name'),
                },
                'width': 18,
            },
            '02_advance_number': {
                'header': {
                    'value': _('Advance Number')
                },
                'data': {
                    'value': self._render('object.number'),
                },
                'width': 18,
            },
            '03_supplier_invoice_number': {
                'header': {
                    'value': _('Supplier Invoice Number')
                },
                'data': {
                    'value': self._render('object.invoice_id.number'),
                },
                'width': 18,
            },
            '04_remark': {
                'header': {
                    'value': _('Document Header Text')
                },
                'data': {
                    'value': self._render('object.remark'),
                },
                'width': 18,
            },
            '05_posting_date': {
                'header': {
                    'value': _('Posting Date')
                },
                'data': {
                    'value': self._render('object.invoice_id.date_invoice'),
                    'type': 'datetime',
                },
                'width': 18,
            },
            '06_due_date': {
                'header': {
                    'value': _('Due Date')
                },
                'data': {
                    'value': self._render('object.date_due'),
                    'type': 'datetime',
                },
                'width': 18,
            },
            '07_employee_code': {
                'header': {
                    'value': _('Employee Code')
                },
                'data': {
                    'value': self._render('object.employee_id.employee_code'),
                },
                'width': 18,
            },
            '08_employee_name': {
                'header': {
                    'value': _('Employee Name')
                },
                'data': {
                    'value': self._render('employee_name'),
                },
                'width': 18,
            },
            '09_amount': {
                'header': {
                    'value': _('Amount')
                },
                'data': {
                    'value': self._render('object.amount_advanced'),
                    'type': 'number',
                },
                'width': 18,
            },
            '10_av_balance': {
                'header': {
                    'value': _('AV Balance')
                },
                'data': {
                    'value': self._render('object.amount_to_clearing'),
                    'type': 'number',
                },
                'width': 18,
            },
            '11_days': {
                'header': {
                    'value': _('Number of Days')
                },
                'data': {
                    'value': self._render('number_of_days'),
                    'format': self.format_right,
                },
                'width': 18,
            },
            '12_not_due': {
                'header': {
                    'value': _('Not Due')
                },
                'data': {
                    'value': self._render('number_of_days and \
                        (number_of_days == "0" or number_of_days < 0) and \
                        object.amount_to_clearing'),
                    'format': self.format_amount_right,
                },
                'width': 18,
            },
            '13_overdue15days': {
                'header': {
                    'value': _('Overdue 1-15 Days')
                },
                'data': {
                    'value': self._render('number_of_days and \
                        number_of_days >= 1 and number_of_days <= 15 and \
                        object.amount_to_clearing'),
                    'format': self.format_amount_right,
                },
                'width': 18,
            },
            '14_overdue30days': {
                'header': {
                    'value': _('Overdue 16-30 Days')
                },
                'data': {
                    'value': self._render('number_of_days and \
                        number_of_days >= 16 and number_of_days <= 30 and \
                        object.amount_to_clearing'),
                    'format': self.format_amount_right,
                },
                'width': 18,
            },
            '15_overdueover30days': {
                'header': {
                    'value': _('Overdue Over 30 Days')
                },
                'data': {
                    'value': self._render('number_of_days and \
                        number_of_days > 30 and object.amount_to_clearing'),
                    'format': self.format_amount_right,
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
                            'sum(objects.results.mapped("amount_advanced"))'),
                        'col': 'I',
                        'type': 'number',
                        },
                        {
                        'value': self._render(
                            'sum(objects.results.mapped("amount_to_clearing"))'
                            ),
                        'col': 'J',
                        'type': 'number',
                        },
                        {
                        'value': self._render('sum_not_due'),
                        'col': 'L',
                        'type': 'number',
                        },
                        {
                        'value': self._render('sum_overdue15'),
                        'col': 'M',
                        'type': 'number',
                        },
                        {
                        'value': self._render('sum_overdue30'),
                        'col': 'N',
                        'type': 'number',
                        },
                        {
                        'value': self._render('sum_overdueover30'),
                        'col': 'O',
                        'type': 'number',
                        }],
                },
            },
        }
        ws_params = {
            'ws_name': 'Employee Advance Status Report',  # Sheet name
            'generate_ws_method': '_common_report',
            'title': _('Employee Advance Status Report - %s') \
            % objects.company_id.name,
            'data_filters':
                [str(x) for x in sorted(objects_head_filters.keys())],
            'col_filters': objects_head_filters,
            'wanted_list': [str(x) for x in sorted(objects_template.keys())],
            'col_specs': objects_template,
            # Optional
            'data_footer': [str(x) for x in sorted(objects_footer.keys())],
            'col_footer': objects_footer,
        }
        return [ws_params]

    def _render_space(self, objects, object):
        """For hook and add field"""
        employee_name = " ".join(list(filter(
            lambda self: self is not False,
            [object.employee_id.title_id.name, object.employee_id.first_name,
             object.employee_id.mid_name, object.employee_id.last_name]
            )))
        # check condition, there is date_due and date_report will return 0.
        not_empty = objects.date_report and object.date_due and True
        number_of_days = fields.Date.from_string(objects.date_report) - \
            fields.Date.from_string(object.date_due)
        if not_empty:
            if number_of_days.days == 0:
                number_of_days = '0'
            else:
                number_of_days = number_of_days.days
        else:
            number_of_days = ''
        render_space = {
            'object': object,
            'employee_name': employee_name,
            'number_of_days': number_of_days,
        }
        return render_space

    def _render_space_footer(self, objects):
        """Example for hook footer"""
        # check condition, there is date_due and date_report will return 0.
        sum_not_due, sum_overdue15 = 0.0, 0.0
        sum_overdue30, sum_overdueover30 = 0.0, 0.0
        for object in objects.results:
            # check condition, there is date_due and date_report will return 0.
            not_empty = objects.date_report and object.date_due and True
            number_of_days = fields.Date.from_string(objects.date_report) - \
                fields.Date.from_string(object.date_due)
            if not_empty and number_of_days.days <= 0:
                sum_not_due += object.amount_to_clearing
            elif not_empty and \
                    number_of_days.days > 0 and number_of_days.days <= 15:
                sum_overdue15 += object.amount_to_clearing
            elif not_empty and \
                    number_of_days.days > 15 and number_of_days.days <= 30:
                sum_overdue30 += object.amount_to_clearing
            elif not_empty and \
                    number_of_days.days > 30:
                sum_overdueover30 += object.amount_to_clearing
        render_space_footer = {
            'objects': objects,
            'sum_not_due': sum_not_due,
            'sum_overdue15': sum_overdue15,
            'sum_overdue30': sum_overdue30,
            'sum_overdueover30': sum_overdueover30,
        }
        return render_space_footer


AdvanceStatusXLSX('report.report_advance_status_xlsx',
                  'xlsx.report.advance.status')
