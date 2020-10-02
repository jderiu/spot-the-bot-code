
import matplotlib.pyplot as plt

from lifelines import KaplanMeierFitter
from lifelines.statistics import pairwise_logrank_test


def estimate_survival(df, plot=True, censoring='right', fig_path=None):

    if censoring not in {'right', 'left'}:
        raise ValueError(f"unknown fit type: {censoring},"
                         f" use one of {{'left', 'right'}}")

    kmf = KaplanMeierFitter(alpha=1.0)  # disable confidence interval

    if plot:
        fig = plt.figure(figsize=(20, 10))
        ax = fig.add_subplot(111)

    medians = {}
    for system in sorted(df.domain_system.unique()):
        if censoring == 'right':
            kmf.fit(
                df.loc[df['domain_system'] == system].time,
                df.loc[df['domain_system'] == system].spotted,
                label=system,
            )
        elif censoring == 'left':
            kmf.fit_left_censoring(
                df.loc[df['domain_system'] == system].time,
                ~df.loc[df['domain_system'] == system].spotted,
                label=system,
            )
        else:
            raise ValueError(f"unknown fit type: {censoring},"
                             f" use one of {{'left', 'right'}}")

        if plot:
            kmf.plot_survival_function(ax=ax)

        medians[system] = kmf.median_survival_time_

    if plot:
        plt.ylim(0.0, 1.0)
        plt.xlabel("Turns")
        plt.ylabel("Survival Probability")
        plt.title("Estimated Survival Function of different systems")
        save_path = fig_path or "survival.png"
        print(f'saving plot of estimated survival functions to: {save_path}')
        plt.savefig(save_path)

    return medians


def comparisons(df, print=True):
    res = pairwise_logrank_test(
        event_durations=df.time,
        event_observed=df.spotted,
        groups=df.domain_system,
    )

    if print:
        res.print_summary()

    return res


if __name__ == '__main__':
    import sys
    from templates.src.scoring_utils import create_black_list
    from analysis.extract_event_data import fetch_event_data

    try:
        use_blacklist = sys.argv[1] == 'blacklist'
    except IndexError:
        use_blacklist = True

    try:
        censoring = sys.argv[2]
    except IndexError:
        censoring = 'right'

    print(f"Fitting {'with' if use_blacklist else 'without'} blacklist and {censoring} censoring.")

    if use_blacklist:
        blacklisted = set(create_black_list())
    else:
        blacklisted = set()

    data = fetch_event_data()
    data = data[~data['user'].isin(blacklisted)]

    # data = data.loc[data['convo_type'] == 'human-bot']

    for domain in data.domain.unique():

        sub = data.loc[data['domain'] == domain]

        medians = estimate_survival(
            sub,
            plot=True,
            censoring=censoring,
            fig_path=f"survival_{domain}.png",
        )
        print("System\tMedian Survival")
        for system in sorted(sub.domain_system.unique()):
            print(f"{system}\t{medians[system]}")

        comparisons(sub, print=True)

        print('*' * 80)
