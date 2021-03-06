# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import json
from armet import http
from .base import BaseResourceTest


class TestResourceGet(BaseResourceTest):

    def test_list(self):
        response, content = self.client.request('/api/poll/')

        assert response.status == http.client.OK

        data = json.loads(content.decode('utf-8'))

        assert isinstance(data, list)
        assert len(data) == 100
        assert data[0]['question'] == 'Are you an innie or an outie?'
        assert (data[-1]['question'] ==
                'What one question would you add to this survey?')

    def test_not_found(self, connectors):
        response, _ = self.client.get('/api/poll/101/')

        assert response.status == http.client.NOT_FOUND

    def test_single(self, connectors):
        response, content = self.client.request('/api/poll/1/')
        data = json.loads(content.decode('utf-8'))

        assert response.status == http.client.OK
        assert isinstance(data, dict)
        assert data['question'] == 'Are you an innie or an outie?'

        response, content = self.client.request('/api/poll/100/')
        data = json.loads(content.decode('utf-8'))

        assert response.status == http.client.OK
        assert isinstance(data, dict)
        assert (data['question'] ==
                'What one question would you add to this survey?')


class TestResourceQuery(BaseResourceTest):

    def test_param_eq_one(self, connectors):
        response, content = self.client.request('/api/poll/?id=1')

        assert response.status == http.client.OK

        data = json.loads(content.decode('utf-8'))

        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['question'] == 'Are you an innie or an outie?'

    def test_param_eq_same_and(self, connectors):
        response, content = self.client.request('/api/poll/?id=1&id=2')

        assert response.status == http.client.OK

        data = json.loads(content.decode('utf-8'))

        assert isinstance(data, list)
        assert len(data) == 0

    def test_param_eq_same_or(self, connectors):
        response, content = self.client.request('/api/poll/?id=1;id=2')

        assert response.status == http.client.OK

        data = json.loads(content.decode('utf-8'))

        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]['question'] == 'Are you an innie or an outie?'

    def test_param_eq_same_or_simple(self, connectors):
        response, content = self.client.request('/api/poll/?id=1,2')

        assert response.status == http.client.OK

        data = json.loads(content.decode('utf-8'))

        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]['question'] == 'Are you an innie or an outie?'

    def test_param_gt_one(self, connectors):
        response, content = self.client.request('/api/poll/?id>99')

        assert response.status == http.client.OK

        data = json.loads(content.decode('utf-8'))

        assert isinstance(data, list)
        assert len(data) == 1

        question = data[0]['question']
        assert question == 'What one question would you add to this survey?'

    def test_param_available_true(self, connectors):
        response, content = self.client.request('/api/poll/?available=true')

        assert response.status == http.client.OK

        data = json.loads(content.decode('utf-8'))

        assert isinstance(data, list)
        assert len(data) == 4

    def test_param_available_false(self, connectors):
        response, content = self.client.request('/api/poll/?available=false')

        assert response.status == http.client.OK

        data = json.loads(content.decode('utf-8'))

        assert isinstance(data, list)
        assert len(data) == 4
