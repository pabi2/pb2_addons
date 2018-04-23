# -*- coding: utf-8 -*-
import pytz
import logging
from datetime import datetime
from openerp import models, api, fields, SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT

logger = logging.getLogger(__name__)


class IrCron(models.Model):
    _inherit = 'ir.cron'

    specific_time = fields.Float(
        string='Specified Time',
        help="If specified, as soon as next run is set, this time will be used"
    )

    def _process_job(self, job_cr, job, cron_cr):
        res = super(IrCron, self)._process_job(job_cr, job, cron_cr)
        with api.Environment.manage():
            cron = self.browse(job_cr, SUPERUSER_ID, job['id'])
            if cron.specific_time:
                # Convert nextcall to nextcall + specific_time
                datepart = datetime.strptime(cron.nextcall, DATETIME_FORMAT).\
                    strftime(DATE_FORMAT)
                hours = int(cron.specific_time)
                minutes = (cron.specific_time * 60) % 60
                seconds = (cron.specific_time * 3600) % 60
                timepart = '%02d:%02d:%02d' % (hours, minutes, seconds)
                dt = datetime.strptime(
                    '%s %s' % (datepart, timepart), DATETIME_FORMAT)
                # Change time zone
                tz_name = self.pool['res.users'].read(
                    job_cr, SUPERUSER_ID, SUPERUSER_ID, ['tz'])['tz']
                if tz_name:
                    try:
                        user_tz = pytz.timezone(tz_name)
                        utc = pytz.utc

                        dt = user_tz.localize(dt).astimezone(utc)
                    except Exception:
                        logger.warn(
                            "Failed to convert the value for a field back "
                            "from the user's timezone (%s) to UTC",
                            tz_name,
                            exc_info=True)
                new_datetime = dt.strftime(DATETIME_FORMAT)
                self.write(job_cr, SUPERUSER_ID, [cron.id],
                           {'nextcall': new_datetime})
                job_cr.commit()
        return res
