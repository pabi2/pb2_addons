# -*- coding: utf-8 -*-
from openerp import models, api
from .common import ReadonlyCommon


class SaleOrder(models.Model, ReadonlyCommon):
    _inherit = 'sale.order'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(SaleOrder, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        res = self.set_right_readonly_group(res)
        return res


class PurchaseOrder(models.Model, ReadonlyCommon):
    _inherit = 'purchase.order'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(PurchaseOrder, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        res = self.set_right_readonly_group(res)
        return res


class PurchaseRequest(models.Model, ReadonlyCommon):
    _inherit = 'purchase.request'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(PurchaseRequest, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        res = self.set_right_readonly_group(res)
        return res


class PurchaseRequisition(models.Model, ReadonlyCommon):
    _inherit = 'purchase.requisition'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(PurchaseRequisition, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        res = self.set_right_readonly_group(res)
        return res


class AccountInvoice(models.Model, ReadonlyCommon):
    _inherit = 'account.invoice'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(AccountInvoice, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        res = self.set_right_readonly_group(res)
        return res


class AccountVoucher(models.Model, ReadonlyCommon):
    _inherit = 'account.voucher'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(AccountVoucher, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        res = self.set_right_readonly_group(res)
        return res


class HRExpenseExpense(models.Model, ReadonlyCommon):
    _inherit = 'hr.expense.expense'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(HRExpenseExpense, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        res = self.set_right_readonly_group(res)
        return res


class BudgetPlanUnit(models.Model, ReadonlyCommon):
    _inherit = 'budget.plan.unit'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(BudgetPlanUnit, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        res = self.set_right_readonly_group(res)
        return res


class BudgetPlanProject(models.Model, ReadonlyCommon):
    _inherit = 'budget.plan.project'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(BudgetPlanProject, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        res = self.set_right_readonly_group(res)
        return res


class BudgetPlanInvestAsset(models.Model, ReadonlyCommon):
    _inherit = 'budget.plan.invest.asset'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(BudgetPlanInvestAsset, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        res = self.set_right_readonly_group(res)
        return res


class BudgetPlanInvestConstruction(models.Model, ReadonlyCommon):
    _inherit = 'budget.plan.invest.construction'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(BudgetPlanInvestConstruction, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        res = self.set_right_readonly_group(res)
        return res


class BudgetPlanPersonnel(models.Model, ReadonlyCommon):
    _inherit = 'budget.plan.personnel'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(BudgetPlanPersonnel, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        res = self.set_right_readonly_group(res)
        return res


class AccountBudget(models.Model, ReadonlyCommon):
    _inherit = 'account.budget'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(AccountBudget, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        res = self.set_right_readonly_group(res)
        return res


class PurchaseBilling(models.Model, ReadonlyCommon):
    _inherit = 'purchase.billing'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(PurchaseBilling, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        res = self.set_right_readonly_group(res)
        return res


class PurchaseWorkAcceptance(models.Model, ReadonlyCommon):
    _inherit = 'purchase.work.acceptance'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(PurchaseWorkAcceptance, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        res = self.set_right_readonly_group(res)
        return res
