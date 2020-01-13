# Cycling Level of Stress Map

Displays a map showing cycling
- levels of traffic stress
- quality of bicycle infrastructure.

The Levels of Traffic Stress (LTS) is based on the work by
[BikeOttawa](https://github.com/BikeOttawa/stressmodel)

The data included with this project is currently only a very small subset for example purposes.

Current Examples:
* Berlin https://ckrey.github.io/stressmap/app/index.html (Default)
* Neuss https://ckrey.github.io/stressmap/app/index.html?town=neuss
* Düsseldorf https://ckrey.github.io/stressmap/app/index.html?town=duesseldorf
* Köln / Aachen https://ckrey.github.io/stressmap/app/index.html?town=koeln
* Hamburg https://ckrey.github.io/stressmap/app/index.html?town=hamburg
* Darmstadt https://ckrey.github.io/stressmap/app/index.html?town=darmstadt
* Karlsruhe https://ckrey.github.io/stressmap/app/index.html?town=karlsruhe
* _others? – create a Issue/PR_

* add `&lts=yes` to see Levels of Traffic Stress (lts) layers too

# TODO describe quality algorithm

# make
	run `make overpass` to retrieve the `.osm` files for neuss and darmstadt
	run `make geofabrik` to retrieve the `.osm` files for berlin, hamburg, etc.
	run `make` to process the `.osm` files into geojson

The last step includes running the stressmodel from Ottawa assuming this is installed in `../stressmodel`
e.g. `../stressmodel node main.js -f ~/bike-stress/berlin-latest.osm -d ~/bike-stress/berlin  -z`:w

