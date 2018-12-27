# -*- coding: UTF-8 -*-
"""
This method change all purchase.order.line dimension
"""
import sys
import os
import csv

# ชื่อไฟล์ CSV ต้องชื่อนี้เท่านั้น
List_CSVFile = [
	'data_section.csv',
	'data_project.csv',
	'data_invest_asset.csv', 
	'data_invest_construction_phase.csv',
	'data_personnel_costcenter.csv'
]

def readCSV(CSVFile):
	d = {}
	if CSVFile == 'data_section.csv' or CSVFile == '-all':
		if os.path.isfile('data_section.csv'):
			with open('data_section.csv') as csvfile:
				data = {}
				rows = csv.reader(csvfile)
				for row in rows:
					key = row[0] or False
					value = row[1] or False
					if key:
						data[key] = value
				d['section_id'] = data
		else:
			print "File data_section.csv not found!"

	if CSVFile == 'data_project.csv' or CSVFile == '-all':
		if os.path.isfile('data_project.csv') and (CSVFile == 'data_project.csv' or CSVFile == '-all'):
			with open('data_project.csv') as csvfile:
				data = {}
				rows = csv.reader(csvfile)
				for row in rows:
					key = row[0] or False
					value = row[1] or False
					if key:
						data[key] = value
				d['project_id'] = data
		else:
			print "File data_project.csv not found!"
	
	if CSVFile == 'data_invest_asset.csv' or CSVFile == '-all':
		if os.path.isfile('data_invest_asset.csv') and (CSVFile == 'data_invest_asset.csv' or CSVFile == '-all'):
			with open('data_invest_asset.csv') as csvfile:
				data = {}
				rows = csv.reader(csvfile)
				for row in rows:
					key = row[0] or False
					value = row[1] or False
					if key:
						data[key] = value
				d['invest_asset_id'] = data
		else:
			print "File data_invest_asset.csv not found!"

	if CSVFile == 'data_invest_construction_phase.csv' or CSVFile == '-all':
		if os.path.isfile('data_invest_construction_phase.csv') and (CSVFile == 'data_invest_construction_phase.csv' or CSVFile == '-all'):
			with open('data_invest_construction_phase.csv') as csvfile:
				data = {}
				rows = csv.reader(csvfile)
				for row in rows:
					key = row[0] or False
					value = row[1] or False
					if key:
						data[key] = value
				d['invest_construction_phase_id'] = data
		else:
			print "File data_invest_construction_phase.csv not found!"

	if CSVFile == 'data_personnel_costcenter.csv' or CSVFile == '-all':
		if os.path.isfile('data_personnel_costcenter.csv') and (CSVFile == 'data_personnel_costcenter.csv' or CSVFile == '-all'):
			with open('data_personnel_costcenter.csv') as csvfile:
				data = {}
				rows = csv.reader(csvfile)
				for row in rows:
					key = row[0] or False
					value = row[1] or False
					if key:
						data[key] = value
				d['personnel_costcenter_id'] = data
		else:
			print "File data_personnel_costcenter.csv not found!"
	return d