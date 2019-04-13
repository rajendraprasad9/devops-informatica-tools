"""IDQ Importer Exporter

This script defines Import and Export functions through which it can communicate with
a Informatica Model Repository.

It also provides some related functions, such as:
	- Create IDQ folder
	- Check in IDQ components

    Parts by Laurens Verhoeven
    Parts by Jac. Beekers
    @Version: 20190412.0  - JBE - Initial version to work with deploy lists
    @License: MIT
"""

import subprocess, datetime
import supporting, logging
import informaticaArtifact.infaConstants as infaConstants
import os
import informaticaArtifact.infaSettings as infaSettings
import supporting.errorcodes as errorcodes

logger = logging.getLogger(__name__)


def ExecuteCommand(commands):
    thisproc = "ExecuteCommand"
    process = ""
    result = errorcodes.OK

    supporting.log(logger, logging.DEBUG, thisproc, "Executing commands >" + commands + "<.")

    output, error = ("", 0)
    my_env = {**os.environ, 'INFA_DEFAULT_DOMAIN_PASSWORD': infaSettings.sourcePassword,
              'INFA_DEFAULT_DOMAIN_USER': infaSettings.sourceUsername,
              'INFA_DEFAULT_SECURITY_DOMAIN': infaSettings.sourceSecurityDomain}
    pipes = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=my_env)
    std_out, std_err = pipes.communicate()

    if pipes.returncode == 0:
        supporting.log(logger, logging.INFO, thisproc, std_out.decode('utf-8'))
    else:
        result = errorcodes.INFACMD_FAILED
        supporting.log(logger, logging.ERROR, thisproc, std_out.decode('utf-8'))

    return result


def ExecuteInfacmd(commands):
    result = ExecuteCommand(commands)

    return result


def BuildCommand(**KeyWordArguments):
    """Build an IDQ command, return it as string"""

    # Process the input aruguments to compose the IDQ command
    # This is doen by first creating a list of strings, that are then joined to form the actual
    # command
    # The syntax used is as follows:
    # $InfaPath + $InfaProgram + $InfaCommand + $InfaArguments

    # Create the list that will hold the parts of the command, in order
    InfaArguments = []

    # Process each input argument.
    # The InfaPath and Tool arguments are processed separetly, because those have to go first
    # For the other arguments, the order does not matter, so they can be processed togetehr
    for key, value in KeyWordArguments.items():
        # If the argument is "InfaPath" , assign the value to the variable InfaPath
        if key == "InfaPath":
            InfaPath = KeyWordArguments["InfaPath"]
        # If the argument is "Tool" , assign the value to the variable Tool, and lookup the Program and
        # Command in AvailableTools, assign those to InfaProgram, InfaCommand
        elif key == "Tool":
            Tool = KeyWordArguments["Tool"]
            (InfaProgram, InfaCommand) = infaConstants.AvailableTools[value]
        # If the argument is anything else, look it up in AvailableArguments and add the found
        # value to InfaArguments
        elif key in infaConstants.AvailableArguments:
            InfaArguments.append(infaConstants.AvailableArguments[key] + " " + '"' + value + '"')

    # Put all parts of the command in the same list, in correct order, and join them into one
    # string
    IDQCommandParts = [InfaPath, InfaProgram, InfaCommand] + InfaArguments
    IDQCommand = " ".join(IDQCommandParts)

    return (IDQCommand)


def Import(**KeyWordArguments):
    """Import IDQ Components"""

    KeyWordArguments["Tool"] = "Import"
    ImportCommand = BuildCommand(**KeyWordArguments)

    output, error = ExecuteInfacmd(ImportCommand)

    return (output, error)


def export_developer_project(**KeyWordArguments):
    thisproc = "Export"

    KeyWordArguments["Tool"] = "Export"
    ExportCommand = BuildCommand(**KeyWordArguments)
    supporting.log(logger, logging.INFO, thisproc, "ExportCommand is >" + ExportCommand + "<.")
    result = ExecuteInfacmd(ExportCommand)

    return (result)


def CreateFolder(**KeyWordArguments):
    """Create IDQ Folder"""

    KeyWordArguments["Tool"] = "CreateFolder"

    CreateFolder = BuildCommand(**KeyWordArguments)

    output, error = ExecuteInfacmd(CreateFolder)

    return (output, error)


def ListCheckedOutObjects(**KeyWordArguments):
    thisproc = "ListCheckedOutObjects"
    """ List Components that are currently checked out """

    KeyWordArguments["Tool"] = "ListCheckOutObjects"
    ListCheckedOutCommand = BuildCommand(**KeyWordArguments)
    output, error = ExecuteInfacmd(ListCheckedOutCommand)

    # The output is in the form of one object per line, with properties spearated by a comma + space.
    # To filter out irrelevant lines, such as "Command succesful", we keep only line that start with "MRS_PATH="
    OutputLines = output.splitlines()
    OutputKeyValuePairLines = [Properties.split(", ") for Properties in OutputLines if
                               Properties.startswith("MRS_PATH=")]

    # ObjectsOLD = [[KVPair.split("=", 1) for KVPair in Line] for Line in OutputKeyValuePairLines]

    # Each object is a dictionary, with properties as keys
    # Since the date field has a comma in it, its not parsed properly. For this reason we need the len == 2 filter
    # If the date is required, the parsing of the output should be adjusted
    Objects = [dict(KVPair.split("=") for KVPair in Line if len(KVPair.split("=")) == 2) for Line in
               OutputKeyValuePairLines]

    supporting.log(logging.DEBUG, thisproc, output)

    return (Objects)


def CheckIn(**KeyWordArguments):
    """Check-in IDQ Components"""

    KeyWordArguments["Tool"] = "CheckIn"
    CheckInCommand = BuildCommand(**KeyWordArguments)
    output, error = ExecuteInfacmd(CheckInCommand)

    return (output, error)


def CheckInMutiple(**KeyWordArguments):
    thisproc = "CheckInMultiple"
    """ Check in Multiple IDQ components """
    for key, value in KeyWordArguments.items():
        if key == "MultipleObjectPaths":
            ObjectPaths = KeyWordArguments["MultipleObjectPaths"]

    KeyWordArguments["Tool"] = "CheckIn"

    CheckInCommands = []
    for ObjectPathName in ObjectPaths:
        KeyWordArguments["ObjectPathName"] = ObjectPathName
        CheckInCommands.append(BuildCommand(**KeyWordArguments))

    CheckInAllCommand = "\n".join(CheckInCommands)

    timebefore = datetime.datetime.now()
    output, error = ExecuteInfacmd(CheckInAllCommand)
    timeafter = datetime.datetime.now()
    duration = timeafter - timebefore

    supporting.log(logging.DEBUG, thisproc,
                   "Infacmd took " + str(duration) + " seconds to check-in " + str(len(ObjectPaths)) + " objects")

    # output, error = (CheckInAllCommand, 0)

    return (output, error)