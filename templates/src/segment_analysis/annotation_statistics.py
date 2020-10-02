"""
Computes the statistics of the Annotators
"""

from templates.src.scoring_utils import labelled_collection
from templates.src.segment_analysis.annotator_scores import get_package_annotations, get_all_annotated_convos
import itertools

def get_total_annotations():
    return labelled_collection.count({})

def get_total_annotation_filtered():
    annotation_id_blacklist = get_package_annotations()

    return labelled_collection.count({'_id': {'$nin': annotation_id_blacklist}})


def number_of_annotators():
    results = labelled_collection.aggregate(pipeline=[
        {
            "$group": {
                "_id": {"uid": "$user_name"},
                "convos": {"$sum": 1}
            }
        }
    ])

    return len(list(results))


def number_of_annotators_filtered():
    annotation_id_blacklist = get_package_annotations()
    results = labelled_collection.aggregate(pipeline=[
        {
            "$match": {
                '_id': {'$nin': annotation_id_blacklist}
            }
        },
        {
            "$group": {
                "_id": {"uid": "$user_name"},
                "convos": {"$sum": 1}
            }
        }
    ])

    return len(list(results))

def average_time_per_package():
    annotation_id_blacklist = get_package_annotations()

    results_start = labelled_collection.aggregate(pipeline=[
        {
            "$match": {
                '_id': {'$nin': annotation_id_blacklist}
            }
        },
        {
            "$group": {
                "_id": {"pid": "$package_id", "uid": "$user_name"},
                "start_time": {"$min": "$start_time"}
            }
        }
    ])

    results_end = labelled_collection.aggregate(pipeline=[
        {
            "$match": {
                '_id': {'$nin': annotation_id_blacklist}
            }
        },
        {
            "$group": {
                "_id": {"pid": "$package_id", "uid": "$user_name"},
                "end_time": {"$max": "$end_time"}
            }
        }
    ])

    min_time_for_id = {(res['_id']['pid'], res['_id']['uid']): res['start_time'] for res in results_start}

    times_in_ms = []
    for result in results_end:
        pid = result['_id']['pid']
        uid = result['_id']['uid']

        end_time = result['end_time']

        if min_time_for_id.get((pid, uid), None) is not None:
            start_time = min_time_for_id[(pid, uid)]
            times_in_ms.append(end_time-start_time)

    sorted_times = sorted(times_in_ms)
    if (len(sorted_times)%2) == 0:
        idx = int(len(sorted_times)/2)
        return (sorted_times[idx] + sorted_times[idx-1])/2
    else:
        idx = int((len(sorted_times) - 1)/2)
        return sorted_times[idx]


def median_time_per_annotation():
    annotation_id_blacklist = get_package_annotations()

    results = labelled_collection.aggregate(pipeline=[
        {
            "$match": {
                '_id': {'$nin': annotation_id_blacklist}
            }
        },
        {
            "$group": {
                "_id": "dummy",
                "elapsed_times": {"$addToSet": "$elapsed_time"}
            }
        }
    ])
    elapsed_times = list(results)[0]['elapsed_times']
    sorted_elapsed_times = sorted(elapsed_times)

    if (len(sorted_elapsed_times) % 2) == 0:
        idx = int(len(sorted_elapsed_times) / 2)
        return (sorted_elapsed_times[idx] + sorted_elapsed_times[idx - 1]) / 2
    else:
        idx = int((len(sorted_elapsed_times) - 1) / 2)
        return sorted_elapsed_times[idx]


def total_time():
    annotation_id_blacklist = get_package_annotations()

    results = labelled_collection.aggregate(pipeline=[
        {
            "$match": {
                '_id': {'$nin': annotation_id_blacklist}
            }
        },
        {
            "$group": {
                "_id": "dummy",
                "total_time": {"$sum": "$elapsed_time"}
            }
        }
    ])
    total_time = list(results)[0]['total_time']
    #convert to hrs
    return total_time/1000/60/60


def annotator_agreement(feature='is_human'):
    convo_id_to_convo = get_all_annotated_convos(ignore_humans=False)
    total = 0
    agreements = 0
    for cid, convo in convo_id_to_convo.items():
        annotations = convo['annotations']
        for tid, annotation_list in annotations.items():
            combos = list(itertools.combinations(annotation_list, 2))
            for c1, c2 in combos:
                if feature=='is_human':
                    p0 = c1['entity0_annotation'][feature]
                    p1 = c2['entity0_annotation'][feature]
                    agreements += int(p0 == p1)

                    p0 = c1['entity1_annotation'][feature]
                    p1 = c2['entity1_annotation'][feature]
                    agreements += int(p0 == p1)
                    total += 2
                else:
                    entity0_annotation1 = c1['entity0_annotation'][feature]
                    entity0_annotation2 = c2['entity0_annotation'][feature]

                    entity1_annotation1 = c1['entity1_annotation'][feature]
                    entity1_annotation2 = c2['entity1_annotation'][feature]

                    agreements += int(entity0_annotation1 == entity0_annotation2 and entity1_annotation1 == entity1_annotation2)
                    total += 1

    return agreements/total

if __name__ == "__main__":
    print('Number of Annotations Raw:\t{}'.format(get_total_annotations()))
    print('Number of Annotations Filtered:\t{}'.format(get_total_annotation_filtered()))
    print('Number of Annotators:\t{}'.format(number_of_annotators()))
    print('Number of Annotators Filtered:\t{}'.format(number_of_annotators_filtered()))
    print('Median Time per HIT:\t{}'.format(average_time_per_package()))
    print('Median Time per Annotation:\t{}'.format(median_time_per_annotation()))
    print('Total Time:\t{}'.format(total_time()))
    print('Agreement for Spot The Bot:\t{}'.format(annotator_agreement()))
    print('Agreement for Fluency:\t{}'.format(annotator_agreement(feature='fluencyValue')))
    print('Agreement for Sensibleness:\t{}'.format(annotator_agreement(feature='sensitivenessValue')))
    print('Agreement for Specificity:\t{}'.format(annotator_agreement(feature='specificityValue')))