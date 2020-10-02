"""
Computes how well the annotators perform the task.
"""

from templates.src.scoring_utils import labelled_collection, sampled_collection, package_collection
from bson import ObjectId
from collections import defaultdict, Counter
user_black_list = ['']


def get_all_annotated_convos(ignore_humans=False, apply_blacklist=True):
    if apply_blacklist:
        annotation_id_blacklist = get_package_annotations()
    else:
        annotation_id_blacklist = ['']
    annotation_results = [res for res in labelled_collection.find({'user_name': {'$nin': user_black_list}, '_id': {'$nin': annotation_id_blacklist}})]
    oids = [ObjectId(ann['convo_id']) for ann in annotation_results]
    convo_results = sampled_collection.find({'_id': {'$in': oids}})

    convo_id_to_convo = {}  # make it searchable
    for convo in convo_results:
        system_name0 = convo['system_type0']
        system_name1 = convo['system_type1']

        if ignore_humans and (system_name0 == 'human' or system_name1 == 'human'):
            #print('Ignore Human')
            continue
        else:
            convo['annotations'] = defaultdict(lambda: [])
            convo_id_to_convo[str(convo['_id'])] = convo

    for annotation in annotation_results:
        annotation['_id'] = str(annotation['_id'])
        convo_id = annotation['convo_id']
        convo = convo_id_to_convo.get(convo_id, None)
        if convo is not None:
            turn_nr = int((annotation['entity0_annotation']['decision_turn'])/2)
            convo['annotations'][turn_nr].append(annotation)

    return convo_id_to_convo

def get_package_annotations():
    results = labelled_collection.aggregate(pipeline=[
        {
            "$group": {
                "_id": {"pid": "$package_id", "uid": "$user_name"},
                "convos": {"$addToSet": "$convo_id"}
            }
        }
    ])

    pres = package_collection.find({})
    pid_to_cids = {str(p['_id']): set([c['convo_id'] for c in p['package'] ])for p in pres}

    annotation_blacklist = []
    for res in results:
        pid = res['_id']['pid']
        convo_ids = set(res['convos'])
        if pid_to_cids.get(pid, None) is None:
            continue
        expected_ids = set(pid_to_cids[pid])

        if not convo_ids == expected_ids:
            annotation_blacklist.append(res['_id'])

    annotation_id_blacklist = []
    for entry in annotation_blacklist:
        annotations = labelled_collection.find({'package_id': entry['pid'], 'user_name': entry['uid']})
        aids = [annotation['_id'] for annotation in annotations]

        annotation_id_blacklist.extend(aids)

    return annotation_id_blacklist


def compute_agreement_for_annotation(annotations, feature='is_human'):
    ent0_ann = set()
    ent1_ann = set()
    for annotation in annotations:
        ann0 = annotation['entity0_annotation'][feature]
        ann1 = annotation['entity1_annotation'][feature]

        ent0_ann.add(ann0)
        ent1_ann.add(ann1)
    #we expect that if all agree, that a set has only one element
    agreement0 = int(len(ent0_ann) == 1)
    agreement1 = int(len(ent1_ann) == 1)

    #agreement score, number of annotations
    return agreement0 + agreement1, 2


def compute_convo_agreement(convo_id_to_convo, feature='is_human'):
    agreement_score, total_annotations = 0, 0
    for cid, convo in convo_id_to_convo.items():
        for tid, annotations in convo['annotations'].items():
            ascore, n = compute_agreement_for_annotation(annotations, feature)
            agreement_score += ascore
            total_annotations += n
    return agreement_score, total_annotations, agreement_score/total_annotations


def annotator_score(convo_id_to_convo):
    correctness_score = defaultdict(lambda : [0, 0])
    for cid, convo in convo_id_to_convo.items():
        is_human0 = convo['is_human0']
        is_human1 = convo['is_human1']
        for tid, annotations in convo['annotations'].items():
            for annotation in annotations:
                ann0 = annotation['entity0_annotation']['is_human']
                ann1 = annotation['entity1_annotation']['is_human']
                user_name = annotation['user_name']
                if ann0 is not None:
                    correctness_score[user_name][0] += int(ann0 == is_human0)
                    correctness_score[user_name][1] += 1
                if ann1 is not None:
                    correctness_score[user_name][0] += int(ann1 == is_human1)
                    correctness_score[user_name][1] += 1

    correctness_rate_for_user = {}
    for user, scores in correctness_score.items():
        correctness_rate_for_user[user] = scores[0]/scores[1]
    return correctness_rate_for_user


def label_distribution_for_annotator(convo_id_to_convo):
    distribution_for_user = defaultdict(lambda: defaultdict(lambda : 0))
    for cid, convo in convo_id_to_convo.items():
        for tid, annotations in convo['annotations'].items():
            for annotation in annotations:
                ann0 = annotation['entity0_annotation']['is_human']
                ann1 = annotation['entity1_annotation']['is_human']
                user_name = annotation['user_name']
                distribution_for_user[user_name][ann0] += 1
                distribution_for_user[user_name][ann1] += 1

    distribution_rate_for_user = defaultdict(lambda: defaultdict(lambda : 0))
    for user, ratio in distribution_for_user.items():
        total = sum(ratio.values())
        for label, val in ratio.items():
            r = val/total
            distribution_rate_for_user[user][label] = r
    return distribution_rate_for_user


def unfinished_packets():
    annotation_id_blacklist = get_package_annotations()
    annotation_results = [res for res in labelled_collection.find({'_id': {'$nin': annotation_id_blacklist}})]
    package_ids = set([(res['package_id'], res['user_name'])for res in annotation_results])
    expected_pids = set([str(res['_id']) for res in package_collection.find({})])

    pid_cnt = Counter()
    for pid, uid in package_ids:
        pid_cnt.update([pid])
    for pid, cnt in pid_cnt.items():
        if cnt != 2:
            print(pid, cnt)
    rest = expected_pids.difference(pid_cnt.keys())
    for pid in rest:
        print(pid, 0)

if __name__ == "__main__":
    annotation_id_blacklist = get_package_annotations()
    convo_id_to_convo = get_all_annotated_convos(ignore_humans=False)
    print(compute_convo_agreement(convo_id_to_convo))
    print(compute_convo_agreement(convo_id_to_convo, feature='fluencyValue'))
    print(compute_convo_agreement(convo_id_to_convo, feature='sensitivenessValue'))
    print(compute_convo_agreement(convo_id_to_convo, feature='specificityValue'))
    correctness_rate_for_user = annotator_score(convo_id_to_convo)
    for user, rate in correctness_rate_for_user.items():
        print(user, rate)

    distribution_rate_for_user = label_distribution_for_annotator(convo_id_to_convo)
    for user, rate in distribution_rate_for_user.items():
        print(user, rate)

    unfinished_packets()