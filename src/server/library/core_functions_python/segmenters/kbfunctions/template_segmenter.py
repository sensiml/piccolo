"""
Copyright 2017-2024 SensiML Corporation

This file is part of SensiML™ Piccolo AI™.

SensiML Piccolo AI is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

SensiML Piccolo AI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with SensiML Piccolo AI. If not, see <https://www.gnu.org/licenses/>.
"""

import copy
import sys

import numpy as np
from matplotlib.mlab import PCA
from pandas import DataFrame
from scipy.optimize import curve_fit
from scipy.stats import pearsonr
from sklearn.cluster import KMeans


def calculatenorm(myData):
    # calculate norm
    # change from 3 X 3952 to 3952 X 3
    myData = map(list, zip(*myData))
    norm = []
    for i in range(len(myData)):
        x = 0.0
        for j in range(len(myData[i])):
            x = x + myData[i][j] * myData[i][j]
        x = np.sqrt(x)
        norm.append(x)
    return norm


def setInitialPeaks(zz, outlers, average, theLimit):
    width = 0
    width12 = zz[2] - zz[1]
    width02 = zz[2] - zz[0]
    if abs(width02 - average) <= theLimit:
        # the second peak is bad
        outlers.append(1)
        width = width02
    else:
        if abs(width12 - average) <= theLimit:
            # the first peak is bad
            outlers.append(0)
            width = width12
        else:
            # both the first & second peaks are bad
            outlers.append(0)
            outlers.append(1)
    return width


def findOutliersBasedOnWidth(zz, mean, limit):
    outlers = []
    widths = [np.nan] * (len(zz) - 1)
    skip = False
    width = 0

    for k in range(1, len(zz)):
        if skip:
            skip = False
            continue
        width = zz[k] - zz[k - 1]
        if abs(width - mean) > limit:
            # need to decide initial peak
            if (k == 1) and (k + 1 < len(zz)):  # at least we have three peaks
                width = setInitialPeaks(zz, outlers, mean, limit)
                if width == 0:
                    # raise
                    pass
                    # let go even if the first of two peaks failed to be the good one, assume the third is good.
                else:
                    widths[k - 1] = width
                skip = True  # skip both conditions
            else:  # so pass the intial
                outlers.append(k)
        else:  # good width
            widths[k - 1] = width
    return outlers


def findOutliersBasedOnPeaks(peaks, mean, limit):
    outLiers = []
    for k in range(len(peaks)):
        if abs(peaks[k] - mean) > limit:
            outLiers.append(k)
    return outLiers


def calWidths(peaks):
    widths = []
    for k in range(1, len(peaks)):
        ww = peaks[k] - peaks[k - 1]
        widths.append(ww)
    return widths


def computePCA(myData):
    # construct your numpy array of data
    myArray = np.array(myData)
    myArray = myArray.T
    results = PCA(myArray)
    results.fracs
    myPCA = results.Y
    myPCA = myPCA.T
    myPCA = list(myPCA)
    return myPCA


def findPeaksByKMeans(ZT):
    estimator = KMeans(init="k-means++", max_iter=300, n_clusters=2, n_init=50)
    # init='random'
    estimator.fit(ZT)
    dd = list(estimator.labels_)
    mm = []
    nn = []
    for i, j in enumerate(dd):
        if j > 0:
            mm.append(i)
        else:
            nn.append(i)
    return (mm, nn)


def PlotHistogram(z, myDataList, n):
    actualPeaks = []
    for i in z:
        if i in range(len(myDataList)):
            actualPeaks.append(myDataList[i])
    actualPeaks = sorted(actualPeaks, reverse=True)
    # plt.hist(actualPeaks)
    return actualPeaks


def linearCurveFit(x, a0, a1):
    return a0 + a1 * x


def wrapper_linearCurveFit(inVec1, indArr1, inVec2):
    indArr2 = np.arange(len(inVec2))
    popt, pcov = curve_fit(linearCurveFit, indArr1, inVec1)
    newFit = linearCurveFit(indArr2, popt[0], popt[1])
    newList = inVec2 - newFit
    return (newFit, newList)


def calMeanStd(myList):
    Mean = sum(myList) / float(len(myList))
    Stdev = np.std(myList)
    return (Mean, Stdev)


def findPeaksBasedOnCorr(xaxisRange, windowSize, xVector, templateSignal, rThreshold):
    i = 0
    peakPoints = []
    totalLength = len(xaxisRange)
    halfWindowSize = windowSize / 2
    # intialDist = halfWindowSize
    while i < (totalLength - windowSize):

        qSignal = xVector[i : i + windowSize]
        z = pearsonr(qSignal, templateSignal)
        if z[0] >= rThreshold:
            maxR = z[0] * 0.95
            temp = [(i, z[0])]
            j = 1
            newR = z[0]
            endNew = i + windowSize + j
            while (
                (j < int(windowSize * 0.2))
                and (newR > maxR)
                and (endNew <= totalLength)
            ):
                qSignal = xVector[i + j : i + windowSize + j]
                newZ = pearsonr(qSignal, templateSignal)
                newR = newZ[0]
                temp.append((i + j, newR))
                j = j + 1
                endNew = i + windowSize + j

            from operator import itemgetter

            sortedTemp = sorted(temp, key=itemgetter(1), reverse=True)

            temp = sortedTemp[0][0] + halfWindowSize
            print >> sys.stderr, "temp " + str(temp) + " R " + str(sortedTemp[0][1])
            peakPoints.append((sortedTemp[0][0] + halfWindowSize, sortedTemp[0][1]))
            i = sortedTemp[0][0] + int(windowSize * 0.8)
        else:
            i = i + 1

    return peakPoints


def findPeaksBasedOnEnergy(xaxisRange, windowSize, xVector, templateSignal, eThreshold):
    i = 0
    peakPoints = []
    totalLength = len(xaxisRange)
    halfWindowSize = windowSize / 2
    # intialDist = halfWindowSize
    while i < (totalLength - windowSize):

        qSignal = xVector[i : i + windowSize]
        energy = sum([abs(x) for x in qSignal])
        if energy >= eThreshold:
            maxR = energy * 0.95
            delta = halfWindowSize
            temp = [(i + delta, energy)]
            j = 1
            newR = energy
            while (j < int(windowSize * 0.6)) and (newR > maxR):
                qSignal = xVector[i + j : i + windowSize + j]
                newR = sum([x for x in qSignal if x > 0])
                # print >> sys.stderr, newR
                temp.append((i + j + delta, newR))
                j = j + 1

            from operator import itemgetter

            sortedTemp = sorted(temp, key=itemgetter(1), reverse=True)

            # print >> sys.stderr,  sortedTemp

            # print >> sys.stderr, str(z[0]) + " " + str(rThreshold)
            peakPoints.append((sortedTemp[0][0], sortedTemp[0][1]))
            i = sortedTemp[0][0] - delta + int(windowSize * 0.8)
        else:
            i = i + 1

    return peakPoints


def cleanupEnergyPeaks(myPeaksE, myPeaks, windowSize):
    copyE = copy.copy(myPeaksE)
    for x in myPeaksE:
        minDist = 10 * windowSize
        for y in myPeaks:
            newDist = abs(x[0] - y[0])
            if newDist < minDist:
                minDist = newDist
        if minDist < windowSize:
            copyE.remove(x)
    return copyE


def cleanupEnergyPeaks2(myPeaksE, windowSize):
    copyE = copy.copy(myPeaksE)
    prev = myPeaksE[0][0]
    for x in myPeaksE[1:]:
        dist = x[0] - prev
        if dist < int(windowSize * 0.6):
            copyE.remove(x)
        prev = x[0]

    return copyE


def recalCorrForEnergyPeaks(xaxisRange, xVector, peakPoints, templateSignal):

    windowSize = len(templateSignal)
    halfWindow = windowSize / 2

    finalPeaks = []
    for x in peakPoints:
        newPeaks = []
        j = 1
        start = x[0] - halfWindow
        end = start + windowSize
        qSignal = xVector[start : start + windowSize]
        z = pearsonr(qSignal, templateSignal)
        newPeaks.append((x[0], z[0], x[1], 1))
        print >> sys.stderr, "loc " + str(x[0]) + " r " + str(z[0]) + " energy " + str(
            x[1]
        )
        while (
            (j < int(windowSize * 0.5))
            and ((start - j) > 0)
            and ((end + j) < len(xaxisRange))
        ):

            left = start - j
            qSignal = xVector[left : left + windowSize]
            z = pearsonr(qSignal, templateSignal)
            newE = sum([x for x in qSignal if x > 0])
            newPeaks.append(((left + halfWindow), z[0], newE, 1))
            right = start + j
            qSignal = xVector[right : right + windowSize]
            z = pearsonr(qSignal, templateSignal)
            newE = sum([x for x in qSignal if x > 0])
            newPeaks.append(((right + halfWindow), z[0], newE, 1))
            j = j + 1
        from operator import itemgetter

        sortedTemp = sorted(newPeaks, key=itemgetter(1), reverse=True)
        # print >> sys.stderr, sortedTemp
        finalPeaks.append(
            (sortedTemp[0][0], sortedTemp[0][1], sortedTemp[0][2], sortedTemp[0][3])
        )

    return finalPeaks


def recalEngeryForCorrPeaks(xaxisRange, xVector, peakPoints, templateSignal):
    windowSize = len(templateSignal)
    halfWindow = windowSize / 2
    tempE = sum([x for x in templateSignal if x > 0])
    # print >> sys.stderr, "Temp " + str(tempE)
    finalPeaks = []
    for x in peakPoints:
        start = x[0] - halfWindow
        qSignal = xVector[start : start + windowSize]
        newE = sum([y for y in qSignal if y > 0])
        # print >> sys.stderr, newE
        if newE > tempE * 0.3:

            newT = x + (newE, 0)
            finalPeaks.append(newT)

    return finalPeaks


def execute(myDataList, tempSt, tempEnd, rThreshold):
    print >> sys.stderr, "execute enter."

    template = myDataList[tempSt:tempEnd]

    totalNumberOfPointsSampled = len(myDataList)
    xaxisRange = range(0, totalNumberOfPointsSampled)
    windowSize = len(template)

    myPeaks = findPeaksBasedOnCorr(
        xaxisRange, windowSize, myDataList, template, rThreshold
    )
    # for i in myPeaks:
    #    if i[0] in range (len(myDataList)):
    #        #print i
    #        plt.plot(i[0], myDataList[i[0]], 'ro', color= 'yellow')

    eThreshold = sum([abs(x) for x in template]) * rThreshold

    myPeaksE = findPeaksBasedOnEnergy(
        xaxisRange, windowSize, myDataList, template, eThreshold
    )

    # for i in myPeaksE:
    #    if i[0] in range (len(myDataList)):
    #        #print i
    #        plt.plot(i[0], myDataList[i[0]], 'ro', color= 'r')

    copyE = cleanupEnergyPeaks(myPeaksE, myPeaks, windowSize)

    # for i in copyE:
    #    if i[0] in range (len(myDataList)):
    #        #print i
    #        plt.plot(i[0], myDataList[i[0]], 'ro', color= 'r')

    peaksEwithR = recalCorrForEnergyPeaks(xaxisRange, myDataList, copyE, template)

    newPeaks = [i for i in peaksEwithR if i[1] > rThreshold * 0.60]

    newNewPeaks = []

    if len(newPeaks) > 0:
        newPeaks2 = cleanupEnergyPeaks2(newPeaks, windowSize)
        if len(newPeaks2) > 0:
            newNewPeaks = cleanupEnergyPeaks(newPeaks2, myPeaks, windowSize)
    newCorrPeaks = recalEngeryForCorrPeaks(xaxisRange, myDataList, myPeaks, template)
    CombinedPeaks = newCorrPeaks + newNewPeaks
    from operator import itemgetter

    sortedPeaks = sorted(CombinedPeaks, key=itemgetter(0), reverse=False)
    singletonPeaks = [x[0] for x in sortedPeaks]
    widths = calWidths(singletonPeaks)
    ####
    reshape = []
    for x in range(len(widths)):
        reshape.append([widths[x]])

    choice1, choice2 = findPeaksByKMeans(reshape)

    choice11 = [widths[x] for x in choice1]
    choice22 = [widths[x] for x in choice2]

    mean1 = float(sum(choice11) / len(choice11))
    mean2 = float(sum(choice22) / len(choice22))

    widePeak = []
    norrowPeak = []
    if mean1 > mean2:
        for x in choice1:
            widePeak.append((x, 1))
        for y in choice2:
            norrowPeak.append((y, 0))
    else:
        for x in choice2:
            widePeak.append((x, 1))
        for y in choice1:
            norrowPeak.append((y, 0))

    finalPeak = widePeak + norrowPeak

    sortedWidths = sorted(finalPeak, key=itemgetter(0), reverse=False)

    ####
    nn = 0.5
    ww = 0.35
    frontSearch = []
    if sortedWidths[0][1] > 0:
        theFirst = singletonPeaks[0] - int(widths[0] * ww)
    else:
        theFirst = singletonPeaks[0] - int(widths[0] * nn)
    if theFirst < 0:
        theFirst = 0

    frontSearch.append(theFirst)

    for j in range(1, len(singletonPeaks)):
        if sortedWidths[j - 1][1] > 0:
            region = singletonPeaks[j] - int(widths[j - 1] * ww)
        else:
            region = singletonPeaks[j] - int(widths[j - 1] * nn)
        # print region
        frontSearch.append(region)

    ##plt.plot(myDataList)
    # for i in frontSearch:
    #    if i in range (len(myDataList)):
    #        #print i
    #        plt.plot(i, myDataList[i], 'ro', color= 'c')

    backSearch = []
    for j in range(0, len(singletonPeaks) - 1):

        if sortedWidths[j][1] > 0:
            region = singletonPeaks[j] + int(widths[j] * ww)
        else:
            region = singletonPeaks[j] + int(widths[j] * nn)
        # print j
        backSearch.append(region)

    if sortedWidths[-1][1] > 0:
        thelast = singletonPeaks[-1] + int(widths[-1] * ww)
    else:
        thelast = singletonPeaks[-1] + int(widths[-1] * nn)

    if thelast > len(myDataList):
        thelast = myDataList[-1]

    backSearch.append(thelast)

    # for i in backSearch:
    #    if i in range (len(myDataList)):
    #        #print i
    #        plt.plot(i, myDataList[i], 'ro', color= 'm')

    FinalStartEndPair = []
    for i in range(len(frontSearch)):
        FinalStartEndPair.append((frontSearch[i], backSearch[i]))

    FinalStartEndPair_with_offset = [(x[0], x[1]) for x in FinalStartEndPair]

    return FinalStartEndPair_with_offset


def template_detect(
    time_series,
    start,
    end,
    sensor_index=0,
    threshold=-1.00,
    percent_start_to_skip=-1.00,
):
    """
    {"pre": [
    {"name": "time_series", "type": "DataFrame"},
    {"name": "start", "type": "int"},
    {"name": "end", "type": "int"}
    ],

    "post": [
    {"name": "output_data", "type": "DataFrame"}],

    "description" : "Takes a single sensor stream, and a definition of the template window.\nTemplate window is defined by two sample numbers, such as a label in the DTK. "
    }
    """

    myData = time_series.tolist()

    myData1 = copy.copy(myData)

    length = len(myData1)
    front = 200
    _end = length - 1000

    if start == -1 and end == -1:
        return None

    myData1 = myData1[front:_end]

    ave = np.average(myData1)
    myDataList = [x - ave for x in myData1]

    if threshold < 0:
        threshold = 0.8
    print >> sys.stderr, start, end, threshold
    found_list = execute(myDataList, start - front, end - front, threshold)

    found_list_adjusted = [(x[0] + front, x[1] + front) for x in found_list]

    found_frame = DataFrame(
        [
            (found_list_adjusted[i][0], found_list_adjusted[i][1])
            for i in range(len(found_list_adjusted))
        ],
        columns=["start", "end"],
    )
    return found_frame
