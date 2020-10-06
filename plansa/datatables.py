from sqlalchemy.orm import joinedload
from clld.db.util import get_distinct_values
from clld.db.models import common
from clld.web import datatables
from clld.web.datatables.base import LinkCol, Col, LinkToMapCol
from clld.web.datatables.parameter import Parameters
from clld.web.datatables.value import Values, ValueNameCol

from clld_glottologfamily_plugin.models import Family
from clld_glottologfamily_plugin.datatables import FamilyCol


from plansa import models


class Languages(datatables.Languages):
    def base_query(self, query):
        return query.join(Family).options(joinedload(models.Variety.family)).distinct()

    def col_defs(self):
        return [
            LinkCol(self, 'name'),
            FamilyCol(self, 'Family', models.Variety),
            Col(self,
                'latitude',
                sDescription='<small>The geographic latitude</small>'),
            Col(self,
                'longitude',
                sDescription='<small>The geographic longitude</small>'),
            LinkToMapCol(self, 'm'),
        ]


class Taxa(Parameters):
    def col_defs(self):
        res = [
            LinkCol(self, 'name'),
            Col(self, 'english', model_col=models.Taxon.name_english),
        ]
        for label, col in [
            ('kingdom', models.Taxon.kingdom),
            ('phylum', models.Taxon.phylum),
            ('class', models.Taxon.class_),
            ('order', models.Taxon.order),
            ('family', models.Taxon.family),
            #('genus', models.Taxon.genus),
        ]:
            res.append(Col(self, label, model_col=col, choices=get_distinct_values(col)))
        return res


class Names(Values):
    def col_defs(self):
        if self.language:
            return [
                ValueNameCol(self, 'value'),
                LinkCol(self,
                        'parameter',
                        sTitle='Scientific name',
                        model_col=common.Parameter.name,
                        get_object=lambda i: i.valueset.parameter),
                Col(self,
                    'english',
                    model_col=models.Taxon.name_english,
                    get_object=lambda i: i.valueset.parameter),
                Col(self,
                    'spanish',
                    model_col=models.Taxon.name_spanish,
                    get_object=lambda i: i.valueset.parameter),
                Col(self,
                    'portuguese',
                    model_col=models.Taxon.name_portuguese,
                    get_object=lambda i: i.valueset.parameter),
            ]
        return Values.col_defs(self)


def includeme(config):
    config.register_datatable('values', Names)
    config.register_datatable('parameters', Taxa)
    config.register_datatable('languages', Languages)
