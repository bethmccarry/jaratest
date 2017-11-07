import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from jaratoolbox import settings
from jaratoolbox import extraplots
import figparams
reload(figparams)

FIGNAME = 'frequency_tuning'
dataDir = os.path.join(settings.FIGURES_DATA_PATH, figparams.STUDY_NAME, FIGNAME)

PANELS = [1, 1, 1, 1, 1, 1, 1, 1, 1] # Plot panel i if PANELS[i]==1

SAVE_FIGURE = 1
outputDir = '/tmp/'
figFilename = 'plots_frequency_tuning' # Do not include extension
figFormat = 'svg' # 'pdf' or 'svg'
figSize = [7,7] # In inches

fontSizeLabels = figparams.fontSizeLabels
fontSizeTicks = figparams.fontSizeTicks
fontSizePanel = figparams.fontSizePanel

labelPosX = [0.07, 0.39, 0.69]   # Horiz position for panel labels
labelPosY = [0.92, 0.60, 0.28]    # Vert position for panel labels

# Define colors, use figparams
laserColor = figparams.colp['blueLaser']

fig = plt.gcf()
fig.clf()
fig.set_facecolor('w')

gs = gridspec.GridSpec(3, 3)
gs.update(left=0.15, right=0.98, top=0.95, bottom=0.05, wspace=.4, hspace=0.3)


##### Thalamus #####
# -- Panel: Thalamus sharp tuning --
axSharp = plt.subplot(gs[0, 0])
axSharp.annotate('A', xy=(labelPosX[0],labelPosY[0]), xycoords='figure fraction',
             fontsize=fontSizePanel, fontweight='bold')
if PANELS[0]:
    # Plot stuff
    pass
# -- Panel: Thalamus wide tuning --
axWide = plt.subplot(gs[0, 1])
axWide.annotate('B', xy=(labelPosX[1],labelPosY[0]), xycoords='figure fraction',
             fontsize=fontSizePanel, fontweight='bold')
if PANELS[1]:
    # Plot stuff
    pass
# -- Panel: Thalamus histogram --
axHist = plt.subplot(gs[0, 2])
axHist.annotate('C', xy=(labelPosX[2],labelPosY[0]), xycoords='figure fraction',
             fontsize=fontSizePanel, fontweight='bold')
axHist.set_xlabel('BW10')
axHist.set_ylabel('% Neurons')
if PANELS[2]:
    # Plot stuff
    pass

##### Cortex #####
# -- Panel: Cortex sharp tuning --
axSharp = plt.subplot(gs[1, 0])
axSharp.annotate('D', xy=(labelPosX[0],labelPosY[1]), xycoords='figure fraction',
             fontsize=fontSizePanel, fontweight='bold')
if PANELS[3]:
    # Plot stuff
    pass
# -- Panel: Cortex wide tuning --
axWide = plt.subplot(gs[1, 1])
axWide.annotate('E', xy=(labelPosX[1],labelPosY[1]), xycoords='figure fraction',
             fontsize=fontSizePanel, fontweight='bold')
if PANELS[4]:
    # Plot stuff
    pass
# -- Panel: Cortex histogram --
axHist = plt.subplot(gs[1, 2])
axHist.annotate('F', xy=(labelPosX[2],labelPosY[1]), xycoords='figure fraction',
             fontsize=fontSizePanel, fontweight='bold')
axHist.set_xlabel('BW10')
axHist.set_ylabel('% Neurons')
if PANELS[5]:
    # Plot stuff
    pass


##### Striatum #####
# -- Panel: Striatum sharp tuning --
axSharp = plt.subplot(gs[2, 0])
axSharp.annotate('G', xy=(labelPosX[0],labelPosY[2]), xycoords='figure fraction',
             fontsize=fontSizePanel, fontweight='bold')
if PANELS[6]:
    # Plot stuff
    pass
# -- Panel: Striatum wide tuning --
axWide = plt.subplot(gs[2, 1])
axWide.annotate('H', xy=(labelPosX[1],labelPosY[2]), xycoords='figure fraction',
             fontsize=fontSizePanel, fontweight='bold')
if PANELS[7]:
    # Plot stuff
    pass
# -- Panel: Striatum histogram --
axHist = plt.subplot(gs[2, 2])
axHist.annotate('I', xy=(labelPosX[2],labelPosY[2]), xycoords='figure fraction',
             fontsize=fontSizePanel, fontweight='bold')
axHist.set_xlabel('BW10')
axHist.set_ylabel('% Neurons')
if PANELS[8]:
    # Plot stuff
    pass


plt.show()

if SAVE_FIGURE:
    extraplots.save_figure(figFilename, figFormat, figSize, outputDir)