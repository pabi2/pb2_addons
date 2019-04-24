# -*- coding: utf-8 -*-
from openerp.addons import jasper_reports

def jasper_print(cr, uid, ids, data, context):
    # For ORM, just pass ids
    return {
            'ids': data['parameters']['ids'],
    }

def budget_report_parser(cr, uid, ids, data, context):
    return {
        'ids': data['parameters']['ids'],
        'parameters': {
            'report_type': data['parameters']['report_type'],
            'fiscal_year': data['parameters']['fiscal_year'],
            'org': data['parameters']['org'],
            'po_document': data['parameters']['po_document'],
            'order_date': data['parameters']['order_date'],
            'budget_overview': data['parameters']['budget_overview'],
            'budget_method': data['parameters']['budget_method'],
            'run_by': data['parameters']['run_by'],
            'run_date': data['parameters']['run_date'],
        }
    }


jasper_reports.report_jasper(
                            'report.rpt_budget_future_commit_report',  # report_name in report_data.xml
                            'rpt.budget.future.commit.line',  # Model View name
                            parser=budget_report_parser,
)
jasper_reports.report_jasper(
                            'report.rpt_budget_future_commit_summary_report',  # report_name in report_data.xml
                            'rpt.budget.future.commit.summary.line',  # Model View name
                            parser=jasper_print,
)
jasper_reports.report_jasper(
                            'report.rpt_budget_commit_report',  # report_name in report_data.xml
                            'rpt.budget.commit.line',  # Model View name
                            parser=budget_report_parser,
)
