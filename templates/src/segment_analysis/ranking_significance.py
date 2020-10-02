from templates.src.segment_analysis.win_significance import sample_convos_for_bot_pair
from templates.src.mongo_client import SAMPLED_COLLECTION_NAME
from templates.src.segment_analysis.segmented_bootstrap_sampling import bootstrap_sampling, get_all_annotated_convos, create_set_of_matches
from itertools import combinations
from collections import defaultdict, Counter
from tqdm import tqdm
import multiprocessing
import argparse
import os
import itertools


from datetime import datetime

convo_id_to_convo = get_all_annotated_convos(ignore_humans=True)

def get_list_of_systems():
    systems = set()
    for convo in convo_id_to_convo.values():
        s0 = convo['system_type0']
        s1 = convo['system_type1']

        systems.update([s0, s1])
    return systems

def range_overlap(range0, range1):
    if range0[1] < range1[0] or range1[1] < range0[0]:
        return False
    else:
        return True

def get_range_cluster(overlap_for_pair, system, assigned_systems):
    cluster = set()
    overlapping_systems = get_overlapping_systems_for_system(overlap_for_pair, system)
    #if there is no change in the assigned systems return
    if overlapping_systems.union(assigned_systems) == assigned_systems:
        return overlapping_systems
    assigned_systems = overlapping_systems.union(assigned_systems)
    cluster = overlapping_systems.union(cluster)
    for osystem in overlapping_systems:
        overlapping_systems = get_range_cluster(overlap_for_pair, osystem, assigned_systems)
        assigned_systems = assigned_systems.union(overlapping_systems)
        cluster = overlapping_systems.union(cluster)
    return cluster


def get_overlapping_systems_for_system(overlap_for_pair, system):
    overlapping_systems = set()
    for other_system, overlap in overlap_for_pair[system].items():
        if overlap:
            overlapping_systems.add(other_system)
    return overlapping_systems


def create_clusters(rank_range_for_system):
    overlap_for_pair = defaultdict(lambda : defaultdict(lambda : False))
    systems = list(rank_range_for_system.keys())
    lower_bound_to_bots = defaultdict(lambda : set())
    for system0, system1 in combinations(systems, r=2):
        range0 = rank_range_for_system[system0]
        range1 = rank_range_for_system[system1]
        overlap = range_overlap(range0, range1)
        overlap_for_pair[system0][system1] = overlap
        overlap_for_pair[system1][system0] = overlap
        lower_bound_to_bots[range0[0]].add(system0)
        lower_bound_to_bots[range1[0]].add(system1)

    assigned_systems = set()
    clusters = []
    for i in range(len(systems)):
        range_systems = lower_bound_to_bots.get(i, None)
        if range_systems is None:
            continue
        overlapping_systems = set()
        for system in range_systems:
            cluster = get_range_cluster(overlap_for_pair, system, {s for s in assigned_systems})
            cluster.add(system)
            if assigned_systems.union(cluster) == assigned_systems:
                continue
            assigned_systems = assigned_systems.union(cluster)
            overlapping_systems = overlapping_systems.union(cluster)

        if len(overlapping_systems) > 0:
            clusters.append(overlapping_systems)
    return clusters


def reduced_dict(convo_id_to_convo, system_names):
    reduced_cid_to_convo = {}
    for cid, convo in convo_id_to_convo.items():
        if convo['system_type0'] in system_names or convo['system_type1'] in system_names:
            continue

        reduced_cid_to_convo[cid] = convo
    return reduced_cid_to_convo

def leave_out_significance(args):
    repetitions, rep, n_samples, trueskill, naive, leave_n_out, feature, ps = args
    system_names = get_list_of_systems()

    #all combinations of system-sets to leave out
    combos = list(itertools.combinations(system_names, leave_n_out))
    date_time = datetime.now().strftime("%Y%m%d-%H%M%S")

    with open(os.path.join('data', 'rank_significance', 'output-{}.txt'.format(date_time)), 'wt', encoding='utf-8') as ofile:
        ofile.write('Sig Repetitions\t{}\n'.format(sig_repetitions))
        ofile.write('Sample Repetitions\t{}\n'.format(sample_repetitions))
        ofile.write('Number of Samples\t{}\n'.format(n_samples))
        ofile.write('Use TrueSkill\t{}\n'.format(trueskill))
        ofile.write('Use Naive\t{}\n'.format(naive))
        ofile.write('Levae Out\t{}\n'.format(leave_n_out))
        ofile.write('Pool Size\t{}\n'.format(ps))
        ofile.write('Feature\t{}\n'.format(feature))
        ofile.write('Domain\t{}\n'.format(SAMPLED_COLLECTION_NAME))

        for system_subset in combos:
            ofile.write(', '.join(list(system_subset)) + '\n')
            ofile.flush()
            rep_args = [(i, repetitions, rep, n_samples, trueskill, naive, system_subset, feature) for i in range(3, 45, 1)]
            pool = multiprocessing.Pool(ps)
            outputs = pool.map(repeat_ranking, rep_args)
            pool.close()
            for op in outputs:
                ofile.write('{}\t{}\n'.format(op[0], op[1]))
            ofile.flush()


def repeat_ranking(args):
    sij, repetitions, rep, n_samples, trueskill, naive, leave_out, feature = args
    print('Start:', sij)
    repetitions = repetitions
    cluster_count = Counter()
    for _ in tqdm(range(repetitions)):
        if leave_out is not None:
            reduced_convo_id_to_convo = reduced_dict(convo_id_to_convo, set(leave_out))
            sampled_convo_id_to_convo = sample_convos_for_bot_pair(reduced_convo_id_to_convo, sij)
        else:
            sampled_convo_id_to_convo = sample_convos_for_bot_pair(convo_id_to_convo, sij)
        matches = create_set_of_matches(sampled_convo_id_to_convo, feature=feature)
        #matches = create_naive_matches(sampled_convo_id_to_convo, feature=None)
        rank_range_for_system, _, _ = bootstrap_sampling(matches, sampled_convo_id_to_convo, compute_scores=False, naive=naive, feature=feature, trueskill=trueskill, rep=rep, n_samples=n_samples)
        cluster = create_clusters(rank_range_for_system)
        hashable_cluster = tuple([tuple(sorted(cl)) for cl in cluster])
        cluster_count.update([hashable_cluster])
    most_common, n = sorted(cluster_count.items(), key=lambda x: x[1], reverse=True)[0]
    print('{}:\t{}\t{}'.format(sij, most_common, n/repetitions))
    print('End:',sij)
    return sij, n / repetitions

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compute Ranking Significance with respect to Number of Pairwise Conversations.')
    parser.add_argument('-r', '--repetitions', dest='repetitions', type=int, default=1000)
    parser.add_argument('-sr', '--sample-repetitions', dest='sample_repetitions', type=int, default=1000)
    parser.add_argument('-ns', '--number-samples', dest='n_samples', type=int, default=5000)
    parser.add_argument('-ts', '--true-skill', dest='trueskill', type=bool, default=False)
    parser.add_argument('-nv', '--naive', dest='naive', type=bool, default=False)
    parser.add_argument('-lo', '--leave-one-out', dest='loo', type=int, default=0)
    parser.add_argument('-f', '--feature', dest='feature', type=str, default=None)
    parser.add_argument('-ps', '--pool-size', dest='pool_size', type=int, default=2)
    args = parser.parse_args()

    sig_repetitions = args.repetitions
    sample_repetitions = args.sample_repetitions
    n_samples = args.n_samples
    trueskill = args.trueskill
    naive = args.naive
    loo = args.loo
    ps = args.pool_size
    feature = args.feature

    if loo == 0:
        #repeat_ranking(30)
        rep_args = [(i, sig_repetitions, sample_repetitions, n_samples, trueskill, naive, None, feature) for i in
                    range(3, 45, 1)]
        pool = multiprocessing.Pool(ps)
        outputs = pool.map(repeat_ranking, rep_args)
        date_time = datetime.now().strftime("%Y%m%d-%H%M%S")
        with open(os.path.join('data', 'rank_significance', 'output-{}.txt'.format(date_time)), 'wt', encoding='utf-8') as ofile:
            ofile.write('Sig Repetitions\t{}\n'.format(sig_repetitions))
            ofile.write('Sample Repetitions\t{}\n'.format(sample_repetitions))
            ofile.write('Number of Samples\t{}\n'.format(n_samples))
            ofile.write('Use TrueSkill\t{}\n'.format(trueskill))
            ofile.write('Use Naive\t{}\n'.format(naive))
            ofile.write('Pool Size\t{}\n'.format(ps))
            ofile.write('Feature\t{}\n'.format(feature))
            ofile.write('Domain\t{}\n'.format(SAMPLED_COLLECTION_NAME))
            for op in outputs:
                ofile.write('{}\t{}\n'.format(op[0], op[1]))
    else:
        leave_out_significance((sig_repetitions, sample_repetitions, n_samples, trueskill, naive, loo, feature, ps))