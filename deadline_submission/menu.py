"""
This file adds the command to the Nuke user interface.

You can change the shortcut by changing the shortcut
variable. For example: shortcut = "ctrl+R" will use
ctrl + r for the submission shortcut.
"""

import deadline_submission

shortcut = "F5"

menubar = nuke.menu("Nuke")
deadline_menu = menubar.addMenu("&Render")
deadline_menu.addCommand("-", "", "")
deadline_menu.addCommand(
    "Submit to Deadline",
    "deadline_submission.DeadlineSubmission().submit_selected_node()",
    shortcut,
)
