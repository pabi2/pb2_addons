# -*- coding: utf-8 -*-
from openerp import models


class BudgetPlanTempalte(models.Model):
    _name = "budget.plan.tempalte"


class BudgetPlanTemplate(models.Model):
    _name = "budget.plan.template"


class BudgetPlanTemplateLine(models.Model):
    _name = "budget.plan.tempalte.line"


class BudgetPlanLineTemplate(models.Model):
    _name = "budget.plan.line.template"


class BudgetFiscalPolicy(models.Model):
    _name = "budget.fiscal.policy"


class BudgetFiscalPolicyLine(models.Model):
    _name = "budget.fiscal.policy.line"


class BudgetFiscalPolicyBreakdown(models.Model):
    _name = "budget.fiscal.policy.breakdown"


class BudgetFiscalBreakdownLine(models.Model):
    _name = "budget.fiscal.policy.breakdown.line"
