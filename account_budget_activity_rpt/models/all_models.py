# -*- coding: utf-8 -*-
from openerp import models
from .account_activity import ActivityCommon

# During plannin, we may not need it.
# class AccountBudgetLine(ActivityCommon, models.Model):
#     _inherit = "account.budget.line"


class AccountInvoiceLine(ActivityCommon, models.Model):
    _inherit = 'account.invoice.line'


class ProcurementOrder(ActivityCommon, models.Model):
    _inherit = 'procurement.order'


class PurchaseRequestLine(ActivityCommon, models.Model):
    _inherit = 'purchase.request.line'


class PurchaseRequisitionLine(ActivityCommon, models.Model):
    _inherit = 'purchase.requisition.line'


class HRExpenseLine(ActivityCommon, models.Model):
    _inherit = 'hr.expense.line'


class HRSalaryLine(ActivityCommon, models.Model):
    _inherit = 'hr.salary.line'


class PurchaseOrderLine(ActivityCommon, models.Model):
    _inherit = 'purchase.order.line'


class SaleOrderLine(ActivityCommon, models.Model):
    _inherit = 'sale.order.line'


class StockMove(ActivityCommon, models.Model):
    _inherit = 'stock.move'
