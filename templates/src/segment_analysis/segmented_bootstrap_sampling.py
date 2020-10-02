from templates.src.segment_analysis.win_function import compute_winner_for_convo, compute_pairwise_wins, \
    compute_naive_winner_for_feature_annotation, compute_naive_winner_for_ssa_annotation, \
    compute_naive_winner_for_annotation, compute_naive_win_rate
from templates.src.segment_analysis.annotator_scores import get_all_annotated_convos
from collections import defaultdict, Counter
import random
from trueskill import rate_1vs1, TrueSkill
import numpy as np
import trueskill


def compute_rank_range(rank_count_for_system, p=950):
    rank_range_for_system = {}
    for system, rank_count in rank_count_for_system.items():
        min_rank = min(list(rank_count.keys()))
        max_rank = max(list(rank_count.keys()))
        range_to_count = {}
        for lower_bound in range(min_rank, max_rank + 1, 1):
            for upper_bound in range(lower_bound, max_rank + 1):
                range_to_count[lower_bound, upper_bound] = 0
                for i in range(lower_bound, upper_bound + 1):
                    range_to_count[lower_bound, upper_bound] += rank_count[i]
        filtered_ranges = [rng for rng, cnt in range_to_count.items() if cnt > p]

        len_sorting = sorted(filtered_ranges, key=lambda x: x[1] - x[0])
        rank_sorted = sorted(len_sorting, key=lambda x: x[0])
        # best range? smallest range?
        best_rank = rank_sorted[0]
        rank_range_for_system[system] = best_rank
    return rank_range_for_system


def compute_win_rate_for_system(sampled_matches):
    ranking_for_sample = defaultdict(lambda: [0, 0])
    for match in sampled_matches:
        system_name0, system_name1, win0, win1 = match
        ranking_for_sample[system_name0][0] += win0
        ranking_for_sample[system_name1][0] += win1
        ranking_for_sample[system_name0][1] += 1
        ranking_for_sample[system_name1][1] += 1

    win_rates = {system_type: x[0] / x[1] for system_type, x in ranking_for_sample.items()}
    ranking = sorted(win_rates.items(), key=lambda x: x[1], reverse=True)
    return ranking


def compute_trueskill_ranking(matches):
    env = TrueSkill(0, 0.5)
    env.beta = 0.025 * (0.5 ** 2) * len(matches)
    env.tau = 0
    player_objects = defaultdict(lambda: env.create_rating())
    for match in matches:
        system_name0, system_name1, win0, win1 = match
        player0 = player_objects[system_name0]
        player1 = player_objects[system_name1]

        if win0 == 1 and win1 == 0:
            new_player0, new_player1 = rate_1vs1(player0, player1)
        elif win1 == 1 and win0 == 0:
            new_player1, new_player0 = rate_1vs1(player1, player0)
        else:
            new_player0, new_player1 = rate_1vs1(player0, player1, drawn=True)

        player_objects[system_name0] = new_player0
        player_objects[system_name1] = new_player1
    ranking = sorted(player_objects.items(), key=lambda x: x[1].mu, reverse=True)
    return ranking


def bootstrap_sampling(matches, convo_id_to_convo, compute_scores=True, naive=False, feature=None, trueskill=False, rep=1000, n_samples=5000):
    rank_count_for_system = defaultdict(lambda: Counter())
    trueskill_scores_for_system = defaultdict(lambda: 0)
    scores_for_system = defaultdict(lambda: 0)
    for i in range(rep):
        if not trueskill:
            #rand_ids = np.random.choice(len(matches), size=n_samples, replace=True)
            rand_ids = np.random.randint(0, len(matches), size=n_samples)
            sample = [matches[rid] for rid in rand_ids]
            ranking = compute_win_rate_for_system(sample)
        else:
            random.shuffle(matches)
            #sampled_matches = random.sample(matches, k=n_samples)
            ranking = compute_trueskill_ranking(matches)

        for rank, (system, rate) in enumerate(ranking):
            rank_count_for_system[system].update([rank])
            if trueskill:
                trueskill_scores_for_system[system] += rate.mu

    if trueskill:
        for system, sum_mu in trueskill_scores_for_system.items():
            trueskill_scores_for_system[system] = sum_mu / rep

    if not naive:
        pairs_to_win_score = compute_pairwise_wins(convo_id_to_convo, feature=feature)
    else:
        pairs_to_win_score = compute_naive_win_rate(convo_id_to_convo, feature=feature)

    if compute_scores:
        system_names = sorted(list(set([x[0] for x in pairs_to_win_score.keys()])))
        for system_name in system_names:
            for system_name_other in set(system_names).difference([system_name]):
                wins = pairs_to_win_score[system_name, system_name_other][0]
                losses = pairs_to_win_score[system_name_other, system_name][0]
                if not wins + losses == 0:
                    scores_for_system[system_name] += (1 / (len(system_names) - 1)) * (wins / (wins + losses))

    rank_range_for_system = compute_rank_range(rank_count_for_system, p=int(rep * 0.995))
    return rank_range_for_system, scores_for_system, trueskill_scores_for_system


def create_set_of_matches(convo_id_to_convo, feature=None, ignore_human=False):
    matches = []
    for cid, convo in convo_id_to_convo.items():
        system_name0 = convo['system_type0']
        system_name1 = convo['system_type1']

        if ignore_human:
            if system_name0 == 'human' or system_name1 == 'human':
                continue

        win_score = compute_winner_for_convo(convo, feature)
        if win_score == 1:
            matches.append((system_name0, system_name1, 1, 0))
        elif win_score == -1:
            matches.append((system_name0, system_name1, 0, 1))
        else:
            matches.append((system_name0, system_name1, 0, 0))
    return matches


def create_naive_matches(convo_id_to_convo, feature=None):
    matches = []
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

                if win_score == 1:
                    matches.append((system_name0, system_name1, 1, 0))
                elif win_score == -1:
                    matches.append((system_name0, system_name1, 0, 1))
                else:
                    matches.append((system_name0, system_name1, 0, 0))
    return matches


def print_result(convo_id_to_convo, naive=True, feature=None, trueskill=False):
    if naive:
        matches = create_naive_matches(convo_id_to_convo, feature=feature)
    else:
        matches = create_set_of_matches(convo_id_to_convo, feature=feature)
    print('Draws: ', len([x for x in matches if x[2] == x[3] == 0]) / len(matches))
    rank_range_for_system, scores_for_system, trueskill_scores_for_system = bootstrap_sampling(matches ,convo_id_to_convo, naive=naive, feature=feature, trueskill=trueskill)
    for system, rrange in rank_range_for_system.items():
        print('{}\t{}\t{}\t{}\t{}'.format(system, trueskill_scores_for_system[system], scores_for_system[system],
                                          rrange[0] + 1, rrange[1] + 1))
    print('\n\n')


if __name__ == "__main__":
    convo_id_to_convo = get_all_annotated_convos(ignore_humans=True, apply_blacklist=False)
    trueskill = False
    naive = True
    print('SPOT THE BOT')
    print_result(convo_id_to_convo, naive=naive, feature=None, trueskill=trueskill)
    print('SSA')
    print_result(convo_id_to_convo, naive=naive, feature='ssa', trueskill=trueskill)
    print('Fluency')
    print_result(convo_id_to_convo, naive=naive, feature='fluencyValue', trueskill=trueskill)
    print('Sensibleness')
    print_result(convo_id_to_convo, naive=naive, feature='sensitivenessValue', trueskill=trueskill)
    print('Specificity')
    print_result(convo_id_to_convo, feature='specificityValue', trueskill=trueskill)
