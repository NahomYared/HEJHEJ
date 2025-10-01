import webbrowser, os, json
from textwrap import dedent

COUNTRY_CITIES = {
    "Andorra": ["Andorra la Vella", "Escaldes-Engordany", "Encamp"],
    "Albania": ["Tirana", "Durrës", "Vlorë"],
    "Austria": ["Vienna", "Graz", "Linz"],
    "Åland Islands": ["Mariehamn", "Jomala", "Finström"],
    "Bosnia and Herzegovina": ["Sarajevo", "Banja Luka", "Tuzla"],
    "Belgium": ["Brussels", "Antwerp", "Ghent"],
    "Bulgaria": ["Sofia", "Plovdiv", "Varna"],
    "Belarus": ["Minsk", "Gomel", "Mogilev"],
    "Switzerland": ["Zurich", "Geneva", "Basel"],
    "Cyprus": ["Nicosia", "Limassol", "Larnaca"],
    "Czech Republic": ["Prague", "Brno", "Ostrava"],
    "Germany": ["Berlin", "Hamburg", "Munich"],
    "Denmark": ["Copenhagen", "Aarhus", "Odense"],
    "Estonia": ["Tallinn", "Tartu", "Narva"],
    "Spain": ["Madrid", "Barcelona", "Valencia"],
    "Finland": ["Helsinki", "Espoo", "Tampere"],
    "Faroe Islands": ["Tórshavn", "Klaksvík", "Runavík"],
    "France": ["Paris", "Marseille", "Lyon"],
    "United Kingdom": ["London", "Birmingham", "Manchester"],
    "Guernsey": ["St Peter Port", "St Sampson", "Castel"],
    "Greece": ["Athens", "Thessaloniki", "Patras"],
    "Croatia": ["Zagreb", "Split", "Rijeka"],
    "Hungary": ["Budapest", "Debrecen", "Szeged"],
    "Ireland": ["Dublin", "Cork", "Limerick"],
    "Isle of Man": ["Douglas", "Onchan", "Ramsey"],
    "Iceland": ["Reykjavik", "Kopavogur", "Hafnarfjordur"],
    "Italy": ["Rome", "Milan", "Naples"],
    "Jersey": ["Saint Helier", "Saint Saviour", "St Brelade"],
    "Liechtenstein": ["Schaan", "Vaduz", "Balzers"],
    "Lithuania": ["Vilnius", "Kaunas", "Klaipėda"],
    "Luxembourg": ["Luxembourg City", "Esch-sur-Alzette", "Differdange"],
    "Latvia": ["Riga", "Daugavpils", "Liepaja"],
    "Monaco": ["Monaco-Ville", "Monte Carlo", "La Condamine"],
    "Moldova, Republic of": ["Chișinău", "Tiraspol", "Bălți"],
    "Macedonia, The Former Yugoslav Republic of": ["Skopje", "Bitola", "Kumanovo"],
    "Malta": ["Birkirkara", "Mosta", "Qormi"],
    "Netherlands": ["Amsterdam", "Rotterdam", "The Hague"],
    "Norway": ["Oslo", "Bergen", "Stavanger"],
    "Poland": ["Warsaw", "Krakow", "Łódź"],
    "Portugal": ["Lisbon", "Porto", "Vila Nova de Gaia"],
    "Romania": ["Bucharest", "Cluj-Napoca", "Timișoara"],
    "Russian Federation": ["Moscow", "Saint Petersburg", "Novosibirsk"],
    "Sweden": ["Stockholm", "Gothenburg", "Malmö"],
    "Slovenia": ["Ljubljana", "Maribor", "Celje"],
    "Svalbard and Jan Mayen": ["Longyearbyen", "Barentsburg", "Ny-Ålesund"],
    "Slovakia": ["Bratislava", "Košice", "Prešov"],
    "San Marino": ["Serravalle", "Borgo Maggiore", "San Marino"],
    "Ukraine": ["Kyiv", "Kharkiv", "Odesa"],
    "Holy See (Vatican City State)": ["Vatican City"]
}

COUNTRY_ANCHORS = {
    "Andorra": [42.5078, 1.5211],
    "Albania": [41.3275, 19.8187],
    "Austria": [48.2082, 16.3738],
    "Åland Islands": [60.0973, 19.9348],
    "Bosnia and Herzegovina": [43.8563, 18.4131],
    "Belgium": [50.8503, 4.3517],
    "Bulgaria": [42.6977, 23.3219],
    "Belarus": [53.9045, 27.5615],
    "Switzerland": [46.9480, 7.4474],
    "Cyprus": [35.1856, 33.3823],
    "Czech Republic": [50.0755, 14.4378],
    "Germany": [52.5200, 13.4050],
    "Denmark": [55.6761, 12.5683],
    "Estonia": [59.4370, 24.7536],
    "Spain": [40.4168, -3.7038],
    "Finland": [60.1699, 24.9384],
    "Faroe Islands": [62.0079, -6.7900],
    "France": [48.8566, 2.3522],
    "United Kingdom": [51.5074, -0.1278],
    "Guernsey": [49.4550, -2.5369],
    "Greece": [37.9838, 23.7275],
    "Croatia": [45.8150, 15.9819],
    "Hungary": [47.4979, 19.0402],
    "Ireland": [53.3498, -6.2603],
    "Isle of Man": [54.1523, -4.4861],
    "Iceland": [64.1466, -21.9426],
    "Italy": [41.9028, 12.4964],
    "Jersey": [49.1865, -2.1065],
    "Liechtenstein": [47.1415, 9.5215],
    "Lithuania": [54.6872, 25.2797],
    "Luxembourg": [49.6116, 6.1319],
    "Latvia": [56.9496, 24.1052],
    "Monaco": [43.7384, 7.4246],
    "Moldova, Republic of": [47.0105, 28.8638],
    "Macedonia, The Former Yugoslav Republic of": [41.9973, 21.4280],
    "Malta": [35.8989, 14.5146],
    "Netherlands": [52.3676, 4.9041],
    "Norway": [59.9139, 10.7522],
    "Poland": [52.2297, 21.0122],
    "Portugal": [38.7223, -9.1393],
    "Romania": [44.4268, 26.1025],
    "Russian Federation": [55.7558, 37.6173],
    "Sweden": [59.3293, 18.0686],
    "Slovenia": [46.0569, 14.5058],
    "Svalbard and Jan Mayen": [78.2232, 15.6469],
    "Slovakia": [48.1486, 17.1077],
    "San Marino": [43.9356, 12.4473],
    "Ukraine": [50.4501, 30.5234],
    "Holy See (Vatican City State)": [41.9029, 12.4534]
}

COUNTRY_CITIES_JS = json.dumps(COUNTRY_CITIES, ensure_ascii=False)
COUNTRY_ANCHORS_JS = json.dumps(COUNTRY_ANCHORS, ensure_ascii=False)

html = dedent(f"""
<!doctype html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Europa – länder & topp-3 städer</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css">
<style>
  html, body {{ height:100%; margin:0; }}
  #map {{ height:100vh; width:100vw; background:#eef2f5; }}
  .panel {{
    position:absolute; top:8px; left:8px; z-index:1000;
    background:#fff; border:1px solid #ddd; border-radius:8px;
    padding:10px 12px; box-shadow:0 2px 10px rgba(0,0,0,.08);
    max-width:320px; font-family:system-ui, sans-serif;
  }}
  .panel h3 {{ margin:0 0 6px; }}
  .leaflet-popup-content button {{
    margin:4px 2px; padding:6px 8px; border:1px solid #888;
    border-radius:6px; background:#f7f7f7; cursor:pointer;
  }}
  #err {{ position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
    background:#fff3cd; color:#533f03; padding:10px 12px; border:1px solid #ffeeba; border-radius:6px; display:none; }}
</style>
</head>
<body>
<div id="map"></div>
<div class="panel">
  <h3>Europa – länder & topp-3 städer</h3>
  <small>Klicka en land-markör (vid huvudstaden). Välj stad i popup → markör & zoom.</small>
</div>
<div id="err">Kartan kunde inte laddas (Leaflet blockerades). Prova att stänga adblock/VPN eller öppna filen i en annan webbläsare.</div>

<script>
  window.COUNTRY_CITIES = {COUNTRY_CITIES_JS};
  window.COUNTRY_ANCHORS = {COUNTRY_ANCHORS_JS};
</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
<script>
(function () {{
  if (typeof L === 'undefined') {{
    document.getElementById('err').style.display = 'block';
    return;
  }}
  const map = L.map('map', {{ center:[55,15], zoom:4, worldCopyJump:true }});
  L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    maxZoom: 18,
    attribution: '&copy; OpenStreetMap'
  }}).addTo(map);

  async function geocode(q) {{
    const url = 'https://nominatim.openstreetmap.org/search?format=json&q=' + encodeURIComponent(q);
    try {{
      const res = await fetch(url, {{ headers:{{'Accept-Language':'en'}} }});
      if (!res.ok) return null;
      const data = await res.json();
      return (Array.isArray(data) && data.length) ? {{
        lat: +data[0].lat, lon: +data[0].lon, disp: data[0].display_name
      }} : null;
    }} catch(e) {{ return null; }}
  }}

  function addCityMarker(country, city) {{
    const q = country==="Russian Federation" ? city+", Russia"
            : country==="Czech Republic" ? city+", Czechia"
            : country==="Macedonia, The Former Yugoslav Republic of" ? city+", North Macedonia"
            : country==="Holy See (Vatican City State)" ? "Vatican City"
            : city + ", " + country;
    geocode(q).then(loc => {{
      if (!loc) return alert("Kunde inte hitta position för: " + city + " ("+country+")");
      const m = L.marker([loc.lat, loc.lon]).addTo(map);
      m.bindPopup(`<b>${{city}}</b><br/><small>${{country}}</small><br/><i>${{loc.disp}}</i>`).openPopup();
      map.setView([loc.lat, loc.lon], 8, {{animate:true}});
    }});
  }}

  function countryPopupHtml(country) {{
    const cities = window.COUNTRY_CITIES[country] || [];
    if (!cities.length) return `<b>${{country}}</b><br/><i>Inga städer i listan.</i>`;
    const btns = cities.map(c => `<button onclick="addCityMarker('${{country}}','${{c.replace(/'/g, "\\'")}}')">${{c}}</button>`).join('');
    return `<b>${{country}}</b><br/>Välj stad:<br/>` + btns;
  }}

  // Exponera funktionen för inline onclick
  window.addCityMarker = addCityMarker;

  Object.entries(window.COUNTRY_ANCHORS).forEach(([country, coord]) => {{
    const m = L.marker(coord).addTo(map);
    m.bindPopup(countryPopupHtml(country));
  }});
}})();
</script>
</body>
</html>
""")

outfile = "eu_cities_map.html"
with open(outfile, "w", encoding="utf-8") as f:
    f.write(html)

webbrowser.open("file://" + os.path.join(os.getcwd(), outfile))
print("Klar:", outfile)
