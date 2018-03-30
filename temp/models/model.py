# -*- coding: utf-8 -*-
from openerp import api, models, fields


class A(models.Model):
    _name = "budget.carry.over"


class B(models.Model):
    _name = "budget.carry.over.line"


class C(models.Model):
    _name = "budget.carry.over.line.view"
    _auto = False
