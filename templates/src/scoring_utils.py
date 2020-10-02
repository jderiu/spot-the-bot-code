from templates.src.mongo_client import labelled_collection, sampled_collection, package_collection
from bson import ObjectId
from collections import defaultdict

user_black_list = ['']


def get_annotator_names():
    results = labelled_collection.aggregate(pipeline=[
        {
            "$group": {
                "_id": "$user_name",
                "convos": {"$addToSet": "$convo_id"}  # group by convo_ids
            }
        }
    ])

    user_names = {res['_id']: res['convos'] for res in results}

    return user_names


def get_elapsed_time_per_annotator():
    results = labelled_collection.aggregate(pipeline=[
        {
            "$group": {
                "_id": "$user_name",
                "times": {"$addToSet": "$elapsed_time"}  # group by convo_ids
            }
        }
    ])

    user_names = {res['_id']: int(sum(res['times'])/len(res['times'])/1000) for res in results}

    return user_names

def get_nannotation_per_user():
    results = labelled_collection.aggregate(pipeline=[
        {
            "$group": {
                "_id": "$user_name",
                "convos": {"$sum": 1}  # group by convo_ids
            }
        }
    ])

    user_names = {res['_id']: res['convos'] for res in results}

    return user_names


def create_black_list():
    user_names = get_annotator_names()
    black_list = []
    for user_name in user_names:
        annotations_for_user = get_annotations_for_user(user_name)
        annotated_convos_for_user = get_annotated_convos_for_user(user_names[user_name])
        cid_to_annotated_convo = combine_annotations_and_convos_for_user(annotations_for_user, annotated_convos_for_user)
        score = average_score_for_user(cid_to_annotated_convo)
        avg_turn_penalty = average_turn_penalty_for_user(cid_to_annotated_convo)
        avg_corr = average_correctness_for_user(cid_to_annotated_convo)
        if (avg_turn_penalty <= 0.25 and avg_corr <= 0.75) or avg_corr <= 0.6:
            black_list.append(user_name)
        if len(annotated_convos_for_user) < 10:
            black_list.append(user_name)
    return black_list


def get_annotations_for_user(user_name):
    results = labelled_collection.find({'user_name': user_name})
    annotations_for_user = list(results)
    return annotations_for_user


def get_annotated_convos_for_user(convo_ids):
    oids = [ObjectId(cid) for cid in convo_ids]
    results = sampled_collection.find({'_id': {'$in': oids}})
    new_results = []
    for result in results:
        result['_id'] = str(result['_id'])
        new_results.append(result)
    return list(new_results)


def combine_annotations_and_convos_for_user(annotations_for_user, annotated_convos_for_user):
    convo_id_to_convo = {}  # make it searchable
    for convo in annotated_convos_for_user:
        convo_id_to_convo[convo['_id']] = convo

    cid_to_annotated_convo = {}
    for annotation in annotations_for_user:
        convo_id = annotation['convo_id']
        convo = convo_id_to_convo.get(convo_id, None)
        if convo is None:
            continue
        cid_to_annotated_convo[convo_id] = (annotation, convo)

    return cid_to_annotated_convo


def compute_score_for_convo(annotation, convo):
    entitiy0_pred = annotation['entity0_annotation']['is_human']
    entitiy1_pred = annotation['entity1_annotation']['is_human']

    # need to adapt this to handle human-bot convos
    entitiy0_true = convo['is_human0']
    entitiy1_true = convo['is_human1']

    decision_turn0 = annotation['entity0_annotation']['decision_turn']
    decision_turn1 = annotation['entity1_annotation']['decision_turn']
    convo_len = len(convo['convo'])

    #score = 0.5 * int(entitiy0_pred == entitiy0_true) + 0.5 * int(entitiy1_pred == entitiy1_true)
    score0 = int(entitiy0_pred == entitiy0_true)
    score1 = int(entitiy1_pred == entitiy1_true)
    if score0 >= 0 and decision_turn0 > 2:
        if convo_len > 2:
            turn_penalty0 = (decision_turn0 - 2) / (convo_len - 2)
            score0 -= 0.25*turn_penalty0

    if score1 >= 0 and decision_turn1 > 2:
        if convo_len > 2:
            turn_penalty1 = (decision_turn1 - 2) / (convo_len - 2)
            score1 -= 0.25*turn_penalty1
    score = 0.5*(score0 + score1)
    return score


def compute_turn_penalty_for_convo(annotation, convo):
    decision_turn0 = annotation['entity0_annotation']['decision_turn']
    decision_turn1 = annotation['entity1_annotation']['decision_turn']
    convo_len = len(convo['convo'])
    turn_penalty0 = 0
    if decision_turn0 > 2 and convo_len > 2:
        turn_penalty0 = (decision_turn0 - 2) / (convo_len - 2)
    turn_penalty1 = 0
    if decision_turn1 > 2 and convo_len > 2:
        turn_penalty1 = (decision_turn1 - 2) / (convo_len - 2)
    return 0.5*turn_penalty0 + 0.5*turn_penalty1


def compute_human_confusion_for_convo(annotation, convo):
    entitiy0_pred = annotation['entity0_annotation']['is_human']
    entitiy1_pred = annotation['entity1_annotation']['is_human']

    # need to adapt this to handle human-bot convos
    entitiy0_true = convo['is_human0']
    entitiy1_true = convo['is_human1']

    score = 0
    if entitiy0_true and not entitiy0_pred:
        score+=1
    if entitiy1_true and not entitiy1_pred:
        score+=1
    return score


def compute_corectness_for_convo(annotation, convo):
    entitiy0_pred = annotation['entity0_annotation']['is_human']
    entitiy1_pred = annotation['entity1_annotation']['is_human']

    # need to adapt this to handle human-bot convos
    entitiy0_true = convo['is_human0']
    entitiy1_true = convo['is_human1']

    score = 0.5 * int(entitiy0_pred == entitiy0_true) + 0.5 * int(entitiy1_pred == entitiy1_true)
    return score


def average_correctness_for_user(cid_to_annotated_convo):
    total_correctness = 0
    for cid, (annotation, convo) in cid_to_annotated_convo.items():
        score = compute_corectness_for_convo(annotation, convo)
        total_correctness += score
    score = 0
    if len(cid_to_annotated_convo) > 0:
        score = total_correctness / len(cid_to_annotated_convo)
    return score


def average_turn_penalty_for_user(cid_to_annotated_convo):
    total_turn_penalty = 0
    for cid, (annotation, convo) in cid_to_annotated_convo.items():
        turn_penalty_i = compute_turn_penalty_for_convo(annotation, convo)
        total_turn_penalty += turn_penalty_i
    score = 0
    if len(cid_to_annotated_convo) > 0:
        score = total_turn_penalty / len(cid_to_annotated_convo)
    return score

def average_human_confusion_for_user(cid_to_annotated_convo):
    total_turn_penalty = 0
    for cid, (annotation, convo) in cid_to_annotated_convo.items():
        turn_penalty_i = compute_human_confusion_for_convo(annotation, convo)
        total_turn_penalty += turn_penalty_i
    score = 0
    if len(cid_to_annotated_convo) > 0:
        score = total_turn_penalty / (2*len(cid_to_annotated_convo))
    return score


def average_score_for_user(cid_to_annotated_convo):
    score_sum = 0
    for cid, (annotation, convo) in cid_to_annotated_convo.items():
        score_i = compute_score_for_convo(annotation, convo)
        score_sum += score_i
    score = 0
    if len(cid_to_annotated_convo) > 0:
        score = score_sum / len(cid_to_annotated_convo)
    return score


def compute_confusion_matrix_for_user(cid_to_annotated_convo):
    confusion_matrix = defaultdict(lambda: 0)
    for cid, (annotation, convo) in cid_to_annotated_convo.items():
        entitiy0_pred = annotation['entity0_annotation']['is_human']
        entitiy1_pred = annotation['entity1_annotation']['is_human']

        # need to adapt this to handle human-bot convos
        entitiy0_true = convo['is_human0']
        entitiy1_true = convo['is_human1']

        confusion_matrix[(entitiy0_true, entitiy0_pred)] += 1
        confusion_matrix[(entitiy1_true, entitiy1_pred)] += 1

    return confusion_matrix


def get_all_annotated_convos():
    annotation_results = [res for res in labelled_collection.find({'user_name': {'$nin': user_black_list}})]
    oids = [ObjectId(ann['convo_id']) for ann in annotation_results]
    convo_results = sampled_collection.find({'_id': {'$in': oids}})

    convo_id_to_convo = {}  # make it searchable
    for convo in convo_results:
        convo['annotations'] = []
        convo_id_to_convo[str(convo['_id'])] = convo

    for annotation in annotation_results:
        convo_id = annotation['convo_id']
        convo = convo_id_to_convo[convo_id]
        convo['annotations'].append(annotation)

    return convo_id_to_convo


def compute_fools_for_system(convo_id_to_convo, ignore_human_bot=False, human_bot_only=False):
    # system: algo trained on a domain
    system_name_to_scores = defaultdict(lambda: [0, 0, 0])
    for cid, convo in convo_id_to_convo.items():
        system_name0 = '{}/{}'.format(convo['domain_name'], convo['system_type0'])  # need to change this in the data-format
        system_name1 = '{}/{}'.format(convo['domain_name'], convo['system_type1'])  # need to change this in the data-format
        is_human0 = convo['is_human0']
        is_human1 = convo['is_human1']
        if ignore_human_bot:
            if not is_human0 == is_human1:
                continue
        if human_bot_only:
            if is_human0 == is_human1:
                continue

        convo_len = len(convo['convo'])
        if convo_len == 0:
            print('ConvoLen: 0', cid)
            continue
        for annotation in convo['annotations']:
            entitiy0_pred = annotation['entity0_annotation']['is_human']
            entitiy1_pred = annotation['entity1_annotation']['is_human']
            decision_turn0 = annotation['entity0_annotation']['decision_turn']
            decision_turn1 = annotation['entity1_annotation']['decision_turn']

            system_name_to_scores[system_name0][0] += int(entitiy0_pred != is_human0)
            system_name_to_scores[system_name1][0] += int(entitiy1_pred != is_human1)
            system_name_to_scores[system_name0][1] += 1
            system_name_to_scores[system_name1][1] += 1
            system_name_to_scores[system_name0][2] += decision_turn0/convo_len
            system_name_to_scores[system_name1][2] += decision_turn1/convo_len
    return system_name_to_scores


def compute_fools_for_algorithm(convo_id_to_convo, ignore_human_bot=False, human_bot_only=False):
    # system: algo trained on a domain
    system_name_to_scores = defaultdict(lambda: [0, 0, 0])
    for cid, convo in convo_id_to_convo.items():
        system_name0 = convo['system_type0']  # need to change this in the data-format
        system_name1 = convo['system_type1']  # need to change this in the data-format
        is_human0 = convo['is_human0']
        is_human1 = convo['is_human1']
        if ignore_human_bot:
            if not is_human0 == is_human1:
                continue
        if human_bot_only:
            if is_human0 == is_human1:
                continue

        convo_len = len(convo['convo'])
        if convo_len == 0:
            print('Convo Len: 0')
            continue
        for annotation in convo['annotations']:
            entitiy0_pred = annotation['entity0_annotation']['is_human']
            entitiy1_pred = annotation['entity1_annotation']['is_human']
            decision_turn0 = annotation['entity0_annotation']['decision_turn']
            decision_turn1 = annotation['entity1_annotation']['decision_turn']

            system_name_to_scores[system_name0][0] += int(entitiy0_pred != is_human0)
            system_name_to_scores[system_name1][0] += int(entitiy1_pred != is_human1)
            system_name_to_scores[system_name0][1] += 1
            system_name_to_scores[system_name1][1] += 1
            system_name_to_scores[system_name0][2] += decision_turn0 / convo_len
            system_name_to_scores[system_name1][2] += decision_turn1 / convo_len
    return system_name_to_scores


def get_is_human_agreement(convo_id_to_convo, ignore_human_bot=False):
    total_cnt = 0
    agreement_count = 0
    for cid, convo in convo_id_to_convo.items():
        system0_preds = []
        system1_preds = []
        is_human0 = convo['is_human0']
        is_human1 = convo['is_human1']
        if ignore_human_bot:
            if not is_human0 == is_human1:
                continue

        if not len(convo['annotations']) >= 2:
            print(cid, 'NOT 2 ANNOTATIONS')
            continue

        for annotation in convo['annotations']:
            system0_preds.append(annotation['entity0_annotation']['is_human'])
            system1_preds.append(annotation['entity1_annotation']['is_human'])
        if len(set(system0_preds)) == 1:
            agreement_count += 1
        if len(set(system1_preds)) == 1:
            agreement_count += 1
        total_cnt += 2

    return agreement_count/total_cnt


def compute_average_scores_for_bot(convo_id_to_convo, ignore_human_bot=False, human_bot_only=False):
    system_name_to_scores = defaultdict(lambda: [0, 0, 0, 0])
    for cid, convo in convo_id_to_convo.items():
        system_name0 = '{}/{}'.format(convo['domain_name'], convo['system_type0'])  # need to change this in the data-format
        system_name1 = '{}/{}'.format(convo['domain_name'], convo['system_type1'])  # need to change this in the data-format
        is_human0 = convo['is_human0']
        is_human1 = convo['is_human1']
        if ignore_human_bot:
            if not is_human0 == is_human1:
                continue
        if human_bot_only:
            if is_human0 == is_human1:
                continue

        for annotation in convo['annotations']:
            fluency_0 = int(annotation['entity0_annotation']['fluencyValue'])
            fluency_1 = int(annotation['entity1_annotation']['fluencyValue'])

            specificity_0 = int(annotation['entity0_annotation']['specificityValue'])
            specificity_1 = int(annotation['entity1_annotation']['specificityValue'])

            sensibleness_0 = int(annotation['entity0_annotation']['sensitivenessValue'])
            sensibleness_1 = int(annotation['entity1_annotation']['sensitivenessValue'])
            system_name_to_scores[system_name0][0] += fluency_0
            system_name_to_scores[system_name1][0] += fluency_1
            system_name_to_scores[system_name0][1] += specificity_0
            system_name_to_scores[system_name1][1] += specificity_1
            system_name_to_scores[system_name0][2] += sensibleness_0
            system_name_to_scores[system_name1][2] += sensibleness_1
            system_name_to_scores[system_name1][3] += 1 #count number of occurrences
            system_name_to_scores[system_name0][3] += 1 #count number of occurrences

    return system_name_to_scores

def compute_average_scores_for_algo(convo_id_to_convo, ignore_human_bot=False):
    system_name_to_scores = defaultdict(lambda: [0, 0, 0, 0])
    for cid, convo in convo_id_to_convo.items():
        system_name0 = convo['system_type0']  # need to change this in the data-format
        system_name1 = convo['system_type1']  # need to change this in the data-format
        is_human0 = convo['is_human0']
        is_human1 = convo['is_human1']
        if ignore_human_bot:
            if not is_human0 == is_human1:
                continue
        for annotation in convo['annotations']:
            fluency_0 = int(annotation['entity0_annotation']['fluencyValue'])
            fluency_1 = int(annotation['entity1_annotation']['fluencyValue'])

            specificity_0 = int(annotation['entity0_annotation']['specificityValue'])
            specificity_1 = int(annotation['entity1_annotation']['specificityValue'])

            sensibleness_0 = int(annotation['entity0_annotation']['sensitivenessValue'])
            sensibleness_1 = int(annotation['entity1_annotation']['sensitivenessValue'])
            system_name_to_scores[system_name0][0] += fluency_0
            system_name_to_scores[system_name1][0] += fluency_1
            system_name_to_scores[system_name0][1] += specificity_0
            system_name_to_scores[system_name1][1] += specificity_1
            system_name_to_scores[system_name0][2] += sensibleness_0
            system_name_to_scores[system_name1][2] += sensibleness_1
            system_name_to_scores[system_name1][3] += 1 #count number of occurrences
            system_name_to_scores[system_name0][3] += 1 #count number of occurrences

    return system_name_to_scores


def compute_scores_for_user(user_name):
    user_names = get_annotator_names()
    annotations_for_user = get_annotations_for_user(user_name)
    annotated_convos_for_user = get_annotated_convos_for_user(user_names[user_name])
    cid_to_annotated_convo = combine_annotations_and_convos_for_user(annotations_for_user, annotated_convos_for_user)

    score = average_score_for_user(cid_to_annotated_convo)
    avg_turn_penalty = average_turn_penalty_for_user(cid_to_annotated_convo)
    avg_corr = average_correctness_for_user(cid_to_annotated_convo)

    return score, avg_corr, avg_turn_penalty

def get_leaderboard():
    user_names = get_annotator_names()
    elapsed_time = get_elapsed_time_per_annotator()
    leaderboard = []
    convo_id_to_convo = get_all_annotated_convos()
    for user_name in user_names:
        if user_name in user_black_list:
            continue
        annotations_for_user = get_annotations_for_user(user_name)
        annotated_convos_for_user = get_annotated_convos_for_user(user_names[user_name])
        cid_to_annotated_convo = combine_annotations_and_convos_for_user(annotations_for_user, annotated_convos_for_user)
        score = average_score_for_user(cid_to_annotated_convo)
        avg_turn_penalty = average_turn_penalty_for_user(cid_to_annotated_convo)
        avg_corr = average_correctness_for_user(cid_to_annotated_convo)
        human_confusion = average_human_confusion_for_user(cid_to_annotated_convo)

        entry = {
            'user_name': user_name,
            'number_of_annotations': len(annotations_for_user),
            'score': score,
            'avg_correctness': avg_corr,
            'avg_turn_penalty': avg_turn_penalty,
            'elo_score': -1,
            'elapsed_time': elapsed_time.get(user_name, -1),
            'human_confusion': human_confusion,
            'competence': 0.0
        }

        leaderboard.append(entry)

    entry = {
        'user_name': 'BASELINE',
        'number_of_annotations': 10000,
        'score': 0.75,
        'avg_correctness': 0.78,
        'avg_turn_penalty': -1,
        'elo_score': -1,
        'elapsed_time': -1,
        'human_confusion': 0,
        'competence': -1
    }
    leaderboard.append(entry)

    entry = {
        'user_name': 'MINIMAL-BASELINE',
        'number_of_annotations': 10000,
        'score': 0.58,
        'avg_correctness': 0.5,
        'avg_turn_penalty': -1,
        'elo_score': -1,
        'elapsed_time': -1,
        'human_confusion': 0,
        'competence': -1
    }
    leaderboard.append(entry)
    leaderboard = sorted(leaderboard, key=lambda x: x['score'], reverse=True)
    return leaderboard


class Player:
    def __init__(self, user_name, match_score):
        self.user_name = user_name
        self.match_score = match_score

    def __eq__(self, other):
        return self.user_name == other.user_name

    def __hash__(self):
        return hash(self.user_name)

    def __str__(self):
        return self.user_name

    def __repr__(self):
        return self.user_name


def record_single_match(player1, player2, score0_player1, score0_player2, decision_turn0_player1, decision_turn0_player2):
    if score0_player1 > score0_player2:
        match_pair = (Player(player1, 1), Player(player2, 0))
    elif score0_player2 > score0_player1:
        match_pair = (Player(player1, 0), Player(player2, 1))
    else:
        if decision_turn0_player1 + 2 < decision_turn0_player2:
            match_pair = (Player(player1, 1), Player(player2, 0))
        elif decision_turn0_player1 > decision_turn0_player2 + 2:
            match_pair = (Player(player1, 0), Player(player2, 1))
        else:
            match_pair = (Player(player1, 1), Player(player2, 1))

    return match_pair


def compute_winner(ann1, ann2, is_human0: bool, is_human1: bool):
    player1 = ann1['user_name']
    player2 = ann2['user_name']

    score0_player1 = int(ann1['entity0_annotation']['is_human'] == is_human0)
    score0_player2 = int(ann2['entity0_annotation']['is_human'] == is_human0)
    decision_turn0_player1 = ann1['entity0_annotation']['decision_turn']
    decision_turn0_player2 = ann2['entity0_annotation']['decision_turn']
    match_pair0 = record_single_match(player1, player2, score0_player1, score0_player2, decision_turn0_player1, decision_turn0_player2)
    score1_player1 = int(ann1['entity1_annotation']['is_human'] == is_human1)
    score1_player2 = int(ann2['entity1_annotation']['is_human'] == is_human1)
    decision_turn1_player1 = ann1['entity1_annotation']['decision_turn']
    decision_turn1_player2 = ann2['entity1_annotation']['decision_turn']
    match_pair1 = record_single_match(player1, player2, score1_player1, score1_player2, decision_turn1_player1, decision_turn1_player2)
    return match_pair0, match_pair1


if __name__ == "__main__":
    ignore_human_bot = False
    human_bot_only = False
    for entry in get_leaderboard():
        if entry['number_of_annotations'] >= 0:
            print('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(entry['user_name'], entry['number_of_annotations'], entry['score'], entry['avg_correctness'], entry['avg_turn_penalty'], entry['elapsed_time'], entry['human_confusion'], entry['competence']))
    #user_black_list = create_black_list()
    print(user_black_list)
    convo_id_to_convo = get_all_annotated_convos()
    system_name_to_scores = compute_fools_for_system(convo_id_to_convo, ignore_human_bot, human_bot_only)
    print('\n\n')
    for system_name, scores in sorted(system_name_to_scores.items(), key=lambda x: x[0]):
        print('{}\t{}\t{}'.format(system_name ,scores[0] / scores[1], scores[2]/scores[1]))
    print('\n\n')


    system_name_to_scores = compute_fools_for_algorithm(convo_id_to_convo, ignore_human_bot, human_bot_only)
    for system_name, scores in sorted(system_name_to_scores.items(), key=lambda x: x[0]):
        print('{}\t{}\t{}\t{}'.format(system_name , scores ,scores[0] / scores[1], scores[2]/scores[1]))
    print('\n\n')
    avg_scores_for_bot = compute_average_scores_for_bot(convo_id_to_convo, ignore_human_bot, human_bot_only)
    for system_name, scores in sorted(avg_scores_for_bot.items(), key=lambda x: x[0]):
        print('{}\t{}\t{}\t{}\t{}'.format(
            system_name,
            scores[-1],
            scores[0] / scores[-1],
            scores[2] / scores[-1],
            scores[1] / scores[-1],
        ))
    print('\n\n')
    avg_scores_for_bot = compute_average_scores_for_algo(convo_id_to_convo, ignore_human_bot)
    for system_name, scores in sorted(avg_scores_for_bot.items(), key=lambda x: x[0]):
        print('{}\t{}\t{}\t{}\t{}'.format(
            system_name,
            scores[-1],
            scores[0] / scores[-1],
            scores[2] / scores[-1],
            scores[1] / scores[-1],
        ))

    print(get_is_human_agreement(convo_id_to_convo, ignore_human_bot))
