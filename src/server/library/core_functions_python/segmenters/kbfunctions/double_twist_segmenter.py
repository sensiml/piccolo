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


from pandas import concat
from pandas import DataFrame
import numpy as np
import copy
from scipy.signal import lfilter

WINDOW_WIDTH = 470  # 550 #370 # 470 #550         #
INITIAL_PEAK = 8000  #
TAPS = 3  #
MIN_TWIST_WIDTH = 20
MAX_TWIST_WIDTH = 80
PERCENT_PEAK = 0.5
BTW_GESTURE_MIN_DISTANCE = 100
GESTURE_MAX_LIMIT = 350  # 300#410 #250 #350 #410
GESTURE_LIMIT = 300  # 250 #200 #300 #350 #
COMBINE_PEAK_LIMIT = 10
DELAY_SEND = 90  # 90#100 #90 #100
B0 = 0.06896542
B1 = 0.86206916
B2 = 0.06896542
B_COEFF = np.array([B0, B1, B2])


def streaming_gesture_spotting(
    input_data, streams_to_use, axis_of_interest, group_columns
):
    """
    {"pre": [
    {"name": "input_data", "type": "DataFrame"},
    {"name": "streams_to_use", "type": "list"},
    {"name": "axis_of_interest", "type": "str"},
    {"name": "group_columns", "type": "list", "element_type": "str"}],

    "post": [
    {"name": "output_data", "type": "DataFrame"}],

    "description": "Performs gesture spotting and truncates all event data
    streams to just the section of the time series determined to be a valid
    gesture. There should be multiple gestures expected per group, and each
    will be given a rep ID in the output. The user must provide the names of
    at least four data streams to return and one stream to use for spotting."
    }
    """
    spotted = DataFrame()
    if len(group_columns):
        grouped = input_data.groupby(group_columns, sort=False, as_index=False)
        for name, group in grouped:
            group = group.reset_index(drop=True)
            spot = call_recognition_module_to_find_start_end(
                group, streams_to_use, axis_of_interest
            )
            for c, i in enumerate(spot.index):
                df = group.ix[
                    spot.ix[i, "Peak_Begin"] : spot.ix[i, "Peak_End"], :
                ].copy()
                df["Rep"] = c
                spotted = concat([spotted, df], axis=0)

            # Rename the columns correctly if needed
            if len(group_columns) == 1:
                spot[group_columns[0]] = name
            else:
                for i, col in enumerate(group_columns):
                    spot[group_columns[i]] = name[i]
    else:
        # For a single group/streaming data
        spot = call_recognition_module_to_find_start_end(
            input_data, streams_to_use, axis_of_interest
        )
        for c, i in enumerate(spot.index):
            df = input_data.ix[
                spot.ix[i, "Peak_Begin"] : spot.ix[i, "Peak_End"], :
            ].copy()
            df["Rep"] = c
            spotted = concat([spotted, df], axis=0)

    return spotted.reset_index(drop=True)


def filterSig(signal):

    # signal = [10,2,3,4,5,6,7,8,9]
    filtered_signal = lfilter(B_COEFF, 1.0, signal)

    return filtered_signal


def intitialize(mySignal, taps):
    streamData = mySignal
    filtered_signal = filterSig(streamData)
    length = len(filtered_signal)

    dff = [0]

    for i in range(length - 1):
        dff.append(filtered_signal[i + 1] - filtered_signal[i])

    BgPKEnd = []
    singleRun = []
    singleRunNeg = []
    begin = -1
    peak = -1
    end = -1

    for i in range(len(dff)):
        if dff[i] > 0.0:
            singleRun.append(i)
            if len(singleRunNeg) > 0:

                if begin >= 0:
                    end = singleRunNeg[-1]
                    # outLog.write( "B "+str(begin)+" P "+str(peak)+" E "+str(end)+ "\n")
                    BgPKEnd.append((begin, peak, end))
                    begin = peak = -1
                singleRunNeg = []

        else:
            if len(singleRun) > 0:
                begin = singleRun[0]
                peak = singleRun[-1]
                # outLog.write( "B "+str(begin)+" P "+str(peak)+ "\n")
                singleRun = []
            singleRunNeg.append(i)

    return (BgPKEnd, singleRun, singleRunNeg, dff, begin, peak, end)


def twistState(threeTwists, x100, lastTwist, threeTwistsCopy, calledFrom, offset1):
    assert len(threeTwists) < 3
    if len(threeTwists) == 0:
        # outLog.write( "threeTwists3" + "\n")
        if ((x100[1] - lastTwist) > BTW_GESTURE_MIN_DISTANCE) or (
            len(threeTwistsCopy) > 0
        ):
            threeTwists.append((x100[0], x100[1], x100[2]))
        else:
            lastTwist = x100[1]
            # outLog.write( "skip this twist1: "+str(x100[1]+offset1) + calledFrom + "\n")
    else:
        if len(threeTwists) == 1:  # double twists
            if ((x100[1] - threeTwists[-1][1]) > MAX_TWIST_WIDTH) or (
                (x100[1] - threeTwists[-1][1]) < MIN_TWIST_WIDTH
            ):
                threeTwists.pop()
                # outLog.write( "threeTwists4"+ calledFrom + "\n")
                threeTwists.append((x100[0], x100[1], x100[2]))
            else:
                # outLog.write( "threeTwists5"+ calledFrom + "\n")
                threeTwists.append((x100[0], x100[1], x100[2]))
        else:  # end twist
            if (x100[1] - threeTwists[-1][1]) < MAX_TWIST_WIDTH:
                # take care the case, a user did more than two twists at the beginning
                # outLog.write( "threeTwists6"+ calledFrom + "\n")
                temp = threeTwists[-1]
                threeTwists = []
                threeTwists.append(temp)
                threeTwists.append((x100[0], x100[1], x100[2]))
            else:
                # outLog.write( "threeTwists7"+ calledFrom + "\n")
                threeTwists.append((x100[0], x100[1], x100[2]))
    return (threeTwists, lastTwist)


def findPeak(
    newBump,
    filtered_samples,
    peakList,
    lastIndex,
    aveBtwPeakFoot,
    taps,
    threeTwists,
    threeTwistsCopy,
    lastTwist,
):

    # streamData is a series so the index is like [sampleOffset:500+sampleOffset]
    x = newBump
    n = len(peakList)

    # offset1 is the distance from the beginning of the CSV file or 0 to the current
    # beginning of the window, we need to keep this reference, for the real streamming
    # need to think it over
    offset1 = lastIndex  # streamData.index[0]
    # assert(offset1 == lastIndex)
    # outLog.write( "offset1 " + str(offset1) + "\n")
    signalTest = filtered_samples
    ff10 = copy.copy(peakList)
    average2 = copy.copy(aveBtwPeakFoot)

    x100 = x
    #  x0 = x[0] - offset1
    #  x1 = x[1] - offset1
    #  x2 = x[2] - offset1
    #  if (x0 < 0):
    #      outLog.write( "the bump is longer than the width of the window: " + str(x[0]) + " " + str(offset1) + "\n")
    #      return (ff10, average2, [])
    #
    #  x = (x0,x1,x2)
    #

    if len(ff10) == 0:
        if (signalTest[x[1]]) > average2:
            # outLog.write( " 1 " + str(x100[1]+offset1) + "\n")

            average2 = signalTest[x[1]]
            # outLog.write( "average2: " + str(average2)+ "\n")
            newEntry = (
                x100[0],
                x100[1],
                x100[2],
                (signalTest[x[1]] - signalTest[x[2]]),
                signalTest[x[1]],
                x100[1],
                offset1,
            )
            ff10.append(newEntry)
            threeTwists = []
            # outLog.write( "threeTwists0" + "\n")
            threeTwists.append((x100[0], x100[1], x100[2]))

        # else: # skipping
        #     outLog.write( " 11 " + str(x100[1]+offset1) + "\n")

    else:
        if (
            x100[0] - ff10[-1][2]
        ) == 1:  # neighbor's peak, test if we should combine them
            # outLog.write( "Combine 2 " + str(x100[1]+offset1) + "\n")
            if (
                signalTest[x[1]]
            ) > PERCENT_PEAK * average2:  # Ok the previous peak is a peak,
                # outLog.write( " 3 " + str(x100[1]+offset1) + "\n")

                # outLog.write( "x100[1]: " + str(x100[1]+offset1)+ " ff10[-1][5]: " + str(ff10[-1][5]+offset1)+"\n")
                if (x100[1] - ff10[-1][5]) < COMBINE_PEAK_LIMIT:
                    # outLog.write( str(x100[1] - ff10[-1][5])+ "\n")
                    y = ff10.pop()

                    if signalTest[x[1]] > y[4]:
                        ff10.append(
                            (
                                y[0],
                                x100[1],
                                x100[2],
                                (signalTest[x[1]] - (y[4] - y[3])),
                                signalTest[x[1]],
                                x100[1],
                                offset1,
                            )
                        )
                    else:
                        ff10.append((y[0], y[1], x100[2], y[3], y[4], x100[1], offset1))
                    if len(threeTwists) > 0:
                        # outLog.write( "threeTwists1"+ "\n")
                        threeTwists.pop()
                    # outLog.write( "threeTwists2"+ "\n")
                    threeTwists.append((ff10[-1][0], ff10[-1][1], ff10[-1][2]))
                else:
                    if len(ff10) > 1:
                        ff10.pop(
                            0
                        )  # keep ff10 not deep since we only use the latest one
                        # outLog.write( "len(ff10): " + str(len(ff10))+ "\n")
                    # else:
                    # outLog.write( "len(ff10), did not pop: " + str(str(x100[1]+offset1))+ "\n")

                    ff10.append(
                        (
                            x100[0],
                            x100[1],
                            x100[2],
                            (signalTest[x[1]] - signalTest[x[0]]),
                            signalTest[x[1]],
                            x100[1],
                            offset1,
                        )
                    )

                    average2 = average2 * (n - 1) / n + ff10[-1][4] / n
                    # outLog.write( "average2: 2 " + str(average2)+ " offset1 " + str(ff10[-1][4]) + " n " + str(n)+ "\n")

                    calledFrom = " called from 1 "
                    threeTwists, lastTwist = twistState(
                        threeTwists,
                        x100,
                        lastTwist,
                        threeTwistsCopy,
                        calledFrom,
                        offset1,
                    )

        else:
            # outLog.write( " 8 " + str(x100[1]+offset1)+ "\n")
            assert x100[1] == x[1]
            # if ((x100[1] - ff10[-1][5]) < COMBINE_PEAK_LIMIT):
            # outLog.write( "Miss " + str(x100[1] - ff10[-1][5])+ "\n")
            # outLog.write( "Warning " + str((x100[0]-ff10[-1][2]))+ "\n")
            if (
                signalTest[x[1]]
            ) > PERCENT_PEAK * average2:  # Ok the previous peak is a peak,
                # outLog.write( " 9 " + str(x100[1]+offset1) + "\n")
                # outLog.write( "ff10[-1][0]_offset1_9: " + str(ff10[-1][0]+offset1) + " " + str(offset1)+ "\n")

                newEntry = (
                    x100[0],
                    x100[1],
                    x100[2],
                    (signalTest[x[1]] - signalTest[x[2]]),
                    signalTest[x[1]],
                    x100[1],
                    offset1,
                )
                if len(ff10) > 1:
                    ff10.pop(0)  # keep ff10 not deep since we only use the latest one
                    # outLog.write( "len(ff10): " + str(len(ff10))+ "\n")
                # else:
                # outLog.write( "len(ff10), did not pop: " + str(str(x100[1]+offset1))+ "\n")

                ff10.append(newEntry)
                average2 = average2 * (n - 1) / n + ff10[-1][4] / n
                # outLog.write( "average2: 3 " + str(average2)+ " offset1 " + str(ff10[-1][4]) + " n " + str(n)+ "\n")

                calledFrom = " called from 2 "
                threeTwists, lastTwist = twistState(
                    threeTwists, x100, lastTwist, threeTwistsCopy, calledFrom, offset1
                )  # , outLog)
            # else:
            # outLog.write( "Skip, signalTest[x[1]]: " + str(signalTest[x[1]]) + " " + str(PERCENT_PEAK*average2)+ "\n")

    return (ff10, average2, threeTwists, lastTwist)


def doWork(
    mySample,
    mySignal,
    singleRun,
    singleRunNeg,
    begin,
    peak,
    end,
    ff10,
    lastTwist,
    average2,
    threeTwists,
    threeTwistsCopy,
    nRestart,
    beginEnd,
    globalIndex,
):

    pass
    # BgPKEnd = []
    # dff = []

    # print(globalIndex)

    # notInitial = False
    if len(mySignal) < WINDOW_WIDTH - 1:
        # without warm up period
        different = WINDOW_WIDTH - 1 - len(mySignal)
        new_list = different * [mySample]
        mySignal.extend(new_list)
        # old with warmup period
        # mySignal.append(mySample)

        return (0, mySignal, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    if len(mySignal) == WINDOW_WIDTH - 1:
        mySignal.append(mySample)
        # print(len(mySignal))

        # reqSignal = [x[4] for x in mySignal]
        reqSignal = [x for x in mySignal]
        streamDataRaw = (
            reqSignal  # .ix[0:index] # we get 500 samples vs list only get 499
        )
        average = np.average(streamDataRaw)
        streamData = streamDataRaw - average

        BgPKEnd, singleRun, singleRunNeg, dff, begin, peak, end = intitialize(
            streamData, TAPS
        )

        # print(BgPKEnd, singleRun, singleRunNeg, dff, begin, peak, end)
        # sleep(2)

        ff10 = []

        lastTwist = -1000

        average2 = INITIAL_PEAK
        globalIndex = 0

        offset = TAPS / 2

        threeTwists = []
        threeTwistsCopy = []
        nRestart = -1
        beginEnd = []
        globalIndex = 0

        return (
            0,
            mySignal,
            0,
            0,
            singleRun,
            singleRunNeg,
            begin,
            peak,
            end,
            ff10,
            lastTwist,
            average2,
            threeTwists,
            threeTwistsCopy,
            nRestart,
            beginEnd,
        )
    else:
        mySignal.pop(0)
        mySignal.append(mySample)
        BgPKEnd = []
        globalIndex = globalIndex - WINDOW_WIDTH + 1
        offset = TAPS / 2

        #### very important, we assume there is NO gesture in the first 500 warm up
        # if (len(singleRun) > 0):
        #    singleRun = [x-1 for x in singleRun]
        # outLog.write("Positive"+ str(singleRun) + "\n")
        # if (len(singleRunNeg) > 0):
        #    singleRunNeg = [x-1 for x in singleRunNeg]
        # outLog.write("Negative"+ str(singleRunNeg) + "\n")

        # reqSignal = [x[4] for x in mySignal]
        reqSignal = [x for x in mySignal]
        streamDataRaw = reqSignal

        average = np.average(streamDataRaw)
        streamData = streamDataRaw - average

        filtered_signal = filterSig(streamData)

        # dff.append(filtered_signal[-1] - filtered_signal[-2])

        dff100 = filtered_signal[-1] - filtered_signal[-2]

        ### update the relative index

        # update the index by one
        if len(singleRun) > 0:
            singleRun = [x - 1 for x in singleRun]

        if len(singleRunNeg) > 0:
            singleRunNeg = [x - 1 for x in singleRunNeg]

        if begin > 0:
            begin = begin - 1

        if peak > 0:
            peak = peak - 1

        if end > 0:
            end = end - 1  # end

        temp = []
        for y in threeTwistsCopy:
            yy = (y[0] - 1, y[1] - 1, y[2] - 1)
            temp.append(yy)
        threeTwistsCopy = copy.copy(temp)

        # temp = []
        # for y in BgPKEnd:
        #    yy = (y[0]-1,y[1]-1,y[2]-1)
        #    temp.append(yy)
        # BgPKEnd = copy.copy(temp)

        temp = []
        for y in threeTwists:
            yy = (y[0] - 1, y[1] - 1, y[2] - 1)
            temp.append(yy)
        threeTwists = copy.copy(temp)

        lastTwist = lastTwist - 1

        temp = []

        for y in ff10:
            yy = (y[0] - 1, y[1] - 1, y[2] - 1, y[3], y[4], y[5] - 1, y[6] + 1)
            temp.append(yy)
        ff10 = copy.copy(temp)

        ### end of update the relative index
        # dff_index = [(i,dff[i]) for i in range(len(dff))]

        # if dff_index[-1][1] > 0.0:
        if dff100 > 0.0:

            # singleRun.append(dff_index[-1][0])
            singleRun.append(WINDOW_WIDTH - 1)

            if len(singleRunNeg) > 0:

                if begin >= 0:
                    end = singleRunNeg[-1]
                    # outLog.write( "B "+str(begin+globalIndex)+" P "+str(peak+globalIndex)+" E "+str(end+globalIndex)+ "\n")
                    BgPKEnd.append((begin, peak, end))
                    #         newBump, filtered_samples, peakList, lastIndex, aveBtwPeakFoot, taps, threeTwists, threeTwistsCopy, lastTwist, outLog

                    ff10, average2, threeTwists, lastTwist = findPeak(
                        BgPKEnd[-1],
                        filtered_signal,
                        ff10,
                        globalIndex,
                        average2,
                        TAPS,
                        threeTwists,
                        threeTwistsCopy,
                        lastTwist,
                    )
                    if len(threeTwists) == 3:
                        # outLog.write( "nn2: " + str(globalIndex)+ "\n")
                        threeTwistsCopy = copy.copy(threeTwists)
                        if (
                            threeTwistsCopy[2][1] - threeTwistsCopy[1][1]
                        ) >= GESTURE_MAX_LIMIT:  # this is the case when an user did two twists, then nothing, then start 2 twists, a gesture and end twist
                            # outLog.write( "Error: too wide1 "+"offset100: " +str(offset100) + " "+str(threeTwistsCopy[0][1]+globalIndex)+" "+str(threeTwistsCopy[1][1]+globalIndex) + " " + str(threeTwistsCopy[2][1]+globalIndex) + "\n")
                            threeTwists = []
                            temp = threeTwistsCopy[2]
                            threeTwists.append(temp)
                            # outLog.write( "Check: " + str(threeTwists[0][1]+globalIndex) + "\n")
                            threeTwistsCopy = []
                            nRestart = -1
                        else:
                            lastTwist = threeTwistsCopy[2][1]
                            threeTwists = []
                            nRestart = 0
                    else:
                        if len(threeTwistsCopy) > 0:
                            assert len(threeTwists) <= 1
                            assert len(threeTwistsCopy) == 3

                            if len(threeTwists) == 1:
                                # test if combined had done before
                                if (
                                    threeTwists[0][0] == threeTwistsCopy[2][0]
                                ):  # combined in the last bump
                                    threeTwistsCopy.pop()
                                    threeTwistsCopy.append(threeTwists[0])
                                    # outLog.write( "combine in the copy: " + str(threeTwistsCopy[2][0]+globalIndex) + " "+ str(threeTwistsCopy[2][1]+globalIndex)+" "+ str(threeTwistsCopy[2][2]+globalIndex) +"\n")
                                    threeTwists = []
                                    nRestart = 0
                                else:
                                    if (
                                        threeTwistsCopy[2][1] - threeTwistsCopy[1][1]
                                    ) > GESTURE_LIMIT:  # only throw away when there is a double twists at the end of a gesture
                                        # outLog.write( "Throw away: " + str(threeTwistsCopy[2][1]+globalIndex) + " "+ str(threeTwistsCopy[1][1]+globalIndex)+" "+ str(threeTwistsCopy[2][1]-threeTwistsCopy[1][1]) +"\n")
                                        temp1 = threeTwists[0]
                                        temp0 = threeTwistsCopy[2]
                                        threeTwistsCopy = []
                                        threeTwists = []
                                        threeTwists.append(temp0)
                                        threeTwists.append(temp1)
                                        nRestart = -1
                                    else:
                                        # outLog.write( "Send beginEnd1: " + str(threeTwistsCopy[0][1]+globalIndex)+ " "+ str(threeTwistsCopy[1][1]+globalIndex)+" "+str(threeTwistsCopy[2][1]+globalIndex) + "\n")
                                        # outLog.write( "Send beginEnd1: " + str(threeTwistsCopy[0][1])+ " "+ str(threeTwistsCopy[1][1])+" "+str(threeTwistsCopy[2][1]) + "\n")
                                        beginEnd.append(
                                            (
                                                threeTwistsCopy[0][1]
                                                + globalIndex
                                                - offset,
                                                threeTwistsCopy[1][1]
                                                + globalIndex
                                                - offset,
                                                threeTwistsCopy[2][1]
                                                + globalIndex
                                                - offset,
                                            )
                                        )
                                        # outLog.write( "Throw away end double twist: " + str(threeTwistsCopy[2][1]+globalIndex) + " "+ str(threeTwists[0][1]+globalIndex)+ " "+ str(threeTwists[0][1]-threeTwistsCopy[2][1]) + " " + str(nRestart) + "\n")

                                        y0 = threeTwistsCopy[1][1] - offset
                                        y1 = threeTwistsCopy[2][1] - offset

                                        threeTwistsCopy = []
                                        threeTwists = []
                                        nRestart = -1

                                        # TODO: ncheck it. come back
                                        return (
                                            1,
                                            mySignal,
                                            y0,
                                            y1,
                                            singleRun,
                                            singleRunNeg,
                                            begin,
                                            peak,
                                            end,
                                            ff10,
                                            lastTwist,
                                            average2,
                                            threeTwists,
                                            threeTwistsCopy,
                                            nRestart,
                                            beginEnd,
                                        )

                    # outLog.write( "average2 " + str(average2)+ "\n")
                    begin = peak = -1
                singleRunNeg = []

        else:
            if len(singleRun) > 0:
                begin = singleRun[0]
                peak = singleRun[-1]
                # outLog.write( "B "+str(begin+globalIndex)+" P "+str(peak+globalIndex) + "\n")
                singleRun = []
            # singleRunNeg.append(dff_index[-1][0])
            singleRunNeg.append(WINDOW_WIDTH - 1)

        # print singleRun
        # print singleRunNeg

        if nRestart >= 0:
            nRestart = nRestart + 1
            # outLog.write( "nRestart "+str(nRestart) + "\n")

            if nRestart > DELAY_SEND:
                assert len(threeTwistsCopy) == 3
                # outLog.write( "Send beginEnd2: " + str(threeTwistsCopy[0][1]+globalIndex)+ " "+ str(threeTwistsCopy[1][1]+globalIndex)+" "+str(threeTwistsCopy[2][1]+globalIndex) + "\n")
                # outLog.write( "Send beginEnd2: " + str(threeTwistsCopy[0][1])+ " "+ str(threeTwistsCopy[1][1])+" "+str(threeTwistsCopy[2][1]) + "\n")

                beginEnd.append(
                    (
                        threeTwistsCopy[0][1] + globalIndex - offset,
                        threeTwistsCopy[1][1] + globalIndex - offset,
                        threeTwistsCopy[2][1] + globalIndex - offset,
                    )
                )
                y0 = threeTwistsCopy[1][1] - offset
                y1 = threeTwistsCopy[2][1] - offset

                threeTwistsCopy = []
                nRestart = -1
                return (
                    1,
                    mySignal,
                    y0,
                    y1,
                    singleRun,
                    singleRunNeg,
                    begin,
                    peak,
                    end,
                    ff10,
                    lastTwist,
                    average2,
                    threeTwists,
                    threeTwistsCopy,
                    nRestart,
                    beginEnd,
                )

        ##### end

        return (
            0,
            mySignal,
            0,
            0,
            singleRun,
            singleRunNeg,
            begin,
            peak,
            end,
            ff10,
            lastTwist,
            average2,
            threeTwists,
            threeTwistsCopy,
            nRestart,
            beginEnd,
        )


def ActivitySpotting_TopInterface(
    data, pFrameData, numByteReqToStoreAccReading
):  # Segnemtation algorithm goes here
    # Call Yuans segmentation algorithm here
    pFrameData.extend(data)
    # print("In gesture spotting")
    nRetSpotting = (
        1  # always 1 for continuous data. Detection based onslidig window only
    )
    nFrameLenInBytes = len(pFrameData) * numByteReqToStoreAccReading
    return (nRetSpotting, nFrameLenInBytes, pFrameData)


def reshapeToDFgivenInterleavedValues(pFrameData, streams):
    mydf = DataFrame(np.reshape(pFrameData, (-1, len(streams))), columns=streams)
    return mydf


def Bound(x):
    x_max = np.max(x)
    x_min = np.min(x)
    a = 2 / float(x_max - x_min)
    b = -(x_max + x_min) / float(x_max - x_min)
    y = np.multiply(a, x) + b
    return y


# def call_recognition_module_to_find_start_end(time_series, streams_to_use, axis_of_interest_for_segmentation):
def call_recognition_module_to_find_start_end(time_series):
    """
    {"pre": [
    {"name": "time_series", "type": "DataFrame"}
    ],

    "post": [
    {"name": "output_data", "type": "DataFrame"}],

    "description" : "Takes a Double Twist Gesture stream and segments the data into small time slices."
    }
    """
    # time_series = time_series[streams_to_use]
    # time_series = time_series[axis_of_interest_for_segmentation]

    mysensorData = time_series

    # col_to_use_for_segmentation = list(time_series.columns).index(axis_of_interest_for_segmentation)
    nFrameIdx = 0  # How many frames read up until now
    idx = 0  # To keep track of the index currently reading
    pltBegEndTuples_for_plotting = []
    ff10 = []

    lastTwist = -1000

    average2 = INITIAL_PEAK

    TAPS / 2

    threeTwists = []
    threeTwistsCopy = []
    nRestart = -1
    beginEnd = []
    BgPKEnd, singleRun, singleRunNeg, dff, begin, peak, end = [], 0, 0, [], 0, 0, 0
    globalIndex = -1

    mySignal = []
    for mySample in mysensorData:
        # mySample =list(mySample)
        globalIndex = -1
        idx = idx + 1
        (
            nRetSpotting,
            pFrameData,
            peak_start,
            peak_end,
            singleRun,
            singleRunNeg,
            begin,
            peak,
            end,
            ff10,
            lastTwist,
            average2,
            threeTwists,
            threeTwistsCopy,
            nRestart,
            beginEnd,
        ) = doWork(
            mySample,
            mySignal,
            singleRun,
            singleRunNeg,
            begin,
            peak,
            end,
            ff10,
            lastTwist,
            average2,
            threeTwists,
            threeTwistsCopy,
            nRestart,
            beginEnd,
            globalIndex,
        )
        mySignal = pFrameData
        if (
            nRetSpotting == 1
        ):  # if gesture spotting algo return 1 and exceeds max buffer length
            numSamplesInBuff = len(mySignal)
            nFrameIdx = nFrameIdx + 1
            pltBegEndTuples_for_plotting.append(
                (idx - numSamplesInBuff + peak_start, idx - numSamplesInBuff + peak_end)
            )
        else:
            continue

    df = DataFrame(pltBegEndTuples_for_plotting, columns=["start", "end"])
    return df
