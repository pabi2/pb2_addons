# -*- encoding: utf-8 -*-
from openerp.addons import jasper_reports


def pabi_partner_dunning_letter_1st_parser(cr, uid, ids, data, context):
    # For ORM, just pass ids
    return {
        'ids': data['parameters']['ids'],
        'parameters': data['parameters']
    }


jasper_reports.report_jasper(
    'report.pabi_customer_dunning_letter_1st',  # report_name report_data.xml
    'pabi.partner.dunning.report',  # Model View name
    parser=pabi_partner_dunning_letter_1st_parser,
)


def pabi_partner_dunning_letter_2nd_parser(cr, uid, ids, data, context):
    # For ORM, just pass ids
    return {
        'ids': data['parameters']['ids'],
        'parameters': data['parameters']
    }


jasper_reports.report_jasper(
    'report.pabi_customer_dunning_letter_2nd',  # report_name report_data.xml
    'pabi.partner.dunning.report',  # Model View name
    parser=pabi_partner_dunning_letter_2nd_parser,
)


def pabi_partner_dunning_letter_3rd_parser(cr, uid, ids, data, context):
    # For ORM, just pass ids
    return {
        'ids': data['parameters']['ids'],
        'parameters': data['parameters']
    }


jasper_reports.report_jasper(
    'report.pabi_customer_dunning_letter_3rd',  # report_name report_data.xml
    'pabi.partner.dunning.report',  # Model View name
    parser=pabi_partner_dunning_letter_3rd_parser,
)
