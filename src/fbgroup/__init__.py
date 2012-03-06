import json
from collections import namedtuple

import redis
from flask import abort, Blueprint, current_app, make_response, \
    render_template, request, url_for

facebook_group_widget = Blueprint('facebook_group_widget', __name__,
                                  static_folder='static',
                                  template_folder='templates')

Group = namedtuple('Group', ['name', 'url', 'members_count'])
GroupMember = namedtuple('GroupMember', ['id', 'name', 'url', 'picture'])

def _get_group_info(redis_client, group_id):
    group_name = redis_client.get('fbgroup:%s:name' % group_id).decode('utf-8')
    group_url = 'http://www.facebook.com/groups/%s/' % group_id

    group_members_count = redis_client.scard('fbgroup:%s:members' % group_id)

    return Group(group_name, group_url, group_members_count)

def _get_random_group_members(redis_client, group_id, count=4, retries=100):
    members = []
    chosen_members = set()

    key_members = 'fbgroup:%s:members' % group_id
    for i in xrange(retries):
        if len(chosen_members) == count:
            break
        member_id = redis_client.srandmember(key_members)
        if member_id in chosen_members:
            continue

        chosen_members.add(member_id)
        member_name = redis_client.get(
            'fbgroupmember:%s:name' % member_id).decode('utf-8')
        member_name = member_name.split(' ')[0]
        member_url = 'http://www.facebook.com/profile.php?id=%s' % member_id
        member_picture = 'http://graph.facebook.com/%s/picture/' % member_id
        members.append(
            GroupMember(member_id, member_name, member_url, member_picture))

    return members

@facebook_group_widget.route('/<group_id>')
def widget(group_id):
    r = redis.Redis(**current_app.config.get('REDIS_PARAMETERS', {}))

    if group_id not in current_app.config.get('FACEBOOK_GROUPS', {}):
        abort(404)

    group = _get_group_info(r, group_id)
    members = _get_random_group_members(r, group_id)

    html = render_template('widget.html',
                           group=group,
                           members=members)
    callback_name = request.args.get('callback', 'callback')
    jsonp = '%s(%s)' % (callback_name, json.dumps({'html': html}))

    resp = make_response(jsonp)
    resp.headers['content_type'] = 'text/javascript'
    return resp
