# -*- coding: utf-8 -*-
from openerp import models
from openerp.addons.document_status_history.models.document_history import \
    LogCommon


class StockRquest(LogCommon, models.Model):
    _inherit = 'stock.request'
