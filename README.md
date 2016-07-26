# Newark Parcel Routing
Docker setup for a Newark OpenTripPlanner instance that generates data for distances
and times between every residential parcel in Newark and each school.

## Docker Machine Setup
```
docker-machine create -d virtualbox --virtualbox-memory 8192 newark-parcels
eval $(docker-machine env newark-parcels)
docker build -t newark-otp .
```

## Create Shapefiles
Create a CSV of all results with:
`docker run -v /path/newark-parcel-routing:/var/otp/scripting newark-otp --router newark --script /var/otp/scripting/parcel-routing-otp.py`

Then, access the inside of the Docker container and create the shapefiles with:
```
docker run -v /path/newark-parcel-routing:/var/otp/scripting -i -t --entrypoint=/bin/bash newark-otp
cd /var/otp/scripting
python make-shp.py
```

---

## Notes

### Data Sources
Parcel data from [Newark Open Data](http://data.ci.newark.nj.us/dataset/parcels/resource/05698a31-49ab-4294-89a0-8df45ab7a909), with
only parcels of `PROPCLASS` 2 or 4C selected for residential.

School list comes from [Newark Public Schools](http://www.nps.k12.nj.us/schools/).

### Data Units
**Distance:** Meters

**Time:** Seconds

### OpenTripPlanner JAR
OpenTripPlanner JAR file was created with a modification that adds the `getTotalDistance()`
method to the scripting API router providing the total distance of a given route
(currently only a method for walking distance exists).
