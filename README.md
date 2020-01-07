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

# TODO describe download and processing of .osm files
- download .bz2 file from e.g. https://download.geofabrik.de/europe/germany/nordrhein-westfalen/duesseldorf-regbez.html
- gunzip
- in ../stressmodel node main.js -f ~/bike-stress/berlin-latest.osm -d ~/bike-stress/berlin  -z
