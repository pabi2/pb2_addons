# -*- coding: utf-8 -*-
from openerp import models


class QueueJob(models.Model):
    _inherit = 'queue.job'

    def init(self, cr):
        """ Ensure that, the all queue_job will be rerun """
        cr.execute("""
            update queue_job set state='pending'
            where state in ('started', 'enqueued')
        """)
