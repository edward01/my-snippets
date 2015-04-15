@virtual_numbers_app.route('/export-subscribers', methods=['GET'])
def export_subscribers():
	beacon_columns = [
		'beacon_id',
		'uuid',
		'major',
		'minor',
		'beacon_type_id',
		'latest_battery_level',
		'merchant_id',
		'beacon_id'
	]
	search_filter = {}
	if rec_search_val is not None:
		search_filter['$or'] = []
		search_filter['$or'].append({'tags': {'$regex': rec_search_val, '$options': '-i'}})  #-- tags
		for col in beacon_columns:
			if col in ['latest_battery_level', 'major', 'minor'] and rec_search_val.isdigit():
				search_filter['$or'].append({col: int(rec_search_val)})
			else:
				search_filter['$or'].append({col: {'$regex': rec_search_val, '$options': '-i'}})
	beacons = app.db.beacons.find(search_filter, {'beacon_id': True, 'uuid': True, 'major': True, 'minor': True})

	def generate():
		for beacon in beacons:
			yield beacon['beacon_id'] + ',' + beacon['uuid'] + ',' + str(beacon['major']) + ',' + str(beacon['minor']) + '\n'
	return Response(generate(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=beacons.csv'})
