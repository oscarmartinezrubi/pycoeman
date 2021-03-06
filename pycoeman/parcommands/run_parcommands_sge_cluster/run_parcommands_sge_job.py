#!/usr/bin/python
import sys, os, shutil
from lxml import etree
from pycoeman import utils_execution

# Parse the parameters
configFile = sys.argv[1]
commandId = sys.argv[2]
dataDirAbsPath = sys.argv[3]
remoteExeDir = sys.argv[4]
localOutDirAbsPath = sys.argv[5]

# Read the command information from the XML and the provided commandId
if not os.path.isfile(configFile):
    raise Exception(configFile + " could not be found!")
e = etree.parse(open(configFile)).getroot()
componentInfo = e.xpath("//id[text() = '" + commandId + "']/parent::*")[0]

(commandId, command, requiredElements, outputElements) = utils_execution.parseComponent(componentInfo, dataDirAbsPath)
print("CommandId: " + commandId)
print("Command: " + command)

# Create a local working directory using the specified remoteExeDir
lwd = remoteExeDir + '/' + commandId
shutil.rmtree(lwd, True)
os.makedirs(lwd)
# Change directory to be in the local working dir
os.chdir(lwd)

# Create a output directory in the shared folder to copy back the results
commandLocalOutDirAbsPath = localOutDirAbsPath + '/' + commandId
shutil.rmtree(commandLocalOutDirAbsPath, True)
os.makedirs(commandLocalOutDirAbsPath)

# Copy required files and folders in the data directory
for requiredElement in requiredElements:
    if os.path.isfile(requiredElement):
        os.system('cp ' + requiredElement + ' .')
    elif os.path.isdir(requiredElement):
        os.system('cp -r ' + requiredElement + ' .')
    else:
        raise Exception(requiredElement + " could not be found!")

# Run the execution of the command (which includes cpu, mem and disk monitoring)
(logFile, monitorFile, monitorDiskFile) = utils_execution.executeCommandMonitor(commandId, command, lwd, False)

# Copy the monitor files back to the output dir in the shared folder
for f in (logFile, monitorFile, monitorDiskFile):
    if os.path.isfile(f):
        os.system('cp ' + f + ' ' + commandLocalOutDirAbsPath)
    else:
        raise Exception(f + " could not be found!")
# Copy other output files and folders back to the output dir in the shared folder
for outputElement in outputElements:
    if outputElement.count('/'):
        # The element is somehow defined in a output folder, so we need to create the folder locally
        os.makedirs(commandLocalOutDirAbsPath + '/' + '/'.join(outputElement.split('/')[:-1]))
    if os.path.isfile(outputElement):
        os.system('cp ' + outputElement + ' ' + commandLocalOutDirAbsPath + '/' +  outputElement)
    elif os.path.isdir(outputElement):
        os.system('cp -r ' + outputElement + ' ' + commandLocalOutDirAbsPath + '/' +  outputElement)
    else:
        raise Exception(outputElement + " could not be found!")

# Clean the local working dir
os.system('rm -r ' + lwd)
