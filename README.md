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
* Neuss City https://ckrey.github.io/stressmap/app/index.html?town=neuss-small
* Düsseldorf https://ckrey.github.io/stressmap/app/index.html?town=duesseldorf
* Düsseldorf City  https://ckrey.github.io/stressmap/app/index.html?town=duesseldorf-small
* Köln / Aachen https://ckrey.github.io/stressmap/app/index.html?town=koeln
* Hamburg https://ckrey.github.io/stressmap/app/index.html?town=hamburg
* Darmstadt https://ckrey.github.io/stressmap/app/index.html?town=darmstadt
* Karlsruhe https://ckrey.github.io/stressmap/app/index.html?town=karlsruhe
* München https://ckrey.github.io/stressmap/app/index.html?town=muenchen
* Leipzig https://ckrey.github.io/stressmap/app/index.html?town=leipzig
* Halle https://ckrey.github.io/stressmap/app/index.html?town=halle
* ...
* _others? – create a Issue/PR_

* add `&lts=yes` to see Levels of Traffic Stress (lts) layers too

# Quality Algorithm

Way are assigned a Bike Quality Level ranging from 0 to 999, which is clustered in 100s (000-099, 100-101, etc.)

## 0xx means cycling is not possible or not permitted
## 1xx means cycling is possible but shared with motorized traffic (or foot traffic)
## 2xx Marked Lanes
If a `highway` has a tag beginning with `cycleway` and is marked with `lane` (201) or `opposite_lane` (202) it is
in assumed to be on marked lanes (2xx)
## 3xx Cycling on Tracks
If a `highway` has a tag beginning with `cycleway` and is marked with `track` (301) or `opposite_track` (302) it is
in assumed to be on tracks (3xx)
## 4xx Cycling in a Designated Cyclestreet
If a `highway` has a tag `cyclestreet=yes` (401) or `bicycle_road=yes` (402) it is assumed to be a cyclestreet (4xx)
## 5xx Cycling on a Separated Path
## (6xx means cycling is very good)
## 7xx Designated Cycleway

## (8xx means cycling is as good as it can be on earth)
## (9xx means cycling here would be like being in heaven.

### TODO
- shared footways vs. shared streets
- shared bus-lanes


# make
	run `make overpass` to retrieve the `.osm` files for neuss and darmstadt
	run `make geofabrik` to retrieve the `.osm` files for berlin, hamburg, etc.
	run `make` to process the `.osm` files into geojson

The last step includes running the stressmodel from Ottawa assuming this is installed in `../stressmodel`
e.g. `../stressmodel node main.js -f ~/bike-stress/berlin-latest.osm -d ~/bike-stress/berlin  -z`:w

