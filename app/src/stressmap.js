var urlParams = new URLSearchParams(window.location.search);

var town = urlParams.get('town');
var map;

if (town == 'neuss') {
	map = L.map('mapid').setView([51.1762, 6.7066], 12)
} else if (town == 'darmstadt') {
	map = L.map('mapid').setView([49.8730, 8.5612], 11)
} else if (town == 'duesseldorf') {
	map = L.map('mapid').setView([51.4831, 6.6028], 9)
} else if (town == 'koeln') {
	map = L.map('mapid').setView([50.9976, 6.8409], 9)
} else if (town == 'hamburg') {
	map = L.map('mapid').setView([53.5586, 10.0785], 10)
} else {
        town = 'berlin'
	map = L.map('mapid').setView([52.5173, 13.3889], 10)
}

const settings = [

{ color: '#FF7777', weight: 6, key: 'LTS0', zIndex: 1, title: 'LTS 0 - Biking not permitted', url: 'data/' + town + '/level_0.json' },
{ color: '#0099cc', weight: 6, key: 'LTS1', zIndex: 2, title: 'LTS 1 - Suitable for Children', url: 'data/' + town + '/level_1.json' },
{ color: '#1C7C54', weight: 6, key: 'LTS2', zIndex: 3, title: 'LTS 2 - Low Stress', url: 'data/' + town + '/level_2.json' },
{ color: '#F0C808', weight: 6, key: 'LTS3', zIndex: 4, title: 'LTS 3 - Moderate Stress', url: 'data/' + town + '/level_3.json' },
{ color: '#DD5454', weight: 6, key: 'LTS4', zIndex: 5, title: 'LTS 4 - High Stress', url: 'data/' + town + '/level_4.json' },

{ color: '#FF0000', weight: 2, key: '0', zIndex: 6, title: '0xx - No Biking Permitted', url: 'data/' + town + '/quality_0.json' },
{ color: '#00FF00', weight: 2, key: '1', zIndex: 7, title: '1xx - Biking Possible', url: 'data/' + town + '/quality_1.json' },
{ color: '#0000FF', weight: 2, key: '5', zIndex: 8, title: '5xx - Biking Separated', url: 'data/' + town + '/quality_5.json' }
]
const homePage = 'https://bikeottawa.ca/index.php/advocacy/advocacy-news/213-data_group'
const legendTitle = 'Cycling Stress Map'
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
      title: 'mapnik',
      icon: 'img/icons-mapnik.png',
      layer: L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          maxZoom: 22,
          attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      })
  });

  providers.push({
      title: 'osm bw',
      icon: 'img/icons-osm-bw.png',
      layer: L.tileLayer('http://{s}.tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png', {
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


function displayOsmElementInfo(element, latlng) {

  const xhr = new XMLHttpRequest()
  xhr.open('GET','https://api.openstreetmap.org/api/0.6/'+element)
  xhr.onload = function () {
    let popup = '<b><a href="https://www.openstreetmap.org/' + element + '" target="_blank">' + element + '</a></b><hr>'
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
    displayOsmElementInfo(features[0].id, e.latlng);
    highlight = new L.geoJson(features[0],{style: {color:'#df42f4',  weight: 5}}).addTo(map);
    map.on('popupclose', function() {
     map.removeLayer(highlight)
   });
  }
 });
