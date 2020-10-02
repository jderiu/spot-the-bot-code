"""
Analyse correlation of feature annotations
! needs to be run from repo root dir to work, not from this folder !
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Tuple, Union, List
from collections import Counter, defaultdict
from scipy.stats import pearsonr, spearmanr
from sklearn.preprocessing import minmax_scale, scale, robust_scale

FEATURES = ['fluencyValue', 'sensitivenessValue', 'specificityValue', 'is_human']


def get_bot_name(bot_name: str, domain: str = None) -> str:
    if 'convai2' in bot_name:
        bot_name = bot_name.replace('convai2', 'personachat')
    if bot_name[0] == '/':
        bot_name = bot_name[1:]
    if '/' not in bot_name:
        if domain:
            bot_name = domain + '/' + bot_name
        return bot_name
    if bot_name == 'human' and domain:
        bot_name = domain + '/' + bot_name
    if 'human' in bot_name:
        return bot_name
    return '/'.join(bot_name.split('/')[1:3])


def rescale_annotations(annotator_bot_feature_vals: Dict) -> Dict:
    rescaled_annotations = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for annotator, domains in annotator_bot_feature_vals.items():
        for domain, features_scores in domains.items():
            for feature, scores in features_scores.items():
                rescaled_annotations[annotator][domain][feature] = robust_scale(scores)
    return rescaled_annotations


def get_annotator_bot_feature_vals(convos: Dict, per_domain: bool = True, specific_domain: str = None,
                                   skip_human_bot_convos: bool = False, only_human_bot_convos: bool = False) -> Tuple[List, Dict]:
    """Extract annotators and their feature annotations per bot"""
    annotators_to_convo_ids = get_annotator_names()
    annotators = list(annotators_to_convo_ids.keys())
    if 'A1V6CP5I0TOSAR' in annotators:
        annotators.remove('A1V6CP5I0TOSAR')

    features = FEATURES
    annotator_bot_feature_vals = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for convo in convos.values():

        if per_domain:
            bot_0 = get_bot_name(convo['system_name0'], domain=convo['domain_name'])
            bot_1 = get_bot_name(convo['system_name1'], domain=convo['domain_name'])
            if specific_domain and not bot_0.startswith(specific_domain):
                continue
        else:
            bot_0 = get_bot_name(convo['system_type0'])
            bot_1 = get_bot_name(convo['system_type1'])

        if skip_human_bot_convos and len([e for e in [bot_1, bot_0] if 'human' in e]) == 1:
            continue

        if only_human_bot_convos and not len([e for e in [bot_1, bot_0] if 'human' in e]) == 1:
            continue

        for annotation in convo['annotations']:
            curr_ann = annotation['user_name']

            for feature in features:
                annotator_bot_feature_vals[curr_ann][bot_0][feature].append(
                    float(annotation['entity0_annotation'][feature])
                )
                annotator_bot_feature_vals[curr_ann][bot_1][feature].append(
                    float(annotation['entity1_annotation'][feature])
                )

    return annotators, annotator_bot_feature_vals


def average_ranking(convos: Dict, per_domain: bool = True, outdir: str = '/tmp/', specific_domain: str = None) -> None:
    """
    1. Per annotator/bot/feature calculate average score
    2. Per annotator/feature, create ranking of bots based on average scores
    3. Per feature, average ranks of annotators to create ranking of bots
    """
    annotators, annotator_bot_feature_vals = get_annotator_bot_feature_vals(convos, per_domain=per_domain,
                                                                            specific_domain=specific_domain)
    features_bots_ranks = defaultdict(lambda: defaultdict(list))

    for annotator, bots in annotator_bot_feature_vals.items():
        average_feature_scores_bots = defaultdict(lambda: defaultdict(float))

        for bot, feature_scores in bots.items():
            for feature, scores in feature_scores.items():
                if len(scores) > 1:
                    average_feature_scores_bots[feature][bot] = np.mean(scores)

        for feature, bot_scores in average_feature_scores_bots.items():
            ranking_ixs = np.argsort(list(bot_scores.values()))
            ranked_bots = list(np.take(list(bot_scores.keys()), ranking_ixs))
            ranked_bots.reverse()
            ranks = minmax_scale(range(1, len(ranked_bots) + 1))
            for i, bot in zip(ranks, ranked_bots):
                features_bots_ranks[feature][bot].append(i)

    for feature, bot_ranks in features_bots_ranks.items():
        bot_names = sorted(list(bot_ranks.keys()))
        x_pos = list(range(1, len(bot_names) + 1))
        labels = bot_names
        means = [np.mean(bot_ranks[bot]) for bot in bot_names]
        errors = [np.std(bot_ranks[bot]) for bot in bot_names]

        fig, ax = plt.subplots()
        ax.bar(x_pos, means, yerr=errors, alpha=0.5, align='center', ecolor='black', capsize=10)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels, rotation=90)
        ax.set_title(f'Annotator: ALL')
        ax.set_ylabel(f'Rank of feature: {feature}')
        fig.tight_layout()

        if per_domain:
            outfile = os.path.join(outdir, f'ALL_{feature}_rank_domains.png')
        else:
            outfile = os.path.join(outdir, f'ALL_{feature}_rank.png')
        plt.savefig(outfile)
        plt.close()


def average_feature_annotations(convos: Dict, outdir: str = '/tmp', plot_per_annotator: bool = False,
                                per_domain: bool = True, rescaling: bool = False, specific_domain: str = None,
                                skip_human_bot_convos: bool = False, only_human_bot_convos: bool = False) -> None:
    """ Per annotator, bot, and feature, get all annotations, then plot """

    annotators, annotator_bot_feature_vals = get_annotator_bot_feature_vals(convos, per_domain=per_domain,
                                                                            specific_domain=specific_domain,
                                                                            skip_human_bot_convos=skip_human_bot_convos,
                                                                            only_human_bot_convos=only_human_bot_convos)

    annotation_count = defaultdict(lambda: defaultdict(Counter))
    all_feature_values = defaultdict(lambda: defaultdict(list))

    if rescaling:
        annotator_bot_feature_vals = rescale_annotations(annotator_bot_feature_vals)

    for annotator in annotators:
        print(annotator)

        for feature in FEATURES:
            annotated_bots, plot_data = list(), list()
            means, errors = list(), list()

            for bot, feature_scores in annotator_bot_feature_vals[annotator].items():
                vals = feature_scores[feature]

                if len(vals) > 0:
                    plot_data.append(vals)
                    annotated_bots.append(bot)
                    means.append(np.mean(vals))
                    errors.append(np.std(vals))
                    annotation_count[annotator][bot][feature] += len(vals)
                    if len(vals) > 2:
                        all_feature_values[feature][bot].append(np.mean(vals))

            if plot_per_annotator:
                x_pos = list(range(1, len(annotated_bots)+1))
                labels = [f'{bot} ({annotation_count[annotator][bot][feature]})' for bot in annotated_bots]

                fig, ax = plt.subplots()
                ax.bar(x_pos, means, yerr=errors, alpha=0.5, align='center', ecolor='black', capsize=10)
                ax.set_xticks(x_pos)
                ax.set_xticklabels(labels, rotation=90)
                ax.set_title(f'Annotator: {annotator}')
                ax.set_ylabel(f'Feature: {feature}')
                fig.tight_layout()

                outfile = os.path.join(outdir, f'{annotator}_{feature}.png')
                plt.savefig(outfile)
                plt.close()

    features_bots_mean = defaultdict(lambda: defaultdict(float))

    for feature, bots in all_feature_values.items():
        bot_names = sorted(list(bots.keys()))
        x_pos = list(range(1, len(bots) + 1))
        labels = [f'{bot} ({len(bots[bot])})' for bot in bot_names]
        means = [np.mean(bots[bot]) for bot in bot_names]
        errors = [np.std(bots[bot]) for bot in bot_names]

        for bot, mean_val in zip(labels, means):
            features_bots_mean[feature][bot] = round(mean_val, 2)

        fig, ax = plt.subplots()
        ax.bar(x_pos, means, yerr=errors, alpha=0.5, align='center', ecolor='black', capsize=10)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels, rotation=90)
        ax.set_title(f'Annotator: ALL')
        ax.set_ylabel(f'Feature: {feature}')
        fig.tight_layout()

        if per_domain:
            if specific_domain:
                outfile = os.path.join(outdir, f'ALL_{feature}_{specific_domain}.png')
            else:
                outfile = os.path.join(outdir, f'ALL_{feature}_domains.png')
        else:
            outfile = os.path.join(outdir, f'ALL_{feature}.png')
        plt.savefig(outfile)
        plt.close()

    for feature, bot_means in features_bots_mean.items():
        print(f'\t{feature}')
        for bot, mean_val in bot_means.items():
            print(f'{bot}\t{mean_val}')


def get_correlation(vals1: List[Union[int, float]], vals2: [Union[int, float]]) -> Union[Tuple[float, float], None]:

    if not type(vals1[0]) is float:
        vals1 = [float(val) for val in vals1]

    if not type(vals2[0]) is float:
        vals2 = [float(val) for val in vals2]

    # correlation = pearsonr(vals1, vals2)
    correlation = spearmanr(vals1, vals2)

    if np.isnan(correlation[0]):
        # This means both lists are equal and there's no variation; set correlation and p-value manually
        correlation = None

    return correlation


def print_corel_avg(feature: str, correlation: List[Tuple]) -> None:
    correlations = [r[0] for r in correlation]
    mean_correlation = np.mean(correlations)
    std_correlations = np.std(correlations)
    p_values = [r[1] if not np.isnan(r[1]) else 1 for r in correlation]
    mean_pvalue = np.mean(p_values)
    std_p_values = np.std(p_values)
    print(f'{feature} ({len(correlations)}): {mean_correlation} ({std_correlations}) '
          f'({mean_pvalue} ({std_p_values}))')


def annotation_correlation(convos: Dict) -> None:
    """
    Correlate annotated values pair-wise
    aggregate the scores per feature
    annotator1: bot: feature: values
    annotator2: bot: feature: values
    values lists are aligned, i.e. for the same convos
    """
    annotators_to_convo_ids = get_annotator_names()
    annotators = list(annotators_to_convo_ids.keys())
    if 'A1V6CP5I0TOSAR' in annotators:  # spammer
        annotators.remove('A1V6CP5I0TOSAR')

    features = FEATURES
    correlations_per_feature = defaultdict(list)
    correlations_per_bot_per_feature = defaultdict(lambda: defaultdict(list))

    for i, ann1 in enumerate(annotators):

        for ann2 in annotators[i+1:]:
            shared_convos = set(annotators_to_convo_ids[ann1]).intersection(set(annotators_to_convo_ids[ann2]))

            if len(shared_convos) > 1:  # Is 2 enough?
                feature_scores = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

                for convo_id in shared_convos:
                    bot_0 = convos[convo_id]['system_type0']  # change to system_name0 for domain-specificity
                    bot_1 = convos[convo_id]['system_type1']
                    seen_annotators = set()  # Skip multiple annotations by one annotator

                    for annotation in convos[convo_id]['annotations']:
                        curr_ann = annotation['user_name']

                        if curr_ann in [ann1, ann2] and curr_ann not in seen_annotators:

                            for feature in features:
                                feature_scores[curr_ann][bot_0][feature].append(annotation['entity0_annotation'][feature])
                                feature_scores[curr_ann][bot_1][feature].append(annotation['entity1_annotation'][feature])

                            seen_annotators.add(curr_ann)

                # Start the analysis
                print(ann1, '<->', ann2)

                for feature in features:
                    ann1_vals, ann2_vals = list(), list()

                    for bot in feature_scores[ann1].keys():
                        feature_vals1 = feature_scores[ann1][bot][feature]
                        feature_vals2 = feature_scores[ann2][bot][feature]

                        if len(feature_vals1) != len(feature_vals2):
                            continue

                        if len(feature_vals1) > 1:
                            correlation = get_correlation(feature_vals1, feature_vals2)
                            if correlation:
                                correlations_per_bot_per_feature[bot][feature].append(correlation)

                        ann1_vals.extend(feature_vals1)
                        ann2_vals.extend(feature_vals2)

                    assert len(ann1_vals) == len(ann2_vals), "unequal length of annotated scores"

                    if ann1_vals:
                        correlation = get_correlation(ann1_vals, ann2_vals)
                        if correlation:
                            print(f'{feature} ({len(ann1_vals)}): {correlation}')
                            correlations_per_feature[feature].append(correlation)
                print()

    print('\nAverages per bot\nFeature: correlation (std) (p-value (std))')
    for bot, feature_corels in correlations_per_bot_per_feature.items():
        print(bot)

        for feature, correlation in feature_corels.items():
            print_corel_avg(feature, correlation)

        print()

    print('\nAverages\nFeature: correlation (std) (p-value (std))')
    for feature, correlation in correlations_per_feature.items():
        print_corel_avg(feature, correlation)


if __name__ == '__main__':
    import sys
    import pickle
    sys.path.append('./')
    from templates.src.scoring_utils import get_annotator_names

    pickle_file = 'convo_data.pkl'
    if not os.path.exists(pickle_file):
        print('Downloading data')
        from templates.src.scoring_utils import get_all_annotated_convos
        data = get_all_annotated_convos()
        with open('convo_data.pkl', 'wb') as f:
            pickle.dump(data, f)
    else:
        with open('convo_data.pkl', 'rb') as f:
            data = pickle.load(f)

    per_domain = True
    specific_domain = 'personachat' if per_domain else False
    skip_human_bot_convos = False
    only_human_bot_convos = False

    average_feature_annotations(data, per_domain=per_domain, specific_domain=specific_domain,
                                skip_human_bot_convos=skip_human_bot_convos,
                                only_human_bot_convos=only_human_bot_convos)

    # annotation_correlation(data)
    
   # average_ranking(data, per_domain=per_domain, specific_domain=specific_domain)

    """
    configs
    "sampled_collection_name": "sampled-dialogues-amt-tournament1-personachat",
    "labelled_collection_name": "sampled-dialogues-annotation-amt-tournament1-personachat"
        "sampled_collection_name": "sampled-dialogues-amt-test1",
 "labelled_collection_name": "sampled-dialogues-annotation-amt-test1"
    """