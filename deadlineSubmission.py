import nuke
import nukescripts
import os
import shutil
import tempfile
from subprocess import check_output

# Defining current Nuke version for Python compatibility
nukeVersion = float(str(nuke.NUKE_VERSION_MAJOR) + '.' + str(nuke.NUKE_VERSION_MINOR))

# Submitting function
def submitJob(jobName, priority, frameList, selectedNode):
    scriptPath = nuke.root().name()

    if nukeVersion < 13:
        temporaryDirectory = tempfile.mkdtemp()
    else:
        # Create jobInfo and pluginInfo file
        temporaryDirectory = tempfile.TemporaryDirectory()


    # Get environment value of deadline path
    deadlinePath = os.getenv('DEADLINE_PATH')

    try:
        # Setting job properties
        if nukeVersion < 13:
            jobInfoPath = os.path.join(temporaryDirectory, "job_info.txt")
        else:
            jobInfoPath = os.path.join(temporaryDirectory.name, "job_info.txt")

        jobInfo = open(jobInfoPath, "w+")
        jobInfo.write('Plugin=Nuke\n' + 'Frames=' + frameList + '\n' + 'Priority=' +str(priority) + '\n' + 'Name=' + jobName + '\n' + 'Department=Compositing' )
        jobInfo.seek(0)
        jobInfo.close()

        # Setting plugin properties
        if nukeVersion < 13:
            pluginInfoPath = os.path.join(temporaryDirectory, "plugin_info.txt")
        else:
            pluginInfoPath = os.path.join(temporaryDirectory.name, "plugin_info.txt")
        pluginInfo = open(pluginInfoPath, "w+")
        pluginInfo.write('Version=' + str(nukeVersion) + '\n' + 'WriteNode='+ selectedNode + '\n' + 'SceneFile='+ scriptPath )
        pluginInfo.seek(0)
        pluginInfo.close()

        # Creating deadline command for submission
        deadlineCommand = "\"" + os.path.join(deadlinePath, 'deadlinecommand') + "\" " + jobInfoPath + " " + pluginInfoPath

        # Submission to deadline
        deadlineExecute = check_output(deadlineCommand, shell=True).decode()
        nuke.message(deadlineExecute)


    except Exception as exception:
      nuke.message("An error occured.\n" + str(exception))

    # Making sure temp directory is removed
    finally:
        if nukeVersion < 13:
            shutil.rmtree(temporaryDirectory)

def main(specifiedNode = False):
    class deadlineSubmissionPanel(nukescripts.PythonPanel):
        def __init__(self):
            # Header
            nukescripts.PythonPanel.__init__(self, 'Submit to farm')

            # Defining nobs
            self.submissionName = nuke.String_Knob('submissionName', 'Submission name')
            self.priority = nuke.Int_Knob('priority','Priority')
            self.frameListSelect = nuke.Enumeration_Knob('frameListSelect', 'Frame range', ['global', 'input', 'in-out'])
            self.frameList = nuke.String_Knob('frameList', '', '%s-%s' % (nuke.root().firstFrame(), nuke.root().lastFrame()))
            self.frameList.clearFlag(nuke.STARTLINE)

            # Adding knobs
            for knobs in (self.submissionName, self.priority, self.frameListSelect, self.frameList):
                self.addKnob(knobs)

            # Setting knob values
            self.priority.setValue(70)
            projectName = os.path.basename(nuke.root().knob('name').value())
            self.submissionName.setValue(projectName)

        # Actions when knobs change
        def knobChanged( self, knob ):
            selectedNode = nuke.selectedNode()
            if knob is self.frameListSelect:
                if self.frameListSelect.value() == 'global':
                    self.frameList.setValue('%s-%s' % (nuke.root().firstFrame(), nuke.root().lastFrame()))
                elif self.frameListSelect.value() == 'input':
                    self.frameList.setValue('%s-%s' % (selectedNode.firstFrame(), selectedNode.lastFrame()))
                else:
                    self.frameList.setValue(nuke.activeViewer().node().knob('frame_range').getValue())

    # Detect if script is saved
    if not nuke.Root().name() == 'Root':

        # Detect if script has unsaved changes
        if nuke.Root().modified():
            if nuke.ask("The script has unsaved changes, would you like to save them?"):
                nuke.scriptSave()
            else:
                return

        try:
            # Setting selectedNode
            if not specifiedNode:
                selectedNode = nuke.selectedNode()
            else:
                selectedNode = nuke.toNode(specifiedNode)

            # Making sure selected node is a write node
            if selectedNode.Class() in ["Write", "WriteTank"]:
                deadlineSubmission = deadlineSubmissionPanel()

                if deadlineSubmission.showModalDialog():
                    # Setting values specified by user
                    jobName = deadlineSubmission.submissionName.value()
                    priority = deadlineSubmission.priority.value()
                    frameList = deadlineSubmission.frameList.value()
                    writeNode = selectedNode.name()

                    try:
                        # Submit to deadline using submission script
                        submitJob(jobName, priority, frameList, writeNode)

                    except Exception as exception:
                        # If error occurs print error in message
                        nuke.message("An error occured.\n" + str(exception))

            else:
                nuke.message("A write node must be selected.")

        except:
            nuke.message("No node selected.")
