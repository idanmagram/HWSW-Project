
"""Script for testing the performance of json parsing and serialization.

This will dump/load several real world-representative objects a few
thousand times. The methodology below was chosen for was chosen to be similar
to real-world scenarios which operate on single objects at a time.
"""

# Python imports
import json_opt as json
from json_opt import FastKey
import random
import sys


# Local imports
import pyperf


DICT = {
    FastKey('ads_flags'): 0,
    FastKey('age'): 18,
    FastKey('bulletin_count'): 0,
    FastKey('comment_count'): 0,
    FastKey('country'): 'BR',
    FastKey('encrypted_id'): 'G9urXXAJwjE',
    FastKey('favorite_count'): 9,
    FastKey('first_name'): '',
    FastKey('flags'): 412317970704,
    FastKey('friend_count'): 0,
    FastKey('gender'): 'm',
    FastKey('gender_for_display'): 'Male',
    FastKey('id'): 302935349,
    FastKey('is_custom_profile_icon'): 0,
    FastKey('last_name'): '',
    FastKey('locale_preference'): 'pt_BR',
    FastKey('member'): 0,
    FastKey('tags'): ['a', 'b', 'c', 'd', 'e', 'f', 'g'],
    FastKey('profile_foo_id'): 827119638,
    FastKey('secure_encrypted_id'): 'Z_xxx2dYx3t4YAdnmfgyKw',
    FastKey('session_number'): 2,
    FastKey('signup_id'): '201-19225-223',
    FastKey('status'): 'A',
    FastKey('theme'): 1,
    FastKey('time_created'): 1225237014,
    FastKey('time_updated'): 1233134493,
    FastKey('unread_message_count'): 0,
    FastKey('user_group'): '0',
    FastKey('username'): 'collinwinter',
    FastKey('play_count'): 9,
    FastKey('view_count'): 7,
    FastKey('zip'): ''}

TUPLE = (
    [265867233, 265868503, 265252341, 265243910, 265879514,
     266219766, 266021701, 265843726, 265592821, 265246784,
     265853180, 45526486, 265463699, 265848143, 265863062,
     265392591, 265877490, 265823665, 265828884, 265753032], 60)


def mutate_dict(orig_dict, random_source):
    new_dict = dict(orig_dict)
    for key, value in new_dict.items():
        rand_val = random_source.random() * sys.maxsize
        if isinstance(value, (int, bytes, str)):
            new_dict[key] = type(key)(rand_val)
    return new_dict


random_source = random.Random(5)  # Fixed seed.
DICT_GROUP = [mutate_dict(DICT, random_source) for _ in range(3)]


def bench_json_loads(objs):
    for obj in objs:
        # 20 loads
        json.loads(obj)
        json.loads(obj)
        json.loads(obj)
        json.loads(obj)
        json.loads(obj)
        json.loads(obj)
        json.loads(obj)
        json.loads(obj)
        json.loads(obj)
        json.loads(obj)
        json.loads(obj)
        json.loads(obj)
        json.loads(obj)
        json.loads(obj)
        json.loads(obj)
        json.loads(obj)
        json.loads(obj)
        json.loads(obj)
        json.loads(obj)
        json.loads(obj)


if __name__ == "__main__":
    runner = pyperf.Runner()
    runner.metadata['description'] = "Benchmark json.loads()"

    json_dict = json.dumps(DICT)
    json_tuple = json.dumps(TUPLE)
    json_dict_group = json.dumps(DICT_GROUP)
    objs = (json_dict, json_tuple, json_dict_group)

    runner.bench_func('json_loads', bench_json_loads, objs, inner_loops=20)