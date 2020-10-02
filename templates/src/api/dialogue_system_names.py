from templates.src.mongo_client import sampled_collection
from flask import jsonify


def get_dialogue_systems():
    """
    GET /api/leaderboard/list
    Returns a list of leaderboard entries.
    """
    results = sampled_collection.aggregate(pipeline=[
         {
            "$group": {
                "_id": "$system_name",
            }
        }
    ])

    dialogue_systems = sorted([{'id': res['_id'], 'name': res['_id']} for res in results], key=lambda x: x['name'])

    return jsonify(dialogue_systems)

def get_dialogue_domains():
    results = sampled_collection.aggregate(pipeline=[
        {
            "$group": {
                "_id": "$domain_name",
            }
        }
    ])

    dialogue_systems = sorted([{'id': res['_id'], 'name': res['_id']} for res in results], key=lambda x: x['name'])

    return jsonify(dialogue_systems)


routes = [{'url': '/api/dialouge_systems',
           'name': 'dialouge_systems',
           'fn': get_dialogue_systems,
           'methods': ['GET']},
          {'url': '/api/dialouge_domains',
           'name': 'dialouge_domains',
           'fn': get_dialogue_domains,
           'methods': ['GET']}]
