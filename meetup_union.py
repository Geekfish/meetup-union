import os
import argparse
from collections import Counter
from json import JSONDecodeError
from time import sleep

import requests
from urllib.parse import urlencode
from meetup.api import Client as MeetupClient

MEETUP_API_ROOT = 'https://api.meetup.com/'
MEETUP_ATTENDANCE_ENDPOINT = '{urlname}/events/{event_id}/attendance'

MEETUP_API_KEY = os.environ.get('MEETUP_API_KEY')

MEMBER, MEMBER_OF_TARGET, MEMBER_OF_BOTH = 1, 2, 3


def fetch_attendee_ids(own_meetup, event_id):
    """
    We don't use the meetup api library for this ones, it appears to be buggy
    and never returns results...

    NB: This returns all RSVPs but further filtering is possible.
    """
    # Build url
    attendance_endpoint = MEETUP_ATTENDANCE_ENDPOINT.format(**{
        'urlname': own_meetup,
        'event_id': event_id,
    })
    auth_params = urlencode({'sign': 'true', 'key': MEETUP_API_KEY})
    url = f'{MEETUP_API_ROOT}{attendance_endpoint}?{auth_params}'

    # Do query
    response = requests.get(url)

    # Parse JSON data
    return [_a['member']['id'] for _a in response.json()]


def fetch_member_groups_urlnames(client, member_id):
    try:
        groups_joined = client.GetGroups(member_id=member_id).results
    except (JSONDecodeError, TypeError):
        sleep(0.5)
        try:
            # Poor man's retry strategy - it looks like Meetup's API
            # can randomly return blank pages, so wait a bit and retry
            groups_joined = client.GetGroups(member_id=member_id).results
        except (JSONDecodeError, TypeError) as e:
            print(e)
            print("Unexpected api client error, skipping member")
            groups_joined = []
    return [_r['urlname'] for _r in groups_joined]


def get_membership_state(urlnames, own_meetup, target_meetup):
    common_groups = {
        own_meetup,
        target_meetup,
    }.intersection(set(urlnames))

    if len(common_groups) == 0:
        # These people probably have their groups set to private
        return None

    if len(common_groups) == 2:
        return MEMBER_OF_BOTH

    if MEMBER_OF_TARGET in common_groups:
        # Also Hmmm...
        # don't they also need to be a member of our meetup to attend?
        return MEMBER_OF_TARGET

    return MEMBER


def print_results(states, own_meetup, target_meetup):
    state_counter = Counter(states)
    print("\n"*4)
    print("====="*20)
    print(f"Members of only {own_meetup}: "
          f"{state_counter[MEMBER]}")
    print(f"Members of only {target_meetup}: "
          f"{state_counter[MEMBER_OF_TARGET]}")
    print(f"Members both: "
          f"{state_counter[MEMBER_OF_BOTH]}")
    print(f"Members of neither (private?): "
          f"{state_counter[None]}")


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("own_meetup",
                        help="String identifier Found in the Meetup's URL")
    parser.add_argument("target_meetup",
                        help="String identifier Found in the Meetup's URL")
    parser.add_argument("event_id",
                        type=int,
                        help="Numeric id found in the event's URL")
    return parser.parse_args()


def main():
    options = parse_arguments()

    client = MeetupClient(MEETUP_API_KEY)
    attendee_ids = fetch_attendee_ids(options.own_meetup, options.event_id)

    states = []

    for member_id in enumerate(attendee_ids):
        groups_urlnames = fetch_member_groups_urlnames(client, member_id)
        # Sleep after each request, so that we don't trigger rate limiting
        sleep(0.4)

        states.append(
            get_membership_state(
                groups_urlnames,
                options.own_meetup,
                options.target_meetup)
        )

    print_results(states, options.own_meetup, options.target_meetup)


if __name__ == "__main__":
    main()
