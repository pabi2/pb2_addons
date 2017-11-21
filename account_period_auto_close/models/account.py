# -*- coding: utf-8 -*-
import logging
from dateutil.relativedelta import relativedelta
from datetime import datetime
from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)


class AccountFiscalyear(models.Model):
    _inherit = 'account.fiscalyear'

    auto_close = fields.Boolean(
        string='Auto Close/Open Period',
        default=True,
    )
    close_after_days = fields.Integer(
        string='Close after (days)',
        default=3,
        help="Number of days after end of running period to be auto close.\n"
        "0 means no auto close."
    )
    open_before_days = fields.Integer(
        string='Open before (days)',
        default=3,
        help="Number of days before start of next period to be auto open.\n"
        "0 means no auto open."
    )

    @api.multi
    def write(self, vals):
        res = super(AccountFiscalyear, self).write(vals)
        if 'auto_close' in vals or 'close_after_days' in vals or \
                'open_before_days' in vals:
            self._fiscal_calculate_period_auto_close()
        return res

    @api.multi
    def _fiscal_calculate_period_auto_close(self):
        """ This method will write to all periods as per setup in Fiscal """
        for fiscal in self:
            fiscal.period_ids._calculate_period_auto_close()


class AccountPeriod(models.Model):
    _inherit = 'account.period'

    auto_close = fields.Boolean(
        string='Auto Close/Open Period',
        default=False,
    )
    date_open = fields.Date(
        string='Auto Open Date',
    )
    date_close = fields.Date(
        string='Auto Close Date',
    )

    @api.multi
    def action_draft(self):
        self.write({'auto_close': False})
        return super(AccountPeriod, self).action_draft()

    @api.model
    def create(self, vals):
        rec = super(AccountPeriod, self).create(vals)
        rec._calculate_period_auto_close()
        return rec

    @api.multi
    def _calculate_period_auto_close(self):
        """ This method calc open/close date based on fiscalyear """
        for period in self:
            fiscal = period.fiscalyear_id
            date_close = datetime.strptime(
                period.date_stop, DEFAULT_SERVER_DATE_FORMAT) + \
                relativedelta(days=fiscal.close_after_days)
            date_open = datetime.strptime(
                period.date_start, DEFAULT_SERVER_DATE_FORMAT) + \
                relativedelta(days=-fiscal.open_before_days)
            period.write({
                'auto_close': fiscal.auto_close,
                'date_close': date_close.strftime(DEFAULT_SERVER_DATE_FORMAT),
                'date_open': date_open.strftime(DEFAULT_SERVER_DATE_FORMAT),
            })

    @api.model
    def process_period_auto_close(self):
        closing_periods = self.search(
            [('auto_close', '=', True),
             ('state', '=', 'draft'),
             ('date_close', '<', fields.Date.context_today(self))])
        try:
            Move = self.env['account.move']
            if not closing_periods:
                return
            for period in closing_periods:
                moves = Move.search([('period_id', '=', period.id),
                                     ('state', '=', 'draft')])
                if moves:
                    _logger.exception(
                        "Cannot auto close period %s!. To close a period, all "
                        "related journal entires must be posted" % period.name)
                    continue
                self._cr.execute("""
                    update account_journal_period
                    set state=%s where period_id=%s
                """, ('done', period.id))
                self._cr.execute("""
                    update account_period
                    set state=%s where id=%s
                """, ('done', period.id))
                self._cr.commit()
            self.invalidate_cache()
        except Exception:
            _logger.exception("Failed processing period auto close")

    @api.model
    def process_period_auto_open(self):
        opening_periods = self.search(
            [('auto_close', '=', True),
             ('state', '=', 'done'),
             ('date_open', '<=', fields.Date.context_today(self)),
             ('date_close', '>=', fields.Date.context_today(self))])
        try:
            if not opening_periods:
                return
            for period in opening_periods:
                if period.fiscalyear_id.state == 'done':
                    _logger.exception(
                        "Cannot auto open period %s!. It belongs to the closed"
                        " fiscalyear" % period.name)
                    continue
                self._cr.execute("""
                    update account_journal_period
                    set state=%s where period_id=%s
                """, ('draft', period.id))
                self._cr.execute("""
                    update account_period
                    set state=%s where id=%s
                """, ('draft', period.id))
                self._cr.commit()
            self.invalidate_cache()
        except Exception:
            _logger.exception("Failed processing period auto close")
