from typing import Union, Dict, Collection, Callable, Tuple, List, Set
from collections import defaultdict, Counter
import numpy as np
import warnings

def _canonical_form(labels: Collection) -> Tuple:
    """
    transform label sets into a form that can be used as dictionary keys
    """
    if len(labels) == 0:
        return 'label',
    else:
        return tuple(sorted(labels))


class KrippenDorff(object):
    """
    computes Krippendorff's alpha
    """

    def __init__(
            self,
            dist_fun: Callable[[Tuple, Tuple], float]
    ):
        """

        :param dist_fun: distance function used in computation of alpha
        """
        self.dist_fun = dist_fun

    def alpha(self, annotations: List[List[Tuple]]):
        """
        :param annotations: for every item the list of annotations as tuples
        :return: a dictionary of the form
        {
            'alpha': float, the krippendorff alpha
            'disagreement_scores': List[float], for every item the value in the
            enumerator of the krippendorff calculation
        }
        """
        values_by_units: List[Counter] = [
            Counter(anns)
            for anns in annotations
        ]

        # number of annotations per segment
        n_u_dot: List[int] = _n_u_dot(values_by_units)
        # number of times a specific label_set has been observed
        # excluding times where it is the only annotation
        n_dot_u: Dict[Tuple, int] = _n_dot_u(
            values_by_units,
            n_u_dot,
        )
        # total number of possible confusable label_sets
        n_dot_dot: int = sum(v for _, v in n_dot_u.items())

        per_unit_disagreements: List[float] = self._per_unit_disagreement(values_by_units)
        observed_disagreement: float = sum(per_unit_disagreements)

        expected_disagreement = self._expected_disagreement(n_dot_u)
        if np.isclose(expected_disagreement, 0.0):
            warnings.warn(
                message=f"expected disagreement is (close to) 0, you might need to check your data or dist_fn",
                category=RuntimeWarning,
            )
            alpha = 1.0
        else:
            alpha: float = 1 - (n_dot_dot - 1)*(observed_disagreement / expected_disagreement)

        return {
            'alpha': alpha,
            'disagreement_scores': per_unit_disagreements,
        }

    def _expected_disagreement(self, n_dot_u: Dict[Tuple, int]) -> float:
        result: float = 0.0
        all_tuples: List[Tuple] = list(n_dot_u.keys())
        for i in range(len(all_tuples)):
            for j in range(i + 1, len(all_tuples)):
                tup1 = all_tuples[i]
                tup2 = all_tuples[j]

                result += n_dot_u[tup1]*n_dot_u[tup2]*self.dist_fun(tup1, tup2)
        return result

    def _per_unit_disagreement(self, values_per_units) -> List[float]:
        return [
            self._single_unit_disagreement(counter)
            for counter in values_per_units
        ]

    def _single_unit_disagreement(self, counter: Counter) -> float:
        # number of annotations for this specific item
        n_u_dot: int = sum(c for _, c in counter.items())
        # no disagreement if not enough annotations
        if n_u_dot < 2:
            return 0.0

        result: float = 0.0
        tups: List[Tuple] = list(counter.keys())
        for i in range(len(tups)):
            for j in range(i + 1, len(tups)):
                tup1 = tups[i]
                tup2 = tups[j]
                result += counter[tup1]*counter[tup2]*self.dist_fun(tup1, tup2)

        return result / (n_u_dot - 1)


def _n_u_dot(values_by_units: List[Counter]) -> List[int]:
    """
    helper function computing number of annotations for a segment
    """
    return [
        sum(c for _, c in counter.items())
        for counter in values_by_units
    ]


def _n_dot_u(values_by_units: List[Counter], n_u_dot: List[int]) -> Dict[Tuple, int]:
    """
    number of times a specific tuple is pairable in the data
    (pairable means there is at least 1 other annotation on the same segment)
    """
    all_observed_sets = {
        tup
        for counter in values_by_units
        for tup, _ in counter.items()
    }

    return {
        tup: sum(
            counter[tup]
            for i, counter in enumerate(values_by_units)
            if n_u_dot[i] > 1
        )
        for tup in all_observed_sets
    }


def dist_fn(tup1, tup2):
    assert len(tup1) == 1
    assert len(tup2) == 1
    return 1.0 - float(tup1[0] == tup2[0])


if __name__ == '__main__':
    import sys
    sys.path.append('./')
    from templates.src.segment_analysis.annotator_scores import get_all_annotated_convos

    """
    try:
        use_blacklist = sys.argv[1] == 'blacklist'
    except IndexError:
        use_blacklist = True

    if use_blacklist:
        blacklisted = set(create_black_list())
    else:
        blacklisted = set()
    """
    blacklisted = set()

    convo_id_to_annotators = {}
    convo_ids = []
    annotations = []
    systems = []
    convos = get_all_annotated_convos()

    for convo_id, convo in convos.items():
        decision_exchanges = convo['annotations'].keys()
        for decision_exchange in decision_exchanges:
            ent0_anns = [
                ('human' if ann['entity0_annotation']['is_human'] else 'bot',)
                for ann in convo['annotations'][decision_exchange]
                if ann['user_name'] not in blacklisted
            ]
            ent1_anns = [
                ('human' if ann['entity1_annotation']['is_human'] else 'bot',)
                for ann in convo['annotations'][decision_exchange]
                if ann['user_name'] not in blacklisted
            ]
            convo_id_to_annotators[convo_id] = [
                ann['user_name']
                for ann in convo['annotations'][decision_exchange]
                if ann['user_name'] not in blacklisted
            ]
            if len(ent0_anns) > 0:
                convo_ids.append(convo_id + '-ent0')
                annotations.append(ent0_anns)
                systems.append(convo['system_type0'])
            if len(ent1_anns) > 0:
                convo_ids.append(convo_id + '-ent1')
                annotations.append(ent1_anns)
                systems.append(convo['system_type1'])

    kripp = KrippenDorff(dist_fun=dist_fn)
    kripp_res = kripp.alpha(annotations=annotations)
    print(f"krippendorff alpha\toverall:\t{kripp_res['alpha']:.3f}")

    for system_name in sorted(set(systems)):
        k = KrippenDorff(dist_fun=dist_fn).alpha(
            annotations=[
                ann
                for ann, name in zip(annotations, systems)
                if name == system_name
            ]
        )
        print(f"krippendorff alpha\t{system_name}:\t{k['alpha']:.3f}")

    annotator_disagreements = {}
    for convo_id, score in zip(convo_ids, kripp_res['disagreement_scores']):
        annotators = convo_id_to_annotators[convo_id[:-5]]
        for a in annotators:
            if annotator_disagreements.get(a) is None:
                annotator_disagreements[a] = []
            annotator_disagreements[a].append(score)

    average_disagreement_per_annotator = {
        a: np.mean(disagreements)
        for a, disagreements in annotator_disagreements.items()
    }

    print("annotator\taverage disagreement per annotation")
    for item in sorted(
            average_disagreement_per_annotator.items(),
            key=lambda tup: tup[1],
            reverse=True):
        print("\t".join(map(str, item)))
