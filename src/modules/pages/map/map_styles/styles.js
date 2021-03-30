// collections of functions to add appropriate layers on top of mapbox light base map

const layers = {
  zones: {
    sourceDef: {
      url: 'https://tiles.dvrpc.org/data/dvrpc-tim-zones.json',
      type: 'vector',
    },
    layers: {
      hoverFill:  {
        type: 'fill',
        source: 'tim-zones',
        paint: {
          "fill-translate-anchor": "map",
          "fill-color": "rgb(139,178,63)",
          "fill-opacity": 1,
        },
        visibility: "none",
        filter: [
          "==",
          "no",
          ""
        ],
        placement: "waterway-label"
      },
      clickFill:  {
        type: 'fill',
        source: 'tim-zones',
        paint: {
          "fill-translate-anchor": "map",
          "fill-color": "#d8c72e",
          "fill-outline-color": "#f00",
        },
        visibility: "none",
        filter: [
          "==",
          "no",
          ""
        ],
        placement: "waterway-label"
      },
      base:{
        type: 'line',
        source: 'tim-zones',
        paint: {
          'line-width': [
            'interpolate', ['linear'], ['zoom'],
            7, 0.1,
            12, 1
          ],
          'line-color': '#08506d',
          'line-opacity': [
            'interpolate', ['linear'], ['zoom'],
            7, 0.1,
            12, 1
          ],
        },
        visibility: "none",
        placement: "admin-2-boundaries"
      }
    }
  },
  zoneReference: {
    sourceDef: {
      url: 'https://tiles.dvrpc.org/data/dvrpc-tim-zones.json',
      type: 'vector',
    },
    layers: {
      base: {
        type: 'fill',
        source: 'tim-zones',
        paint: {
          "fill-translate-anchor": "map",
          "fill-color": "rgb(255,255,255)",
          "fill-opacity": 0,
        },
        visibility: "none",
        placement: null,
        filter: [
          "!=",
          "no",
          ""
        ]
      },
    }
  },
  muniReference:{
    sourceDef: {
      data: 'https://arcgis.dvrpc.org/portal/rest/services/Boundaries/MunicipalBoundaries/FeatureServer/0/query?where=1=1&outFields=geoid%2Cdvrpc_reg&outsr=4326&f=geojson',
      type: 'geojson',
    },
    layers:{
      base:{
        type: 'fill',
        paint: {
          "fill-translate-anchor": "map",
          "fill-color": "rgb(255,255,255)",
          "fill-opacity": 0,
        },
        visibility: "none",
        placement: null,
        filter: [
          "==",
          "dvrpc_reg",
          "Yes"
        ]
      }
    }
  },
  county: {
    sourceDef: {
      url: 'https://tiles.dvrpc.org/data/dvrpc-municipal.json',
      type: 'vector',
    },
    layers:{
      county: {
        type: 'line',
        source: 'county',
        paint: {
          "line-color": "#aaa",
          "line-width": 1
        },
        filter: [
          "==",
          "dvrpc",
          "Yes"
        ],
        placement: "admin-2-boundaries"
      }
    }
  },
  boundaries:{
    sourceDef: {
      type: 'geojson',
      data: 'https://arcgis.dvrpc.org/portal/rest/services/Boundaries/MunicipalBoundaries/FeatureServer/0/query?where=1=1&outFields=geoid&outsr=4326&f=geojson',
    },
    layers:{
      muni: {
        type: 'line',
        paint: {
          'line-width': [
            'interpolate', ['linear'], ['zoom'],
            7, 0.1,
            12, 1
          ],
          'line-color': '#08506d',
          'line-opacity': [
            'interpolate', ['linear'], ['zoom'],
            7, 0.1,
            12, 1
          ],
        },
        visibility: "none",
        placement: null
      },
      hover:  {
        type: 'fill',
        paint: {
          "fill-translate-anchor": "map",
          "fill-color": "rgb(139,178,63)",
          "fill-opacity": 1,
        },
        visibility: "none",
        filter: [
          "==",
          "geoid",
          ""
        ],
        placement: "waterway-label"
      },
      click:  {
        type: 'fill',
        paint: {
          "fill-translate-anchor": "map",
          "fill-color": "#d8c72e",
          "fill-outline-color": "#f00",
        },
        visibility: "none",
        filter: [
          "==",
          "geoid",
          ""
        ],
        placement: "waterway-label"
      }
    }
  }
}

export {layers}