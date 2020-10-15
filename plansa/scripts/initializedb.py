import pathlib
import itertools
import collections

from pycldf import Sources
from clldutils.misc import nfilter
from clldutils.color import qualitative_colors
from clld.cliutil import Data, bibtex2source
from clld.db.meta import DBSession
from clld.db.models import common
from clld.lib import bibtex

from clld_glottologfamily_plugin.util import load_families
from pytsammalex.clld import load


import plansa
from plansa import models
#from .util import load_ecoregions, get_vernacular_names



def main(args):
    assert args.glottolog, 'The --glottolog option is required!'

    data = Data()
    data.add(
        common.Dataset,
        plansa.__name__,
        id=plansa.__name__,
        domain='plansa.clld.org',

        publisher_name="Max Planck Institute for the Science of Human History",
        publisher_place="Jena",
        publisher_url="http://www.shh.mpg.de",
        license="http://creativecommons.org/licenses/by/4.0/",
        jsondata={
            'license_icon': 'cc-by.png',
            'license_name': 'Creative Commons Attribution 4.0 International License'},

    )

    datasets = []
    for ds in load.iter_datasets(
        pathlib.Path(plansa.__file__).parent.parent.parent,
        filter=lambda d: d.properties.get('rdf:ID') is not None
    ):
        #if ds.properties['rdf:ID'] in ['zillcattle', 'tsammalexv1']:
        if ds.properties['rdf:ID'] in ['bridchaco']:
            datasets.append(ds)

    refs = collections.defaultdict(list)
    seen_taxa = set()
    for ds in datasets:
        print('Loading {} ...'.format(ds.properties['rdf:ID']))
        skipped = collections.Counter()
        contrib = data.add(
            common.Contribution,
            None,
            id=ds.properties['rdf:ID'],
            name=ds.properties.get('dc:title'),
            description=ds.properties.get('dc:bibliographicCitation'),
        )

        for lang in ds.iter_rows('LanguageTable', 'id', 'glottocode', 'name', 'latitude', 'longitude'):
            l = data['Variety'].get(lang['id'])
            if not l:
                data.add(
                    models.Variety,
                    lang['id'],
                    id=lang['id'],
                    name=lang['name'],
                    latitude=lang['latitude'],
                    longitude=lang['longitude'],
                    glottocode=lang['glottocode'],
                )

        try:
            for rec in bibtex.Database.from_file(ds.bibpath, lowercase=True):
                data.add(common.Source, rec.id, _obj=bibtex2source(rec))
        except:
            pass


        params = {p['id']: p['GBIF_ID'] for p in ds.iter_rows('ParameterTable', 'id')}
        for param, vnames, taxon in load.iter_taxa(ds, ('eng', 'spa', 'por'), seen=seen_taxa):
            data.add(
                models.Taxon,
                param['GBIF_ID'],
                id=param['GBIF_ID'],
                name=param['canonicalName'] or param['GBIF_NAME'],
                description=param['GBIF_NAME'],
                name_english=vnames.get('eng'),
                name_spanish=vnames.get('spa'),
                name_portuguese=vnames.get('por'),
                **taxon                
            )

        for form in ds.iter_rows('FormTable', 'id', 'form', 'languageReference', 'parameterReference', 'source'):
            if params[form['parameterReference']] not in data['Taxon']:
                skipped.update([form['parameterReference']])
                continue
            vsid = (form['languageReference'], params[form['parameterReference']])
            vs = data['ValueSet'].get(vsid)
            if not vs:
                vs = data.add(
                    common.ValueSet,
                    vsid,
                    id='-'.join(vsid),
                    language=data['Variety'][form['languageReference']],
                    parameter=data['Taxon'][params[form['parameterReference']]],
                    contribution=contrib,
                )
            for ref in form.get('source', []):
                sid, pages = Sources.parse(ref)
                refs[(vsid, sid)].append(pages)
            data.add(
                common.Value,
                form['id'],
                id=form['id'],
                name=form['form'],
                valueset=vs,
            )
        for k, v in skipped.most_common():
            print('skipped {} names for {}'.format(v, k))

    for (vsid, sid), pages in refs.items():
        DBSession.add(common.ValueSetReference(
            valueset=data['ValueSet'][vsid],
            source=data['Source'][sid],
            description='; '.join(nfilter(pages))
        ))
    load_families(
        Data(),
        [(l.glottocode, l) for l in data['Variety'].values()],
        glottolog_repos=args.glottolog,
        isolates_icon='tcccccc',
        strict=False,
    )
    load.load_ecoregions(filter=lambda eco_code, props: eco_code.startswith('NT'))


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """
