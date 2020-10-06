import pathlib
import functools
import itertools

from clldutils.jsonlib import load
from clldutils.misc import nfilter

try:
    from pytsammalex.gbif import GBIF
except:
    GBIF = None

import plansa
from plansa.models import Ecoregion, Biome


def get_center(arr):
    return functools.reduce(
        lambda x, y: [x[0] + y[0] / len(arr), x[1] + y[1] / len(arr)], arr, [0.0, 0.0])


def get_vernacular_names(key, rank):
    return GBIF().get_vernacular_names(key, rank=rank, language_tags={'eng', 'por', 'spa'})


def load_ecoregions(data):
    ecoregions = load(pathlib.Path(plansa.__file__).parent / 'static' / 'ecoregions.json')['features']

    biome_map = {
        1: ('Tropical & Subtropical Moist Broadleaf Forests', '008001'),
        2: ('Tropical & Subtropical Dry Broadleaf Forests', '557715'),
        3: ('Tropical & Subtropical Coniferous Forests', ''),
        4: ('Temperate Broadleaf & Mixed Forests', ''),
        5: ('Temperate Conifer Forests', ''),
        6: ('Boreal Forests/Taiga', ''),
        7: ('Tropical & Subtropical Grasslands, Savannas & Shrublands', '98ff66'),
        8: ('Temperate Grasslands, Savannas & Shrublands', ''),
        9: ('Flooded Grasslands & Savannas', '0265fe'),
        10: ('Montane Grasslands & Shrublands', 'cdffcc'),
        11: ('Tundra', ''),
        12: ('Mediterranean Forests, Woodlands & Scrub', 'cc9900'),
        13: ('Deserts & Xeric Shrublands', 'feff99'),
        14: ('Mangroves', '870083'),
    }

    for eco_code, features in itertools.groupby(
            sorted(ecoregions, key=lambda e: e['properties']['eco_code']),
            key=lambda e: e['properties']['eco_code']):
        if not eco_code.startswith('NT'):
            continue
        features = list(features)
        props = features[0]['properties']
        if int(props['BIOME']) not in biome_map:
            continue
        biome = data['Biome'].get(props['BIOME'])
        if not biome:
            name, color = biome_map[int(props['BIOME'])]
            biome = data.add(
                Biome, props['BIOME'],
                id=str(int(props['BIOME'])),
                name=name,
                description=color or 'ffffff')
        centroid = (None, None)
        f = sorted(features, key=lambda _f: _f['properties']['AREA'])[-1]
        if f['geometry']:
            coords = f['geometry']['coordinates'][0]
            if f['geometry']['type'] == 'MultiPolygon':
                coords = coords[0]
            centroid = get_center(coords)

        polygons = nfilter([_f['geometry'] for _f in features])
        data.add(
            Ecoregion, eco_code,
            id=eco_code,
            name=props['ECO_NAME'],
            description=props['G200_REGIO'],
            latitude=centroid[1],
            longitude=centroid[0],
            biome=biome,
            area=props['area_km2'],
            gbl_stat=Ecoregion.gbl_stat_map[int(props['GBL_STAT'])],
            realm=Ecoregion.realm_map[props['REALM']],
            jsondata=dict(polygons=polygons))
