import urllib
import urllib2
import urlparse
from itertools import chain
import mimetypes
import os.path
import json
from contextlib import closing

from flask import current_app
from flaskext.script import Command

from fbgroup import facebook_group_widget

class UpdateCommand(Command):
    "prints hello world"

    def run(self):
        groups = current_app.config.get('FACEBOOK_GROUPS', {})
        for group_id, token in groups.iteritems():
            print 'updating', group_id
            Updater(group_id, token).update()

GROUPS_PICTURES_DIR = os.path.join(facebook_group_widget.static_folder, 'groups')

class Updater(object):
    def __init__(self, group_id, token):
        self.group_id = group_id
        self.token = token

    def _update_url_with_access_token(self, url):
        url_parts = list(urlparse.urlparse(url))
        query = url_parts[4]
        query_dict = urlparse.parse_qs(query)
        query_dict['access_token'] = [self.token]
        query_list = []
        query_list = list(chain(*[[(key, value) for value in values]\
                                      for key, values in query_dict.iteritems()]))
        url_parts[4] = urllib.urlencode(query_list)
        return urlparse.urlunparse(url_parts)

    def _graph_data_from_url(self, url):
        # adding access token to get parameters
        url = self._update_url_with_access_token(url)

        with closing(urllib2.urlopen(url)) as resp:
            return json.loads(resp.read())

    def _graph_url_for_object(self, graph_object):
        return 'https://graph.facebook.com/%s' % graph_object

    def _graph_data(self, graph_object):
        url = self._graph_url_for_object(graph_object)
        return self._graph_data_from_url(url)

    def update(self):
        name = self._graph_data(self.group_id)['name']

        members = set()
        members_url = self._graph_url_for_object('%s/members' % self.group_id)
        while members_url:
            members_json = self._graph_data_from_url(members_url)
            for member in members_json['data']:
                members.add((member['id'], member['name']))
            members_url = members_json['paging'].get('next')

        import redis
        r = redis.Redis().pipeline()
        r.multi()
        timeout = 6 * 60 * 60

        key_name = 'fbgroup:%s:name' % self.group_id
        r.set(key_name, name)
        r.expire(key_name, timeout)

        key_members = 'fbgroup:%s:members' % self.group_id
        r.delete(key_members)
        for member_id, member_name in members:
            r.sadd(key_members, member_id)

            key_member_name = 'fbgroupmember:%s:name' % member_id
            r.set(key_member_name, member_name)
            r.expire(key_member_name, timeout)
        r.expire(key_members, timeout)
        r.execute()
