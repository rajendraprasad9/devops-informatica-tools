##
# Process deploy list for database artifacts
# @Since: 23-MAR-2019
# @Author: Jac. Beekers
# @Version: 20190323.0 - JBE - Initial

import supporting.errorcodes as err
import supporting, logging, os
import supporting.environmentvars as env
import supporting.filehandling as filehandling
import re

def processList(deployList):
    thisproc = "processList"
    latestError = err.OK
    global entrynr
    entrynr = 0
    global level
    level = 0
    supporting.log(logging.DEBUG, thisproc, "Started to work on deploy list >" + deployList + "<.")

    try:
        with open(deployList) as theList:
            for line in theList:
                entrynr += 1
                level = 0
                result = processEntry(line.rstrip('\n'))
                if (result.rc != err.OK.rc):
                    latestError = result
    except IOError:
        supporting.log(logging.ERROR, thisproc, "File not found")
        latestError = err.FILE_NF

    supporting.log(logging.DEBUG, thisproc,
                   "Completed with rc >" + str(latestError.rc) + "< and code >" + latestError.code + "<.")
    return latestError


def processEntry(deployEntry):
    thisproc = "processEntry"
    result = err.OK
    supporting.log(logging.DEBUG, thisproc, "Started to work on deploy entry >" + deployEntry + "<.")

    schema, sqlfile = deployEntry.split(':', 2)
    supporting.log(logging.DEBUG, thisproc, 'Schema is >' + schema + '< and sqlfile is >' + sqlfile + '<')

    result = generate_orderedsql(schema, sqlfile)

    supporting.log(logging.DEBUG, thisproc,
                   "Completed with rc >" + str(result.rc) + "< and code >" + result.code + "<.")
    return result


def generate_orderedsql(schema, input_sqlfile):
    thisproc = "generate_orderedsql"
    result = err.OK
    sourcesqldir = os.environ.get(env.varSourceSqlDir)
    if not sourcesqldir:
        supporting.log(logging.ERROR, thisproc, "SourceSqlDir is not set")
        return err.SOURCESQLDIR_NOTSET

    targetsqldir = os.environ.get(env.varTargetSqlDir)
    if not targetsqldir:
        supporting.log(logging.ERROR, thisproc, "TargetSqlDir is not set")
        return err.TARGETSQLDIR_NOTSET

    the_source_sqldir  = sourcesqldir + "/" + schema + "/"
    the_source_sqlfile = input_sqlfile
    orderedsqlfilename = targetsqldir + "/" + "%02d" % entrynr + "_ordered.sql"

    filehandling.removefile(orderedsqlfilename)
    processlines(the_source_sqldir, the_source_sqlfile, orderedsqlfilename)

    return result

def ignoreline(line):
    if(re.match("^--", line) or re.match("^\n$",line)):
        return True
    return False


def calltosubsql(line):
    thisproc="calltosubsql"
    if(re.match("^@@", line)):
        return True
    return False

def processlines(the_source_sqldir, the_source_sqlfile, orderedsqlfilename):
    result = err.OK
    global level
    level +=1
    thisproc="processlines-" + "%03d" % level
    supporting.log(logging.DEBUG, thisproc, "level is >" + "%03d" % level +"<.")

    try:
        with open(the_source_sqldir + the_source_sqlfile) as thesql:
            for line in thesql:
                if (ignoreline(line)):
                    continue
                if (calltosubsql(line)):
                    supporting.log(logging.DEBUG, thisproc, "Found '@@', a call to another script.")
                    write2file(orderedsqlfilename, "-- Start expansion -- " + line)
                    subsql = line[2:-1].split(' ', 1)[0]
                    completepathsql = the_source_sqldir + subsql
                    supporting.log(logging.DEBUG, thisproc, "Sub file name determined as >" + subsql +"<. Complete file path >"
                                   + completepathsql +"<.")
                    #thesubsqlfile = the_source_sqldir + subsql
                    processlines(the_source_sqldir, subsql, orderedsqlfilename)
                    write2file(orderedsqlfilename, "-- End expansion -- " + line)
                else:
                    write2file(orderedsqlfilename, line)

    except IOError:
        supporting.log(logging.ERROR, thisproc, "Could not find file >" + the_source_sqlfile + "<.")
        write2file(orderedsqlfilename,"ERROR: Could not find file >" + the_source_sqlfile +"<.")
        result = err.FILE_NF

    return result

def write2file(filename, line):
    thisproc="write_sql"
    result = err.OK

    try:
        with open(filename, 'a') as the_result_file:
            if "\n" == line[-1]:
                the_result_file.write(line)
            else:
                the_result_file.write(line +"\n")
    except IOError:
        supporting.log(logging.ERROR, thisproc, "Could not write to file >" + filename + "<.")
        result = err.FILE_NW

    return result