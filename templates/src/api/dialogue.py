from templates.src.mongo_client import sampled_collection, labelled_collection, package_collection
from flask import jsonify, request
import random
from bson import ObjectId
import time
from templates.src.utils import load_config

config = load_config()


def get_random_dialogue():
    """
    GET /api/leaderboard/list
    Returns a list of leaderboard entries.
    """
    dialogue_system = request.args.get('dialogue_system', None)
    dialogue_domains = request.args.get('dialogue_domains', None)

    if dialogue_system is not None and dialogue_domains is not None and not dialogue_system == 'Select Item':
        results = list(sampled_collection.find({'system_name': dialogue_system, 'domain_name': dialogue_domains}))
    elif dialogue_system is not None and not dialogue_system == 'Select Item':
        results = list(sampled_collection.find({'system_name': dialogue_system}))
    elif dialogue_domains is not None and not dialogue_domains == 'All Domains':
        results = list(sampled_collection.find({'domain_name': dialogue_domains}))
    else:
        results = list(sampled_collection.find({}))

    dialogue = random.choice(results)
    dialogue['_id'] = str(dialogue['_id'])
    return jsonify(dialogue)


def get_list_of_dialogues():
    dialogue_system = request.args.get('dialogue_system', None)
    domain = request.args.get('domain', None)
    dummy_value = 'All Domains'
    if dialogue_system is not None and domain is not None and not dialogue_system == dummy_value:
        results = list(sampled_collection.find({'system_name': dialogue_system, 'domain_name': domain}))
    elif dialogue_system is not None and not dialogue_system == dummy_value:
        results = list(sampled_collection.find({'system_name': dialogue_system}))
    elif domain is not None and not domain == dummy_value:
        results = list(sampled_collection.find({'domain_name': domain}))
    else:
        results = list(sampled_collection.find({}))

    result_ids = [str(result['_id']) for result in results]
    return jsonify(result_ids)


def get_dialogue_for_id():
    """
        GET /api/leaderboard/list
        Returns a list of leaderboard entries.
        """
    dialogue_id = request.args.get('dialogue_id', None)
    if dialogue_id == 'Select Item':
        return jsonify(None)
    dialogue = sampled_collection.find_one({'_id': ObjectId(dialogue_id)})
    if dialogue is None:
        return jsonify({}), 500
    now = int(round(time.time() * 1000))

    dialogue['_id'] = str(dialogue['_id'])
    dialogue['start_time'] = now
    return jsonify(dialogue)


def get_package_for_id():
    package_id = request.args.get('package_id', None)
    package = package_collection.find_one({'_id': ObjectId(package_id)})
    return jsonify({'pkg_list': package['package']})


def post_dialogue():
    if request.method == 'POST':
        data = request.get_json(force=True)
        now = int(round(time.time() * 1000))
        data['end_time'] = now
        data['elapsed_time'] = now - data['start_time']
        print(data)
        labelled_collection.insert_one(data)
        return jsonify({'msg': 'OK'}), 200
    else:
        return 'OK', 201


def get_number_of_packages_for_user():
    user_name = request.args.get('user_name', None)
    pipeline = [
        {
            "$group": {
                "_id": "$user_name",
                "packages": {"$addToSet": "$package_id"}
            }
        }
    ]
    result = labelled_collection.aggregate(pipeline)
    n_packages = [len(res['packages']) for res in result if res['_id'] == user_name]
    if n_packages == []:
        n_packages = 0
    else:
        n_packages = n_packages[0]

    max_package_per_user = config['max_package_per_user']
    return jsonify({'package_for_user': n_packages, 'max_package_per_user': max_package_per_user})



routes = [{'url': '/api/random_dialogue',
           'name': 'random_dialogue',
           'fn': get_random_dialogue,
           'methods': ['GET']},

          {'url': '/api/list_of_dialogues',
           'name': 'list_of_dialogues',
           'fn': get_list_of_dialogues,
           'methods': ['GET']},

          {'url': '/api/get_dialogue_for_id',
           'name': 'get_dialogue_for_id',
           'fn': get_dialogue_for_id,
           'methods': ['GET']},

          {'url': '/api/post_decision',
           'name': 'post_decision',
           'fn': post_dialogue,
           'methods': ['POST']},

          {'url': '/api/get_package_for_id',
           'name': 'get_package_for_id',
           'fn': get_package_for_id,
           'methods': ['GET']},

          {'url': '/api/get_number_of_packages_for_user',
           'name': 'get_number_of_packages_for_user',
           'fn': get_number_of_packages_for_user,
           'methods': ['GET']}
          ]
