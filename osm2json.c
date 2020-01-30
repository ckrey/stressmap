#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <libxml/SAX.h>
#include "uthash.h"
#include "utarray.h"

int read_xmlfile(FILE *f);
xmlSAXHandler make_sax_handler();

static void OnStartElementNs(
    void *ctx,
    const xmlChar *localname,
    const xmlChar *prefix,
    const xmlChar *URI,
    int nb_namespaces,
    const xmlChar **namespaces,
    int nb_attributes,
    int nb_defaulted,
    const xmlChar **attributes
);

static void OnEndElementNs(
    void* ctx,
    const xmlChar* localname,
    const xmlChar* prefix,
    const xmlChar* URI
);

static void OnCharacters(void* ctx, const xmlChar * ch, int len);

struct a_node {
	long id;
 	double lat;
	double lon; 
    	UT_hash_handle hh;
};
static struct a_node *node = NULL;
static struct a_node *nodes = NULL;

struct a_tag {
	char *key;
	xmlChar *value;
	UT_hash_handle hh;
};
static struct a_tag *tag = NULL;

UT_icd long_icd = {sizeof(long), NULL, NULL, NULL };
struct a_way {
	long id;
 	double lat;
	double lon; 
        struct a_tag *tags;
	UT_array *noderefs;
    	UT_hash_handle hh;
};
static struct a_way *way = NULL;
static struct a_way *ways = NULL;

int main(int argc, char *argv[]) {
	char *infile = "default.osm";
	int c;

	opterr = 0;

	while ((c = getopt (argc, argv, "i:")) != -1) {
		switch (c) {
			case 'i':
				infile = optarg;
				break;
			default:
				puts("option error.");
				abort ();
		}
      }

	fprintf(stderr, "Scanning: %s\n", infile);
	FILE *f = fopen(infile, "r");
	if (!f) {
		puts("file open error.");
		exit(1);
	}

	if(read_xmlfile(f)) {
		puts("xml read error.");
		exit(1);
	}

	fprintf(stderr, "numNodes: %u, numWays: %u\n", HASH_COUNT(nodes), HASH_COUNT(ways));

	char *outfile = malloc(strlen(infile) + sizeof(".json") + 1);
	strcpy(outfile, infile);
	strcat(outfile, ".json");	

	fprintf(stderr, "Writing: %s\n", outfile);
	FILE *fout = fopen(outfile, "w");
	if (!fout) {
		puts("file open output error.");
		exit(2);
	}

        int firstNode = 1;
	fprintf(fout, "{\"nodes\": {\n");
    	for (struct a_node *node = nodes; node != NULL; node = node->hh.next) {
		//printf("node id %ld: lat=%f lon=%f\n", node->id, node->lat, node->lon);
		fprintf(fout, "%s\"%ld\": {\"identifier\":\"%ld\", \"lat\": %f, \"lon\": %f}\n",
			firstNode ? "": ", ", node->id, node->id, node->lat, node->lon);
		firstNode = 0;
	}
	int firstWay = 1;
	fprintf(fout, "},\"ways\": {\n");
    	for (struct a_way *way = ways; way != NULL; way = way->hh.next) {
		//printf("way id %ld:\n", way->id);
		int firstTag = 1;
		fprintf(fout, "%s\"%ld\": {\"id\":\"%ld\", \"tags\": {\n",
			firstWay ? "" : ", ",  way->id, way->id);
		for (struct a_tag *tag = way->tags; tag != NULL; tag = tag->hh.next) {
			//printf("tag %s: %s\n", tag->key, tag->value);
			fprintf(fout, "%s\"%s\": \"",
				firstTag ? "" : ", ", tag->key);
			for (xmlChar *p = tag->value; *p; p++) {
				if (*p == '\"') {
					fprintf(fout, "\\\"");
				} else if (*p == '\\') {
					fprintf(fout, "\\\\");
				} else if (*p == '\b') {
					fprintf(fout, "\\b");
				} else if (*p == '\r') {
					fprintf(fout, "\\r");
				} else if (*p == '\n') {
					fprintf(fout, "\\n");
				} else if (*p == '\f') {
					fprintf(fout, "\\f");
				} else if (*p == '\t') {
					fprintf(fout, "\\t");
				} else {
					fprintf(fout, "%c", *p);
				}
			}
			fprintf(fout, "\"\n");
			firstTag = 0;
		}
		int firstNoderef = 1;
		fprintf(fout, "}, \"nodes\": [\n");
		long *noderefp = NULL;
		while ( (noderefp = (long*)utarray_next(way->noderefs, noderefp))) {
			//printf("ref: %ld\n", *noderefp);
			fprintf(fout, "%s\"%ld\"\n",
				firstNoderef ? "" : ", ", *noderefp);
			firstNoderef = 0;
		}
		fprintf(fout, "]\n}\n");
		firstWay = 0;
	}

	fprintf(fout, "}\n}\n");
	fclose(fout);
	fclose(f);
	fprintf(stderr, "Finished\n");
	return 0;
}

int read_xmlfile(FILE *f) {
    char chars[1024];
    int res = fread(chars, 1, 4, f);
    if (res <= 0) {
        return 1;
    }

    xmlSAXHandler SAXHander = make_sax_handler();
 
    xmlParserCtxtPtr ctxt = xmlCreatePushParserCtxt(
        &SAXHander, NULL, chars, res, NULL
    );

    while ((res = fread(chars, 1, sizeof(chars), f)) > 0) {
        if(xmlParseChunk(ctxt, chars, res, 0)) {
            xmlParserError(ctxt, "xmlParseChunk");
            return 1;
        }
    }
    xmlParseChunk(ctxt, chars, 0, 1);

    xmlFreeParserCtxt(ctxt);
    xmlCleanupParser();

    return 0;
}

xmlSAXHandler make_sax_handler (){
    xmlSAXHandler SAXHandler;

    memset(&SAXHandler, 0, sizeof(xmlSAXHandler));

    SAXHandler.initialized = XML_SAX2_MAGIC;
    SAXHandler.startElementNs = OnStartElementNs;
    SAXHandler.endElementNs = OnEndElementNs;

    return SAXHandler;
}

static void OnStartElementNs(
    void *ctx,
    const xmlChar *localname,
    const xmlChar *prefix,
    const xmlChar *URI,
    int nb_namespaces,
    const xmlChar **namespaces,
    int nb_attributes,
    int nb_defaulted,
    const xmlChar **attributes
) {
	//printf("start %s\n", localname);
	if (xmlStrcmp(localname, (xmlChar *)"node") == 0) {
		node = malloc(sizeof(struct a_node));
	}
	if (xmlStrcmp(localname, (xmlChar *)"tag") == 0) {
		tag = malloc(sizeof(struct a_tag));
	}
	if (xmlStrcmp(localname, (xmlChar *)"way") == 0) {
		way = malloc(sizeof(struct a_way));
		way->tags = NULL;
		utarray_new(way->noderefs, &long_icd);

	}
    	//printf("nb_attributes: %d:\n", nb_attributes);
    	//printf("nb_defaulted: %d:\n", nb_defaulted);
	const xmlChar **p = attributes;
	while (*p != NULL) {
		const xmlChar *localname = *p;
    		//printf("localname: %s\n", *p);
		p++;
    		//printf("prefix: %s\n", *p);
		p++;
    		//printf("URI: %s\n", *p);
		p++;
		const xmlChar *v = *p;
		p++;
		const xmlChar *e = *p;
		xmlChar *value = malloc(e-v+1);
		memcpy(value, v, e-v);
		value[e-v] = '\0';
    		//printf("value: %s\n", value);
		if (xmlStrcmp(localname, (xmlChar *)"id") == 0) {
			if (node != NULL) {
				node->id = strtol((char *)value, NULL, 10);
			}
			if (way != NULL) {
				way->id = strtol((char *)value, NULL, 10);
			}
		}
		if (xmlStrcmp(localname, (xmlChar *)"lat") == 0) {
			if (node != NULL) {
				node->lat = strtod((char *)value, NULL);
			}
		}
		if (xmlStrcmp(localname, (xmlChar *)"lon") == 0) {
			if (node != NULL) {
				node->lon = strtod((char *)value, NULL);
			}
		}
		if (xmlStrcmp(localname, (xmlChar *)"ref") == 0) {
			if (way != NULL) {
				long noderef = strtol((char *)value, NULL, 10);
				utarray_push_back(way->noderefs, &noderef);
			}
		}
		if (xmlStrcmp(localname, (xmlChar *)"k") == 0) {
			if (tag != NULL) {
				tag->key = (char *)xmlStrdup(value);
			}
		}
		if (xmlStrcmp(localname, (xmlChar *)"v") == 0) {
			if (tag != NULL) {
				tag->value = xmlStrdup(value);
			}
		}
		free(value);

		p++;
	}
}

static void OnEndElementNs(
    void* ctx,
    const xmlChar* localname,
    const xmlChar* prefix,
    const xmlChar* URI
) {
	//printf("end %s\n", localname);
	if (xmlStrcmp(localname, (xmlChar *)"node") == 0) {
		HASH_ADD(hh, nodes, id, sizeof(long), node);
		node = NULL;
	}
	if (xmlStrcmp(localname, (xmlChar *)"tag") == 0) {
		if (way != NULL) {
			HASH_ADD_STR(way->tags, key, tag);
		} else {
			free(tag);
		}
		tag = NULL;
	}
	if (xmlStrcmp(localname, (xmlChar *)"way") == 0) {
		struct a_tag *tag;

		HASH_FIND_STR(way->tags, "highway", tag);
		if (tag != NULL) {
			HASH_ADD(hh, ways, id, sizeof(long), way);
		}
		way = NULL;
	}
	if ((HASH_COUNT(nodes) + HASH_COUNT(ways)) % 1000 == 1) {
		fprintf(stderr, "numNodes: %u, numWays: %u\r", HASH_COUNT(nodes), HASH_COUNT(ways));
	}
}

