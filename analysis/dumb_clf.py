
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, plot_confusion_matrix

import matplotlib.pyplot as plt

from templates.src.scoring_utils import get_all_annotated_convos

SEED = 0xDEADBEEF

CONVOS = list(get_all_annotated_convos().values())

TRAIN, TEST = train_test_split(
    CONVOS,
    test_size=0.2,
    random_state=SEED,
    shuffle=True,
    stratify=[
        '_'.join(sorted([convo['system_type0'], convo['system_type1']]))
        for convo in CONVOS
    ],
)


def pipeline():
    return Pipeline(
        steps=[
            ('vec', TfidfVectorizer(ngram_range=(1, 3), sublinear_tf=True)),
            ('clf', LinearSVC(random_state=SEED, class_weight='balanced')),
        ]
    )


def extract_clf_data(dataset, n_turns):
    texts = []
    labels = []

    for convo in dataset:
        label1 = convo['system_type0']
        turns1 = [
            entry['text']
            for entry in convo['convo']
            if entry['id'] == label1
        ]
        text1 = '\n'.join(turns1[:n_turns])

        label2 = convo['system_type1']
        turns2 = [
            entry['text']
            for entry in convo['convo']
            if entry['id'] == label2
        ]
        text2 = '\n'.join(turns2[:n_turns])

        texts.append(text1)
        labels.append(label1)
        texts.append(text2)
        labels.append(label2)

    return {
        'x': texts,
        'y': labels,
    }


def experiment(n_turns, binary_task=False):

    train = extract_clf_data(TRAIN, n_turns=n_turns)
    test = extract_clf_data(TEST, n_turns=n_turns)
    if binary_task:
        train['y'] = [
            'human' if label == 'human' else 'bot'
            for label in train['y']
        ]
        test['y'] = [
            'human' if label == 'human' else 'bot'
            for label in test['y']
        ]

    clf = pipeline()

    clf.fit(train['x'], train['y'])

    print("n turns:\t", n_turns)
    print(classification_report(y_true=test['y'], y_pred=clf.predict(test['x'])))
    print('*' * 80)

    display = plot_confusion_matrix(
        estimator=clf,
        X=test['x'],
        y_true=test['y']
    )
    display.plot()
    name = "binary" if binary_task else 'all'
    plt.savefig(f"confusions_{n_turns}_{name}.png")

    return clf


if __name__ == '__main__':
    for turns in range(1, 10):
        experiment(turns, binary_task=False)
