# Append these lines to menu.py

# Deadline integration
import deadlineSubmission
menubar = nuke.menu("Nuke")
deadlineMenu = menubar.addMenu("&Render")
deadlineMenu.addCommand("-", "", "")
deadlineMenu.addCommand("Submit Nuke To Deadline", deadlineSubmission.main, "Ctrl+R")
