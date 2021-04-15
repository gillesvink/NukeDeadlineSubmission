# NukeDeadlineSubmission
Simple script to easily submit Nuke script to Deadline renderfarm. It will only submit the write node the artist has selected.
(Currently used at the Netherlands Filmacademy)

## Compatibility
* Tested on Windows and Nuke 12/13

## How to use
1. Copy deadlineSubmission.py to the .nuke installation folder.
2. Append the lines from menu.py to your menu.py file. (Or copy the lines from below)
```
# Deadline integration
import deadlineSubmission
menubar = nuke.menu("Nuke")
deadlineMenu = menubar.addMenu("&Render")
deadlineMenu.addCommand("-", "", "")
deadlineMenu.addCommand("Submit Nuke To Deadline", deadlineSubmission.main, "Ctrl+R")
```

3. Use CTRL + R to submit the write node you have selected.


#### Preview of submission panel
![Preview of submission panel](https://vinkvfx.com/afb/SubmitToFarm.png)

## Usage of script in custom tools
* The script can also be used from Python Script buttons. Use for example the following code:
```
import deadlineSubmission
selectedNode = nuke.thisNode()
deadlineSubmission.main(selectedNode)
```
