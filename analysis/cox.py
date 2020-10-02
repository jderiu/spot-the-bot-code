
import sys

import matplotlib.pyplot as plt

from lifelines import CoxPHFitter

from analysis.extract_event_data import fetch_event_data
from templates.src.scoring_utils import create_black_list

try:
    use_blacklist = sys.argv[1] == 'blacklist'
except IndexError:
    use_blacklist = True

if use_blacklist:
    blacklisted = set(create_black_list())
else:
    blacklisted = set()

EVENT_DATA = fetch_event_data()
EVENT_DATA = EVENT_DATA[~EVENT_DATA['user'].isin(blacklisted)]
EVENT_DATA = EVENT_DATA[
    ['domain_system', 'spotted', 'time', 'fluency', 'sensible', 'specific']
]
# EVENT_DATA['inv_specific'] = 50. / (1. + EVENT_DATA.specific)
# EVENT_DATA['inv_fluency'] = 50. / (1. + EVENT_DATA.fluency)
# EVENT_DATA['inv_sensible'] = 50. / (1. + EVENT_DATA.sensible)

for system_domain in EVENT_DATA.domain_system.unique():
    print(system_domain)
    cph = CoxPHFitter()
    # to_drop = ['fluency', 'specific', 'sensible', 'domain_system']
    to_drop = ['domain_system']
    data = EVENT_DATA.loc[EVENT_DATA['domain_system'] == system_domain].drop(columns=to_drop)
    cph.fit(
        data,
        duration_col='time',
        event_col='spotted',
        robust=True,
        show_progress=True,
        step_size=0.1,
    )

    # cph.check_assumptions(data, show_plots=True)
    # plt.show()

    cph.print_summary()

    cph.plot()
    plt.title(f"Predictors {system_domain}")
    # plt.show()
    plt.savefig(f"predictors_{'-'.join(system_domain.split('/'))}.png")
    plt.close()
    print('*' * 80)

