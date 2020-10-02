import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Union
from collections import Counter, defaultdict
from scipy.stats import wilcoxon, pearsonr


def convo_type_match(convo: Dict, convo_type: Union[str, None]) -> bool:
    if convo_type not in (None, 'human-human', 'human-bot', 'bot-bot'):
        raise NotImplementedError
    if not convo_type:
        return True
    num_humans = len([entity for entity in (convo['system_type0'], convo['system_type1']) if entity == 'human'])
    if convo_type == 'human-human' and num_humans == 2:
        matches = True
    elif convo_type == 'human-bot' and num_humans == 1:
        matches = True
    elif convo_type == 'bot-bot' and num_humans == 0:
        matches = True
    else:
        matches = False
    return matches


def time_stats(convos: Dict, convo_type: str = None, print_per_annotator: bool = False) -> None:

    time_per_annotator = defaultdict(list)
    correctness_per_annotator = defaultdict(list)

    for _, convo in convos.items():

        if not convo_type_match(convo, convo_type):
            continue

        for annotation in convo['annotations']:
            time_per_annotator[annotation['user_name']].append(annotation['elapsed_time']/1000)
            if convo['is_human0'] == annotation['entity0_annotation']['is_human']:
                correctness_per_annotator[annotation['user_name']].append(1)
            else:
                correctness_per_annotator[annotation['user_name']].append(0)
            if convo['is_human1'] == annotation['entity1_annotation']['is_human']:
                correctness_per_annotator[annotation['user_name']].append(1)
            else:
                correctness_per_annotator[annotation['user_name']].append(0)

    print('\nAverage time (ms) per task (std)')
    overall_time, overall_correct = list(), list()
    for annotator, times in time_per_annotator.items():
        if print_per_annotator:
            print(f'{annotator}: {int(round(np.mean(times)))} ({np.std(times)}); correctness: {np.mean(correctness_per_annotator[annotator])}')
        overall_time.append(int(round(np.mean(times))))
        overall_correct.append(np.mean(correctness_per_annotator[annotator]))
    print(f'OVERALL time: {np.mean(overall_time)}')
    print(f'OVERALL correct: {np.mean(overall_correct)}')


def decision_turn_stats(convos: Dict, convo_type: str = None) -> None:
    """Calculate mean/std of decision turn and their diff"""

    decision_turns_per_annotator_per_bot = defaultdict(lambda: defaultdict(list))
    diffs_per_annotator_per_bot = defaultdict(lambda: defaultdict(list))  # annotator -> bot -> diff

    for _, convo in convos.items():

        if not convo_type_match(convo, convo_type):
            continue

        for annotation in convo['annotations']:

            bot_0 = convo['system_type0']
            bot_1 = convo['system_type1']

            decision_turn0 = np.ceil(annotation['entity0_annotation']['decision_turn'] / 2)
            decision_turn1 = np.floor(annotation['entity1_annotation']['decision_turn'] / 2)
            decision_turns_per_annotator_per_bot[annotation['user_name']][bot_0].append(decision_turn0)
            decision_turns_per_annotator_per_bot[annotation['user_name']][bot_1].append(decision_turn1)

            diff = abs(decision_turn0 - decision_turn1)
            diffs_per_annotator_per_bot[annotation['user_name']][bot_0].append(diff)
            diffs_per_annotator_per_bot[annotation['user_name']][bot_1].append(diff)

    print('\nAnalysis of decision turns')
    print('Mean of decision turns (std)')
    # Calculate mean per annotators, take mean of means
    mean_decision_turn_per_bot = defaultdict(list)
    for annotator, decision_turn_per_bot in decision_turns_per_annotator_per_bot.items():
        for bot, decision_turns in decision_turn_per_bot.items():
            mean_decision_turn_per_bot[bot].append(np.mean(decision_turns))
    all_mean_turns = list()
    for bot, mean_decision_turns in mean_decision_turn_per_bot.items():
        print(f'{bot}:\t {np.mean(mean_decision_turns)}\t({np.std(mean_decision_turns)})')
        all_mean_turns.append(np.mean(mean_decision_turns))
    print(f'OVERALL:\t{np.mean(all_mean_turns)}\t({np.std(all_mean_turns)})')

    print('\nMean diff (std) of decision turns')
    # Calculate mean per annotators, take mean of means
    mean_diffs_per_bot = defaultdict(list)
    for annotator, bot_diffs in diffs_per_annotator_per_bot.items():
        for bot, diffs in bot_diffs.items():
            mean_diffs_per_bot[bot].append(np.mean(diffs))
    all_mean_diffs = list()
    for bot, mean_diffs in mean_diffs_per_bot.items():
        print(f'{bot}:\t{np.mean(mean_diffs)}\t({np.std(mean_diffs)})')
        all_mean_diffs.append(np.mean(mean_diffs))
    print(f'OVERALL:\t{np.mean(all_mean_diffs)}\t({np.std(all_mean_diffs)})')

    """
    print(f'Mean (std) decision turn: {np.mean(decision_turns)} ({np.std(decision_turns)})')
    print(f'Mean (std) diffs: {np.mean(diffs)} ({np.std(diffs)})')
    print(f'Mean (std) convo length: {np.mean(convo_length)} ({np.std(convo_length)})')

    print('Distribution of diffs:')
    for cnt in Counter(diffs).most_common():
        print(cnt)

    print('Distribution of decision turns:')
    for cnt in Counter(decision_turns).most_common():
        print(cnt)

    print('Distribution of convo length:')
    for cnt in Counter(convo_length).most_common():
        print(cnt)
    """


def fooling_rate(convos: Dict, convo_type: str = None) -> None:

    detection_rates = defaultdict(Counter)

    for _, convo in convos.items():

        if not convo_type_match(convo, convo_type):
            continue

        bot_0 = convo['system_type0']
        bot_1 = convo['system_type1']

        for annotation in convo['annotations']:
            detection_rates[bot_0][annotation['entity0_annotation']['is_human']] += 1
            detection_rates[bot_1][annotation['entity1_annotation']['is_human']] += 1

    print('\nRaw fooling rates:')
    for bot, stats in detection_rates.items():
        if bot == 'human':
            deception_percentage = stats[False] / (stats[True] + stats[False]) if stats[False] > 0 else 0.
        else:
            deception_percentage = stats[True] / (stats[True] + stats[False]) if stats[True] > 0 else 0.
        print(f'{bot}\t{stats}\t{deception_percentage}')


def fooling_rate_per_annotator(convos: Dict, min_freq: int = 2, convo_type: str = None,
                               per_annotator_printing: bool = False) -> None:

    detection_stats = defaultdict(lambda: defaultdict(Counter))
    decision_turns_per_annotator = defaultdict(list)

    for _, convo in convos.items():

        if not convo_type_match(convo, convo_type):
            continue

        bot_0 = convo['system_type0']
        bot_1 = convo['system_type1']

        # TODO add decision turn per bot
        for annotation in convo['annotations']:
            detection_stats[annotation['user_name']][bot_0][annotation['entity0_annotation']['is_human']] += 1
            detection_stats[annotation['user_name']][bot_1][annotation['entity1_annotation']['is_human']] += 1
            decision_turn0 = np.ceil(annotation['entity0_annotation']['decision_turn'] / 2)
            decision_turn1 = np.floor(annotation['entity1_annotation']['decision_turn'] / 2)
            decision_turns_per_annotator[annotation['user_name']].extend([decision_turn0, decision_turn1])

    avg_detection_rates = defaultdict(list)

    print('\nFooling rates per annotator')
    for annotator, bot_stats in detection_stats.items():
        if per_annotator_printing:
            print(annotator)
        annotation_count = 0
        fooling_rates = list()

        for bot, stats in bot_stats.items():

            if sum(stats.values()) < min_freq:  # skip annotators which have less annotations for the entity
                continue

            if bot == 'human':
                fooling_rate = stats[False] / (stats[True] + stats[False]) if stats[False] > 0 else 0.
            else:
                fooling_rate = stats[True] / (stats[True] + stats[False]) if stats[True] > 0 else 0.
            fooling_rates.append(fooling_rate)

            if per_annotator_printing:
                print(bot, stats, fooling_rate)
            annotation_count += stats[False] + stats[True]
            avg_detection_rates[bot].append(fooling_rate)

        if annotation_count > 0 and per_annotator_printing:
            print('Total annotations:', annotation_count)
            print('Average fooling rate:', np.mean(fooling_rates))
            print(f'Average decision turn (std): {np.mean(decision_turns_per_annotator[annotator])} ({np.std(decision_turns_per_annotator[annotator])})\n')

    print('Averaged fooling rates')
    for bot, rates in avg_detection_rates.items():
        print(f'{bot}\t({len(rates)} annotators):\t{np.mean(rates)}')


def detection_ratio_per_turn(convos: Dict, convo_type: str = None) -> None:

    decision_turns = defaultdict(lambda: defaultdict(Counter))

    for _, convo in convos.items():

        if not convo_type_match(convo, convo_type):
            continue

        bot_0 = convo['system_type0']  # change to system_name0 for domain-specificity
        bot_1 = convo['system_type1']

        for annotation in convo['annotations']:
            decision_turn0 = np.ceil(annotation['entity0_annotation']['decision_turn'] / 2)
            decision_turn1 = np.floor(annotation['entity1_annotation']['decision_turn'] / 2)
            decision_turns[bot_0][decision_turn0][annotation['entity0_annotation']['is_human']] += 1
            decision_turns[bot_1][decision_turn1][annotation['entity1_annotation']['is_human']] += 1

    legend = list()

    print('\nFooling rates per turn')

    for bot, turns in decision_turns.items():
        print(bot)
        legend.append(bot)
        deception_rates = list()

        for turn in sorted(turns.keys()):
            stats = turns[turn]
            if bot == 'human':
                deception_rate = stats[False] / (stats[True]  + stats[False]) if stats[False] > 0 else 0.
            else:
                deception_rate = stats[True] / (stats[True] + stats[False]) if stats[False] > 0 else 1.
            deception_rates.append(deception_rate)
            print(turn, stats, deception_rate)

        plt.plot(sorted(turns.keys()), deception_rates)

    plt.legend(legend)
    plt.title('Fooling probabilities per turn')
    plt.savefig('/tmp/fooling_probs.png')
    plt.clf()


def segment_points(convos: Dict, convo_type: str = None) -> None:

    seg_bot_bot_point_diff = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    seg_bot_bot_points = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    seg_bot_bot_label_count = defaultdict(lambda: defaultdict(lambda: defaultdict(Counter)))
    bot_seg_points = defaultdict(lambda: defaultdict(list))

    def get_points(annotation):
        if annotation is None:
            return 1
        elif annotation is True:
            return 2
        else:
            return 0

    for _, convo in convos.items():

        if not convo_type_match(convo, convo_type):
            continue

        bot_0 = convo['system_type0']  # change to system_name0 for domain-specificity
        bot_1 = convo['system_type1']

        for annotation in convo['annotations']:

            turn0 = annotation['entity0_annotation']['decision_turn']
            turn1 = annotation['entity1_annotation']['decision_turn']

            points_bot0 = get_points(annotation['entity0_annotation']['is_human'])
            points_bot1 = get_points(annotation['entity1_annotation']['is_human'])

            bot_seg_points[bot_0][turn0].append(points_bot0)
            bot_seg_points[bot_1][turn1].append(points_bot1)

            seg_bot_bot_point_diff[turn0][bot_0][bot_1].append(points_bot0 - points_bot1)
            seg_bot_bot_point_diff[turn1][bot_1][bot_0].append(points_bot1 - points_bot0)

            seg_bot_bot_points[turn0][bot_0][bot_1].append(points_bot0)
            seg_bot_bot_points[turn1][bot_1][bot_0].append(points_bot1)

            seg_bot_bot_label_count[turn0][bot_0][bot_1][annotation['entity0_annotation']['is_human']] += 1
            seg_bot_bot_label_count[turn1][bot_1][bot_0][annotation['entity1_annotation']['is_human']] += 1



    bots = list(bot_seg_points.keys())
    segs = sorted(list(seg_bot_bot_point_diff.keys()))  # has some spurious segment annotations?

    print('Avg. points per segment length')
    for bot in bots:
        print(bot)
        seg_avgs = list()

        for seg in segs:
            print(seg, np.mean(bot_seg_points[bot][seg]), len(bot_seg_points[bot][seg]))
            seg_avgs.append(np.mean(bot_seg_points[bot][seg]))

        plt.plot(segs, seg_avgs)

    plt.legend(bots)
    plt.xticks(segs)
    plt.title('Avg. points per segment')
    plt.savefig('/tmp/scores_per_seg.png')
    plt.clf()

    print('\nPoint diffs')
    for seg in segs:
        print(seg)
        print('\t' + '\t'.join(bots))

        for bot1 in bots:
            out_str = list()

            for bot2 in bots:
                if bot1 == bot2:
                    out_str.append('-')
                else:
                    # wilcoxon_result = wilcoxon(seg_bot_bot_points[seg][bot1][bot2], seg_bot_bot_points[seg][bot2][bot1])
                    # pearsonr_result = pearsonr(seg_bot_bot_points[seg][bot1][bot2], seg_bot_bot_points[seg][bot2][bot1])
                    out_str.append(
                        str(round(np.mean(seg_bot_bot_point_diff[seg][bot1][bot2]), 2))
                        # + ' (' + str(len(seg_bot_bot_point_diff[seg][bot1][bot2])) + ')'
                        # + ' (' + str(round(wilcoxon_result.pvalue, 4)) + ')'
                        # + ' (' + str(round(pearsonr_result[0], 2)) + '; ' + str(round(pearsonr_result[1], 3)) +')'
                    )

            print(bot1 + '\t' + '\t'.join(out_str))
    print()


if __name__ == '__main__':
    import os, sys, pickle
    sys.path.append('./')

    from templates.src.segment_analysis.annotator_scores import get_all_annotated_convos
    print('Downloading data')
    data = get_all_annotated_convos()

    """
    pickle_file = 'convo_data.pkl'
    if not os.path.exists(pickle_file):
        print('Downloading data')
        #from templates.src.segment_analysis.win_function import get_all_annotated_convos
        from templates.src.scoring_utils import get_all_annotated_convos
        data = get_all_annotated_convos()
        with open('convo_data.pkl', 'wb') as f:
            pickle.dump(data, f)
    else:
        with open('convo_data.pkl', 'rb') as f:
            data = pickle.load(f)
    """

    convo_type = None

    """
    segment_points(data, convo_type=convo_type)
    time_stats(data, convo_type=convo_type)
    fooling_rate(data, convo_type=convo_type)
    fooling_rate_per_annotator(data, convo_type=convo_type, min_freq=0, per_annotator_printing=False)
    detection_ratio_per_turn(data, convo_type=convo_type)
    # decision_turn_stats(data, convo_type=convo_type)
    """

    """
    # unpackaged, w/o human-bot
    "sampled_collection_name": "sampled-dialogues-amt-tournament2-personachat",
"labelled_collection_name": "annotated-dialogues-amt-tournament2-personachat",
    "sampled_collection_name": "sampled-dialogues-amt-tournament4-personachat",
    "labelled_collection_name": "sampled-dialogues-annotation-amt-tournament4-personachat"
    """

    """
    # internal packaged
    "package_collection_name": "packed-amt-tournament-personachat-new",
"sampled_collection_name": "sampled-dialogues-amt-tournament-personachat-new",
"labelled_collection_name": "annotated-dialogues-amt-tournament-personachat-new",
"""

    """
   # amt packaged 1 with human-bot
"package_collection_name": "packed-amt-tournament1-personachat-new",
"sampled_collection_name": "sampled-dialogues-amt-tournament1-personachat-new",
"labelled_collection_name": "annotated-dialogues-amt-tournament1-personachat-new",
"""

    """"
    # amt packaged 2 without human-bot
    package_collection_name": "packed-amt-tournament2-personachat-new",
"sampled_collection_name": "sampled-dialogues-amt-tournament2-personachat-new",
"labelled_collection_name": "annotated-dialogues-amt-tournament2-personachat-new",
"""
    # old host: "host": "160.85.252.62",

    """
    # segmented amt
    "package_collection_name": "packed-amt-segmented-tournament1-personachat-new",
"sampled_collection_name": "sampled-dialogues-amt-tournament1-personachat-new",
"labelled_collection_name": "annotated-segmented-dialogues-amt-tournament1-personachat-new",
"""

    """
     # segmented amt wo human-bot
    	"package_collection_name": "packed-amt-segmented-tournament2-personachat-new",
	"sampled_collection_name": "sampled-dialogues-amt-tournament2-personachat-new",
	"labelled_collection_name": "annotated-segmented-dialogues-amt-tournament2-personachat-new",
    """