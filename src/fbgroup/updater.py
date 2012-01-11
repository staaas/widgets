import urllib
import urllib2
import urlparse
from itertools import chain
import mimetypes
import os.path
import json
from contextlib import closing

FB_ACCESS_TOKEN = 'AAACfbxksx4gBALSa3rgvdHAHkN4fkbF3ZCnnT3ZC8scxZCUbEXzuDV9GgwmZBf0q00xakZAOaEgTbJ7RH4L9sBpHNZCgI1aEEzHjgMvM5j2QZDZD'
group_id = '213523202010635'
GROUPS_PICTURES_DIR = 'static/groups'

def update_url_with_access_token(url):
    url_parts = list(urlparse.urlparse(url))
    query = url_parts[4]
    query_dict = urlparse.parse_qs(query)
    query_dict['access_token'] = [FB_ACCESS_TOKEN]
    query_list = []
    query_list = list(chain(*[[(key, value) for value in values]\
                             for key, values in query_dict.iteritems()]))
    url_parts[4] = urllib.urlencode(query_list)
    return urlparse.urlunparse(url_parts)

def graph_data_from_url(url):
    # adding access token to get parameters
    url = update_url_with_access_token(url)

    try:
        with closing(urllib2.urlopen(url)) as resp:
            return json.loads(resp.read())
    except Exception:
        print url
        raise

def graph_url_for_object(graph_object):
    return 'https://graph.facebook.com/%s' % graph_object

def graph_data(graph_object):
    url = graph_url_for_object(graph_object)
    return graph_data_from_url(url)

def raw_graph_data(graph_object):
    pass

def update():
    name = graph_data(group_id)['name']

    members = set()
    members_url = graph_url_for_object('%s/members' % group_id)
    while members_url:
        members_json = graph_data_from_url(members_url)
        for member in members_json['data']:
            members.add((member['id'], member['name']))
        members_url = members_json['paging'].get('next')

    picture_url = update_url_with_access_token(
        graph_url_for_object('%s/picture' % group_id))
    with closing(urllib2.urlopen(picture_url)) as resp:
        picture_data = resp.read()
        picture_ext = mimetypes.guess_extension(resp.info().gettype())

    picture_fname = os.path.join(GROUPS_PICTURES_DIR,
                                 '%s%s' % (group_id, picture_ext))
    with open(picture_fname, 'w') as picture_file:
        picture_file.write(picture_data)

    import redis
    r = redis.Redis().pipeline()
    r.multi()
    timeout = 6 * 60 * 60

    key_name = 'fbgroup:%s:name' % group_id
    r.set(key_name, name)
    r.expire(key_name, timeout)

    key_picture = 'fbgroup:%s:picture' % group_id
    r.set(key_picture, os.path.basename(picture_fname))
    r.expire(key_picture, timeout)

    key_members = 'fbgroup:%s:members' % group_id
    r.delete(key_members)
    for member_id, member_name in members:
        r.sadd(key_members, member_id)

        key_member_name = 'fbgroupmember:%s:name' % member_id
        r.set(key_member_name, member_name)
        r.expire(key_member_name, timeout)
    r.expire(key_members, timeout)
    r.execute()

if __name__ == '__main__':
    update()
        
