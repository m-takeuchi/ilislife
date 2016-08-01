#!/usr/bin/env python3
# coding: utf-8

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec

# datafile = 'data/160725-171642.dat'

def generate_plot(datafile):
    base = datafile.rsplit('.dat')[0]
    pdffile = base+'.pdf'

    data = pd.read_csv(datafile, delimiter='\t', comment='#',names=['date','time','Ve','Ig','Ic'],           dtype={'Ve':'float64','Ig':'float64','Ic':'float64'})
    # fig = plt.figure()
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 3])
    # ax1 = fig.add_subplot(211)
    # ax2 = fig.add_subplot(212)
    ax1 = plt.subplot(gs[0])
    ax2 = plt.subplot(gs[1])
    time_h = data['time']/3600

    ax1.set_ylabel('Ve (kV)')
    ax1.set_ylim(0,10)
    ax1.set_xticklabels('')
    ax2.set_ylabel('Ig, Ic (1e-5*V)')
    ax2.set_xlabel('Time (h)')

    ax1.plot(time_h, data['Ve']/1e3, 'k-')
    ax2.plot(time_h, data['Ig']/1e5, 'g-')
    ax2.plot(time_h, data['Ic']/1e5, 'b-')

    plt.savefig(pdffile)
