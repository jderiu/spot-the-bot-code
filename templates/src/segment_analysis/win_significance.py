from templates.src.segment_analysis.win_function import compute_pairwise_wins, compute_naive_win_rate
from templates.src.segment_analysis.annotator_scores import get_all_annotated_convos
from scipy.stats import binom_test, chi2_contingency
import itertools
from collections import defaultdict
import random
import numpy as np

def create_random_annotations(convo_id_to_convo):
    random_cid_to_convo = {}
    pairs_to_win_score = compute_pairwise_wins(convo_id_to_convo, feature=None)
    system_names = sorted(list(set([x[0] for x in pairs_to_win_score.keys()])))
    cid = 0
    for i in range(10000):
        for system_name in system_names:
            for system_name_other in set(system_names).difference([system_name]):
                convo = {}
                convo['system_type0'] = system_name
                convo['system_type1'] = system_name_other
                tid_to_annotation = {}
                for tid in [2,3, 5]:
                    annotations = []
                    for _ in range(2):
                        annotation = {}
                        annotation['entity0_annotation'] = {}
                        annotation['entity1_annotation'] = {}
                        annotation['entity0_annotation']['is_human'] = random.choice([True, False, None])
                        annotation['entity1_annotation']['is_human'] = random.choice([True, False, None])
                        annotations.append(annotation)
                    tid_to_annotation[tid] = annotations
                convo['annotations'] = tid_to_annotation
                random_cid_to_convo[cid] = convo
                cid += 1

    return random_cid_to_convo


def compute_significane_rate(convo_id_to_convo, naive=False, feature=None, verbose=False):
    if not naive:
        pairs_to_win_score = compute_pairwise_wins(convo_id_to_convo, feature=feature)
    else:
        pairs_to_win_score = compute_naive_win_rate(convo_id_to_convo, feature=feature)
    total_significance = 0
    n_pairs = 0
    system_names = sorted(list(set([x[0] for x in pairs_to_win_score.keys()])))

    for system_name, system_name_other in itertools.combinations(system_names, r=2):
        wins = pairs_to_win_score[system_name, system_name_other][0]
        losses = pairs_to_win_score[system_name_other, system_name][0]
        total = pairs_to_win_score[system_name, system_name_other][1]
        tie = total - wins - losses

        contingency_talbe = np.array([[wins, losses], [total - wins, total -losses]])

        #pval_win = binom_test(x=[tie, total-tie], p= 1, alternative='less')
        #pval_loss = binom_test(x=[losses, losses + wins], p= 1/ 2, alternative='two-sided')
        chi2, p, dof, expected = chi2_contingency(contingency_talbe)
        if verbose:
            print(system_name, system_name_other, p)

        total_significance += int(p < 0.05)
        n_pairs += 1

    return total_significance / n_pairs


def get_system_names_from_dict(convo_id_to_convo):
    system_names = set()
    for cid, convo in convo_id_to_convo.items():
        system_names.add(convo['system_type0'])
        system_names.add(convo['system_type1'])

    return list(system_names)


def reduced_dict(convo_id_to_convo, system_names):
    reduced_cid_to_convo = {}
    for cid, convo in convo_id_to_convo.items():
        if convo['system_type0'] in system_names and convo['system_type1'] in system_names:
            reduced_cid_to_convo[cid] = convo
    return reduced_cid_to_convo


def sample_convos_for_bot_pair(convo_id_to_convo, sij):
    pair_to_convos = defaultdict(lambda : [])
    for cid, convo in convo_id_to_convo.items():
        system_type0 = convo['system_type0']
        system_type1 = convo['system_type1']
        if pair_to_convos.get((system_type0, system_type1)) is None and pair_to_convos.get((system_type1, system_type0)) is None:
            pair_to_convos[system_type0, system_type1].append(convo)
        elif pair_to_convos.get((system_type0, system_type1)) is not None:
            pair_to_convos[system_type0, system_type1].append(convo)
        elif pair_to_convos.get((system_type1, system_type0)) is not None:
            pair_to_convos[system_type1, system_type0].append(convo)

    #sample sij convos for each pair
    sampled_convo_id_to_convo = {}
    for system_pair, convos in pair_to_convos.items():
        sampled_convos = random.sample(convos, k=sij)
        for convo in sampled_convos:
            sampled_convo_id_to_convo[str(convo['_id'])] = convo

    return sampled_convo_id_to_convo



def average_significance_for_reduced(convo_id_to_convo, sij, feature=None, naive=False):
    repetitions = 1000
    total_rate = 0
    for _ in range(repetitions):
        sampled_convo_id_to_convo = sample_convos_for_bot_pair(convo_id_to_convo, sij)
        total_rate += compute_significane_rate(sampled_convo_id_to_convo, feature=feature, naive=naive)
    return total_rate/repetitions

def average_significance_rate(convo_id_to_convo, b, sij, feature=None, naive=False):
    system_names = get_system_names_from_dict(convo_id_to_convo)

    total_rate = 0
    combos = list(itertools.combinations(system_names, b))
    for system_subset in combos:
        reduced_convo_id_to_convo = reduced_dict(convo_id_to_convo, set(system_subset))
        total_rate += average_significance_for_reduced(reduced_convo_id_to_convo, sij, naive=naive, feature=feature)

    return total_rate/len(combos)

if __name__ == "__main__":
    #user_black_list = create_black_list()
    feature='ssa'
    convo_id_to_convo = get_all_annotated_convos(ignore_humans=True)
    naive = False
    print(compute_significane_rate(convo_id_to_convo, feature=feature, naive=naive, verbose=True))

    pairs_to_win_score = compute_naive_win_rate(convo_id_to_convo, feature=feature,)
    system_names = sorted(list(set([x[0] for x in pairs_to_win_score.keys()])))
    print('\t'.join([''] + system_names))
    for system_name0 in system_names:
        oline = system_name0
        for system_name1 in system_names:
            if system_name0 == system_name1:
                oline += '\t'
            else:
                nwins, nann = pairs_to_win_score[system_name0, system_name1]
                nlosses, nann = pairs_to_win_score[system_name1, system_name0]
                if nann > 0:
                    oline += '\t{}'.format(nwins / (nlosses +nwins))
                    #oline += '\t{}/{}'.format(nwins, (nlosses +nwins))
                    #oline += '\t{}/{}'.format(nwins, nann)
                else:
                    oline += '\t{}'.format('-')
        print(oline)
    print('\n\n')

    for sij in range(10, 45):
        rate = average_significance_rate(convo_id_to_convo, b=4, sij=sij, naive=naive, feature=feature)
        print('{}\t{}'.format(sij, rate))