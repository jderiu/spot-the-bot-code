"""
Shows the pairwise winning rates.
"""
from collections import defaultdict
from templates.src.segment_analysis.annotator_scores import get_all_annotated_convos

user_black_list = ['']


def compute_naive_win_rate(convo_id_to_convo, feature=None):
    pairs_to_win_score = defaultdict(lambda: [0, 0])
    for cid, convo in convo_id_to_convo.items():
        system_name0 = convo['system_type0']
        system_name1 = convo['system_type1']
        for tid, annotations in convo['annotations'].items():
            for annotation in annotations:
                if feature is None:
                    win_score = compute_naive_winner_for_annotation(annotation)
                elif feature == 'ssa':
                    win_score = compute_naive_winner_for_ssa_annotation(annotation)
                else:
                    win_score = compute_naive_winner_for_feature_annotation(annotation, feature)

                if  win_score == 1:
                    pairs_to_win_score[system_name0, system_name1][0] += 1
                elif win_score == -1:
                    pairs_to_win_score[system_name1, system_name0][0] += 1
                pairs_to_win_score[system_name1, system_name0][1] += 1
                pairs_to_win_score[system_name0, system_name1][1] += 1
    return pairs_to_win_score


def compute_naive_winner_for_annotation(annotation):
    score0 = 0
    if annotation['entity0_annotation']['is_human'] is True:
        score0 = 2
    elif annotation['entity0_annotation']['is_human'] is None:
        score0 = 1

    score1 = 0
    if annotation['entity1_annotation']['is_human'] is True:
        score1 = 2
    elif annotation['entity1_annotation']['is_human'] is None:
        score1 = 1

    if score0 > score1:
        return 1
    elif score1 > score0:
        return -1
    else:
        return 0


def compute_naive_winner_for_feature_annotation(annotation, feature):
    human0_pred = annotation['entity0_annotation'][feature]
    human1_pred = annotation['entity1_annotation'][feature]

    if human0_pred and not human1_pred:
        return 1
    elif not human0_pred and human1_pred:
        return -1
    else:
        return 0

def compute_naive_winner_for_ssa_annotation(annotation):
    sensiblenessValue0 = annotation['entity0_annotation']['sensitivenessValue']
    sensiblenessValue1 = annotation['entity1_annotation']['sensitivenessValue']

    specificityValue0 = annotation['entity0_annotation']['specificityValue']
    specificityValue1 = annotation['entity1_annotation']['specificityValue']

    if sensiblenessValue0 and specificityValue0 and not sensiblenessValue1 and not specificityValue1:
        return 1
    elif sensiblenessValue1 and specificityValue1 and not specificityValue0 and not specificityValue0:
        return -1
    else:
        return 0

def compute_winner_for_annotation(annotations):
    ent0_score = 0
    ent1_score = 0

    ent0_wins = 0
    ent1_wins = 0

    for annotation in annotations:
        match_score0, match_score1 = 0, 0
        human0_pred = annotation['entity0_annotation']['is_human']
        human1_pred = annotation['entity1_annotation']['is_human']

        if human0_pred is True:
            match_score0 = 2
        elif human0_pred is None:
            match_score0 = 1

        if human1_pred is True:
            match_score1 = 2
        elif human1_pred is None:
            match_score1 = 1

        ent0_score += match_score0
        ent1_score += match_score1

        if match_score0 > match_score1:
            ent0_wins += 1
        elif match_score1 > match_score0:
            ent1_wins += 1

    if ent0_wins > ent1_wins:
        return 1
    elif ent1_wins > ent0_wins:
        return -1
    else:
        if ent0_score > ent1_score:
            return 1
        elif ent1_score > ent0_score:
            return -1
        else:
            return 0


def compute_winner_for_feature_annotations(annotations, feature):
    ent0_score = 0
    ent1_score = 0

    ent0_wins = 0
    ent1_wins = 0

    for annotation in annotations:
        match_score0, match_score1 = 0, 0
        human0_pred = annotation['entity0_annotation'][feature]
        human1_pred = annotation['entity1_annotation'][feature]

        if human0_pred and not human1_pred:
            match_score0 = 2
        elif human0_pred and human1_pred:
            match_score0 = 1
            match_score1 = 1
        elif human1_pred and not human0_pred:
            match_score1 = 2

        ent0_score += match_score0
        ent1_score += match_score1

        if match_score0 > match_score1:
            ent0_wins += 1
        elif match_score1 > match_score0:
            ent1_wins += 1

    if ent0_wins > ent1_wins:
        return 1
    elif ent1_wins > ent0_wins:
        return -1
    else:
        if ent0_score > ent1_score:
            return 1
        elif ent1_score > ent0_score:
            return -1
        else:
            return 0


def compute_ssa_winner_annotation(annotations):
    ent0_score = 0
    ent1_score = 0

    ent0_wins = 0
    ent1_wins = 0

    for annotation in annotations:
        match_score0, match_score1 = 0, 0
        sensiblenessValue0 = annotation['entity0_annotation']['sensitivenessValue']
        sensiblenessValue1 = annotation['entity1_annotation']['sensitivenessValue']

        specificityValue0 = annotation['entity0_annotation']['specificityValue']
        specificityValue1 = annotation['entity1_annotation']['specificityValue']

        if sensiblenessValue0 and specificityValue0 and not sensiblenessValue1 and not specificityValue1:
            match_score0 = 2
        elif sensiblenessValue1 and specificityValue1 and not specificityValue0 and not specificityValue0:
            match_score1 = 2
        else:
            match_score0 = 1
            match_score1 = 1

        ent0_score += match_score0
        ent1_score += match_score1

        if match_score0 > match_score1:
            ent0_wins += 1
        elif match_score1 > match_score0:
            ent1_wins += 1

    if ent0_wins > ent1_wins:
        return 1
    elif ent1_wins > ent0_wins:
        return -1
    else:
        if ent0_score > ent1_score:
            return 1
        elif ent1_score > ent0_score:
            return -1
        else:
            return 0


def compute_winner_for_convo(convo, feature=None):
    ent0_wins = 0
    ent1_wins = 0
    for tid, annotations in convo['annotations'].items():
        if feature is None:
            win_id = compute_winner_for_annotation(annotations)
        elif feature == 'ssa':
            win_id = compute_ssa_winner_annotation(annotations)
        else:
            win_id = compute_winner_for_feature_annotations(annotations, feature)
        if win_id == 1:
            ent0_wins += tid
        elif win_id == -1:
            ent1_wins += tid

    if ent0_wins > ent1_wins:
        return 1
    elif ent1_wins > ent0_wins:
        return -1
    else:
        return 0


def compute_pairwise_wins(convo_id_to_convo, feature=None):
    pairs_to_win_score = defaultdict(lambda: [0, 0])
    for cid, convo in convo_id_to_convo.items():
        system_name0 = convo['system_type0']
        system_name1 = convo['system_type1']

        if system_name0 == 'human' or system_name1 == 'human':
            continue

        win_score = compute_winner_for_convo(convo, feature=feature)
        if win_score == 1:
            pairs_to_win_score[system_name0, system_name1][0] += 1

        elif win_score == -1:
            pairs_to_win_score[system_name1, system_name0][0] += 1
        pairs_to_win_score[system_name1, system_name0][1] += 1
        pairs_to_win_score[system_name0, system_name1][1] += 1
    return pairs_to_win_score


def print_result(convo_id_to_convo, naive=False, feature=None):
    if not naive:
        pairs_to_win_score = compute_pairwise_wins(convo_id_to_convo, feature=feature)
    else:
        pairs_to_win_score = compute_naive_win_rate(convo_id_to_convo, feature=feature)
    system_names = sorted(list(set([x[0] for x in pairs_to_win_score.keys()])))
    print('\t'.join([''] + system_names))
    for system_name0 in system_names:
        oline = system_name0
        for system_name1 in system_names:
            if system_name0 == system_name1:
                oline += '\t'
            else:
                nwins, nann = pairs_to_win_score[system_name0, system_name1]
                nlosses, _ = pairs_to_win_score[system_name1, system_name0]
                if nlosses + nwins > 0:
                    oline += '\t{:10.2f}'.format(nwins / (nlosses + nwins))
                else:
                    oline += '\t{}'.format('-')
        print(oline)
    print('\n\n')

if __name__ == "__main__":
    # user_black_list = create_black_list()
    convo_id_to_convo = get_all_annotated_convos(ignore_humans=True, apply_blacklist=False)

    naive = True
    print_result(convo_id_to_convo, naive, None)
    print_result(convo_id_to_convo, naive, 'ssa')
    print_result(convo_id_to_convo, naive, 'fluencyValue')
    print_result(convo_id_to_convo, naive, 'sensitivenessValue')
    print_result(convo_id_to_convo, naive, 'specificityValue')
