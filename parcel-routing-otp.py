# Create a router
router = otp.getRouter()

# Create a default request for a given time
req = otp.createRequest()

# set DateTime of the request to Monday, April 18th, 2016 at 8:00AM
req.setDateTime(2016, 4, 18, 8, 00, 00)

newark_schools = otp.loadCSVPopulation('/var/otp/scripting/data/newark-schools.csv', 'lat', 'lon')
parcels = otp.loadCSVPopulation('/var/otp/scripting/data/newark-residential-parcels-centroid.csv', 'lat', 'lon')

# Create a CSV output
newarkCsv = otp.createCSVOutput()
newarkCsv.setHeader([ 'ID', 'school', 'mode', 'min_time', 'walk_distance',
					  'route_distance' ])

# Likely can't just do "TRANSIT" as mode because more limiting than web API
modes = ["WALK","CAR","TRANSIT,WALK"]

# For each point of the synthetic grid
for school in newark_schools:
	# Vertex count gets number, need to add both coords
	for mode in modes:
		print "Processing: ", school, mode
		req.setOrigin(school)
		#req.setMaxTimeSec(1800)
		req.setModes(mode)

		spt = router.plan(req)
		if spt is None: continue
		# Evaluate each school against all fake students
		res = spt.eval(parcels)

		# Iterate through all schools returned
		for r in res:
			# Get various times and distances from each returned individual
			minTime = r.getTime()
			tripDistance = r.getTotalDistance()
			walkDistance = r.getWalkDistance()
			# Create a row from found data (use schoolid instead of name)
			newarkCsv.addRow([ r.getIndividual().getStringData("ID"),
				school.getStringData("schoolid"), mode, minTime,
				walkDistance, tripDistance ])

# Save the result
newarkCsv.save('/var/otp/scripting/output/otp-scripting-newark-parcels.csv')
