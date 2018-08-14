# -*- coding: utf-8 -*-
from openerp import models


class a(models.Model):
    _name = 'xlsx.report.gl.payable'
    _auto = False


class b(models.Model):
    _name = 'xlsx.report.gl.receivable'
    _auto = False


class c(models.Model):
    _name = 'receivable.confirmation.letter'
    _auto = False


class d(models.Model):
    _name = 'jasper.report.receivable.follow.up'
    _auto = False


class e(models.Model):
    _name = 'jasper.report.payment.history'
    _auto = False


class f(models.Model):
    _name = 'payable.confirmation.letter'
    _auto = False


class g(models.Model):
    _name = 'xlsx.report.purchase.contract'
    _auto = False


class h(models.Model):
    _name = 'xlsx.report.supplier.invoice.detail'
    _auto = False


class i(models.Model):
    _name = 'xlsx.report.partner.list'
    _auto = False
