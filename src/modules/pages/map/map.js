import '../../../css/pages/map/map.css'
import { geography } from './sidebar/queryInput/queryInput.js'
import { layers } from './map_styles/styles.js'
import { Sidebar } from "./sidebar/sidebar.js"
import { ResultsSummary } from './sidebar/resultsSummary';
import { LoadLayers, addRailLayers } from '../../../utils/loadMapLayers.js'
import { CreateDvrpcNavControl } from '../../../utils/defaultExtentControl';

// adjust zoom level on mobile
let mobileZoom;
const windowWidth = window.innerWidth
if(windowWidth <= 420) mobileZoom = 7.3

const extent = {
  center: [-75.234, 40.061],
  zoom: mobileZoom || 8.4
}

/* BuildMap() -- rbeatty
    @desc: Build the map that the page lands on
    @params:
        NONE
    @returns: returns a map reference object that can be used throughout component
*/
const BuildMap = () => {
    // grab/create relevant HTML elements
    const appBody = document.querySelector('.gap'),
        mapBody = document.createElement('div')
    mapBody.className = "map__container"
    appBody.appendChild(mapBody);
    mapboxgl.accessToken = 'pk.eyJ1IjoiYmVhdHR5cmUxIiwiYSI6ImNqOGFpY3o0cTAzcXoycXE4ZTg3d3g5ZGUifQ.VHOvVoTgZ5cRko0NanhtwA';
    // initiate map
    let map = new mapboxgl.Map({
        container: mapBody,
        style: 'mapbox://styles/beattyre1/cjdbtddl12scq2st5zybjm8r6',
        center: extent.center,
        zoom: extent.zoom
    })

    map.on('load', e=>{
        map.resize();
        map.flyTo({
            center: extent.center,
            zoom: extent.zoom
        })
        LoadBusLayer(map)
        LoadLayers(map, layers)
        addRailLayers(map)
        CreateDvrpcNavControl(extent, map)
    })
    return map
}



/* zoneSelection(target, output) -- rbeatty
    @desc: Grab the zones based on user interaction (click) that should be passed to API query
    @params:
        *!~ target: object return by click event, used to grab the zone number based on user interaction
        *!~ output: object returned by this function that will be based to the API query 
*/
const zoneSelection = (target, output) => {
    let zone = target.features[0].properties['no'],
        selection = output.selection,
        index = selection.indexOf(zone);
    // if value is already in array, remove it, otherwise add it
    index != -1 ? selection.splice(index, 1) : selection.push(zone);
    return selection;
}
const LoadRegionalSummary = map =>{
    const SummaryLayerToggle = event =>{
        let header = event.target,
            tabName = header.getAttribute('data-type'),
            otherLayers = ['zones-analysis', 'zones-clickFill', 'boundaries-click']
                
        if(tabName != 'summary') {
            otherLayers.map(layer=>{
                if (map.getLayer(layer)) map.setLayoutProperty(layer, 'visibility', 'visible')
            })
            map.setLayoutProperty('zones-summary', 'visibility', 'none')
        }
        else{
            otherLayers.map(layer=>{
                if (map.getLayer(layer)) map.setLayoutProperty(layer, 'visibility', 'none')
            })
            map.setLayoutProperty('zones-summary', 'visibility', 'visible')
        }
    }
    let helper = {
        colorScheme: {
            1: "rgba(250,228,205, .4)",
            2: "rgba(245,206,164, .4)",
            3: "rgba(237,165,89, .4)",
            4: "rgba(232,146,50, .6)",
            5: "rgba(186,134,78, .9)",
            6: "rgba(141,115,85, .9)",
            7: "rgba(181,223,209, .1)",
            8: "rgba(144,209,190, .2)",
            9: "rgba(44,185,154, .3)",
            10: "rgba(89,159,140, .3)",
            11: "rgba(93,128,120, .3)",
            12: "rgba(79,82,90, 1)",
            13: "rgba(0,0,0,0)"
        },
        fillExpression: ["match", ["get", "no"]],
        check: {},
        layer: {}
    }
    fetch('https://alpha.dvrpc.org/api/rtps/gap?summary')
    .then(cargo=> { if (cargo.ok) return cargo.json()})
    .then(data=>{
        let layerDef = {
            id: 'zones-summary',
            source: 'zones',
            type: 'fill',
            'source-layer': 'tim-zones',
            paint: {
                'fill-opacity': 1
            },
            layout: {
                visibility: 'visible'
            }
        }
        for (let zone in data.cargo){
            if (!helper.check[zone]){
                // create fill expression item for zones that don't already have one
                helper.fillExpression.push(parseInt(zone), helper.colorScheme[data.cargo[zone]])
                helper.check[zone] = zone
            }
        }
        helper.fillExpression.push("rgba(0,0,0,0)")
        layerDef.paint['fill-color'] = helper.fillExpression
        return layerDef
    })
    .then(layer=>{
        map.addLayer(layer, 'zones-base')
    })
    let headers = document.querySelectorAll('.map__sidebar-menuHeader')
    for (let tab of headers){
        tab.onclick = e=> SummaryLayerToggle(e)
    }
}
/* ProcessData(data, helper) -- rbeatty
    @desc: Iterate through API query return and create mapbox gl layer definition object that will be used to add and style the analysis layer for display 
    @params: 
        *!~ data: raw API json that needs to be cleaned for use
        *!~ helper: Object to be used as a helper reference to build the paint property for the layer definition 
    @returns:
        *!~ layerDef: Layer definition object that contains information specified in mapbox gl documentation that will be passed to map.addLayer() to symbolize analysis
*/
const ProcessData = (data, helper) => {
    Object.keys(data).forEach(item => {
        if (!helper.check[item]) {
            const val = data[item]

            // create fill expression item for zones that don't already have one
            helper.fillExpression.push(parseInt(item), helper.colorScheme[val])
            helper.check[item] = item
        }
    })

    helper.fillExpression.push("rgba(0,0,0,0)") // default color (nothing)

    let layerDef = {
        "id": `zones-analysis`,
        "type": "fill",
        "source": "zones",
        "source-layer": "tim-zones",
        "paint": {
            "fill-color": helper.fillExpression, // big long match expression
            "fill-opacity": 0.75
        }
    }

    return layerDef
}

/* PerformQuery(selection) -- rbeatty
    @desc: Make API call and parse it into a json that will be processed to create the symbology for the analysis layer
    @params:
        *!~ selection: array containing zone no. to be used in the API call
    @returns:
        *!~ helpers: object that contains layer definition
*/
const PerformQuery = async input => {
    let helpers = {
        colorScheme: {
            1: "rgba(250,228,205, .4)",
            2: "rgba(245,206,164, .4)",
            3: "rgba(237,165,89, .4)",
            4: "rgba(232,146,50, .6)",
            5: "rgba(186,134,78, .9)",
            6: "rgba(141,115,85, .9)",
            7: "rgba(181,223,209, .1)",
            8: "rgba(144,209,190, .2)",
            9: "rgba(44,185,154, .3)",
            10: "rgba(89,159,140, .3)",
            11: "rgba(93,128,120, .3)",
            12: "rgba(79,82,90, 1)",
            13: "rgba(0,0,0,0)"
        },
        fillExpression: ["match", ["get", "no"]],
        check: {},
        analysisLayers: {}
    }
    input.direction == 'To' ? input.direction = 'To Zone' : input.direction = 'From Zone'
    let fetchData = input.type === 'zone' ?
        await fetch(`https://alpha.dvrpc.org/api/rtps/gap?zones=[${input.selection}]&direction=${input.direction}`) :
        await fetch(`https://alpha.dvrpc.org/api/rtps/gap?muni=${input.selection}&direction=${input.direction}`)

    if (fetchData.ok) {
        let rawData = await fetchData.json()    
        const cargo = rawData.cargo
        const demandScore = rawData.demandScore ? rawData.demandScore[0].toLocaleString() : null

        if (rawData.status == 'success'){
            helpers.analysisLayers= ProcessData(cargo, helpers) // process data

            new ResultsSummary(input, rawData.cargo, demandScore)
        }
        else{
            alert(`Error! ${rawData.message}`)
        }
    }
    return helpers.analysisLayers
}

/* ClearQuery(map) -- rbeatty
    @desc: Return map to base state and remove any zone selections
    @params:
        *!~ map: Map reference object returned by BuildMap():L158
    @returns: NONE
*/
const ClearQuery = map => {

    // reset zone selection
    map.setFilter('zones-clickFill', ["==", "no", ""])
    map.setPaintProperty('zones-clickFill', "fill-color", "#d8c72e")
    map.setFilter('zones-base', undefined)

    // reset muni selection
    map.setFilter('boundaries-muni', undefined)
    map.setFilter('boundaries-click', ['==', 'geoid', ''])
    map.setPaintProperty('boundaries-click', 'fill-color', '#d8c72e')

    // remove analysis layer
    if (map.getLayer('zones-analysis')) {
        map.removeLayer('zones-analysis')
    }

    let queryContainer = document.querySelector('.sidebar__input-dropdowns')
    // reset query inputs
    for (let key in geography){
        queryContainer.setAttribute(`data-${key}`, '')
        geography[key] = undefined
    }
    // mute colors of buttons
    let buttons = document.querySelectorAll('.input__query-button')
    for (let btn of buttons){
        if (btn.classList.contains('active')){ 
            btn.classList.remove('active')
        } 
    }

    // reset dropdowns to default option
    let inputs = document.querySelectorAll('.input__query-input')
    for (let option of inputs){
        option.selectedIndex = 0
    }

    ['boundaries-muni', 'muniReference-base', 'zoneReference-base', 'zones-base'].forEach(layer=>{
        map.setLayoutProperty(layer, 'visibility', 'none')
    })

    // clear results summary
    document.querySelector('#gap__results-section').innerHTML = 'Please perform an analysis query to populate this area with results.'
}

/* AddListeners(map) -- rbeatty
    @desc: Add collection of listeners for the map for interactivity
    @params:
        *!~ map: Map reference object returned by BuildMap():L158
    @returns: NONE
*/
const AddListeners = map => {
    let popup = new mapboxgl.Popup({
        anchor: 'bottom',
        closeButton: false,
        closeOnClick: true,
        offset: {
            'top': [0, 0],
            'top-left': [0,0],
            'top-right': [0,0],
            'bottom': [0, -5],
            'bottom-left': [0, 0],
            'bottom-right': [0, 0],
            'left': [0, 0],
            'right': [0, 0]
          }
    });

    // @UPDATE - add geoid back to endpoint
    const GeneratePopup = (popup, e) =>{
      let muni = document.querySelector(`.input__input-option[value="${e.features[0].properties.geoid}"]`).innerText
      popup.setLngLat(e.lngLat)
      .setHTML(muni)
      .addTo(map)
    }

// ZONE LISTENERS
    // hover => green fill
    map.on('mousemove', "zoneReference-base", (e) => {
        map.getCanvas().style.cursor = 'pointer'
        map.setFilter("zones-hoverFill", ["==", "no", e.features[0].properties.no])
    })
    // leave hover => no fill
    map.on('mouseleave', "zoneReference-base", (e) => {
        map.getCanvas().style.cursor = ''
        map.setFilter("zones-hoverFill", ["==", "no", ""]);
    })

    // click => yellow fill
    map.on('click', "zoneReference-base", (e) => {
        if (geography && geography.type == 'zone') {
            var filtered = zoneSelection(e, geography)
            filtered.length != 0 ? map.setFilter('zones-clickFill', ['match', ['get', 'no'], filtered, true, false]) : map.setFilter('zones-clickFill', ['==', 'no', '']);
            let buttons = document.querySelectorAll('.input__query-button')
            
            for (let btn of buttons){
                btn.classList.contains('active') ? null : btn.classList.add('active')
            }
        }
        else { alert('Select a geography before continuing!') }
    })

// MUNI LISTENERS
    // hover => green fill
    map.on('mousemove', "muniReference-base", (e) => {
        let feature = e.features[0]

        map.getCanvas().style.cursor = 'pointer'
        map.setFilter("boundaries-hover", ["==", "geoid", feature.properties.geoid])
        GeneratePopup(popup, e)
    })
    // leave hover => no fill
    map.on('mouseleave', "muniReference-base", (e) => {
        map.getCanvas().style.cursor = ''
        map.setFilter("boundaries-hover", ["==", "geoid", ""])
        popup.remove()
    })
    // click => yellow fill
    map.on('click', "muniReference-base", (e) => {
        let geoid = e.features[0].properties.geoid
        document.querySelector('#muni').value = geoid
        geography.selection = geoid
        muni ? map.setFilter('boundaries-click', ['==', 'geoid', geoid]) : null
        let buttons = document.querySelectorAll('.input__query-button')

        if (geography.direction){
            for (let btn of buttons){
                btn.classList.contains('active') ? null : btn.classList.add('active')
            }
        }
        document.querySelector('.sidebar__input-dropdowns').setAttribute('data-selection', geoid)
    })

    // perform query
    document.querySelector('#execute').addEventListener('click', e => {
        e.preventDefault()

        // if exists, remove
        if (map.getLayer('zones-analysis')) {
            map.removeLayer('zones-analysis')
        }
        let spinner = document.querySelector(".map__spinner")
        spinner.style.display = 'block';

        PerformQuery(geography).then(x => {
            map.addLayer(x, "zones-base")
            spinner.style.display = 'none'
            
            // resymbolize other layers for aesthetics
            if (geography.type == 'zone'){
                map.setLayoutProperty('zones-hoverFill', 'visibility', 'none')
                map.setPaintProperty("zones-clickFill", "fill-color", "red")
                map.setFilter("zones-base", ['==', 'no', ''])
            }
            else{
                map.setLayoutProperty('boundaries-hover', 'visibility', 'none')
                map.setPaintProperty("boundaries-click", "fill-color", "red")
                map.setFilter('boundaries-muni', ['==', 'geoid', geography.selection])
            }
        })
    })

    // clear query
    document.querySelector('#clear').addEventListener('click', () => {
        geography.type == 'zone' ? geography.selection = new Array() : undefined
        ClearQuery(map)
    })

    document.querySelector('#muni').addEventListener('change', e => {
        let geoid = e.target.value
        map.getLayer('boundaries-click') ? map.setFilter('boundaries-click', ['==', 'geoid', geoid]) : null
    })

    document.querySelector('#geography').addEventListener('change', e=>{
        let geom = e.target.value
        let layers = {
            zone: ['zoneReference-base','zones-base', 'zones-hoverFill', 'zones-clickFill'],
            muni: ['muniReference-base', 'boundaries-muni', 'boundaries-hover', 'boundaries-click']
        }
        if (geom == 'Zone'){
            layers.zone.map(item=>{
                map.setLayoutProperty(item, 'visibility', 'visible')
            })
            layers.muni.map(item=>{
                map.getLayoutProperty(item, 'visibility') != 'none' ?  map.setLayoutProperty(item, 'visibility', 'none') : null
            })
        }
        else{
            layers.muni.map(item=>{
                map.setLayoutProperty(item, 'visibility', 'visible')
            })
            layers.zone.forEach(item=>{
                map.getLayoutProperty(item, 'visibility') != 'none' ?  map.setLayoutProperty(item, 'visibility', 'none') : null
            })
        }
    })
}

const AddLoadingSpinner = (target) =>{
    let container = document.createElement('div')
    container.classList = 'map__spinner'
    target._container.appendChild(container)
}

const LoadBusLayer = map =>{
    map.addSource("transit", {
      type: "vector",
      url: "https://tiles.dvrpc.org/data/dvrpc-tim-transit.json"
    });
    
    fetch("https://alpha.dvrpc.org/api/rtps/frequency?bus")
    .then(
        response =>
        response.ok ? response.json() : console.error("error, will robinson")
    )
    .then(bus => {
        let filterExp = ['any']
        bus.cargo.map(line=>{
            let exp = ['match', ['get', 'linename'], line.linename, true, false]
            filterExp.push(exp)
        })
        let layerDef = {
            id : 'bus-lines',
            source: 'transit',
            "source-layer": 'transit_lines',
            type: 'line',
            filter: filterExp,
            paint: {
              "line-width" : [
                "interpolate",
                ["linear"],
                ["zoom"],
                9,
                .05,
                12,
                3
              ],
              "line-color" : '#8bb23f'
            },
            layout:{
                visibility: 'none'
            }
          }

          map.addLayer(layerDef, 'admin-2-boundaries')
    });

}

class Map {
    constructor() {
        this.render()
    }

    render() {
        let appPage = document.querySelector('main')
        appPage.id = 'gap'
        let gap = document.createElement('div')
        gap.classList = 'gap'
        appPage.appendChild(gap)
        let map = BuildMap()
        AddLoadingSpinner(map)
        map.on('load', _ => {
            if (!document.querySelector('aside')) new Sidebar(this)
            else {
                gap.removeChild(document.querySelector('aside'))
                new Sidebar(this)
            }
            AddListeners(map)
            LoadRegionalSummary(map)
        });
        this.map = map
    }
}


export { Map };