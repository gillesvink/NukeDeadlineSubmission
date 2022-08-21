"""
Nuke Deadline Submitter by Gilles Vink (2022)

This module includes the panel for submission
the user will use to submit to Deadline
"""

import nuke
import nukescripts
import os


class SubmissionPanel(nukescripts.PythonPanel):
    """
    Class containing the dialog for submission

    Will ask the user for the following parameters:
    - Submission name
    - Framerange
    - Render mode

    Will require a node as input
    """

    def __init__(self, node):
        # Header
        nukescripts.PythonPanel.__init__(self, "Submit to Deadline 📤")

        # Defining knobs
        self.submission_name = nuke.String_Knob(
            "submissionName", "Submission name 📝"
        )
        self.divider = nuke.Text_Knob("dividerOne", "")
        self.priority = nuke.Int_Knob("priority", "Priority 🚦")
        self.framerange_select = nuke.Enumeration_Knob(
            "frameRangeSelect", "Frame range 🎞", ["global", "input", "in-out"]
        )
        self.framerange = nuke.String_Knob(
            "frameRange",
            "",
            "%s-%s" % (nuke.root().firstFrame(), nuke.root().lastFrame()),
        )
        self.framerange.clearFlag(nuke.STARTLINE)
        self.render_mode = nuke.Enumeration_Knob(
            "renderMode",
            "Mode 🏋️",
            ["light", "medium", "heavy"],
        )
        self.divider2 = nuke.Text_Knob("dividerTwo", "")

        # Adding all knobs
        for knobs in (
            self.submission_name,
            self.divider,
            self.priority,
            self.framerange_select,
            self.framerange,
            self.render_mode,
            self.divider2,
        ):
            self.addKnob(knobs)

        # Setting initial knob values
        self.priority.setValue(70)

        # Getting script name
        script_name = nuke.root().knob("name").value()
        script_name = os.path.basename(script_name)
        script_name = os.path.splitext(script_name)[0]

        self.submission_name.setValue(script_name)
        self.render_mode.setValue("light")

    # Actions when knobs change
    def knobChanged(self, knob):
        """
        This function wil be called any time any knob
        changes in the dialog

        Will check if the changed knob is the framerange,
        and set the frame range accordingly
        """

        # If knob is framerange node, check what the setting is
        if knob is self.framerange_select:

            # If setting is global, use the global frame range
            if self.framerange_select.value() == "global":
                self.framerange.setValue(
                    "%s-%s"
                    % (nuke.root().firstFrame(), nuke.root().lastFrame())
                )

            # If setting is input, get input from the provided node
            elif self.framerange_select.value() == "input":
                node = self.submission_node
                self.framerange.setValue(
                    "%s-%s"
                    % (
                        node.firstFrame(),
                        node.lastFrame(),
                    )
                )

            # If setting is none of the above, use input from viewer
            else:
                self.framerange.setValue(
                    nuke.activeViewer().node().knob("frame_range").getValue()
                )
