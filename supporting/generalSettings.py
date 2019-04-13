##
# generalSettings
# @Since: 22-MAR-2019
# @Author: Jac. Beekers
# @Version: 20190410.0 - JBE - Initial

import os, logging
import supporting
import supporting.generalConstants as constants

logger = logging.getLogger(__name__)

"""defaults"""
logDir=constants.DEFAULT_LOGDIR
resultDir=constants.DEFAULT_RESULTDIR
artifactDir=constants.DEFAULT_ARTIFACTDIR

def getenvvars():
    thisproc="getenvvars"
    global logDir, resultDir, artifactDir

    supporting.log(logger, logging.DEBUG, thisproc, 'started')

    logDir= os.environ.get(constants.varLogDir, constants.DEFAULT_LOGDIR)
    supporting.log(logger, logging.DEBUG, thisproc, 'logDir set to >' + logDir +"<.")

    resultDir= os.environ.get(constants.varResultDir, constants.DEFAULT_RESULTDIR)
    supporting.log(logger, logging.DEBUG, thisproc, 'resultDir set to >' + resultDir +"<.")

    artifactDir= os.environ.get(constants.varArtifactDir, constants.DEFAULT_ARTIFACTDIR)
    supporting.log(logger, logging.DEBUG, thisproc, 'artifactDir set to >' + artifactDir +"<.")

    supporting.log(logger, logging.DEBUG, thisproc, 'completed')



getenvvars()
