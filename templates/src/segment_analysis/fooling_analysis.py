"""
Generates the plots of how often a bot fools a human.
"""

import seaborn as sns
from templates.src.segment_analysis.win_function import get_all_annotated_convos
from collections import defaultdict, Counter
from pandas import DataFrame
import numpy as np
from templates.src.mongo_client import SAMPLED_COLLECTION_NAME
from pathlib import Path

name_mapping_domain = {
    'personachat': {
        'human': 'Human',
        'model': 'BL',
        'lost_in_conversation': 'LC',
        'bert_rank': 'BR',
        'kvmemnn': 'KV',
        'huggingface': 'HF',
        'suckybot': 'DR'
    },
    'dailydialog': {
        'human': 'Human',
        'seq2seq_att': 'S2',
        'bert_rank': 'BR',
        'huggingface': 'GPT',
        'suckybot': 'DR'
    },
    'empathetic_dialogues': {
        'human': 'Human',
        'model': 'BL',
        'seq2seq_att': 'S2',
        'bert_rank': 'BR',
        'huggingface': 'GPT',
        'suckybot': 'DR'
    },
    'sota':{
        'Human': 'Human',
        'Generative2.7b_bst_0331': 'BL',
        'Meena': 'ME',
        'Cleverbot': 'CL',
        'Mitsuku': 'MI',
    }
}


def decision_distribution(convo_id_to_convo):
    distribution = defaultdict(lambda: [])
    for cid, convo in convo_id_to_convo.items():
        domain = convo['domain_name']
        system_name0 = convo['system_type0']
        system_name1 = convo['system_type1']



        system_name0 = name_mapping_domain[domain][system_name0]
        system_name1 = name_mapping_domain[domain][system_name1]

        for tid, annotations in convo['annotations'].items():
            for annotation in annotations:
                human0_pred = annotation['entity0_annotation']['is_human']
                human1_pred = annotation['entity1_annotation']['is_human']

                distribution['system_name'].append(system_name0)
                distribution['system_name'].append(system_name1)
                distribution['segment'].append(tid)
                distribution['segment'].append(tid)

                if human0_pred is True:
                    distribution['is_human'].append('Human')
                    distribution['is_human_val'].append(1)
                elif human0_pred is False:
                    distribution['is_human'].append('Bot')
                    distribution['is_human_val'].append(1)
                else:
                    distribution['is_human'].append('Undecided')
                    distribution['is_human_val'].append(1)

                if human1_pred is True:
                    distribution['is_human'].append('Human')
                    distribution['is_human_val'].append(1)
                elif human1_pred is False:
                    distribution['is_human'].append('Bot')
                    distribution['is_human_val'].append(0)
                else:
                    distribution['is_human'].append('Undecided')
                    distribution['is_human_val'].append(1)

    df = DataFrame.from_dict(distribution)
    return df


def compute_class_ratio(convo_id_to_convo):
    distribution = defaultdict(lambda: defaultdict(lambda: Counter()))
    for cid, convo in convo_id_to_convo.items():
        domain = convo['domain_name']
        system_name0 = convo['system_type0']
        system_name1 = convo['system_type1']

        if system_name0 == 'Human':
            system_name0 = 'Human_{}'.format(system_name1)
        if system_name1 == 'Human':
            system_name1 = 'Human_{}'.format(system_name0)

        system_name0 = name_mapping_domain[domain].get(system_name0, system_name0)
        system_name1 = name_mapping_domain[domain].get(system_name1, system_name1)

        for tid, annotations in convo['annotations'].items():
            for annotation in annotations:
                human0_pred = annotation['entity0_annotation']['is_human']
                human1_pred = annotation['entity1_annotation']['is_human']

                if human0_pred is True:
                    distribution[system_name0][tid].update(['Human'])
                elif human0_pred is False:
                    distribution[system_name0][tid].update(['Bot'])
                else:
                    distribution[system_name0][tid].update(['Undecided'])

                if human1_pred is True:
                    distribution[system_name1][tid].update(['Human'])
                elif human1_pred is False:
                    distribution[system_name1][tid].update(['Bot'])
                else:
                    distribution[system_name1][tid].update(['Undecided'])

    flat_distr = defaultdict(lambda: [])
    for system_name, tid_to_distr in distribution.items():
        for tid, distr in tid_to_distr.items():
            total = sum(distr.values())
            for cls, cnt in distr.items():
                distr[cls] = cnt / total

                flat_distr['system_name'].append(system_name)
                flat_distr['segment'].append(tid)
                flat_distr['type'].append(cls)
                flat_distr['val'].append(cnt / total)

    flat_df = DataFrame.from_dict(flat_distr)
    return flat_df


def spotting_rate(convo_id_to_convo):
    n_spotted = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for cid, convo in convo_id_to_convo.items():
        domain = convo['domain_name']
        system_name0 = convo['system_type0']
        system_name1 = convo['system_type1']

        system_name0 = name_mapping_domain[domain][system_name0]
        system_name1 = name_mapping_domain[domain][system_name1]
        tid_to_annotations = convo['annotations']
        spotted0 = False
        spotted1 = False
        for tid, anntoations in sorted(tid_to_annotations.items()):
            for annotation in anntoations:
                human0_pred = annotation['entity0_annotation']['is_human']
                human1_pred = annotation['entity1_annotation']['is_human']
                if not human0_pred:
                    spotted0 = True
                if not human1_pred:
                    spotted1 = True
            if spotted0:
                n_spotted[system_name0][tid][0] += 1
            if spotted1:
                n_spotted[system_name1][tid][0] += 1

            n_spotted[system_name0][tid][1] += 1
            n_spotted[system_name1][tid][1] += 1

    for system_name, tid_to_rate in n_spotted.items():
        for tid, rate in tid_to_rate.items():
            print(system_name, tid, rate[0] / rate[1])


def conditioned_fooling_rate():
    convo_id_to_convo = get_all_annotated_convos(ignore_humans=True)

    conditioned_fooling_for_pair = defaultdict(lambda: [0, 0])
    for cid, convo in convo_id_to_convo.items():
        domain = convo['domain_name']
        system_name0 = convo['system_type0']
        system_name1 = convo['system_type1']

        system_name0 = name_mapping_domain[domain][system_name0]
        system_name1 = name_mapping_domain[domain][system_name1]
        tid_to_annotations = convo['annotations']
        for tid, annotations in tid_to_annotations.items():
            for annotation in annotations:
                human0_pred = annotation['entity0_annotation']['is_human']
                human1_pred = annotation['entity1_annotation']['is_human']

                if human0_pred:
                    conditioned_fooling_for_pair[system_name0, system_name1][0] += 1
                if human1_pred:
                    conditioned_fooling_for_pair[system_name1, system_name0][0] += 1
                conditioned_fooling_for_pair[system_name0, system_name1][1] += 1
                conditioned_fooling_for_pair[system_name1, system_name0][1] += 1
    return conditioned_fooling_for_pair


if __name__ == "__main__":
    convo_id_to_convo = get_all_annotated_convos(ignore_humans=False)
    # spotting_rate(convo_id_to_convo)

    conditioned_fooling_for_pair = conditioned_fooling_rate()
    for pair, rate in conditioned_fooling_for_pair.items():
        print('{}\t{}\t{}\t{}\t{}'.format(pair[0], pair[1], rate[0], rate[1], rate[0] / rate[1]))

    Path("figures/{}".format(SAMPLED_COLLECTION_NAME)).mkdir(parents=True, exist_ok=True)

    dataframe = decision_distribution(convo_id_to_convo)
    sns_plt = sns.catplot(x='segment', hue='is_human', col='system_name', kind='count', col_wrap=3, data=dataframe)
    sns_plt.savefig('figures/{}/turn_distribtion'.format(SAMPLED_COLLECTION_NAME))

    dataframe = compute_class_ratio(convo_id_to_convo)
    print(dataframe.head())
    sns_plt = sns.catplot(x='segment', y='val', hue='type', col='system_name', kind='bar', col_wrap=3, data=dataframe)
    sns_plt.savefig('figures/{}/turn_distribtion_rates'.format(SAMPLED_COLLECTION_NAME))

    sns_plt = sns.catplot(x='system_name', y='val', hue='type', kind='bar', data=dataframe, legend_out=False,
                          palette=sns.color_palette(n_colors=3))
    sns_plt.set_axis_labels("", "Fooling Rates").set(ylim=(0, 1.0)).despine(left=True)
    sns_plt.savefig('figures/{}/fooling_rates'.format(SAMPLED_COLLECTION_NAME))

    sns_plt = sns.catplot(x='system_name', y='val', hue='segment', kind='bar',
                          data=dataframe[dataframe.type == 'Human'], legend_out=False,
                          palette=sns.color_palette(n_colors=3))
    sns_plt.set_axis_labels("", "Fooling Rates").set(ylim=(0, 1.0)).despine(left=True)
    sns_plt.savefig('figures/{}/fooling_rates_over_time'.format(SAMPLED_COLLECTION_NAME))

    human_pred_rates = dataframe[dataframe.type == 'Human']
    human_pred_rates = human_pred_rates.sort_values(['val'], ascending=False).reset_index(drop=True)
    sns_plt = sns.catplot(x='system_name', y='val', kind='bar', data=human_pred_rates, legend_out=False, color='royalblue')
    sns_plt.set_axis_labels("", "Predicted as Human").set(ylim=(0, 1.0)).despine(left=True)
    sns_plt.savefig('figures/{}/human_pred_rates'.format(SAMPLED_COLLECTION_NAME))

    segments = np.sort(dataframe.segment.unique())
    for system_name in dataframe.system_name.unique():
        for segment_len in segments:
            human = dataframe[(dataframe.system_name == system_name) & (dataframe.segment == segment_len) & (
                        dataframe.type == 'Human')]
            human_rate = float(human['val']) if human.size > 0 else 0.0

            bot = dataframe[
                (dataframe.system_name == system_name) & (dataframe.segment == segment_len) & (dataframe.type == 'Bot')]
            bot_rate = float(bot['val']) if bot.size > 0 else 0.0

            undecided = dataframe[(dataframe.system_name == system_name) & (dataframe.segment == segment_len) & (
                        dataframe.type == 'Undecided')]
            undecided_rate = float(undecided['val']) if undecided.size > 0 else 0.0
            print('{}\t{}\t{}\t{}\t{}'.format(system_name, segment_len, human_rate, bot_rate, undecided_rate))
        print('\n\n')
