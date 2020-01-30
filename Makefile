# stressmap
all: \
	app/data/neuss \
	app/data/neuss-small \
	app/data/duesseldorf-small \
	app/data/berlin \
	app/data/hamburg \
	app/data/duesseldorf \
	app/data/koeln \
	app/data/karlsruhe \
	app/data/darmstadt \
	osm2json

osm2json: osm2json.c
	cc -o $@ $< `xml2-config --cflags --libs`

clean:
	rm osm2json

%.osm.json: %.osm osm2json
	./osm2json -i $<
	# ./osm2json.py -i $<

app/data/berlin: app/data/berlin/level_0.json app/data/berlin/quality_0.json
app/data/hamburg: app/data/hamburg/level_0.json app/data/hamburg/quality_0.json
app/data/duesseldorf: app/data/duesseldorf/level_0.json app/data/duesseldorf/quality_0.json
app/data/koeln: app/data/koeln/level_0.json app/data/koeln/quality_0.json
app/data/karlsruhe: app/data/karlsruhe/level_0.json app/data/karlsruhe/quality_0.json
app/data/darmstadt: app/data/darmstadt/level_0.json app/data/darmstadt/quality_0.json
app/data/neuss: app/data/neuss/level_0.json app/data/neuss/quality_0.json
app/data/neuss-small: app/data/neuss-small/level_0.json app/data/neuss-small/quality_0.json
app/data/duesseldorf-small: app/data/duesseldorf-small/level_0.json app/data/duesseldorf-small/quality_0.json

app/data/duesseldorf/level_0.json: osmfiles/duesseldorf-regbez-latest.osm 
	node ../stressmodel/main.js -d $(@D) -f $< -i -n -v -z

app/data/duesseldorf/quality_0.json: osmfiles/duesseldorf-regbez-latest.osm.json
	./quality.py -i $< -o $(@D)

app/data/koeln/level_0.json: osmfiles/koeln-regbez-latest.osm 
	node ../stressmodel/main.js -d $(@D) -f $< -i -n -v -z

app/data/koeln/quality_0.json: osmfiles/koeln-regbez-latest.osm.json
	./quality.py -i $< -o $(@D)

app/data/karlsruhe/level_0.json: osmfiles/karlsruhe-regbez-latest.osm 
	node ../stressmodel/main.js -d $(@D) -f $< -i -n -v -z

app/data/karlsruhe/quality_0.json: osmfiles/karlsruhe-regbez-latest.osm.json
	./quality.py -i $< -o $(@D)

app/data/berlin/quality_0.json: osmfiles/berlin-latest.osm.json
	./quality.py -i $< -o $(@D)

app/data/berlin/level_0.json: osmfiles/berlin-latest.osm 
	node ../stressmodel/main.js -d $(@D) -f $< -i -n -v -z

app/data/hamburg/quality_0.json: osmfiles/hamburg-latest.osm.json
	./quality.py -i $< -o $(@D)

app/data/hamburg/level_0.json: osmfiles/hamburg-latest.osm 
	node ../stressmodel/main.js -d $(@D) -f $< -i -n -v -z

app/data/darmstadt/quality_0.json: osmfiles/darmstadt.osm.json
	./quality.py -i $< -o $(@D)

app/data/darmstadt/level_0.json: osmfiles/darmstadt.osm 
	node ../stressmodel/main.js -d $(@D) -f $< -i -n -v -z

app/data/neuss/quality_0.json: osmfiles/neuss.osm.json
	./quality.py -i $< -o $(@D)

app/data/neuss/level_0.json: osmfiles/neuss.osm 
	node ../stressmodel/main.js -d $(@D) -f $< -i -n -v -z

app/data/neuss-small/level_0.json: osmfiles/neuss-small.osm 
	node ../stressmodel/main.js -d $(@D) -f $< -i -n -v -z

app/data/duesseldorf-small/level_0.json: osmfiles/duesseldorf-small.osm 
	node ../stressmodel/main.js -d $(@D) -f $< -i -n -v -z

app/data/neuss-small/quality_0.json: osmfiles/neuss-small.osm.json
	./quality.py -i $< -o $(@D)

app/data/duesseldorf-small/quality_0.json: osmfiles/duesseldorf-small.osm.json
	./quality.py -i $< -o $(@D)


overpass: \
	osmfiles/neuss.osm \
	osmfiles/neuss-small.osm \
	osmfiles/duesseldorf-small.osm \
	osmfiles/darmstadt.osm

osmfiles/neuss.osm:
	curl -o $@ https://overpass-api.de/api/map?bbox=6.6086,51.1425,6.7844,51.2533

osmfiles/neuss-small.osm:
	curl -o $@ https://overpass-api.de/api/map?bbox=6.6752,51.1902,6.7078,51.2076

osmfiles/duesseldorf-small.osm:
	curl -o $@ https://overpass-api.de/api/map?bbox=6.7274,51.1956,6.8141,51.2548

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
