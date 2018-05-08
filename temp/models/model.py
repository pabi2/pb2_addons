# -*- coding: utf-8 -*-
from openerp import models


class A(models.Model):
    _name = "budget.carry.over"


class B(models.Model):
    _name = "budget.carry.over.line"


class C(models.Model):
    _name = "budget.carry.over.line.view"
    _auto = False
