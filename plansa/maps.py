from copy import copy

from clld.web.maps import ParameterMap, Map, Legend, Layer, FilterLegend
from clld.web.util.helpers import map_marker_img
from clld.web.util.htmllib import HTML, literal
from clld.db.meta import DBSession
from clld.db.util import as_int

from pytsammalex.clld.models import Biome


OPTIONS = {'show_labels': True, 'icon_size': 20, 'max_zoom': 8}


class EcoregionsMap(Map):
    def get_options(self):
        return {
            'info_route': 'ecoregion_alt',
            'no_showlabels': True,
            'max_zoom': 8,
        }

    def get_layers(self):
        yield Layer(
            'ecoregions',
            'WWF Eco Regions',
            self.req.route_url('ecoregions_alt', ext='geojson'))

    def get_legends(self):
        items = []

        for biome in DBSession.query(Biome)\
                .filter(Biome.description != 'ffffff')\
                .order_by(as_int(Biome.id)):
            items.append(
                HTML.label(
                    HTML.span(
                        literal('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'),
                        style='background-color: #%s;' % biome.description,
                        class_='biome-color'),
                    literal(biome.name),
                    style='margin-left: 1em; margin-right: 1em;'))
        yield Legend(self, 'categories', items)


class TaxonMap(ParameterMap):
    def __init__(self, ctx, req, eid='map', col=None, dt=None):
        Map.__init__(self, ctx, req, eid=eid)
        self.col, self.dt = col, dt

    def get_options(self):
        opts = copy(OPTIONS)
        #opts['height'] = 300
        opts['hash'] = False
        opts['add_layers_to_control'] = True
        opts['exclude_from_zoom'] = ['ecoregions']
        opts['overlays'] = [
            {
                "name": "Occurrences of {} according to GBIF".format(self.ctx),
                "url": "https://api.gbif.org/v2/map/occurrence/density/{z}/{x}/{y}@1x.png?style=classic.poly&bin=hex&hexPerTile=30&taxonKey=" + str(self.ctx.id),
                "options": {"attribution": "Occurrence data from <a href=\"https://www.gbif.org/\">GBIF</a>"},
                }
            ]
        return opts

    def get_layers(self):
        yield Layer(
            'ecoregions',
            'WWF Eco Regions',
            self.req.route_url('ecoregions_alt', ext='geojson'))
        for i, layer in enumerate(ParameterMap.get_layers(self)):
            if i == 0:
                layer.id = 'names'
            yield layer

    def get_legends(self):
        #yield LineageFilter(self, 'TSAMMALEX.getLineage', col=self.col, dt=self.dt)

        for legend in super(TaxonMap, self).get_legends():
            yield legend


def includeme(config):
    for route_name, cls in dict(
        ecoregions=EcoregionsMap,
        parameter=TaxonMap,
    ).items():
        config.register_map(route_name, cls)
