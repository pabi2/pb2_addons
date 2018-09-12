"""
This method will click button create installment order in loan agreement
"""
import sys
import os
try:
    loan_agreement_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.dirname(loan_agreement_path)
    migration_path = os.path.dirname(script_path)
    controller_path = '%s/controller' % migration_path
    sys.path.insert(0, controller_path)
    from connection import connection
    import log
except Exception:
    pass

# Model
LoanAgreement = connection.get_model('loan.customer.agreement')

# Domain
loan_agreement_ids = [52]
dom = [('id', 'in', loan_agreement_ids)]

# Search Loan Agreement
loan_agreements = LoanAgreement.search_read(dom)

log_loan_agreement_ids = [[], []]
logger = log.setup_custom_logger('loan_agreement_act_create_installment_order')
logger.info('Start process')
logger.info('Total loan agreement: %s' % len(loan_agreements))
for loan_agreement in loan_agreements:
    try:
        LoanAgreement.mork_create_installment_order([loan_agreement['id']])
        log_loan_agreement_ids[0].append(loan_agreement['id'])
        logger.info('Pass ID: %s' % loan_agreement['id'])
    except Exception as ex:
        log_loan_agreement_ids[1].append(loan_agreement['id'])
        logger.error('Fail ID: %s (reason: %s)' % (loan_agreement['id'], ex))
summary = 'Summary: pass %s%s and fail %s%s' \
          % (len(log_loan_agreement_ids[0]),
             log_loan_agreement_ids[0] and
             ' %s' % str(tuple(log_loan_agreement_ids[0])) or '',
             len(log_loan_agreement_ids[1]),
             log_loan_agreement_ids[1] and
             ' %s' % str(tuple(log_loan_agreement_ids[1])) or '')
logger.info(summary)
logger.info('End process')
