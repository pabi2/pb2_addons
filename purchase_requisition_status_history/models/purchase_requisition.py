# -*- coding: utf-8 -*-
from openerp import models
from openerp.addons.document_status_history.models.document_history import \
    LogCommon


class PurchaseRequisition(LogCommon, models.Model):
    _inherit = 'purchase.requisition'
