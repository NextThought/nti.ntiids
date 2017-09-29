#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import raises
from hamcrest import calling
from hamcrest import assert_that
from hamcrest import has_property

from nti.testing.matchers import verifiably_provides

import time
import datetime
from unittest import TestCase

from zope import component
from zope import interface

from nti.ntiids.interfaces import INTIID
from nti.ntiids.interfaces import INTIIDResolver

from nti.ntiids.ntiids import ROOT

from nti.ntiids.ntiids import get_parts
from nti.ntiids.ntiids import hash_ntiid
from nti.ntiids.ntiids import make_ntiid
from nti.ntiids.ntiids import make_provider_safe
from nti.ntiids.ntiids import make_specific_safe
from nti.ntiids.ntiids import validate_ntiid_string
from nti.ntiids.ntiids import find_object_with_ntiid

from nti.ntiids.ntiids import InvalidNTIIDError
from nti.ntiids.ntiids import ImpossibleToMakeSpecificPartSafe

from nti.ntiids.tests import SharedConfiguringTestLayer


class TestNTIIDS(TestCase):

    layer = SharedConfiguringTestLayer

    def test_make_ntiid(self):
        self.assertRaises(ValueError, make_ntiid)
        self.assertRaises(ValueError,
                          make_ntiid,
                          provider=u'foo',
                          specific=u'baz')
        iso_now = datetime.date(*time.gmtime()[:3]).isoformat()

        assert_that(make_ntiid(date=None, nttype=u'Test'),
                    is_('tag:nextthought.com,%s:Test' % iso_now))

        assert_that(make_ntiid(date=0, nttype=u'Test'),
                    is_('tag:nextthought.com,%s:Test' % iso_now))

        assert_that(make_ntiid(date=None, nttype=u'Test', provider=u'TestP'),
                    is_('tag:nextthought.com,%s:TestP-Test' % iso_now))

        assert_that(make_ntiid(date=None, nttype=u'Test', provider=u'TestP', specific=u'Bar'),
                    is_('tag:nextthought.com,%s:TestP-Test-Bar' % iso_now))

        assert_that(make_ntiid(date=None,
                               nttype=u'Test',
                               provider=u'Henry Beach Needham . McClure\u2019s Magazine',
                               specific=u'Bar'),
                    is_('tag:nextthought.com,%s:Henry_Beach_Needham_._McClures_Magazine-Test-Bar' % iso_now))

    def test_parse_ntiid(self):
        ntiid = get_parts(ROOT)
        assert_that(ntiid, verifiably_provides(INTIID))

        ntiid = u'tag:nextthought.com,2011-10:Foo-Bar-With:Many:Colons'
        validate_ntiid_string(ntiid)

        ntiid = get_parts(ntiid)
        assert_that(ntiid, has_property('provider', 'Foo'))
        assert_that(ntiid, has_property('nttype', 'Bar'))
        assert_that(ntiid, has_property('specific', 'With:Many:Colons'))

        with self.assertRaises(InvalidNTIIDError):
            validate_ntiid_string(u'my ünicôdé strįng')

    def test_utc_date(self):
        #"A timestamp should always be interpreted UTC."
        # This date is 2012-01-05 in UTC, but 2012-01-04 in CST
        assert_that(make_ntiid(date=1325723859.140755, nttype=u'Test'),
                    is_('tag:nextthought.com,2012-01-05:Test'))

    def test_make_safe(self):
        assert_that(make_specific_safe(u'-Foo%Bar +baz:?'),
                    is_('_Foo_Bar__baz__'))
        assert_that(make_specific_safe(u'-Foo%Bar/+baz:?'),
                    is_('_Foo_Bar__baz__'))

        # lax lets more through
        assert_that(make_specific_safe(u'-Foo%Bar, +baz:?', strict=False),
                    is_('_Foo_Bar,_+baz:_'))

        # too short
        assert_that(calling(make_specific_safe).with_args(''),
                    raises(ImpossibleToMakeSpecificPartSafe))
        # only invalid characters
        assert_that(calling(make_specific_safe).with_args('     '),
                    raises(ImpossibleToMakeSpecificPartSafe))

        assert_that(calling(make_specific_safe).with_args(u'Алибра школа'),
                    raises(ImpossibleToMakeSpecificPartSafe))

        assert_that(make_provider_safe(u'NSF/[Science]Nation?'),
                    is_('NSF__Science_Nation_'))

        assert_that(make_provider_safe(b'NSF/[Science]Nation?'),
                    is_('NSF__Science_Nation_'))

    def test_hash_ntiid(self):
        ntiid = u'tag:nextthought.com,2011-10:NTI-HTML-764853119912700730'
        assert_that(hash_ntiid(ntiid, '0000'),
                    is_('tag:nextthought.com,2011-10:NTI-HTML-5C60CE517CB52C8631FCBA5F2FD3356CACEF712B2D7665508F2F6CE1712489A3_0055'))

    def test_find_object_with_ntiid(self):
        assert_that(find_object_with_ntiid(None), is_(none()))
        assert_that(find_object_with_ntiid(u'invalid'), is_(none()))

        ntiid = u'tag:nextthought.com,2011-10:NTI-HTML-764853119912700730'
        obj = find_object_with_ntiid(ntiid, error=True)
        assert_that(obj, is_(none()))

        ntiid = u'tag:nextthought.com,2011-10:NTI-UUID-764853119912700730'
        obj = find_object_with_ntiid(ntiid, error=True)
        assert_that(obj, is_(none()))

        @interface.implementer(INTIIDResolver)
        class Resolver(object):
            def resolve(self, unused_key):
                return object()

        resolver = Resolver()
        component.getGlobalSiteManager().registerUtility(resolver, INTIIDResolver, 'HTML')
        try:
            ntiid = u'tag:nextthought.com,2011-10:NTI-HTML-764853119912700730'
            obj = find_object_with_ntiid(ntiid)
            assert_that(obj, is_not(none()))
        finally:
            component.getGlobalSiteManager().unregisterUtility(resolver, 
                                                               INTIIDResolver, 'HTML')
