# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from openerp import _
from openerp.exceptions import Warning as UserError

from openerp.addons.currency_rate_update.services.\
    currency_getter_interface import Currency_getter_interface


_logger = logging.getLogger(__name__)


class THB_getter(Currency_getter_interface):
    """Implementation of Curreny_getter_factory interface
    for THB RSS service
    """

    def get_updated_currency(self, currency_array, main_currency,
                             max_delta_days):
        """implementation of abstract method of Curreny_getter_interface"""
        # LastA.xml is always the most recent one
        #url = 'http://www2.bot.or.th/RSS/fxrates/fxrate-%s.xml'
        url = 'https://www.bot.or.th/App/RSS/fxrate-%s.xml'
        if main_currency in currency_array:
            currency_array.remove(main_currency)

        import feedparser

        for curr in currency_array:
            _logger.debug("BOT currency rate service : connecting...")
            dom = feedparser.parse(url % curr)

            self.validate_cur(curr)

            # check if BOC service is running
            if dom.bozo and dom.status != 404:
                _logger.error("Bank of Thailand - service is down - try again\
                    later...")

            # check if BOC sent a valid response for this currency
            if dom.status != 200:
                _logger.error(
                    "Exchange data for %s is not\
                        reported by Bank of Thailand." % curr)
                raise UserError(_('Exchange data for %s is not '
                                'reported by Bank of Thailand.'
                                % str(curr)))

            _logger.debug("BOT sent a valid RSS file for: " + curr)

            # check for valid exchange data
            if (dom.entries[0].cb_basecurrency == main_currency) and \
                    (dom.entries[0].cb_targetcurrency[:3] == curr):
                value = dom.entries[0].summary_detail.value.split('\n', 1)[0]
                rate = value.split('\n', 1)[0].split()[0]
                factor = value.split('=')[1].split()[0]
                if rate:
                    rate = float(rate) / float(factor)
                else:
                    rate = 1.0
                # rate = 1 / rate

                rate_date_datetime =\
                    datetime.strptime(dom.entries[0].updated, '%Y-%m-%d')
                self.check_rate_date(rate_date_datetime, max_delta_days)

                self.updated_currency[curr] = rate
                _logger.debug("BOT Rate retrieved : %s = %s %s" %
                              (main_currency, rate, curr))
            else:
                _logger.error(
                    "Exchange data format error for Bank of Thailand -"
                    "%s. Please check provider data format "
                    "and/or source code." % curr)
                raise UserError(_('Exchange data format error for '
                                'Bank of Thailand - %s !' % str(curr)))
        return self.updated_currency, self.log_info
