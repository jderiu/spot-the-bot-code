
from templates.src.scoring_utils import (
    get_all_annotated_convos,
    create_black_list,
)

from analysis.krippendorff import KrippenDorff


def _extract_annotation(left_entity_ann: bool, right_entity_ann: bool):
    if (left_entity_ann == True) and (right_entity_ann == True):  # verbose for clarity
        return '=',
    elif (left_entity_ann == True) and (right_entity_ann == False):
        return '>',
    elif (left_entity_ann == False) and (right_entity_ann == True):
        return '<',
    else:
        raise ValueError(f"cannot handle case left: {left_entity_ann}, right {right_entity_ann}")


def _extract_annotations(blacklisted):

    bot_pair_to_annotations = {}
    for convo_id, convo in get_all_annotated_convos().items():
        ent0_type = convo['system_type0']
        ent1_type = convo['system_type1']

        if ent0_type <= ent1_type:
            bot_pair = (ent0_type, ent1_type)
            left_annotation = 'entity0_annotation'
            right_annotation = 'entity1_annotation'
        else:
            bot_pair = (ent1_type, ent0_type)
            left_annotation = 'entity1_annotation'
            right_annotation = 'entity0_annotation'

        annotations = [
            {
                'fluency': _extract_annotation(
                    left_entity_ann=ann[left_annotation]['fluencyValue'],
                    right_entity_ann=ann[right_annotation]['fluencyValue'],
                ),
                'sensitiveness': _extract_annotation(
                    left_entity_ann=ann[left_annotation]['sensitivenessValue'],
                    right_entity_ann=ann[right_annotation]['sensitivenessValue'],
                ),
                'specificity': _extract_annotation(
                    left_entity_ann=ann[left_annotation]['specificityValue'],
                    right_entity_ann=ann[right_annotation]['specificityValue'],
                ),
            }
            for ann in convo['annotations']
            if ann['user_name'] not in blacklisted
        ]

        if len(annotations) > 0:
            if bot_pair_to_annotations.get(bot_pair) is None:
                bot_pair_to_annotations[bot_pair] = []

            bot_pair_to_annotations[bot_pair].append(annotations)

    return {
        bot_pair: {
            'fluency': [[a['fluency'] for a in ann_list] for ann_list in anns],
            'sensitiveness': [[a['sensitiveness'] for a in ann_list] for ann_list in anns],
            'specificity': [[a['specificity'] for a in ann_list] for ann_list in anns],
        }
        for bot_pair, anns in bot_pair_to_annotations.items()
    }


def dist_fn(ann_tup1, ann_tup2):
    assert len(ann_tup1) == 1
    assert len(ann_tup2) == 1

    ann1 = ann_tup1[0]
    ann2 = ann_tup2[0]

    if ann1 == ann2:
        return 0.0
    else:
        if (ann1 == '=') or (ann2 == '='):
            return 0.5
        else:
            return 1.0


def main(use_blacklist):

    blacklisted = set(create_black_list()) if use_blacklist else set()

    annotation_dict = _extract_annotations(blacklisted)

    for bot_pair in sorted(annotation_dict.keys()):
        left, right = bot_pair
        print(f"{left} vs {right}:")
        for feature in ['fluency', 'sensitiveness', 'specificity']:
            alpha = KrippenDorff(dist_fun=dist_fn).alpha(annotation_dict[bot_pair][feature])['alpha']
            print(f'\t{feature}:\t{alpha}')


if __name__ == '__main__':
    import sys
    try:
        blacklist = sys.argv[1] == 'blacklist'
    except IndexError:
        blacklist = True

    main(use_blacklist=blacklist)
