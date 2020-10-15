from zope.interface import implementer
from sqlalchemy import (
    Column,
    String,
    Unicode,
    Integer,
    Float,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin
from clld.db.models import common

from clld_glottologfamily_plugin.models import HasFamilyMixin

from pytsammalex.clld.models import TaxonMixin


#-----------------------------------------------------------------------------
# specialized common mapper classes
#-----------------------------------------------------------------------------

@implementer(interfaces.ILanguage)
class Variety(CustomModelMixin, common.Language, HasFamilyMixin):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    glottocode = Column(Unicode)


@implementer(interfaces.IParameter)
class Taxon(CustomModelMixin, common.Parameter, TaxonMixin):
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)

    name_english = Column(Unicode)
    name_spanish = Column(Unicode)
    name_portuguese = Column(Unicode)

    #characteristics = Column(Unicode)
    #biotope = Column(Unicode)
    #general_uses = Column(Unicode)
    #notes = Column(Unicode)

