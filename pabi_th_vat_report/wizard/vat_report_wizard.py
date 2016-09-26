# -*- coding: utf-8 -*-

from openerp import fields, models, api
from ..report import vat_report


class AccountVatReport(models.TransientModel):
    _inherit = 'account.vat.report'

    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Tax Branch',
        required=True,
    )

    @api.model
    def _prepare_header_data(self):
        header_list = super(AccountVatReport, self)._prepare_header_data()
        header_list.append({
            'priority': 5,
            'label': 'Branch',
            'value': self.taxbranch_id.name
        })
        header_list.append({
            'priority': 6,
            'label': 'Branch ID',
            'value': self.taxbranch_id.code
        })
        return header_list

    @api.model
    def _get_parser_object(self):
        VatParser = vat_report.VatReportParser(
            self._cr, self._uid, 'account.vat.report', self._context
        )
        return VatParser
