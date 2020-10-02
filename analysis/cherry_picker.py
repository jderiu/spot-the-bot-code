import random
from typing import Dict, Union, Optional
from collections import defaultdict
import random


def cherry_pick(convos: Dict, entity0: Optional[str] = None, entity1: Optional[str] = None) -> None:
    convo_list = list(convos.values())
    # random.shuffle(convo_list)

    for convo in convo_list:
        bot_0 = convo['system_type0']
        bot_1 = convo['system_type1']
        if entity0 and entity0 not in [bot_0, bot_1]:
            continue
        if entity1 and entity1 not in [bot_0, bot_1]:
            continue

        for exchange_id, annotations in convo['annotations'].items():
            cherry = True
            for annotation in annotations:
                # Require the full convo to be annotated as not bot in all segments by all annotators
                #if not annotation['entity0_annotation']['is_human'] is True or not annotation['entity1_annotation']['is_human'] is True:
                if annotation['entity0_annotation']['is_human'] is False or \
                        annotation['entity1_annotation']['is_human'] is False:
                    cherry = False

            if cherry and len(annotations) > 1:
                print('Annotation on exchange', exchange_id)
                for turn in convo['convo']:
                    print(turn['id'] + ':\t' + turn['text'])
                breakpoint()


def pick_example_for_segmentation(convos: Dict) -> None:
    for _, convo in convos.items():
        bot_0 = convo['system_type0']
        bot_1 = convo['system_type1']

        if bot_0 == 'human':
            continue

        # analyze annotations per segment, choose convo where annotations change
        decision_turns = sorted(convo['annotations'].keys())
        bot_0_first_annotation = convo['annotations'][decision_turns[0]][0]['entity0_annotation']['is_human']

        if bot_0_first_annotation is not False:
            bot_0_last_annotation = convo['annotations'][decision_turns[-1]][0]['entity0_annotation']['is_human']
            if bot_0_last_annotation is False:
                for decision_turn in decision_turns:
                    labels_e1 = [a['entity0_annotation']['is_human'] for a in convo['annotations'][decision_turn]]
                    labels_e2 = [a['entity1_annotation']['is_human'] for a in convo['annotations'][decision_turn]]
                    for turn in range(decision_turn*2):
                        print(convo['convo'][turn]['id'] + ':', convo['convo'][turn]['text'])
                    print(bot_0, labels_e1, bot_1, labels_e2)
                breakpoint()


def pick_segments_w_different_annotations(convos: Dict, shuffle: bool = True, max_prints: int = 10) -> None:

    if shuffle:
        convos_list = list(convos.items())
        random.shuffle(convos_list)
        convos = dict(convos_list)

    sampled_convos = defaultdict(list)

    for convo_id, convo in convos.items():
        bot_0 = convo['system_type0']
        bot_1 = convo['system_type1']

        if bot_0 == 'human':
            continue

        for decision_turn, annotations in convo['annotations'].items():

            labels_e1 = set([a['entity0_annotation']['is_human'] for a in convo['annotations'][decision_turn]])
            labels_e2 = set([a['entity1_annotation']['is_human'] for a in convo['annotations'][decision_turn]])

            if len(labels_e1) == 1 and len(labels_e2) == 1:  # Enforce annotator agreement

                if (labels_e1 == {True} and labels_e2 == {False}) or (labels_e1 == {False} and labels_e2 == {True}):

                    convo_turns = list()
                    for turn in range(decision_turn*2):
                        convo_turns.append(convo['convo'][turn]['id'] + ':\t' + convo['convo'][turn]['text'])

                    if labels_e1 == {False}:
                        sampled_convos[bot_0].append(dict(convo=convo_turns, partner=bot_1, convo_id=convo_id))
                    else:
                        sampled_convos[bot_1].append(dict(convo=convo_turns, partner=bot_0, convo_id=convo_id))

    for bot, convos in sampled_convos.items():
        convos.sort(key=lambda x: len(x['convo']), reverse=True)
        for convo in convos[:max_prints]:
            partner = convo['partner']
            print(convo['convo_id'])
            print(f'{bot} = bot\t{partner} = human')
            for turn in convo['convo']:
                print(turn)
            print()


def print_human_convos(convos: Dict, shuffle: bool = True, max_prints: int = 10) -> None:
    if shuffle:
        convos_list = list(convos.items())
        random.shuffle(convos_list)
        convos = dict(convos_list)

    for convo_id, convo in convos.items():
        bot_0 = convo['system_type0']
        bot_1 = convo['system_type1']

        if bot_0 == 'human' and bot_1 == 'human':

            print(convo_id)
            for turn in convo['convo']:
                print(turn['text'])
            print()


def pick_convos_w_developing_annotations(convos: Dict, shuffle: bool = True, max_print: int = 10) -> None:

    if shuffle:
        convos_list = list(convos.items())
        random.shuffle(convos_list)
        convos = dict(convos_list)

    printed = 0

    for convo_id, convo in convos.items():

        if printed > max_print:
            break

        bot_0 = convo['system_type0']
        bot_1 = convo['system_type1']

        if bot_0 == 'human':
            continue

        decision_turns = sorted(convo['annotations'].keys())
        label_prog_e1, label_prog_e2 = list(), list()

        for decision_turn in decision_turns:

            labels_e1 = set([a['entity0_annotation']['is_human'] for a in convo['annotations'][decision_turn]])
            labels_e2 = set([a['entity1_annotation']['is_human'] for a in convo['annotations'][decision_turn]])

            label_prog_e1.append(labels_e1)
            label_prog_e2.append(labels_e2)

        if len(label_prog_e1[0]) == 1 and list(label_prog_e1[0])[0] is not False:

            if len(label_prog_e1[1]) == 1 and list(label_prog_e1[1])[0] is False:
                print(bot_0, label_prog_e1, convo_id, '\n')
                for turn in range(min((decision_turns[-1] * 2), len(convo['convo']))):
                    print(convo['convo'][turn]['id'] + ':\t' + convo['convo'][turn]['text'])
                    if (turn + 1) / 2 in decision_turns:
                        print('-' * 10)
                print()
                printed += 1
                # breakpoint()

            elif len(label_prog_e1[-1]) == 1 and list(label_prog_e1[-1])[-1] is False:
                print(bot_0, label_prog_e1, convo_id, '\n')
                for turn in range(min((decision_turns[-1] * 2), len(convo['convo']))):
                    print(convo['convo'][turn]['id'] + ':\t' + convo['convo'][turn]['text'])
                    if (turn + 1) / 2 in decision_turns:
                        print('-' * 10)
                print()
                printed += 1
                # breakpoint()

        if len(label_prog_e2[0]) == 1 and list(label_prog_e2[0])[0] is not False:

            if len(label_prog_e2[1]) == 1 and list(label_prog_e2[1])[0] is False:
                print(bot_1, label_prog_e2, convo_id, '\n')
                for turn in range(min((decision_turns[-1] * 2) , len(convo['convo']))):
                    print(convo['convo'][turn]['id'] + ':\t' + convo['convo'][turn]['text'])
                    if (turn + 1) / 2 in decision_turns:
                        print('-' * 10)
                print()
                printed += 1
                # breakpoint()

            elif len(label_prog_e2[-1]) == 1 and list(label_prog_e2[-1])[0] is False:
                print(bot_1, label_prog_e2, convo_id, '\n')
                for turn in range(min((decision_turns[-1] * 2), len(convo['convo']))):
                    print(convo['convo'][turn]['id'] + ':\t' + convo['convo'][turn]['text'])
                    if (turn + 1) / 2 in decision_turns:
                        print('-' * 10)
                print()
                printed += 1
                # breakpoint()


if __name__ == '__main__':
    import os, sys, pickle, json
    sys.path.append('./')
    from templates.src.segment_analysis.annotator_scores import get_all_annotated_convos
    print('Downloading data')
    data = get_all_annotated_convos()

    pick_convos_w_developing_annotations(data)

    # print_human_convos(data)

    # pick_segments_w_different_annotations(data, max_prints=10)

    """
    pick_example_for_segmentation(data)

    e1 = 'bert_rank'
    e2 = 'huggingface'
    # Specifiy desired annotations
    ann1 = True  # True = human, False = bot, None = undecided
    ann2 = True
    cherry_pick(data, e1, e2, ann1, ann2)
    """