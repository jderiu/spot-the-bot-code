import numpy as np

from collections import defaultdict, Counter
from typing import Dict, List


def feature_agreement(convos: List) -> None:

    def get_feature_decision(annotation: Dict) -> str:
        if annotation['entity0_annotation'][feature] is True and annotation['entity1_annotation'][feature] is True:
            decision = 'draw'
        elif annotation['entity0_annotation'][feature] is True and annotation['entity1_annotation'][feature] is False:
            decision = 'bot_0'
        elif annotation['entity0_annotation'][feature] is False and annotation['entity1_annotation'][feature] is True:
            decision = 'bot_1'
        else:
            breakpoint()
        return decision

    features = {'fluencyValue', 'sensitivenessValue', 'specificityValue'}
    agreement_per_feature = defaultdict(list)
    annotations_per_feature = defaultdict(list)
    draw_count, annotation_count = 0, 0

    for convo in convos:

        for decision_turn, annotations in convo['annotations'].items():

            if len(annotations) != 2:  # Shouldn't happen
                continue
            for feature in features:
                decisions = [get_feature_decision(annotation) for annotation in annotations]
                # if 'draw' in decisions: continue
                draw_count += decisions.count('draw')
                annotation_count += len(decisions)
                agreement = 1 if len(set(decisions)) == 1 else 0
                agreement_per_feature[feature].append(agreement)
                annotations_per_feature[feature].extend(decisions)

    for feature, agreement in agreement_per_feature.items():
        print(f'{feature}\t{round(np.mean(agreement), 2)}\t{len(agreement)}')
    print('Annotations:', annotation_count)
    print('Draws:', draw_count, f'({round(100*draw_count / annotation_count)}%)')
    print('Draws per feature')
    for feature, annotations in annotations_per_feature.items():
        print(feature, round(100*annotations.count('draw') / len(annotations), 2), '%')
    breakpoint()


def label_agreement(convos: List) -> None:

    decision_agreements = defaultdict(list)
    decision_agreements_per_turn = defaultdict(lambda: defaultdict(list))
    label_pairs_per_bot = defaultdict(Counter)  # label_pairs[bot][(label1, label2)] = 11
    label_fractions_per_bot = defaultdict(lambda: defaultdict(list))

    label_names = {True: 'human', False: 'bot', None: 'unsure'}
    for convo in convos:

        bot_0 = convo['system_type0']  # change to system_name0 for domain-specificity
        bot_1 = convo['system_type1']

        # if not {bot_1, bot_0} == {'Human', 'Cleverbot'}: continue  # Only sample specific convos
        # if 'Cleverbot' in {bot_0, bot_1} or 'Mitsuku' in {bot_0, bot_1}: continue  # exclude certain convos

        for decision_turn, annotations in convo['annotations'].items():
            decisions_entity0, decisions_entity1 = list(), list()

            if len(annotations) != 2:
                continue

            for annotation in annotations:
                decisions_entity0.append(annotation['entity0_annotation']['is_human'])
                decisions_entity1.append(annotation['entity1_annotation']['is_human'])

            decision_agreements[bot_0].append(len(set(decisions_entity0)))
            decision_agreements[bot_1].append(len(set(decisions_entity1)))
            decision_agreements_per_turn[bot_0][decision_turn].append(len(set(decisions_entity0)))
            decision_agreements_per_turn[bot_1][decision_turn].append(len(set(decisions_entity1)))

            named_decisions_entity0 = [label_names[label] for label in decisions_entity0]
            named_decisions_entity1 = [label_names[label] for label in decisions_entity1]

            label_pairs_per_bot[bot_0][tuple(sorted(named_decisions_entity0))] += 1
            label_pairs_per_bot[bot_1][tuple(sorted(named_decisions_entity1))] += 1

            for label in named_decisions_entity0:
                agreement = 1 if set(named_decisions_entity0) == {label} else 0
                #agreement = named_decisions_entity0.count(label) / len(named_decisions_entity0)
                label_fractions_per_bot[bot_0][label].append(agreement)
            for label in named_decisions_entity1:
                agreement = 1 if set(named_decisions_entity1) == {label} else 0
                #agreement = named_decisions_entity1.count(label) / len(named_decisions_entity1)
                label_fractions_per_bot[bot_1][label].append(agreement)

    print('Label agreement per bot per turn:')
    decision_turns = sorted(decision_agreements_per_turn[list(decision_agreements_per_turn)[0]].keys())
    print('bot\t' + '\t'.join(str(t) for t in decision_turns) + '\toverall')
    for bot in decision_agreements:
        table_row = [bot]
        turn_agreements = list()
        for turn in decision_turns:
            turn_agreements.append(decision_agreements_per_turn[bot][turn].count(1) / len(decision_agreements_per_turn[bot][turn]))
        table_row.append('\t'.join(str(round(a, 2)) for a in turn_agreements))
        table_row.append(str(round(decision_agreements[bot].count(1) / len(decision_agreements[bot]), 2)))
        print('\t'.join(table_row))

    print('Percentage of annotated label pairs')
    label_pairs_set = set()
    for bot, label_pairs in label_pairs_per_bot.items():
        label_pairs_set.update(label_pairs.keys())
    label_pairs_set = sorted(label_pairs_set)
    label_pairs_str = '\t'.join('-'.join(lp) for lp in label_pairs_set)
    print('Bot\t' + label_pairs_str)
    for bot in label_pairs_per_bot:
        table_row = [bot]
        annotation_count = sum(label_pairs_per_bot[bot].values())
        for label_pair in label_pairs_set:
            table_row.append(str(round(label_pairs_per_bot[bot][label_pair] / annotation_count, 2)))
        print('\t'.join(table_row))

    print('Agreement per label')
    label_set = sorted((label_names.values()))
    print('Bot\t' + '\t'.join(label_set))
    for bot, label_fractions in label_fractions_per_bot.items():
        table_row = [bot]
        for label in label_set:
            table_row.append(str(round(np.mean(label_fractions[label]), 2)))
        print('\t'.join(table_row))


def win_function_agreement(convos: List) -> None:
    agreement_ratios = defaultdict(list)
    for convo in convos:

        bot_0 = convo['system_type0']
        bot_1 = convo['system_type1']
        winners = defaultdict(list)

        for decision_turn, annotations in convo['annotations'].items():

            if len(annotations) != 2 :
                print(convo['_id'], decision_turn, annotations[0]['package_id'])
                continue

            for annotation in annotations:
                e0_ann = annotation['entity0_annotation']['is_human']
                e1_ann = annotation['entity1_annotation']['is_human']
                # Determine winner
                if e0_ann == e1_ann:
                    winner = None  # Draw
                elif e0_ann is None:  # e0 has been annotated as 'Undecided'
                    winner = bot_1 if e1_ann is True else bot_0  # else mean e1_ann = False (annotated as bot)
                elif e0_ann is True:
                    winner = bot_0  # e1_ann is either undecided or bot
                elif e0_ann is False:
                    winner = bot_1  # e0_ann is False and e1_ann is not
                else:
                    raise NotImplementedError  # Sanity check for forgotten conditions
                winners[decision_turn].append(winner)

        for decision_turn, turn_winners in winners.items():
            agreement = 1 if len(set(turn_winners)) == 1 else 0
            agreement_ratios[tuple(sorted([bot_0, bot_1]))].append(agreement)

    print('Agreement on match outcome')
    for pair, ratios in agreement_ratios.items():
        print(f'{pair}\t{np.mean(ratios)}\t{np.std(ratios)}\t{len(ratios)}')


if __name__ == '__main__':
    import sys
    sys.path.append('./')

    """
    from templates.src.segment_analysis.annotator_scores import get_all_annotated_convos
    from templates.src.segment_analysis.fooling_analysis import name_mapping_domain
    convos = get_all_annotated_convos()
    # cast convos[id]['annotations'] as dict to pickle it
    """
    import json
    convos = json.load(open('/home/don/projects/spot_the_bot/autojudge-annotation/data/sampled-dialogues-full-convai2.json'))

    label_agreement(convos)
    feature_agreement(convos)
    # win_function_agreement(convos)

    """
 "package_collection_name": "packed-dialogues-full-dailydialog",
"sampled_collection_name": "sampled-dialogues-full-dailydialog",
"labelled_collection_name": "annotated-dialogues-full-dailydialog"

"package_collection_name": "packed-dialogues-full-empathetic",
"sampled_collection_name": "sampled-dialogues-full-empathetic",
"labelled_collection_name": "annotated-dialogues-full-empathetic"

"package_collection_name": "packed-dialogues-full-convai2",
"sampled_collection_name": "sampled-dialogues-full-convai2",
"labelled_collection_name": "annotated-dialogues-full-convai2"

"package_collection_name": "packed-dialogues-full-sota",
"sampled_collection_name": "sampled-dialogues-full-sota",
"labelled_collection_name": "annotated-dialogues-full-sota",

"package_collection_name": "packed-dialogues-amt-tournament3-dailydialog",
"sampled_collection_name": "sampled-dialogues-amt-tournament3-dailydialog",
"labelled_collection_name": "annotated-dialogues-amt-tournament3-dailydialog"
    """