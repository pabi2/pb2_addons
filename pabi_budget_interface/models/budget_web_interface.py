# -*- coding: utf-8 -*-
import logging
from openerp import models, api, _
from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AccountBudget(models.Model):
    _inherit = 'account.budget'

    BUDGET_LEVEL_MODEL = {
        'activity_group_id': 'account.activity.group',
        # 'activity_id': 'Activity'  # No Activity Level
    }

    @api.model
    def test_pabiweb_check_budget(self):
        doc_date = '2018-01-01'
        doc_type = 'ex'
        budget_type = 'project_base'
        res_id = 4
        fund_id = 2
        doc_lines = [
            {'activity_rpt_id': 4277,
             'amount': 1000000.00},
            # {'activity_rpt_id': 1530,
            #  'select_asset_id': 6,
            #  'amount': 1.00},
            # {'activity_rpt_id': 1534,
            #  'select_asset_id': 7,
            #  'amount': 1.00},
        ]
        res = self.pabiweb_check_budget(doc_type, doc_date,
                                        budget_type, res_id,
                                        fund_id, doc_lines)
        return res

    @api.model
    def pabiweb_check_budget(self, doc_type, doc_date, budget_type,
                             res_id, fund_id, doc_lines, currency_id=False):
        _logger.info(
            'pabiweb_check_budget(), input: [%s, %s, %s, %s, %s, %s, %s]' %
            (doc_type, doc_date, budget_type, res_id,
             fund_id, doc_lines, currency_id))
        """ Combine 3 types of budget check
        1) Checkbudget by structure (i.e., unit_base, project_base, etc.)
        For project_base,
        2) Check fund rule by activity_rpt_id
        For project_base + asset,
        3) Check asset max price
        :param doc_type: pr, av, ex
        :param doc_date: doc_date, document date or date to check budget
        :param budget_type: 1 of the 5 budget types
        :param res_id: resource's id, differ for each type of budget
        :param fund_id: fund (used for budget_type = 'project_base' only)
        :param doc_lines: list of line item, i.e.,
            [{'activity_rpt_id': 1029, 'select_asset_id': 1, 'amount': 400.00}]
        :param currency_id: ID of currency, if not provided, it assume THB
        :return: dict of result
        """
        res = {'budget_ok': True,
               'message': False}

        if budget_type == 'unit_base':
            if not doc_type or not doc_date or not budget_type or not doc_lines:
                return res
            
            Budget = self.env['account.budget']
            
            budget_level = 'section_id'
            amount = doc_lines['amount_total']
            budget_level_res_id = self.env['res.section'].search([('code', '=', doc_lines['budget_code'])])
            fiscal_id = self.env['account.fiscalyear'].search([('date_start', '<=', doc_date),
                                                               ('date_stop', '>=', doc_date)])
            
            check_budget = Budget.check_budget(fiscal_id.id,
                                               budget_type,
                                               budget_level,
                                               budget_level_res_id.id,
                                               amount)
            
            raise ValidationError(_(check_budget))

        if budget_type == 'project_base' and not res_id:
            if not doc_type or not doc_date or not budget_type or not doc_lines:
                return res
            
            Budget = self.env['account.budget']
            
            budget_level = 'project_id'
            amount = doc_lines['amount_total']
            budget_level_res_id = self.env['res.project'].search([('code', '=', doc_lines['budget_code'])])
            fiscal_id = self.env['account.fiscalyear'].search([('date_start', '<=', doc_date),
                                                               ('date_stop', '>=', doc_date)])
            
            check_budget = Budget.check_budget(fiscal_id.id,
                                               budget_type,
                                               budget_level,
                                               budget_level_res_id.id,
                                               amount)
            
            raise ValidationError(_(check_budget))

        if not doc_lines or not res_id or not budget_type:
            return res
        ctx = {'currency_id': currency_id}
        FundRule = self.env['budget.fund.rule'].with_context(ctx)

        # Check for valid doc_type
        if doc_type not in ('pr', 'av', 'ex'):
            res = {'budget_ok': False,
                   'message': 'Invalid document type :not: pr, av, ex'}
            return res

        if doc_type == 'av':  # for AV do nothing
            return res

        # 1) Simple check budget on each structure
        # Note: PABIWeb want to call simple_check_budget directly, so ignore
        # Budget = self.env['account.budget'].with_context(ctx)
        # amount = sum([x.get('amount', 0.0) for x in doc_lines])
        # res = Budget.simple_check_budget(doc_date, budget_type,
        #                                  amount, res_id)
        # if not res['budget_ok']:
        #     return res

        # 2) If budget_type == 'project_base', check fund rule
        if budget_type == 'project_base':
            project_doc_lines = []
            for l in doc_lines:
                project_doc_lines.append({
                    'fund_id': fund_id,
                    'project_id': res_id,
                    'activity_rpt_id': l['activity_rpt_id'],
                    'amount': l['amount']
                })
            res = FundRule.document_check_fund_spending(project_doc_lines)
            if not res['budget_ok']:
                return res

        # 3) If budget_type == 'project_base' and select_asset_id is selected
        if budget_type == 'project_base':
            asset_doc_lines = []
            for l in doc_lines:
                asset_doc_lines.append({
                    'asset_rule_line_id': l.get('select_asset_id', False),
                    'amount': l['amount']
                })
            res = FundRule.document_validate_asset_price(asset_doc_lines)
            if not res['budget_ok']:
                return res
        _logger.info('pabiweb_check_budget(), output: %s' % res)
        return res
