# -*- coding: utf-8 -*-
# ~
# Multiline UI
# entropysoln
# ~
#

import uuid
import datetime
from flask import Blueprint, render_template, abort, current_app as app, request, session, url_for, redirect, flash, jsonify
from utils import validate_form
from pprint import pprint
from datetime import datetime
import time
from werkzeug import secure_filename
import csv


ALLOWED_EXTENSIONS = set(['csv'])


@virtual_numbers_app.route('/upload-entry-post', methods=['POST'])
def upload_entry_post():
	filename = None
	up_status = ''
	status_msgs = []
	file = request.files['csv_file']

	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		up_status = 'ok'
		print 'Upload ok', file.content_length, file.content_type, file.mimetype, file.headers
	elif file.filename != '':
		up_status = 'error'
		print 'File "%s" not allowed. CSV type only.' % (secure_filename(file.filename))

	if up_status == 'ok':
		csv_file = csv.reader(file.stream, delimiter=',')
		virtual_numbers = []
		csv_duplicate_list = []
		line_no = process_cnt = 0

		for line in csv_file:
			line_no += 1
			if len(line) < 6:
				app.logger.warning('==> Invalid format in line #%s' % line_no)
				up_status = 'error'
				status_msgs.append('Invalid column format in file for line #%s' % line_no)
				break

			vmsisdn = line[0]
			vnstatus = line[1]
			allocation_date = line[2]
			availability_date = line[3]
			quarantined_date = line[4]
			homezone = line[5]

			#------- VALIDATIONS -----------------------------------------------
			if not is_valid_upload_int(vnstatus):
				up_status = 'error'
				status_msgs.append('vnstatus should be a number for line #%s' % line_no)

			if not is_valid_upload_date(allocation_date):
				up_status = 'error'
				status_msgs.append('allocation_date invalid (should be "mm/dd/yyyy") for line #%s' % line_no)

			if not is_valid_upload_date(availability_date):
				up_status = 'error'
				status_msgs.append('availability_date invalid (should be "mm/dd/yyyy") for line #%s' % line_no)

			if not is_valid_upload_date(quarantined_date):
				up_status = 'error'
				status_msgs.append('quarantined_date invalid (should be "mm/dd/yyyy") for line #%s' % line_no)

			if not is_valid_upload_int(homezone):
				up_status = 'error'
				status_msgs.append('homezone should be a number for line #%s' % line_no)

			if check_duplicate_pk(vmsisdn):
				up_status = 'error'
				status_msgs.append('unique identifier(%s) already exists for line #%s' % (vmsisdn, line_no))
			#------- VALIDATIONS: END -----------------------------------------------


			#-- check for duplicate uuid-major-minor in csv file
			# has_csv_duplicate = False
			# combi_string = '%s%s%s' % (uuid, major, minor)
			# if combi_string not in csv_duplicate_list:
			# 	csv_duplicate_list.append(combi_string)
			# else:
			# 	has_csv_duplicate = True

			virtual_number = {
				'vmsisdn': vmsisdn,
				'vnstatus': vnstatus,
				'allocation_date': allocation_date,
				'availability_date': availability_date,
				'quarantined_date': quarantined_date,
				'homezone': homezone
			}
			virtual_numbers.append(virtual_number)
			process_cnt += 1

			if len(status_msgs) >= 10:  # trim errors to only 10 messages
				status_msgs.append('... more errors found, please fix above errors first')
				break

		if process_cnt == 0 or up_status == 'error':
			up_status = 'error'
			status_msgs.append('Processing failed.')

		if up_status == 'error':
			return jsonify({'status': 'error', 'message': status_msgs})
		else:
			try:
				sql_conn = app.mysql.get_db()
				cursor = sql_conn.cursor()

				for virtual_number in virtual_numbers:
					insert_stmt = (
						"INSERT INTO virtual_number_pool (vmsisdn, vnstatus, allocation_date, availability_date, quarantined_date, homezone) "
						"VALUES (%s, %s, %s, %s, %s, %s)"
					)
					insert_data = (virtual_number['vmsisdn'], int(virtual_number['vnstatus']), string_to_date_obj(virtual_number['allocation_date']), string_to_date_obj(virtual_number['availability_date']), string_to_date_obj(virtual_number['quarantined_date']), int(virtual_number['homezone']))
					cursor.execute(insert_stmt, insert_data)

				sql_conn.commit()
				return jsonify({'status': 'ok'})

			except Exception as e:
				print 'Exception error:', e
				return jsonify({'status': 'error', 'message': 'Processing error. Please try again later.'})
			finally:
				file.close()
				cursor.close()
	else:
		file.close()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def is_valid_upload_date(input_val):
	try:
		datetime.strptime(input_val, '%m/%d/%Y')
		is_valid_date_format = True
	except ValueError:
		is_valid_date_format = False

	return is_valid_date_format


def is_valid_upload_int(input_val):
	try:
		int(input_val)
		is_valid_int = True
	except ValueError:
		is_valid_int = False

	return is_valid_int
