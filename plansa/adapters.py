from clld.web.adapters.geojson import GeoJson
from clld.interfaces import IIndex

from plansa.interfaces import IEcoregion


class GeoJsonEcoregions(GeoJson):
    def featurecollection_properties(self, ctx, req):
        return {'name': "WWF's Terrestrial Ecoregions of the Afrotropics"}

    def get_features(self, ctx, req):
        for ecoregion in ctx.get_query():
            for polygon in ecoregion.jsondata['polygons']:
                yield {
                    'type': 'Feature',
                    'properties': {
                        'id': ecoregion.id,
                        'label': '%s %s' % (ecoregion.id, ecoregion.name),
                        'color': ecoregion.biome.description,
                        'language': {'id': ecoregion.id},
                        'latlng': [ecoregion.latitude, ecoregion.longitude],
                    },
                    'geometry': polygon,
                }


def includeme(config):
    config.register_adapter(GeoJsonEcoregions, IEcoregion, IIndex)
