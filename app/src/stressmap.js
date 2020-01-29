var urlParams = new URLSearchParams(window.location.search);

var town = urlParams.get('town');
var lts = urlParams.get('lts');
var map;

if (town == 'neuss') {
	map = L.map('mapid').setView([51.1762, 6.7066], 12)
} else if (town == 'neuss-small') {
	map = L.map('mapid').setView([51.2, 6.69], 13)
} else if (town == 'darmstadt') {
	map = L.map('mapid').setView([49.8730, 8.60], 11)
} else if (town == 'duesseldorf') {
	map = L.map('mapid').setView([51.4831, 6.6028], 9)
} else if (town == 'duesseldorf-small') {
	map = L.map('mapid').setView([51.23, 6.8], 13)
} else if (town == 'koeln') {
	map = L.map('mapid').setView([50.9976, 6.8409], 9)
} else if (town == 'hamburg') {
	map = L.map('mapid').setView([53.5586, 10.0785], 10)
} else if (town == 'hessen') {
	map = L.map('mapid').setView([53.5586, 10.0785], 10)
} else if (town == 'niedersachsen') {
	map = L.map('mapid').setView([53.5586, 10.0785], 10)
} else if (town == 'rheinland-pfalz') {
	map = L.map('mapid').setView([53.5586, 10.0785], 10)
} else {
        town = 'berlin'
	map = L.map('mapid').setView([52.5173, 13.3889], 10)
}

const ltsSettings = [

{ color: '#FF7777', weight: 2, key: 'LTS0', zIndex: 11, title: 'LTS 0 - Biking not permitted', url: 'data/' + town + '/level_0.json' },
{ color: '#0099cc', weight: 2, key: 'LTS1', zIndex: 12, title: 'LTS 1 - Suitable for Children', url: 'data/' + town + '/level_1.json' },
{ color: '#1C7C54', weight: 2, key: 'LTS2', zIndex: 13, title: 'LTS 2 - Low Stress', url: 'data/' + town + '/level_2.json' },
{ color: '#F0C808', weight: 2, key: 'LTS3', zIndex: 14, title: 'LTS 3 - Moderate Stress', url: 'data/' + town + '/level_3.json' },
{ color: '#DD5454', weight: 2, key: 'LTS4', zIndex: 15, title: 'LTS 4 - High Stress', url: 'data/' + town + '/level_4.json' }
]
const settings = [
{ color: '#FF0000', weight: 4, key: 'Q0', zIndex: 1, title: '0xx - No Biking Permitted', url: 'data/' + town + '/quality_0.json' }
,{ color: '#00FF00', weight: 4, key: 'Q1', zIndex: 2, title: '1xx - Biking on Streets', url: 'data/' + town + '/quality_1.json' }
,{ color: '#FFFF00', weight: 4, key: 'Q2', zIndex: 3, title: '2xx - Biking on Marked Lanes', url: 'data/' + town + '/quality_2.json' }
,{ color: '#00FFFF', weight: 4, key: 'Q3', zIndex: 4, title: '3xx - Biking on Tracks', url: 'data/' + town + '/quality_3.json' }
,{ color: '#8080FF', weight: 4, key: 'Q4', zIndex: 5, title: '4xx - Biking in Cyclestreet', url: 'data/' + town + '/quality_4.json' }
,{ color: '#0000FF', weight: 4, key: 'Q5', zIndex: 6, title: '5xx - Biking on Separated Infrastructure', url: 'data/' + town + '/quality_5.json' }
//,{ color: '#3333CC', weight: 4, key: 'Q6', zIndex: 7, title: '6xx - Biking very good', url: 'data/' + town + '/quality_6.json' }
,{ color: '#FF00FF', weight: 4, key: 'Q7', zIndex: 8, title: '7xx - Biking on Cycleway', url: 'data/' + town + '/quality_7.json' }
//,{ color: '#66AADD', weight: 4, key: 'Q8', zIndex: 9, title: '8xx - Biking optimal on Earth', url: 'data/' + town + '/quality_8.json' }
//,{ color: '#88CCFF', weight: 4, key: 'Q9', zIndex: 10, title: '9xx - Biking in Heaven', url: 'data/' + town + '/quality_9.json' }
]
const homePage = 'https://ckrey.github.io/stressmap/'
const legendTitle = 'Bicycle Infrastructure Quality Map'
const layers = {}
const tree = rbush.rbush();

addLegend()
addStressLayers()
addIconLayers()


///// Functions ////

function addLegend () {
  const legend = L.control({position: 'topright'})
  legend.onAdd = function (map) {
    const div = L.DomUtil.create('div', 'info legend')
    let legendHtml = '<center><a href="' + homePage + '" target="_blank"><h3>' + legendTitle + '</h3></a></center><table>'
    if (lts == 'yes') {
      for (let setting of ltsSettings) {
        legendHtml += addLegendLine(setting)
      }
    }
    for (let setting of settings) {
      legendHtml += addLegendLine(setting)
    }
    legendHtml += '</table>'
    div.innerHTML = legendHtml
    div.addEventListener('mouseover', function () {map.doubleClickZoom.disable(); });
    div.addEventListener('mouseout', function () {map.doubleClickZoom.enable(); });
    return div
  }
  legend.addTo(map)
}

function addStressLayers () {
  if (lts == 'yes') {
    for (let setting of ltsSettings) {
      addStressLayerToMap(setting)
    }
  }
  for (let setting of settings) {
    addStressLayerToMap(setting)
  }
}

function addStressLayerToMap (setting) {
  const xhr = new XMLHttpRequest()
  xhr.open('GET', setting.url)
  xhr.setRequestHeader('Content-Type', 'application/json')
  xhr.onload = function () {
    if (xhr.status === 200) {
      const data = JSON.parse(xhr.responseText)
      const tileIndex = geojsonvt(data, { maxZoom: 18 })
      tree.load(data)

      const canvasTiles = L.tileLayer.canvas()
      canvasTiles.drawTile = function (canvas, tilePoint, zoom) {
        const tile = tileIndex.getTile(zoom, tilePoint.x, tilePoint.y)
        if (!tile) { return }
        drawFeatures(canvas.getContext('2d'), tile.features, setting.color, setting.weight)
      }
      canvasTiles.addTo(map)
      layers[setting.key] = canvasTiles
    } else {
      alert('Request failed.  Returned status of ' + xhr.status)
    }
  }
  xhr.send()
}

function drawFeatures (ctx, features, lineColor, weight) {
  ctx.strokeStyle = lineColor
  ctx.lineWidth = weight

  for (let feature of features) {
    const type = feature.type
    ctx.fillStyle = feature.tags.color ? feature.tags.color : 'rgba(255,0,0,0.05)'
    ctx.beginPath()
    for (let geom of feature.geometry) {
      const pad = 1
      const ratio = .1
      if (type === 1) {
        ctx.arc(geom[0] * ratio + pad, geom[1] * ratio + pad, 2, 0, 2 * Math.PI, false)
        continue
      }
      for (var k = 0; k < geom.length; k++) {
        var p = geom[k]
        var extent = 4096
        var x = p[0] / extent * 256
        var y = p[1] / extent * 256
        if (k) {
          ctx.lineTo(x + pad, y + pad)
        } else {
          ctx.moveTo(x + pad, y + pad)
        }
      }
    }
    if (type === 3 || type === 1) ctx.fill('evenodd')
    ctx.stroke()
  }
}

function toggleLayer (checkbox) {
  if (checkbox.checked) {
    map.addLayer(layers[checkbox.id])
  } else {
    map.removeLayer(layers[checkbox.id])
  }
}

function addLegendLine (setting) {
  return ('<tr><td><input type="checkbox" id="' +
    setting.key +
    '" onclick="toggleLayer(this)" checked /></td>' +
    '<td><hr style="display:inline-block; width: 50px;" color="' +
    setting.color +
    '" size="5" /></td><td>' +
    setting.title +
    '</td></tr>'
  )
}


function addIconLayers(){

  const providers = [];
  providers.push({
      title: 'osm bw',
      icon: 'img/icons-osm-bw.png',
      layer: L.tileLayer('http://{s}.tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png', {
          maxZoom: 22,
          attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      })
  });
  providers.push({
      title: 'mapnik',
      icon: 'img/icons-mapnik.png',
      layer: L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          maxZoom: 22,
          attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      })
  });


  L.control.iconLayers(providers).addTo(map);

}


function getFeaturesNearby(point, maxMeters, breakOnFirst)
{
  ret = [];
  const pt = turf.helpers.point(point);
  const nearby = tree.search(pt);
  for(let feature of nearby.features){
    if(breakOnFirst && ret.length){return ret;}
    const line = turf.helpers.lineString(feature.geometry.coordinates);
    if(turf.pointToLineDistance(pt, line, {units: 'meters'})<maxMeters){
      ret.push(feature);
    }
  }

  return ret;
}

const qualityLevels = {
        700: "This way is a cycleway because highway='cycleway'.",

        501: "This way is a separated path because highway='path'.",
        502: "footway with cycleway",
        503: "footway with explicit bicycle",

        401: "This way is a cyclestreet because cyclestreet='yes'.",
        402: "This way is a cyclestreet because bicycle_road='yes'.",

        301: "This way is a track because cycleway* is defined as 'track'.",
        302: "This way is a track because cycleway* is defined as 'opposite_track'.",

        201: "This way has a lane because cycleway* is defined as 'lane'.",
        202: "This way has a lane cycleway* is defined as 'opposite_lane'.",

        100: "highway or bicycle in tags",

        1: "Cycling not permitted due to bicycle='no' tag.",
        2: "Cycling not permitted due to access='no' tag.",
        3: "Cycling not permitted due to highway='motorway' tag.",
        4: "Cycling not permitted due to highway='motorway_link' tag.",
        5: "Cycling not permitted due to highway='proposed' tag.",
        6: "Cycling not permitted. When footway='sidewalk' is present, there must be a bicycle='yes' when the highway is 'footway'.",
        7: "Cycling not permitted. When footway='sidewalk' is present, there must be a bicycle='yes' when the highway is 'path'.",
        8: "Cycling not permitted due to highway='construction' tag.",
        9: "footway without explicit cycleway or bicycle",
        10: "Cycling not permitted due to bicycle='use_sidepath' tag.",
        11: "Cycling not permitted due to highway='corridor' tag.",
        12: "Cycling not permitted due to highway='platform' tag.",

	0: "Way has neither a highway tag nor a bicycle=yes tag. The way is not a highway."
}

function displayOsmElementInfo(element, latlng) {

  const xhr = new XMLHttpRequest()
  xhr.open('GET','https://api.openstreetmap.org/api/0.6/'+element.id)
  xhr.onload = function () {
    let popup = '<b><a href="https://www.openstreetmap.org/' + element.id + '" target="_blank">' + element.id + '</a></b><br>quality: ' + element.properties.quality + ' ' + qualityLevels[element.properties.quality] + '<hr>'
    if (xhr.status === 200) {
      const xmlDOM = new DOMParser().parseFromString(xhr.responseText, 'text/xml');
      const tags = xmlDOM.getElementsByTagName("tag");
      for(let i=0; i<tags.length; i++)
      {
        popup += tags[i].attributes["k"].value+": <b>"+tags[i].attributes["v"].value+'</b><br>';
      }
    } else {
      popup += 'Failed to request details from osm.org';
    }
    map.openPopup(popup, latlng);
  }
  xhr.send()
}


let highlight;
let timer;
map.on('mousemove', function(e) {
  const features = getFeaturesNearby([e.latlng.lng,e.latlng.lat], 5, true)
  clearTimeout(timer);
  if (features.length!=0) {
    document.getElementById('mapid').style.cursor = 'pointer'
  }
  else {
    timer = setTimeout(function()
                {
	                 document.getElementById('mapid').style.cursor = ''
                 }, 100);
  }
})

map.on('click', function(e) {
  if (highlight){
    map.removeLayer(highlight)
  }
  const features = getFeaturesNearby([e.latlng.lng,e.latlng.lat], 5, true);
  if (features.length!=0) {
    displayOsmElementInfo(features[0], e.latlng);
    highlight = new L.geoJson(features[0],{style: {color:'#df42f4',  weight: 5}}).addTo(map);
    map.on('popupclose', function() {
     map.removeLayer(highlight)
   });
  }
 });
