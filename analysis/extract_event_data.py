
from templates.src.scoring_utils import (
    get_annotator_names,
    get_annotations_for_user,
    get_annotated_convos_for_user,
    combine_annotations_and_convos_for_user,
    create_black_list
)
from templates.src.segment_analysis.annotator_scores import get_all_annotated_convos
from templates.src.segment_analysis.fooling_analysis import name_mapping_domain


import pandas as pd
import numpy as np


def convo_type(system1, system2):
    if (system1 == 'human') and (system2 == 'human'):
        return 'human-human'
    elif (system1 == 'human') or (system2 == 'human'):
        return 'human-bot'
    else:
        return 'bot-bot'


def turn_to_n_utterances(n_turns, bot_num):
    if bot_num == 0:
        return int((n_turns + 1) / 2)
    elif bot_num == 1:
        return int(n_turns / 2)
    else:
        raise ValueError(f"unknown entity number {bot_num}, use one of {{0, 1}}")


def spotted(is_human_annotation):
    def survived(a):
        if a in {True, None}:
            return True
        else:
            return False

    return not survived(is_human_annotation)


def feature_annotation_to_num(ann0, ann1):

    if ann0 and ann1:
        return 0, 0
    elif ann0 and (not ann1):
        return 1, -1
    elif (not ann0) and ann1:
        return -1, 1
    else:
        raise ValueError(f"this shouldn't happen: {ann0} {ann1}")


def fetch_event_data():
    annotator_info = get_annotator_names()

    raw = []
    for name in annotator_info:
        for _, (annotation, convo) in combine_annotations_and_convos_for_user(
            get_annotations_for_user(name),
            get_annotated_convos_for_user(annotator_info[name]),
        ).items():
            entry0 = {
                'user': name,
                'convo_id': annotation['convo_id'],
                'convo_type': convo_type(convo['system_type0'], convo['system_type1']),
                'system': convo['system_type0'],
                'domain': convo['domain_name'],
                'domain_system': convo['domain_name'] + '/' + convo['system_type0'],
                # 'spotted': int(not annotation['entity0_annotation']['is_human']),
                'spotted': spotted(annotation['entity0_annotation']['is_human']),
                'time': turn_to_n_utterances(annotation['entity0_annotation']['decision_turn'], bot_num=0),
                'fluency': int(annotation['entity0_annotation']['fluencyValue']),
                'sensible': int(annotation['entity0_annotation']['sensitivenessValue']),
                'specific': int(annotation['entity0_annotation']['specificityValue']),
            }
            entry1 = {
                'user': name,
                'convo_id': annotation['convo_id'],
                'convo_type': convo_type(convo['system_type0'], convo['system_type1']),
                'system': convo['system_type1'],
                'domain': convo['domain_name'],
                'domain_system': convo['domain_name'] + '/' + convo['system_type1'],
                # 'spotted': int(not annotation['entity1_annotation']['is_human']),
                'spotted': spotted(annotation['entity1_annotation']['is_human']),
                'time': turn_to_n_utterances(annotation['entity1_annotation']['decision_turn'], bot_num=1),
                'fluency': int(annotation['entity1_annotation']['fluencyValue']),
                'sensible': int(annotation['entity1_annotation']['sensitivenessValue']),
                'specific': int(annotation['entity1_annotation']['specificityValue']),
            }

            raw.append(entry0)
            raw.append(entry1)

    return pd.DataFrame.from_records(raw)


class IDMapping:

    def __getitem__(self, item):
        return item


def fetch_segmented(name_mapping=IDMapping()):
    data = get_all_annotated_convos()

    records = []
    for convo_data in data.values():
        system0 = name_mapping[convo_data['system_type0']]
        system1 = name_mapping[convo_data['system_type1']]
        for exchange, annotations in convo_data['annotations'].items():
            for ann in annotations:

                fluent0, fluent1 = feature_annotation_to_num(
                    ann['entity0_annotation']['fluencyValue'],
                    ann['entity1_annotation']['fluencyValue'],
                )
                sensible0, sensible1 = feature_annotation_to_num(
                    ann['entity0_annotation']['sensitivenessValue'],
                    ann['entity1_annotation']['sensitivenessValue'],
                )
                specific0, specific1 = feature_annotation_to_num(
                    ann['entity0_annotation']['specificityValue'],
                    ann['entity1_annotation']['specificityValue'],
                )

                spotted0 = spotted(ann['entity0_annotation']['is_human'])
                entry0 = {
                    'time_left': 0 if spotted0 else exchange,
                    'time_right': exchange if spotted0 else np.inf,
                    'censor_type': 3 if spotted0 else 0,  #  for R, 0 means right censored, 3 means interval censored
                    'system': system0,
                    'fluent': fluent0,
                    'sensible': sensible0,
                    'specific': specific0,

                }

                spotted1 = spotted(ann['entity1_annotation']['is_human'])
                entry1 = {
                    'time_left': 0 if spotted1 else exchange,
                    'time_right': exchange if spotted1 else np.inf,
                    'censor_type': 3 if spotted1 else 0,
                    'system': system1,
                    'fluent': fluent1,
                    'sensible': sensible1,
                    'specific': specific1,
                }

                records.append(entry0)
                records.append(entry1)

    frame = pd.DataFrame.from_records(records)

    sys_map = {sys: ix for ix, sys in enumerate(frame.system.unique())}
    frame['system_id'] = frame.system.apply(lambda sys: sys_map[sys])

    return frame


def export_to_csv(path):
    black_list = create_black_list()

    data = fetch_event_data()
    data = data[~data['user'].isin(black_list)]

    data['last_alive'] = data.time * ~data.spotted
    data['seen_dead'] = data.time * data.spotted
    data['event_type'] = 3 * data.spotted

    out = data[['last_alive', 'seen_dead', 'event_type', 'system']]

    out.to_csv(path)


if __name__ == '__main__':
    df = fetch_segmented()
    df.to_csv('event_data.csv')

