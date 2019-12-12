# -*- coding: utf-8 -*-
# © 2019 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class MisReportInstance(models.Model):
    _inherit = 'mis.report.instance'

    root_account = fields.Many2one(
        default=lambda l: l._get_root_account()
    )

    @api.multi
    def _get_root_account(self):
        account = self.env['account.account'].search([
            ('type', '=', 'view'),
            ('parent_id', '=', False)
        ])
        return account.id
