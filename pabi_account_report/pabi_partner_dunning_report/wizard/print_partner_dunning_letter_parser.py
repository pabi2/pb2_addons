# -*- encoding: utf-8 -*-
from openerp.addons import jasper_reports


def pabi_partner_dunning_letter_parser(cr, uid, ids, data, context):
    # For ORM, just pass ids
    return {
        'ids': data['parameters']['ids'],
        # 'parameters': {
        #     # 'xxx': data['parameters']['ids'],
        # }
    }


jasper_reports.report_jasper(
    'report.pabi_customer_dunning_letter',  # report_name in report_data.xml
    'pabi.partner.dunning.report',  # Model View name
    parser=pabi_partner_dunning_letter_parser,
)
