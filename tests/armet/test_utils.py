# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import unittest
from armet import utils


class ExtendTestCase(unittest.TestCase):

    def test_mapping(self):
        value = {'x': 10, 'y': 20}
        value = utils.cons(value, {'z': 15})

        assert value == {'x': 10, 'y': 20, 'z': 15}

    def test_list(self):
        value = [10, 20]
        value = utils.cons(value, [15])

        assert value == [10, 20, 15]

    def test_scalar(self):
        value = [10, 20]
        value = utils.cons(value, 15)

        assert value == [10, 20, 15]

    def test_string(self):
        value = ['10', 20]
        value = utils.cons(value, '15')

        assert value == ['10', 20, '15']


class DasherizeTestCase(unittest.TestCase):

    def test_word(self):
        assert utils.dasherize('word') == 'word'

    def test_camel(self):
        assert utils.dasherize('camelCase') == 'camel-case'

    def test_pascal(self):
        assert utils.dasherize('PascalCase') == 'pascal-case'

    def test_underscore(self):
        assert utils.dasherize('under_score') == 'under-score'

    def test_dashed(self):
        assert utils.dasherize('dashed-words') == 'dashed-words'
