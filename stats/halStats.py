#!/usr/bin/env python

#Copyright (C) 2012 by Glenn Hickey
#
#Released under the MIT license, see LICENSE.txt
#!/usr/bin/env python

"""Little python halStats wrapper.  
"""
import argparse
import os
import sys
import copy
import subprocess
from multiprocessing import Pool



def runShellCommand(command):
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                   stderr=sys.stderr, bufsize=-1)
        output, nothing = process.communicate()
        sts = process.wait()
        if sts != 0:
            raise RuntimeError("Command: %s exited with non-zero status %i" %
                               (command, sts))
        return output
    except KeyboardInterrupt:
        raise RuntimeError("Aborting %s" % cmd)

def runParallelShellCommands(cmdList, numProc):
    if numProc == 1 or len(cmdList) == 1:
        map(runShellCommand, cmdList)
    else:
        mpPool = Pool(processes=min(numProc, len(cmdList)))
        result = mpPool.map_async(runShellCommand, cmdList)
        # specifying a timeout allows keyboard interrupts to work?!
        # http://stackoverflow.com/questions/1408356/keyboard-interrupts-with-pythons-multiprocessing-pool
        try:
            result.get(sys.maxint)
        except KeyboardInterrupt:
            mpPool.terminate()
            raise RuntimeError("Keyboard interrupt")
        if not result.successful():
            raise "One or more of commands %s failed" % str(cmdList)

def getHalGenomes(halPath):
    return runShellCommand("halStats %s --genomes" % halPath).split(",")

def getHalNumSegments(halPath, genomeName):
    res = runShellCommand("halStats %s --numSegments %s" %
                          (halPath, genomeName)).split()
    return tuple([int(x) for x in res])

def getHalStats(halPath):
    res = runShellCommand("halStats %s" % (halPath)).split("\n")
    outList = []
    foundHeader = False
    for line in res:
        tokens = line.strip().split(",")
        if len(tokens) == 6 and tokens[0] == "GenomeName":
            foundHeader = True
        elif len(tokens) == 6 and foundHeader:
            outList.append(tuple(tokens))
    return outList

def getHalSequenceStats(halPath, genomeName):
    res = runShellCommand("halStats %s --sequenceStats %s" %
                          (halPath, genomeName)).split("\n")
    outList = []
    for line in res[1:]:
        tokens = line.strip().split(",")
        if len(tokens) == 4:
            outList.append(tuple(tokens))
    return outList
