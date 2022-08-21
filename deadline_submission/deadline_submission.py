"""
Nuke Deadline Submitter by Gilles Vink (2022)

Used to create a small popup, with the possibility to submit
Write nodes via the node itself or by selecting the node.

"""

import nuke
import os
import panel
from sanity_check import SanityCheck
import tempfile
from shutil import rmtree
from subprocess import check_output


class DeadlineSubmission:
    """
    This class contains the logic to submit nodes to Deadline.
    submit_selected_node() will allow the user to submit
    the currently selected node. This function won't require any input.

    submit() will require a node to submit. E.g. submit(nuke.thisNode())
    """

    def __init__(self):
        # Getting the current Nuke version to match the version
        # in Deadline
        self.nuke_version = "%i.%i" % (
            nuke.NUKE_VERSION_MAJOR,
            nuke.NUKE_VERSION_MINOR,
        )

        # This list contains all the classes of nodes that are supported
        # If the node class is in the list, it will proceed submission
        self.supported_nodes = ["Write"]

        # We need the deadline command path so we will get the environment
        self.deadline_command = os.getenv("DEADLINE_PATH")

    def submit_selected_node(self):
        """Submit the currently selected node to Deadline. No input needed.
        Function is basically a wrapper for the submit() function."""
        # If there are any errors, throw them into an exception
        # so the user knows
        try:
            # Get the current selected node
            node = nuke.selectedNode()

            # Validate if node is a supported one
            if node.Class() in self.supported_nodes:
                # If valid, submit selected node
                self.submit(node)

            # If not, we will let the user know
            else:
                nuke.critical(
                    "This node is unfortunately not supported."
                    "\n"
                    "Currently these nodes are supported:"
                    "\n\n"
                    "%s" % self.supported_nodes
                )
        # If anything happens during the execution of this script,
        # for example no node has been selected, let the user know
        except Exception as error:
            nuke.critical("Something went wrong: %s" % str(error))

    def submit(self, node):
        """Submit functionality to Deadline. Requires a node input.

        Will check the script via the sanity check, if validated will give
        the user a submission dialog.

        If submission proceeded, create submission files and
        submit via the __submit_to_deadline() function."""

        # Validate via SanityCheck script
        sanity_check = SanityCheck().validate_script(node)

        # If validated, proceed
        validated = sanity_check.get("validated")
        if validated:

            # If there is a license limit, it will return a integer,
            # otherwise None
            license_limit = sanity_check.get("license_limit")

            # Open the dialog for submission
            submission_panel = panel.SubmissionPanel(node)

            # If user submitted, proceed
            if submission_panel.showModalDialog():

                # Create dictionaries containing all submission parameters
                submission_files = self.__get_submission_parameters(
                    node, submission_panel, license_limit=license_limit
                )

                # Create submission files (job_info.txt and plugin_info.txt)
                # and submit to deadline
                submission = self.__submit_to_deadline(submission_files)

                # Give user submission result
                nuke.message(submission)

    def __get_submission_parameters(
        self, node, submission_panel, license_limit=None
    ):
        """
        Create dictionaries containing all submission parameters
        the panel gives.

        Will return a dictionary:
            {
            "job_info": {
                "Plugin": "Nuke",
                "Frames": "1-100",
                "Priority": 70,
                "Name": "ExampleScript",
                "Department": "Compositing",
                "ConcurrentTasks": 10,
                "ChunkSize": 3,
                "OutputDirectory0": "/example/path",
                "OutputFilename0": "file.exr",
            },
            "plugin_info": {
                "Version": "13.2",
                "WriteNode": "Write1",
                "SceneFile": "/example/path/ExampleScript.nk",
            },
        }
        """
        # Calculating concurrent tasks and chunk size
        render_mode = submission_panel.render_mode.value()
        render_mode = self.__render_mode(render_mode)
        concurrent_tasks = render_mode[0]
        chunk_size = render_mode[1]

        # Get extra parameters
        file_path = node.knob("file").value()
        file_directory = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)

        # Get script path
        script_path = nuke.root().name()

        # Getting job submission parameters
        job_info = {}
        job_info["Plugin"] = "Nuke"
        job_info["Frames"] = submission_panel.framerange.value()
        job_info["Priority"] = submission_panel.priority.value()
        job_info["Name"] = submission_panel.submission_name.value()
        job_info["Department"] = "2D"
        job_info["ConcurrentTasks"] = concurrent_tasks
        job_info["ChunkSize"] = chunk_size
        job_info["OutputDirectory0"] = file_directory
        job_info["OutputFilename0"] = file_name

        # Getting plugin submission parameters
        plugin_info = {}
        plugin_info["Version"] = self.nuke_version
        plugin_info["WriteNode"] = node.name()
        plugin_info["SceneFile"] = script_path

        # If license_limit is not None, add it to the dictionary
        if license_limit:
            plugin_info["LicenseLimit"] = license_limit

        # Create dictionary containing both dictionaries
        submission_files = {
            "job_info": job_info,
            "plugin_info": plugin_info,
        }

        return submission_files

    def __submit_to_deadline(self, submission_parameters):
        """
        This function will create using the provided submission
        dictionary both the job_info.txt file and plugin_info.txt.
        This will be done in a temporary directory.

        After the creation of these files, we call the deadlinecommand
        and submit the job to Deadline.

        """

        # First we will create the necessary files to submit
        # These are the job_info.txt and plugin_info.txt
        # After submitting these files Deadline will understand the submission

        submission_files = []

        # Setting initial message in case something went wrong
        # We will change this variable if submission succeeded
        result = "Something went wrong"

        # Create temporary directory for submission text files
        temporary_directory = tempfile.mkdtemp()

        # We run the code within a try and except to
        # catch any exceptions and give them to the user
        try:

            # Iterating through the provided dictionary, and get
            # the created dictionaries inside.
            for submission_info in submission_parameters.keys():

                # Get the parameters for the specified dictionary
                # (for example job_info)
                info_parameters = submission_parameters.get(submission_info)

                # Create the path for the info_file.txt, for example
                # path/to/temporarydirectory/job_info.txt
                info_file = os.path.join(
                    temporary_directory,
                    submission_info + ".txt",
                )

                # Fix for Windows backward slashes systems
                info_file = info_file.replace(os.sep, "/")

                # Create a text file
                info_file_txt = open(info_file, "w", encoding="utf-8")

                # Iterate through the dictionary for every key
                for parameter in info_parameters.keys():

                    # Get the value per parameter
                    value = info_parameters.get(parameter)

                    # Write the key and value and create a new line
                    # For example:
                    # Plugin=Nuke (key=value)
                    info_file_txt.write(parameter + "=" + str(value) + "\n")

                # Close the file to write parameters
                info_file_txt.close()

                # Add the created text file to the list for submission
                submission_files.append(info_file)

            # Create the command for calling deadline
            deadline_command = [
                os.path.join(self.deadline_command, "deadlinecommand")
            ]

            # Append the text files for the submission parameters
            deadline_command.append(submission_files)

            # Create a subprocess using deadlinecommand and run the submission
            submission = check_output(deadline_command)

            # Return the command output so the user
            # will get the submission information
            result = str(submission)

        # If there is an error, return the error
        # so the user knows
        except Exception as error:
            result = str(error)

        # Always remove the created temporary directory
        finally:
            rmtree(temporary_directory)

        return result

    @staticmethod
    def __render_mode(render_mode):
        """This function will calculate the
        concurrent tasks and the chunk size provided by the
        mode knob in the submission panel.

        There are 3 modes: light, medium, heavy

        Light will render 3 tasks on the same machine simultaneously, with
        each 10 frames. (So a total of 30 frames)

        Medium will render 2 tasks on the same machine at the same time, each
        rendering 5 frames (So a total of 10 frames)

        Heavy will render 1 task at a time, each with 1 frame.

        By using the concurrent tasks and chunk size, a lot more ram and
        computational power can be used while rendering, thus providing
        faster render times.

        """

        # Setting initial values, used for heavy renders
        concurrent_tasks = 1
        chunk_size = 1

        # If render mode is light, change concurrent to
        # 10 frames per time, with 3 tasks at the same time
        if render_mode == "light":
            concurrent_tasks = 10
            chunk_size = 3

        # If render mode is medium, concurrent tasks is 5
        # while rendering 2 tasks at the same time.
        elif render_mode == "medium":
            concurrent_tasks = 5
            chunk_size = 2

        return concurrent_tasks, chunk_size
