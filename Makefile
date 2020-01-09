all: \
	app/data/neuss \
	app/data/neuss-small-overpass \
	app/data/berlin \
	app/data/hamburg \
	app/data/duesseldorf \
	app/data/koeln \
	app/data/karlsruhe \
	app/data/darmstadt

app/data/berlin: osmfiles/berlin-latest.osm 
	./quality.py -i $< -o $@
	node ../stressmodel/main.js -d $@ -f $< -i -n -v -z
	touch $@

app/data/hamburg: osmfiles/hamburg-latest.osm 
	./quality.py -i $< -o $@
	node ../stressmodel/main.js -d $@ -f $< -i -n -v -z
	touch $@

app/data/duesseldorf: osmfiles/duesseldorf-regbez-latest.osm 
	./quality.py -i $< -o $@
	node ../stressmodel/main.js -d $@ -f $< -i -n -v -z
	touch $@

app/data/koeln: osmfiles/koeln-regbez-latest.osm 
	./quality.py -i $< -o $@
	node ../stressmodel/main.js -d $@ -f $< -i -n -v -z
	touch $@

app/data/karlsruhe: osmfiles/karlsruhe-regbez-latest.osm 
	./quality.py -i $< -o $@
	node ../stressmodel/main.js -d $@ -f $< -i -n -v -z
	touch $@

app/data/neuss-small-overpass: osmfiles/neuss-small-overpass.osm 
	./quality.py -i $< -o $@
	node ../stressmodel/main.js -d $@ -f $< -i -n -v -z
	touch $@

app/data/neuss: osmfiles/neuss.osm 
	./quality.py -i $< -o $@
	node ../stressmodel/main.js -d $@ -f $< -i -n -v -z
	touch $@

app/data/darmstadt-overpass: osmfiles/darmstadt-overpass.osm 
	./quality.py -i $< -o $@
	node ../stressmodel/main.js -d $@ -f $< -i -n -v -z
	touch $@

overpass: \
	osmfiles/neuss.osm \
	osmfiles/neuss-small-overpass.osm \
	osmfiles/darmstadt-overpass.osm

osmfiles/neuss.osm:
	curl -o $@ https://overpass-api.de/api/map?bbox=6.6086,51.1425,6.7844,51.2533

osmfiles/neuss-small-overpass.osm:
	curl -o $@ https://overpass-api.de/api/map?bbox=6.6752,51.1902,6.7078,51.2076

osmfiles/darmstadt.osm:
	curl -o $@ https://overpass-api.de/api/map?bbox=8.5638,49.8219,8.7396,49.9359
	
geofabrik: \
	osmfiles/duesseldorf-regbez-latest.osm.bz2 \
	osmfiles/koeln-regbez-latest.osm.bz2 \
	osmfiles/karlsruhe-regbez-latest.osm.bz2 \
	osmfiles/berlin-latest.osm.bz2 \
	osmfiles/hamburg-latest.osm.bz2

%.osm: %.osm.bz2
	gunzip -f -k $<

osmfiles/berlin-latest.osm.bz2:
	curl -z $@ -o $@ https://download.geofabrik.de/europe/germany/berlin-latest.osm.bz2

osmfiles/hamburg-latest.osm.bz2:
	curl -z $@ -o $@ https://download.geofabrik.de/europe/germany/hamburg-latest.osm.bz2

osmfiles/duesseldorf-regbez-latest.osm.bz2:
	curl -z $@ -o $@ https://download.geofabrik.de/europe/germany/nordrhein-westfalen/duesseldorf-regbez-latest.osm.bz2

osmfiles/koeln-regbez-latest.osm.bz2:
	curl -z $@ -o $@ https://download.geofabrik.de/europe/germany/nordrhein-westfalen/koeln-regbez-latest.osm.bz2

osmfiles/karlsruhe-regbez-latest.osm.bz2:
	curl -z $@ -o $@ https://download.geofabrik.de/europe/germany/baden-wuerttemberg/karlsruhe-regbez-latest.osm.bz2
