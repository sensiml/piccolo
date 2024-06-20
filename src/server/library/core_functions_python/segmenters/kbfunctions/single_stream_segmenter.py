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


import argparse
import copy
import os
import re
import sys
import warnings
from traceback import print_exc

import h5py
import matplotlib.pyplot as plt
import pandas as pd
import scipy as sp
from pandas import np
from scipy import optimize, signal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def dataframe_from_h5(hdf):
    """Extract all sensor data for a single device from an h5

    Each column of the resulting DataFrame contains time series for 1 sensor axis

    Arguments:
      hdf (h5py.File or str): h5 file containing data for one device (typically APDM)
        or path to the file which can be opened with h5py.File(hdf, "r")

    Returns:
      DataFrame: 1 column for each sensor axis
    """
    if isinstance(hdf, basestring):
        hdf = h5py.File(hdf, "r")
    sensorIDs = list(hdf.parent.attrs["CaseIdList"])
    sensorLabels = list(hdf.parent.attrs["MonitorLabelList"])
    sensorLabels = [x.split() for x in sensorLabels]
    newSensorLabels = ["_".join(x) for x in sensorLabels]
    sensorNlocationMap = dict(zip(sensorIDs, newSensorLabels))
    # sensorNlocationMap = getAbbreviatedLabels(sensorIDs, sensorLabels)
    topLevelAttrs = [x for x in hdf]
    topLevelAttrs.remove(u"Annotations")  # Remove "Annotation" attribute
    outDF = pd.DataFrame()
    for myattr in topLevelAttrs:
        myAcc = hdf[myattr]["Calibrated/Accelerometers"].value
        myAccDf = pd.DataFrame(
            myAcc,
            columns=[
                ax + "_Accelerometers_" + sensorNlocationMap[myattr]
                for ax in ["X", "Y", "Z"]
            ],
        )
        myGyr = hdf[myattr]["Calibrated/Gyroscopes"].value
        myGyrDf = pd.DataFrame(
            myGyr,
            columns=[
                ax + "_Gyroscopes_" + sensorNlocationMap[myattr]
                for ax in ["X", "Y", "Z"]
            ],
        )
        myMag = hdf[myattr]["Calibrated/Magnetometers"].value
        myMagDf = pd.DataFrame(
            myMag,
            columns=[
                ax + "_Magnetometers_" + sensorNlocationMap[myattr]
                for ax in ["X", "Y", "Z"]
            ],
        )
        outDF = pd.concat([outDF, myAccDf, myGyrDf, myMagDf], axis=1)
    outDF = np.round(outDF, decimals=3)
    return outDF


def convertHDFFileIntoSensorDataAndMetaDataFile(infilename, output_dir, verbosity=0):
    """Extract sensor time series data from h5 file and write it to a CSV file"""
    outfilename = os.path.join(
        output_dir, os.path.basename(infilename).split(".")[0] + "_sensorData.txt"
    )
    myhdf = h5py.File(infilename, "r")
    sensorDf = dataframe_from_h5(myhdf)
    # myhdf.close()
    if verbosity > 0:
        print("Output path: {}".format(outfilename))
    if os.path.exists(outfilename):
        print("Destination file already exists...")
    else:
        print("Processing file " + infilename + "\n")
        # FIXME HL: use true CSV format with comma separators
        sensorDf.to_csv(outfilename, sep="\t", index=False)
    return sensorDf


def cal_Bgin_End2(p1, p2, myData, aveWidth, offset, verbosity=0):
    startS = p1 + 1  # p2 - 8*width/10
    endS = p2 - 1  # p2 - 2*width/10
    minP = 100000.0
    indexS = -1
    for i in range(startS, endS):

        if myData[i - offset] < minP:
            minP = myData[i - offset]
            indexS = i
    if verbosity > 1:
        print("IndexS: " + str(indexS))
    return indexS


def cal_Bgin_End(p1, p2, myData, aveWidth, offset, verbosity=0):
    width = p2 - p1
    startS = p2 - 7 * width / 10
    endS = p2 - 4 * width / 10
    maxP = -100000.0
    indexS = -1
    for i in range(startS, endS):
        if myData[i - offset] > maxP:
            maxP = myData[i - offset]
            indexS = i
    if verbosity > 0:
        print("IndexS: " + str(indexS))
    return indexS


def cal_Bgin_End_Use_BegEnd(p1, p2, end, begin, myData, aveWidth, offset, verbosity=0):
    width = p2 - p1
    if width <= 1.5 * aveWidth:
        startS = end
        endS = begin
        maxP = -100000.0
        indexS = -1
        for i in range(startS, endS):
            if myData[i - offset] > maxP:
                maxP = myData[i - offset]
                indexS = i
        if verbosity > 0:
            print("IndexS: " + str(indexS))
        return indexS
    else:
        return -1


def findPeak(
    newBump,
    filtered_samples,
    peakList,
    streamData,
    aveBtwPeakFoot,
    averageWidth2,
    filter_order,
    verbosity=0,
):
    # streamData is a series so the index is like [sampleOffset:500+sampleOffset]
    x = newBump
    n = len(peakList)
    offset1 = streamData.index[0]
    if verbosity > 0:
        print("offset1 " + str(offset1))
    signalTest = filtered_samples
    ff10 = copy.copy(peakList)
    average2 = copy.copy(aveBtwPeakFoot)
    averageWidth = copy.copy(averageWidth2)
    percent = 0.5  # 0.3 to 0.6 works, peak - of begin height for lifting
    percent2 = 0.3  # peak difference
    percent3 = 0.5  # width for merge

    x100 = x
    x0 = x[0] - offset1
    x1 = x[1] - offset1
    x2 = x[2] - offset1
    if x0 < 0:
        if verbosity > 0:
            print(
                "the bump is longer than the width of the window: "
                + str(x[0])
                + " "
                + str(offset1)
            )
        return (ff10, averageWidth, average2)
    # assert(x0 >= 0)
    # assert(x1 >= 0)
    # assert(x2 >= 0)
    #
    x = (x0, x1, x2)

    if len(ff10) == 0:
        if ((signalTest[x[1]] - signalTest[x[0]])) > average2:
            if verbosity > 1:
                print(" x100[1]: {}".format(x100[1]))
            n = 1
            average2 = signalTest[x[1]] - signalTest[x[0]]
            newEntry = (x100[0], x100[1], x100[2], average2, signalTest[x[1]])
            ff10.append(newEntry)
        else:  # skipping
            if verbosity > 1:
                print(" 11 " + str(x100[1]))

    else:
        if (
            x100[0] - ff10[-1][2]
        ) == 1:  # neighbor's peak, test if we should combine them
            if verbosity > 1:
                print(" 2 " + str(x100[1]))
            if (
                signalTest[x[1]] - signalTest[x[0]]
            ) > percent * average2:  # Ok the previous peak is a peak,
                if verbosity > 1:
                    print(" 3 " + str(x100[1]))
                averageWidth = (
                    averageWidth * (n - 1) / n + (ff10[-1][2] - ff10[-1][0]) / n
                )
                average2 = average2 * (n - 1) / n + ff10[-1][3] / n
                if verbosity > 1:
                    print("average width_3: " + str(averageWidth))
                    print(
                        "ff10[-1][0]_offset1_3: "
                        + str(ff10[-1][0])
                        + " "
                        + str(offset1)
                    )

                # if n > 1:
                y2 = x100
                y1 = ff10.pop()
                # p1,p2,myData,aveWidth,offset
                # index = cal_Bgin_End(y1[1]-offset1,y2[1]-offset1,streamData,averageWidth,offset)
                if verbosity > 1:
                    print("cal_Bgin_End is called 3")
                if ((y1[1] - filter_order / 2) > streamData.index[0]) and (
                    (y2[1] - filter_order / 2) < streamData.index[-1]
                ):
                    index = cal_Bgin_End(
                        y1[1], y2[1], streamData, averageWidth, filter_order / 2
                    )

                    if index > 0:

                        y2_new = (
                            index,
                            y2[1],
                            y2[2],
                            (signalTest[x[1]] - signalTest[x[0]]),
                            signalTest[x[1]],
                        )
                        y1_new = (y1[0], y1[1], index, y1[3], y1[4])
                        ff10.append(y1_new)
                        ff10.append(y2_new)
                    else:
                        ff10.append(y1)
                        newEntry = (
                            x100[0],
                            x100[1],
                            x100[2],
                            (signalTest[x[1]] - signalTest[x[0]]),
                            signalTest[x[1]],
                        )
                        ff10.append(newEntry)
                else:
                    ff10.append(y1)
                    newEntry = (
                        x100[0],
                        x100[1],
                        x100[2],
                        (signalTest[x[1]] - signalTest[x[0]]),
                        signalTest[x[1]],
                    )
                    ff10.append(newEntry)

                n = n + 1
            else:
                if verbosity > 1:
                    print(" 4 " + str(x100[1]))
                # test if we should get rid of it or merge to the previous
                if (abs(signalTest[x[1]] - ff10[-1][4]) < percent2 * average2) and (
                    (x100[1] - ff10[-1][1]) < percent3 * averageWidth
                ):  # combine
                    if verbosity > 1:
                        print(" 5 " + str(x100[1]))
                    y = ff10.pop()
                    if signalTest[x[1]] > y[4]:
                        if verbosity > 1:
                            print(" 6 " + str(x100[1]))
                        ff10.append(
                            (
                                y[0],
                                x100[1],
                                x100[2],
                                y[3] + (signalTest[x[1]] - y[4]),
                                signalTest[x[1]],
                            )
                        )
                    else:
                        if verbosity > 1:
                            print(" 7 " + str(x100[1]))
                        ff10.append((y[0], y[1], x100[2], y[3], y[4]))
                else:
                    if verbosity > 1:
                        print(
                            " 10 " + str(x100[1])
                        )  # Ok skip the current one, but update the stat since confirm the previous one is a peak, need not be update stat, but no harm done since n is not changed
                    averageWidth = (
                        averageWidth * (n - 1) / n + (ff10[-1][2] - ff10[-1][0]) / n
                    )
                    # if ((ff10[-1][1]-offset1 > 0) and (ff10[-1][0]-offset1 > 0)):
                    # average1 = average1*(n-1)/n + signalTest[ff10[-1][1]-offset1]/n
                    average2 = (
                        average2 * (n - 1) / n + ff10[-1][3] / n
                    )  # (signalTest[ff10[-1][1]-offset1] -signalTest[ff10[-1][0]-offset1])/n
                    if verbosity > 0:
                        print("average width_10: " + str(averageWidth))
                        print(
                            "ff10[-1][0]_offset1_10: "
                            + str(ff10[-1][0])
                            + " "
                            + str(offset1)
                        )
                    # else:
                    #    print "Warning_10: " + str(ff10[-1][0]) + " " + str(offset1)

        else:
            if verbosity > 1:
                print(" 8 " + str(x100[1]))
            if (
                signalTest[x[1]] - signalTest[x[0]]
            ) > percent * average2:  # or (signalTest[x[1]] > percent*average1)): #Ok the previous peak is a peak,
                if verbosity > 1:
                    print(" 9 " + str(x100[1]))
                    print(
                        "ff10[-1][0]_offset1_9: "
                        + str(ff10[-1][0])
                        + " "
                        + str(offset1)
                    )
                averageWidth = (
                    averageWidth * (n - 1) / n + (ff10[-1][2] - ff10[-1][0]) / n
                )
                # if ((ff10[-1][1]-offset1 > 0) and (ff10[-1][0]-offset1 > 0)):
                # average1 = average1*(n-1)/n + ff10[-1][4]/n#signalTest[ff10[-1][1]-offset1]/n
                # print "ff10[-1][1]-offset1 " + str(ff10[-1][1]) + " " +str(offset1) #here it is problem, if there is a huge gap between the last ff10 element and the next peak, when at the
                # time of the update signalTest or the filtered data does not have the info (since the window is moving out, so we need to save the peak value at the time when we put in the container)
                average2 = average2 * (n - 1) / n + ff10[-1][3] / n
                if verbosity > 1:
                    print("average width_9: " + str(averageWidth))
                # else:
                #    print "Warning_9: " + str(ff10[-1][0]) + " " + str(offset1)
                ###
                # if n > 1:
                y2 = x100
                y1 = ff10.pop()
                # p1,p2,myData,aveWidth,offset
                # index = cal_Bgin_End(y1[1]-offset1,y2[1]-offset1,streamData,averageWidth,offset)
                if verbosity > 1:
                    print(
                        "cal_Bgin_End is called 9 "
                        + str(y1[1])
                        + " "
                        + str(y2[1])
                        + " "
                        + str(streamData.index[0])
                        + " "
                        + str(streamData.index[-1])
                    )
                if ((y1[1] - filter_order / 2) > streamData.index[0]) and (
                    (y2[1] - filter_order / 2) < streamData.index[-1]
                ):
                    index = cal_Bgin_End(
                        y1[1], y2[1], streamData, averageWidth, filter_order / 2
                    )
                    if index > 0:
                        y2_new = (
                            index,
                            y2[1],
                            y2[2],
                            (signalTest[x[1]] - signalTest[x[0]]),
                            signalTest[x[1]],
                        )
                        y1_new = (y1[0], y1[1], index, y1[3], y1[4])
                        ff10.append(y1_new)
                        ff10.append(y2_new)
                    else:
                        ff10.append(y1)
                        newEntry = (
                            x100[0],
                            x100[1],
                            x100[2],
                            (signalTest[x[1]] - signalTest[x[0]]),
                            signalTest[x[1]],
                        )
                        ff10.append(newEntry)
                else:
                    ff10.append(y1)
                    newEntry = (
                        x100[0],
                        x100[1],
                        x100[2],
                        (signalTest[x[1]] - signalTest[x[0]]),
                        signalTest[x[1]],
                    )
                    ff10.append(newEntry)
                n = n + 1
    return (ff10, averageWidth, average2)


def segment(
    time_series,
    output_dir=os.path.curdir,
    z_score_threshold=1.0,
    filter_order=57,
    block_width=500,
    save=False,
    verbosity=0,
):
    """
    {"pre": [
    {"name": "time_series", "type": "DataFrame"}
    ],

    "post": [
    {"name": "output_data", "type": "DataFrame"}],

    "description" : "Takes a Single stream and segments the data into small time slices.
    Works best on running data."
    }
    """
    average2 = z_score_threshold * time_series.std() + time_series.mean()
    mySignal = time_series
    index = block_width - 1
    n = 0
    streamData = mySignal[0:index]  # we get 500 samples vs list only get 499
    filtered_signal = lpf(streamData, filter_order)
    length = len(filtered_signal)
    dff = [0]

    for i in range(length - 1):
        dff.append(filtered_signal[i + 1] - filtered_signal[i])

    length = len(dff)

    runL = []
    runLNeg = []
    BgPKEnd = []
    singleRun = []
    singleRunNeg = []
    begin = -1
    peak = -1
    end = -1

    test = dff  # [2500:3400]
    signalTest = filtered_signal  # [2500:3400]
    # plt.plot(signalTest)

    for i in range(len(test)):
        if test[i] > 0.0:
            singleRun.append(i)
            if len(singleRunNeg) > 0:
                runLNeg.append(singleRunNeg)
                if begin >= 0:
                    end = singleRunNeg[-1]
                    if verbosity > 1:
                        print("B " + str(begin) + " P " + str(peak) + " E " + str(end))
                    BgPKEnd.append((begin, peak, end))
                    begin = peak = -1
                singleRunNeg = []

        else:
            if len(singleRun) > 0:
                runL.append(singleRun)
                begin = singleRun[0]
                peak = singleRun[-1]
                if verbosity > 1:
                    print("B " + str(begin) + " P " + str(peak))
                singleRun = []
            singleRunNeg.append(i)

    ff10 = []
    percent = 0.5  # 0.3 to 0.6 works, peak - of begin height
    percent2 = 0.3  # peak difference
    percent3 = 0.5  # width for merge
    # average1 = -1.0

    averageWidth = 58.0
    n = 0
    offset = filter_order / 2

    for x in BgPKEnd:
        # x = (426, 453, 483)
        if len(ff10) == 0:
            if ((signalTest[x[1]] - signalTest[x[0]])) > average2:
                if verbosity > 1:
                    print(" 1 " + str(x[1]))
                newEntry = (
                    x[0],
                    x[1],
                    x[2],
                    (signalTest[x[1]] - signalTest[x[0]]),
                    signalTest[x[1]],
                )
                ff10.append(newEntry)
                n = 1
                # average1 = signalTest[x[1]]
                average2 = signalTest[x[1]] - signalTest[x[0]]
            elif verbosity > 1:  # skipping
                print(" 11 " + str(x[1]))

        else:
            if (
                x[0] - ff10[-1][2]
            ) == 1:  # neighbor's peak, test if we should combine them
                if verbosity > 1:
                    print(" 2 " + str(x[1]))
                if (
                    signalTest[x[1]] - signalTest[x[0]]
                ) > percent * average2:  # Ok the previous peak is a peak,
                    if verbosity > 1:
                        print(" 3 " + str(x[1]))
                    averageWidth = (
                        averageWidth * (n - 1) / n + (ff10[-1][2] - ff10[-1][0]) / n
                    )
                    # average1 = average1*(n-1)/n + signalTest[ff10[-1][1]]/n
                    average2 = average2 * (n - 1) / n + ff10[-1][3] / n
                    if verbosity > 0:
                        print("average width (average2): " + str(averageWidth))
                    # if n > 1:
                    # y2 = x
                    y1 = ff10.pop()
                    index = cal_Bgin_End(y1[1], x[1], mySignal, averageWidth, offset)
                    if index > 0:
                        y2_new = (
                            index,
                            x[1],
                            x[2],
                            (signalTest[x[1]] - signalTest[x[0]]),
                            signalTest[x[1]],
                        )
                        y1_new = (y1[0], y1[1], index, y1[3], y1[4])
                        ff10.append(y1_new)
                        ff10.append(y2_new)
                    else:
                        ff10.append(y1)
                        ff10.append(
                            (
                                x[0],
                                x[1],
                                x[2],
                                (signalTest[x[1]] - signalTest[x[0]]),
                                signalTest[x[1]],
                            )
                        )
                    n = n + 1
                else:
                    if verbosity > 1:
                        print("line 404, str(x[1]):" + str(x[1]))
                    # test if we should get rid of it or merge to the previous
                    if (abs(signalTest[x[1]] - ff10[-1][4]) < percent2 * average2) and (
                        (x[1] - ff10[-1][1]) < percent3 * averageWidth
                    ):
                        if verbosity > 1:
                            print("line 404, str(x[1]):" + str(x[1]))
                            print(" 5 " + str(x[1]))
                        y = ff10.pop()
                        if signalTest[x[1]] > y[4]:
                            print(" 6 " + str(x[1]))
                            ff10.append(
                                (
                                    y[0],
                                    x[1],
                                    x[2],
                                    y[3] + (signalTest[x[1]] - y[4]),
                                    signalTest[x[1]],
                                )
                            )  # y[3]+(signalTest[x[1]]-y[4])
                        else:
                            print(" 7 " + str(x[1]))
                            ff10.append((y[0], y[1], x[2], y[3], y[4]))
                    else:
                        print(
                            " 10 " + str(x[1])
                        )  # Ok skip the current one, but update the stat since confirm the previous one is a peak, need not be update stat, but no harm done since n is not changed
                        averageWidth = (
                            averageWidth * (n - 1) / n + (ff10[-1][2] - ff10[-1][0]) / n
                        )
                        average2 = average2 * (n - 1) / n + ff10[-1][3] / n

            else:
                if verbosity > 1:
                    print(" 8 " + str(x[1]))
                if (
                    signalTest[x[1]] - signalTest[x[0]]
                ) > percent * average2:  # or (signalTest[x[1]] > percent*average1)): #Ok the previous peak is a peak,
                    if verbosity > 1:
                        print(" 9 " + str(x[1]))
                    averageWidth = (
                        averageWidth * (n - 1) / n + (ff10[-1][2] - ff10[-1][0]) / n
                    )
                    average2 = average2 * (n - 1) / n + ff10[-1][3] / n
                    if verbosity > 0:
                        print("average width: " + str(averageWidth))
                    y1 = ff10.pop()
                    index = cal_Bgin_End(y1[1], x[1], mySignal, averageWidth, offset)
                    if index > 0:
                        y2_new = (
                            index,
                            x[1],
                            x[2],
                            (signalTest[x[1]] - signalTest[x[0]]),
                            signalTest[x[1]],
                        )
                        y1_new = (y1[0], y1[1], index, y1[3], y1[4])
                        ff10.append(y1_new)
                        ff10.append(y2_new)
                    else:
                        ff10.append(y1)
                        ff10.append(
                            (
                                x[0],
                                x[1],
                                x[2],
                                (signalTest[x[1]] - signalTest[x[0]]),
                                signalTest[x[1]],
                            )
                        )
                    n = n + 1
    n = 0
    index = block_width - 1
    for ii in range(1, len(mySignal) - block_width):  # 64len(mySignal)-block_width):
        # if ii == 21: break
        n = n + 1
        if verbosity > 1:
            print("nn: " + str(n))
        index = index + 1
        streamData = mySignal.ix[n:index]

        filtered_signal = lpf(streamData, filter_order)
        dff.append(filtered_signal[-1] - filtered_signal[-2])
        rr = dff.pop(0)
        del rr
        dff_index = [(i + n, dff[i]) for i in range(len(dff))]
        test = dff_index
        signalTest = filtered_signal
        if test[-1][1] > 0.0:
            singleRun.append(test[-1][0])
            if len(singleRunNeg) > 0:
                runLNeg.append(singleRunNeg)
                if begin >= 0:
                    end = singleRunNeg[-1]
                    if verbosity > 0:
                        print(
                            "begin, peak, end: {}, {}, {}"
                            + str(begin)
                            + " P "
                            + str(peak)
                            + " E "
                            + str(end)
                        )
                    BgPKEnd.append((begin, peak, end))
                    #         newBump, filtered_samples, peakList, streamData, aveBtwPeakFoot, averageWidth2, filter_order

                    ff10, averageWidth, average2 = findPeak(
                        BgPKEnd[-1],
                        filtered_signal,
                        ff10,
                        streamData,
                        average2,
                        averageWidth,
                        filter_order,
                    )
                    if verbosity > 0:
                        print("average2 " + str(average2))
                    begin = peak = -1
                singleRunNeg = []
        else:
            if len(singleRun) > 0:
                runL.append(singleRun)
                begin = singleRun[0]
                peak = singleRun[-1]
                if verbosity > 1:
                    print("B " + str(begin) + " P " + str(peak))
                singleRun = []
            singleRunNeg.append(test[-1][0])
            if verbosity > 1:
                print(singleRun)
                print(singleRunNeg)
        # print "average2 " + str(average2)
        # print "averageWidth " + str(averageWidth)

    start_end_table = pd.DataFrame(
        [(ff10[i][0] - offset, ff10[i][2] - offset) for i in range(len(ff10))],
        columns=["start", "end"],
    )

    if save:
        #
        outfilename = time_series.name + "_startEnd.txt"
        outfileData = os.path.join(output_dir, outfilename)
        Ofd = open(outfileData, "w")
        Ofd.write("start\tend\n")

        for i in range(len(ff10)):
            if ((ff10[i][0] - offset) > 0) and ((ff10[i][2] - offset) > 0):
                Ofd.write(
                    str(ff10[i][0] - offset) + "\t" + str(ff10[i][2] - offset) + "\n"
                )

        Ofd.close()
    return start_end_table


def plot_segments(segments, time_series=pd.Series(), offset=0, save=True, verbosity=1):
    """Plot segment start and end times as dots on the time series line plot"""
    fig = plt.figure()
    fig.suptitle(time_series.name, fontsize=15)

    time_series.plot()
    for x in segments.values:
        if (x[1] - offset) > 0:
            plt.plot(x[1] - offset, time_series[x[1] - offset], "ko", color="m")
        if (x[0] - offset) > 0:
            plt.plot(x[0] - offset, time_series[x[0] - offset], "ko", color="g")
        try:
            # Yuan used to record a 3rd parameter: start, end, 3rdparam?
            plt.plot(x[2] - offset, time_series[x[2] - offset], "ko", color="k")
        except:
            pass
    if save is True:
        save = os.path.join(time_series.name + ".png")
    if save:
        plt.savefig(save)
        if verbosity > 0:
            print("Saved plot to {}".format(save))
        plt.close(fig)
        return None
    elif verbosity > 1:
        print("Figure titled '{}' was shown.".format(time_series.name))
        plt.show(block=False)
        return fig
    elif verbosity > 0:
        print("Plot titled '{}' was not saved or displayed.".format(time_series.name))
        plt.close(fig)
        return None
    return None


def dataframe_from_sensor_file(filename):
    try:
        df = pd.read_csv(filename, index_col=False, header=0)
    except:
        df = dataframe_from_h5(filename)

    if df.index.dtype == "object":
        df.index = df[(c for c in df.columns if c.lower().startswith("seq")).next()]
        df.reindex()
    return df


def segment_files(
    input_dir="M:/NDG-EXOS-PoC/Root/Original/Protocol_V1/U700-701/Piccolo/100Hz_Ankle",
    output_dir="D:/segmentation_results",
    sensors=["gyroz"],
    verbosity=1,
):
    """Segment all *.csv files found in the indicated path

    Arguments:
      input_dir
    """
    if isinstance(sensors, basestring):
        sensors = [sensors]
    if not input_dir:
        warnings.warn(
            "No input directory specified. Nothing to do. Enter `segmenter -h` for usage."
        )
        try:
            input_dir = input(
                "Enter an input directory for reading csv or h5 files from: "
            )
        except SyntaxError:
            print_exc()
            warnings.warn("Unable to interpret the python expression provided.")
            return None
    input_dir = fix_path(input_dir)
    if output_dir is not None:
        output_dir = fix_path(output_dir)
        if not os.path.isdir(input_dir):
            input_dir = fix_path(
                input(
                    "Enter python expression for the path of the directory containing the time series CSV files: "
                )
            )
        try:
            os.mkdir(output_dir)
        except:
            pass
        if not os.path.isdir(output_dir):
            output_dir = os.path.curdir
    if not os.path.isdir(input_dir):
        raise RuntimeError(
            "Unable to find time series input files (*.csv) at {}".format(input_dir)
        )
    # FIXME: regex can't handle os.path.sep character, so have to put both in
    regex = re.compile(r"(U[0-9]{2,3}[^\\/]+[.])(csv|CSV|h5|H5)$")
    filenames = [
        os.path.join(input_dir, f) for f in os.listdir(input_dir) if regex.search(f)
    ]
    if not os.path.exists(output_dir):
        mkdir_p(output_dir)
    df_segments = pd.DataFrame()
    for filename in filenames:
        for sensor in sensors:
            basename = os.path.basename(filename).split(".")[0]
            time_series = dataframe_from_sensor_file(filename)[sensor]
            time_series.name = basename + "_" + time_series.name
            df = segment(time_series, output_dir, verbosity=verbosity - 1)
            try:
                for col in df.columns:
                    df_segments[basename + "_" + col] = df[col]
                df.to_csv(
                    "{}_{}_segments.csv".format(basename, sensor), index_label="rep"
                )
                if verbosity > 0:
                    print("Found {} segments in {}.".format(len(df_segments), filename))
            except:
                print(df_segments)
                print_exc()
                if verbosity >= 0:
                    input("Press Enter to continue...")
    if output_dir is not None:
        df_segments.to_csv(os.path.join(output_dir, "all_segments.csv"))
    return df_segments


def segment_h5_files(
    input_dir, output_dir=os.path.curdir, sensors=["gyroz"], verbosity=0
):
    """DEPRECATED: Generate segment (start, end) files for each h5 file found in `input_dir`

    DEPRECATED: use segment_files instead
    """
    filenames = [
        os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".h5")
    ]
    if not os.path.exists(output_dir):
        mkdir_p(output_dir)
    df_segments = pd.DataFrame()
    for filename in filenames:
        basename = os.path.basename(filename)
        df_signals = convertHDFFileIntoSensorDataAndMetaDataFile(filename, output_dir)
        for sensor in sensors:
            df = segment(
                df_signals[sensor],
                filename,
                output_dir,
                filter_order=57,
                block_width=500,
                verbosity=verbosity - 1,
            )
            # TODO: incorporate h5 files directly into segment_files so this section isn't duplicated
            try:
                for col in df.columns:
                    df_segments[basename + "_" + col] = df[col]
                df.to_csv(
                    "{}_{}_segments.csv".format(basename, sensor), index_label="rep"
                )
                if verbosity > 0:
                    print("Found {} segments in {}.".format(len(df_segments), filename))
            except:
                print(df_segments)
                print_exc()
                input("Press Enter to continue...")
    return 0


def plot_fft(time_series):
    """Plot the Fast Fourier Transformation of a signal (sequence)"""
    Fs = 128.0  # sampling rate
    n = len(time_series)  # length of the signal
    k = np.arange(n)
    T = n / Fs
    frq = k / T  # two sided frequency range
    frq = frq[range(n / 2)]  # one side frequency range

    y = time_series
    Y = np.fft.fft(y) / n  # fft computing and normalization
    Y = Y[range(n / 2)]
    plt.plot(frq, abs(Y), "r")


def lpf(time_series, numtaps=117, Fs=128.0, cutoff=2.0):
    """Filter `time_series` with a FIR lowpass filter of order (numtaps / 2) - 1

    Arguments:
      Fs (float): sample rate (frequency) in Hz
      cutoff (float): cutoff frequency in Hz
      time_series (np.array): sequence of values to be low pass filtered
      numtaps (int): odd integer indicating the desired FIR filter order
        FIR_order = numtaps / 2 - 1

    Output:
      np.array: Filtered signal

    >>> np.round(lpf(np.concatenate([np.arange(3), np.arange(3)])), 4)
    array([ 0.    , -0.0002, -0.0008, -0.0009, -0.0013, -0.002 ])
    """
    nyquist_rate = Fs / 2.0
    # compute the coefficients for a low-pass FIR filter
    fir_coeff1 = signal.firwin(numtaps, cutoff / nyquist_rate)
    filtered_signal = signal.lfilter(fir_coeff1, 1.0, time_series)
    return filtered_signal


def calDisp_1(accelData):
    # data1 = [x/(128.0*128.0) for x in accelData]
    V_Y = sp.integrate.cumtrapz(accelData)
    C0 = V_Y[0]
    V_Y_Adj = [x - C0 for x in V_Y]
    return V_Y_Adj


def linear_polynomial(x, a0, a1):
    """Evaluate the equation of a line for the provided x values, bias, and slope"""
    return a0 + a1 * x


def fit_line(y):
    """Fit a line to a signal or sequence

    Returns:
      np.array: the smoothed signal (evaluations of the line equation)
      np.array: the difference between the original signal and the smoothed signal

    >>> np.round(fit_line(np.arange(6) ** 1.5))  # doctest: +NORMALIZE_WHITESPACE
    array([[ -1.,   1.,   4.,   6.,   8.,  10.],
           [  1.,   0.,  -1.,  -1.,   0.,   1.]])
    """
    index = np.arange(len(y))
    popt, pcov = optimize.curve_fit(linear_polynomial, index, y)
    y_fit = linear_polynomial(index, popt[0], popt[1])
    delta = y - y_fit
    return y_fit, delta


def fix_path(p):
    """Standardize a path string to work on a Windows, DOS, POSIX, and Mac OSX"""
    return os.path.abspath(os.path.expanduser(p))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Segment a time series found in the indicated directory as *.csv files."
    )
    parser.add_argument(
        "input_dir",
        nargs="?",
        type=str,
        default=None,
        help="Input directory containing csv files to be parsed",
    )
    parser.add_argument(
        "output_dir",
        nargs="?",
        type=str,
        default=None,
        help="Output directory where csv files containing segment start and end indices will be written",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    sys.exit(
        segment_files(
            input_dir=getattr(args, "input_dir", None),
            output_dir=getattr(args, "output_dir", None),
        )
    )
