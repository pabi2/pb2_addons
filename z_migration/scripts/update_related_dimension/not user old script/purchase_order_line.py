# -*- coding: UTF-8 -*-
"""
This method change all purchase.order.line dimension
"""
import sys
import os
import csv
try:
    budget_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.dirname(budget_path)
    migration_path = os.path.dirname(script_path)
    controller_path = '%s/controller' % migration_path
    sys.path.insert(0, controller_path)
    from connection import connection
    import log
except Exception:
    pass

print(sys.argv)	
if len(sys.argv) == 3:
	print('Argv ok')	
# Model
ModelTarget = 'purchase.order.line'
Budget = connection.get_model('account.budget')
POLine = connection.get_model(ModelTarget)

# Updates list for all structure from -> to (by code)
#####################################################
d = {}
if os.path.isfile("data_section.csv"):
	with open('data_section.csv') as csvfile:
		data = {}
		rows = csv.reader(csvfile)
		for row in rows:
			key = row[0] or False
			value = row[1] or False
			if key:
				data[key] = value
		d['section_id'] = data

if os.path.isfile("data_project.csv"):
	with open('data_project.csv') as csvfile:
		data = {}
		rows = csv.reader(csvfile)
		for row in rows:
			key = row[0] or False
			value = row[1] or False
			if key:
				data[key] = value
		d['project_id'] = data

if os.path.isfile("data_invest_asset.csv"):
	with open('data_invest_asset.csv') as csvfile:
		data = {}
		rows = csv.reader(csvfile)
		for row in rows:
			key = row[0] or False
			value = row[1] or False
			if key:
				data[key] = value
		d['invest_asset_id'] = data

if os.path.isfile("data_invest_construction_phase.csv"):
	with open('data_invest_construction_phase.csv') as csvfile:
		data = {}
		rows = csv.reader(csvfile)
		for row in rows:
			key = row[0] or False
			value = row[1] or False
			if key:
				data[key] = value
		d['invest_construction_phase_id'] = data

if os.path.isfile("data_personnel_costcenter.csv"):
	with open('data_personnel_costcenter.csv') as csvfile:
		data = {}
		rows = csv.reader(csvfile)
		for row in rows:
			key = row[0] or False
			value = row[1] or False
			if key:
				data[key] = value
		d['personnel_costcenter_id'] = data
		

##################### MANUAL ################################

#d = {
#	'section_id': {'XXX': 'YYY'},
#	'project_id': {'XXX': 'YYY'},
#	'invest_asset_id': {'XXX': 'YYY'},
#	'invest_construction_phase_id': {'XXX': 'YYY'},
#	'personnel_costcenter_id': {'XXX': 'YYY'},
#}

#############################################################

# Domain - get only relevant lines
dom = ['|', '|', '|', '|',
       ('section_id.code', 'in', d.get('section_id', {}).keys()),
       ('project_id.code', 'in', d.get('project_id', {}).keys()),
       ('invest_asset_id.code', 'in', d.get('invest_asset_id', {}).keys()),
       ('invest_construction_phase_id.code', 'in', d.get('invest_construction_phase_id', {}).keys()),
       ('personnel_costcenter_id.code', 'in', d.get('personnel_costcenter_id', {}).keys()), ]

# Search Budget
lines = POLine.search_read(dom, ['id'])

log_budget_names = [[], []]
logger = log.setup_custom_logger('Update Dimension for ' + ModelTarget)
logger.info('Start process model %s' % ModelTarget)
logger.info('Total budget: %s' % len(lines))
for line in lines:
    try:
        Budget.mock_update_related_dimension(
            ModelTarget, [line['id']],
            'account_analytic_id', d)
        log_budget_names[0].append(line['id'])
        logger.info('Pass: %s' % line['id'])
    except Exception as ex:
        log_budget_names[1].append(line['id'])
        logger.error('Fail: %s (reason: %s)' % (line['id'], ex))
summary = 'Summary: pass %s%s and fail %s%s' \
          % (len(log_budget_names[0]),
             log_budget_names[0] and ' %s' % str(tuple(log_budget_names[0]))
             or '', len(log_budget_names[1]),
             log_budget_names[1] and ' %s' % str(tuple(log_budget_names[1]))
             or '')
logger.info(summary)
logger.info('End process')
