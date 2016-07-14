import os
import requests
from eventbrite import Eventbrite


API_URL = 'https://www.eventbriteapi.com/v3/'
ACCESS_TOKEN = os.environ['EVENTBRITE_OAUTH_TOKEN']

eb = Eventbrite(ACCESS_TOKEN)

ATTENDEE_HEADERS = [
    'profile.name',
    'profile.email',
    'status',
    'costs.gross.major_value',
    'event_id',
]

EVENT_HEADERS = [
    'name.text',
    'id',
    'start.local',
]

USER = eb.get_user()
USER_ID = USER['id']

def flatten(d):
    # test: build_dotted_keys({'a': {'b': 2, 'c': {'d': 4}, 'e':[{'f':1231, 'g':{'h':0}}, {'z':34223}]}})
    # test: build_dotted_keys({'a': {'b': 2, 'c': {'d': 4}, 'e':[{'f':1231}]}})
    ret = {}
    for k, v in d.items():
        if isinstance(v, dict):
            for k1, v1 in flatten(v).items():
                key = '%s.%s' % (k, k1)
                ret[key] = v1

        elif isinstance(v, list):
            for i, nested in enumerate(v):
                prefix = '%s.%d' % (k, i)
                for x, y in flatten(nested).items():
                    key = '%s.%s' % (prefix, x)
                    ret[key] = y
        else:
            ret[k] = v
    return ret


def convert_to_csv(data, headers=None):
    """
    Turn nested keys into dotted headers.
    """
    rows = []
    if headers is None:
        headers = flatten(data[0]).keys()

    if isinstance(data, dict):
        flattened = flatten(data)
        row = []
        for header in headers:
            row.append(unicode(flattened.get(header, 'N/A')))
        return row

    for doc in data:
        flattened = flatten(doc)
        row = []
        for header in headers:
            row.append(unicode(flattened.get(header, 'N/A')))
        rows.append(row)
    return rows


def get_event_attendees(eid, page=1):
    return requests.get('{url}/events/{eid}/attendees/?token={token}&page={page}'.format(url=API_URL, eid=eid, token=ACCESS_TOKEN, page=page)).json()


def fetch_all_pages(fn, *args, **kwargs):
    page_number = 1
    payload = fn(*args, page=page_number, **kwargs)
    pagination = payload['pagination']
    key = payload.keys()[1]
    ret = payload[key]
    page_count = pagination['page_count']
    page_number += 1
    
    while page_number <= page_count:
        payload = fn(*args, **kwargs)
        ret += payload[key]
        page_number += 1
    
    return ret


def fetch_all_ended_events_created_by_user(user_id):
    return fetch_all_pages(eb.get_user_events, user_id, status='ended')


def fetch_all_attendees_for_event(event_id):
    return fetch_all_pages(get_event_attendees, event_id)
    

def fetch_eventbrite_attendees():
    """
    Write to csv all eventbrite attendees.
    """
    with open('eventbrite_attendees.csv', 'w') as f:
        writerows = [','.join(ATTENDEE_HEADERS + EVENT_HEADERS)]
        # Get all events owned by this user. Cache event_id => event.
        _events = fetch_all_ended_events_created_by_user(USER_ID)
        events = { event['id']: convert_to_csv(event, EVENT_HEADERS) for event in _events }

        # Get all attendees for each completed event.
        for eid, event in events.items():
            attendees = fetch_all_attendees_for_event(eid)
            rows = convert_to_csv(attendees, ATTENDEE_HEADERS)
    
            # Append event data to each attendee.
            for _row in rows:
                row = _row + event
                writerows.append(','.join(row))
        f.write('\n'.join(writerows).encode('utf-8'))

#e = fetch_all_ended_events_created_by_user(USER_ID)

#a = fetch_all_attendees_for_event(e[0]['id'])
fetch_eventbrite_attendees()
