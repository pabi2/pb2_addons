# -*- coding: utf-8 -*-
from openerp import api, models, fields, _
from openerp.exceptions import ValidationError
from .chartfield import CHART_FIELDS, ChartFieldAction


class AccountAnalyticLine(ChartFieldAction, models.Model):
    _inherit = 'account.analytic.line'

    # ChartfieldAction changed account_id = account.account, must change back
    account_id = fields.Many2one('account.analytic.account')


class AccountAnalyticAccount(ChartFieldAction, models.Model):
    _inherit = 'account.analytic.account'

    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        required=True,  # Some error on adjust asset -> expense, temp remove
    )

    @api.model
    def _analytic_dimensions(self):
        dimensions = super(AccountAnalyticAccount, self)._analytic_dimensions()
        dimensions += dict(CHART_FIELDS).keys()
        return dimensions

    @api.model
    def test_chartfield_active(self, chartfield_dict):
        """ Test with following chartfield is inactive
            :param chartfield_dict: i.e., {'section_id': 1234, ...}
            :return: (active, err_message)
        """
        test_model = {
            'res.section': 'section_id',
            'res.project': 'project_id',
            'res.invest.construction.phase': 'invest_construction_phase_id',
            'res.invest.asset': 'invest_asset_id',
            'res.personnel.costcenter': 'personnel_costcenter_id',
        }
        for model, field in test_model.iteritems():
            if chartfield_dict.get(field, False):
                obj = self.env[model].search(
                    [('id', '=', chartfield_dict[field]),
                     ('active', '=', False)])
                if obj:
                    return (False, _('%s is not active!') % obj.code)
        return (True, False)

    @api.model
    def get_analytic_search_domain(self, rec):
        domain = \
            super(AccountAnalyticAccount, self).get_analytic_search_domain(rec)
        chartfield_dict = dict([(x[0], x[2]) for x in domain])
        active, err_message = self.test_chartfield_active(chartfield_dict)
        if not active:
            raise ValidationError(err_message)
        return domain
