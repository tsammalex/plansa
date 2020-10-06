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


import plansa
from plansa import models
from .util import load_ecoregions, get_vernacular_names


def iteritems(cldf, t, *cols):
    cmap = {cldf[t, col].name: col for col in cols}
    for item in cldf[t]:
        for k, v in cmap.items():
            item[v] = item[k]
        yield item


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


    contrib = data.add(
        common.Contribution,
        None,
        id='cldf',
        name=args.cldf.properties.get('dc:title'),
        description=args.cldf.properties.get('dc:bibliographicCitation'),
    )

    for lang in iteritems(args.cldf, 'LanguageTable', 'id', 'glottocode', 'name', 'latitude', 'longitude'):
        data.add(
            models.Variety,
            lang['id'],
            id=lang['id'],
            name=lang['name'],
            latitude=lang['latitude'],
            longitude=lang['longitude'],
            glottocode=lang['glottocode'],
        )

    for rec in bibtex.Database.from_file(args.cldf.bibpath, lowercase=True):
        data.add(common.Source, rec.id, _obj=bibtex2source(rec))

    refs = collections.defaultdict(list)

    params = {}
    for param in iteritems(args.cldf, 'ParameterTable', 'id', 'concepticonReference', 'name'):
        if (not param['GBIF_ID']) or param['GBIF_ID'] == '-':
            continue
        p = params.get(param['GBIF_ID'])
        if p:
            data['Taxon'][param['id']] = p
        else:
            vnames = get_vernacular_names(param['GBIF_ID'], param['rank'])
            params[param['GBIF_ID']] = data.add(
                models.Taxon,
                param['id'],
                id=param['GBIF_ID'],
                name=param['canonicalName'],
                description=param['GBIF_NAME'],
                name_english=vnames.get('eng'),
                name_spanish=vnames.get('spa'),
                name_portuguese=vnames.get('por'),
                **{k: int(v or 0) if k.endswith('Key') else v
                   for k, v in param.items() if any(k.startswith(s) for s in 'kingdom phylum class order genus family'.split())},
            )
    for form in iteritems(args.cldf, 'FormTable', 'id', 'form', 'languageReference', 'parameterReference', 'source'):
        if form['parameterReference'] not in data['Taxon']:
            continue
        vsid = (form['languageReference'], form['parameterReference'])
        vs = data['ValueSet'].get(vsid)
        if not vs:
            vs = data.add(
                common.ValueSet,
                vsid,
                id='-'.join(vsid),
                language=data['Variety'][form['languageReference']],
                parameter=data['Taxon'][form['parameterReference']],
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
    load_ecoregions(data)


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """
