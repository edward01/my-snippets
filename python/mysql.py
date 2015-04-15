from flask import Flask, render_template, redirect, url_for, session, request
from mysql import MySQL
# from login import login_app
# from config import MYSQL_CONFIG, DEBUG
# from virtual_numbers import virtual_numbers_app
# from dashboard import dashboard_app

app = Flask(__name__)
# app.secret_key = '\xe7\x1e*+cs\xc8a\xcd\xb7\xefF\x94\xa7g\xcby\xd3f\xe3\xd8\x01,.'
# app.debug = DEBUG
# app.reloader = DEBUG
# app.register_blueprint(login_app)
# app.register_blueprint(virtual_numbers_app)
# app.register_blueprint(dashboard_app)


# MYSQL_CONFIG = {
# 	'MYSQL_DATABASE_USER': 'root',
# 	'MYSQL_DATABASE_PASSWORD': '',
# 	'MYSQL_DATABASE_DB': 'reversed_jumper',
# 	'MYSQL_DATABASE_HOST': 'localhost'
# }

app.mysql = MySQL()
app.config.update(MYSQL_CONFIG)
app.mysql.init_app(app)


def sample_calling():
    sql_val = ("SELECT * FROM virtual_number_pool WHERE vmsisdn=%s")
    data_val = (vmsisdn)
    virtual_number_pool = query_sel(sql_val, data_val)

    insert_stmt = (
		"INSERT INTO virtual_number_pool (vmsisdn, vnstatus, allocation_date, availability_date, quarantined_date, homezone) "
		"VALUES (%s, %s, %s, %s, %s, %s)"
	)
	insert_data = (vmsisdn, vnstatus, string_to_date_obj(allocation_date), string_to_date_obj(availability_date), string_to_date_obj(quarantined_date), homezone)
    query_cud(insert_stmt, insert_data)


def query_sel(sql_statement, data_values):
    cursor = app.mysql.get_db().cursor()

    # sql_val = ("SELECT * FROM virtual_number_pool WHERE vmsisdn=%s")
    # data_val = (vmsisdn)

	cursor.execute(sql_statement, data_values)
	result = cursor.fetchone()
	cursor.close()

    return result


def query_cud(sql_statement, data_values):
    try:
		sql_conn = app.mysql.get_db()
		cursor = sql_conn.cursor()

		# insert_stmt = (
		# 	"INSERT INTO virtual_number_pool (vmsisdn, vnstatus, allocation_date, availability_date, quarantined_date, homezone) "
		# 	"VALUES (%s, %s, %s, %s, %s, %s)"
		# )
		# insert_data = (vmsisdn, vnstatus, string_to_date_obj(allocation_date), string_to_date_obj(availability_date), string_to_date_obj(quarantined_date), homezone)

        cursor.execute(sql_statement, data_values)
		sql_conn.commit()

		return True

	except Exception as e:
		print 'Exception error:', e
        return False
		# return jsonify({'status': 'error', 'message': 'Processing error. Please try again later.'})
	finally:
		cursor.close()
