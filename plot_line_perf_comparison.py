import seaborn as sns
from sklearn import preprocessing
import numpy as np
from math import floor
from math import ceil

from scipy.interpolate import make_interp_spline, BSpline
from sklearn.preprocessing.data import MinMaxScaler

sns.set()

import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 14,
                    'legend.fontsize': 14,
                     })

fig, ax = plt.subplots(figsize=(8, 5))


data = {
    'electricity': {
        'RNN-GRU': [131.02334625983568, 266.4695441675886, 398.88785200608567, 435.4095048978169, 454.6632587708118],

        'D-CNN': [109.44010834832092, 206.5636915277131, 289.75570778428374, 283.4357061541986, 287.71427396919216],

        'Seq2seq': [108.98431461787577, 191.61387997977397, 263.9694248835031, 281.30287590431044, 294.9900816084042],
        'Self-boosted': [80.7800216098457, 125.884031056754, 166.07100229556073, 187.81365138799708, 178.61930042880613]
    },

    'temperature': {
        'RNN-GRU': [2.3407691270584845, 5.248765748048668, 9.568963430446352, 11.648340563227174, 13.26482067920708],

        'D-CNN': [2.3858100872418793, 6.324139982298024,  7.465282186813688, 10.299251267859812, 9.879950804658082],

        'Seq2seq': [3.078082957441617, 5.835212628033374, 8.25892000381356, 12.313987901193574, 13.943391468327604],
        'Self-boosted': [1.9635752147334289, 4.744039810925183, 4.612209257297993, 9.939097269454377, 10.98874109033954]

    },

    'exchange_rate': {
        'RNN-GRU': [0.020143499292947852, 0.019995787975780437, 0.022305923520380123, 0.02386032910068699, 0.03157796204146639],

        'D-CNN': [0.008610779318178993, 0.011119592430211326, 0.0113448794715377,  0.012545521873342846, 0.016862703348188804],

        'Seq2seq': [0.02678391863863919, 0.035478865140097106, 0.03656039271160496, 0.03009078860016039, 0.03492806623968887],
        'Self-boosted': [0.0068517864378336004, 0.008769284833771972, 0.00907317391521684, 0.010189584351223335, 0.010705994501009104]

    },


}

# dataset = 'temperature'
# dataset = 'electricity'
dataset = 'exchange_rate'

def create_scaler():
    global dataset
    global data

    my_data = data[dataset]

    all_performances = []
    for method, performances in my_data.items():
        all_performances = all_performances + performances

    min_v = min(all_performances)
    max_v = max(all_performances)
    lower = floor(min_v)
    upper = ceil(max_v)

    if max_v < 1:
        upper = max_v
        lower = min_v

    scaler = MinMaxScaler(feature_range=(lower, upper))
    scaler.fit(np.array(all_performances).reshape(-1, 1))

    return scaler




def create_data_line(data_source, scaler):

    global dataset
    global data
    data_line = data[dataset][data_source]
    total_val = sum(data_line)
    plot_data = []
    Points = []
    index = 1
    for e in data_line:
        # normalized = e / total_val
        # plot_data.append(normalized)
        plot_data.append(e)
        Points += [index]
        index = index + 1

    plot_data = scaler.transform(np.array(plot_data).reshape(-1, 1))
    spl = make_interp_spline(Points, plot_data, k=1)  # type: BSpline
    xnew = np.linspace(min(Points), max(Points), 30)
    power_smooth = spl(xnew)

    return xnew, power_smooth


scaler = create_scaler()
xnew, power_smooth_rnn = create_data_line('RNN-GRU', scaler=scaler)
_, power_smooth_cnn = create_data_line('D-CNN', scaler=scaler)
_, power_smooth_seq2seq = create_data_line('Seq2seq', scaler=scaler)
_, power_smooth_s = create_data_line('Self-boosted', scaler=scaler)

# plt.plot(plot_data, linestyle='-', marker='o', color='#8ebad9')


plt.plot(xnew, power_smooth_rnn, linestyle='-', color='purple')
plt.plot(xnew, power_smooth_cnn, linestyle='-', color='green')
plt.plot(xnew, power_smooth_seq2seq, linestyle='-', color='blue')
plt.plot(xnew, power_smooth_s, linestyle='-', color='red')

# plt.xticks(np.arange(1, 6, step=1))
plt.xticks(np.arange(1, 6, step=1), ['t+1', 't+3', 't+5', 't+7', 't+9'])
# plt.plot(xnew, power_smooth, linestyle='-', marker='o', color='#8ebad9')

# plt.legend(['Using weather'], loc='upper right')
ax.set_ylabel('RMSE')
ax.set_xlabel('Horizon')
ax.legend(['RNN-GRU', 'Dilated CNN', 'Seq2seq', 'Self-boosted'], loc='upper left')

# ax.set_xticklabels(['Aug 23', 'Aug 24', 'Aug 25', 'day4', 'day5', 'day6', 'day7', 'day8', 'day9', 'day10', 'day11'])
# ax.set_title('Hourly average need prediction accuracy on each day')

# plt.ylim([min(plot_data) - 0.01, max(plot_data) + 0.01])

plt.savefig('results/line_perf_' + dataset + '.png')
plt.show()