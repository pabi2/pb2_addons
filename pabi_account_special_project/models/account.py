# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class AccontAccount(models.Model):
    _inherit = 'account.account'

    sp_account_code = fields.Char(
        string='Special Project GL Code',
        compute='_compute_sp_account_code',
        # inverse='_inverse_sp_account_code',
        # search='_search_sp_account_code',
        help="GL Account Code of special project CoA",
    )

    @api.multi
    def _compute_sp_account_code(self):
        Map = self.env['pabi.data.map']
        type = 'special_project'
        model_id = self.env.ref('account.model_account_account').id
        field_id = self.env.ref('account.field_account_account_code').id
        print self._model
        print model_id
        print field_id
        for rec in self:
            rec.sp_account_code = Map.get_out_value(type, model_id, field_id,
                                                    rec.code)

    # @api.multi
    # def _inverse_upper(self):
    #     for rec in self:
    #         rec.name = rec.upper.lower() if rec.upper else False
    #
    # @api.multi
    # def _search_upper(self, operator, value):
    #     if operator == 'like':
    #         operator = 'ilike'
    #     return [('name', operator, value)]
