# NukeDeadlineSubmission

Script to easily submit via the Nuke User Interface to Deadline. It will create a small dialog where the user can submit the selected write node.

![Deadline submitter](/resources/submitter.png)

## Compatibility
* Tested on Linux/Mac/Windows

## How to install
* Copy the `deadline_submission` folder to your `.nuke` folder or any other installation where Nuke is pointed to.
* Copy the `menu.py` file to your `.nuke` folder, or add the following line to your own `menu.py` file. `nuke.pluginAddPath("./deadline_submission")`

## How to change the submission shortcut
* The shortcut can be easily changed via the `menu.py` file inside the `deadline_submission` folder. Change the `shortcut` variable to any shortcut you would like.
```
shortcut = "F5"
```

## Using Deadline submisison inside your tools
* You can use the `submit(node)` function.
```
import deadline_submission
submission_node = nuke.thisNode()
deadline_submission.DeadlineSubmission().submit(submission_node)
```

## Add validations
* Using the `sanity_check` other checks can be added. The file itself provides a guide on where to add your own functions and checks.