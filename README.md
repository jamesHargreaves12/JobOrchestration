#Job Orchestration

## What is the point in this package?
Whilst running long experiments for https://aclanthology.org/2021.eacl-main.219/ There was a number of characteristics /
pain points that felt unaddressed by the current open source packages.
- I want to run large number of experiments that are different in some small number of ways that can be controlled via 
config. 
  - I want to be able to set of a list of experiments that should be run and not have to wait for experiment X to finish 
before I kick off experiment Y 
  - I want to be able to run these in parallel when appropriate.
  - I don't want the failure of one experiment to effect another experiment.
  - These experiments naturally broke down into a set of atomic tasks and when the 4th Task Failed I wanted to be able
to not have to repeat the first 3 experiments.
- If I get a future result that was surprising, I want to be able to go back to an earlier experiment and
  - Look at the raw output including logs from that experiment.
  - Rerun in exactly the same setup as before (including being able to revert my local version of the code base to that
point in time).
  - Be able to compare what has changed in the code base between the two runs.
  - If there was a train model as part of this experiment I wanted this to still be present.
- While the experiments are running I want an easy centralised place that I can see progress some estimation of how long
was left.
- I want validation to run prior to the experiment running. For example, I didn't want to train a model for X hours only 
to find that the result didn't save due to a missing path.

This package is an attempt to provide a basic framework to start to address these pain points. It was also important that
the package was Lightweight and didn't increase the run time significantly. Also while it was accepted that this package 
would require some level opinionation to achieve these goals there was an aim to under index on this for the main feature 
of the package where possible. Finally, we only considered experiments that could be run on a single machine scaling out 
to multiple machines can be achieved by just partitioning the config files.


## Get Started: 
Download the package by running the following commands.
`pip install job-orchestration`

The first thing that you will need to do is set the `JOB_ORCHESTRATION_WORKSPACE` environment variable to tell the
module where you will write logs / output / etc too.

## Interface:
To enable this module to run your code we require that you follow the convention that you have a file called Tasks 
which contains a class that implements the `TaskBase` class. So the class needs a constructor which takes in the config
dictionary and provides a run method to do the actual work. Optionally, you can also provide a validate method
(Recommended that you do ).

## Config Files:
To control the execution of your program you will need to provide one or more yaml config files. As a minimum we require 
that you provide us with the following fields:
    githubRepository: Url of the git repo that your project is under.
    pathToTasks: This is the parent file of the Tasks.py file.
    outputDir: Path to write the output too it - this will be a sub folder of the Output Directory.
    tasks: A list of the tasks that need to be performed by the library. These must contain at least:
        - id - must be unique in the set of tasks in this config file.
        - method - The name of the class in the Tasks file to execute.

These fields plus any others that are present will be passed through to as a dictionary object to the task 
constructor and so can be used to control execution there.


Now the next question is where do I put this config? You must put it in the "ConfigSources" sub-directory under the 
path given by the`JOB_ORCHESTRATION_WORKSPACE` environment variable. (Pro-tip once you have set the environment variable 
just run `python -m job_orchestration` to create all the subdirectories).

Now we need to ready this config file to do this run 
`python -m job_orchestration -action readyConfigs` - this will validate and setup the output location for any configs 
in the ConfigSources directory before moving them to the ConfigsToRun directory.

Finally, we need to run a worker which will run the tasks one by one in each of the yaml files. The worker will run
and pick up a config file from "ConfigsToRun" directory and attempt to run it and repeat.
`python -m job_orchestration -action readyConfigs`

For more clarity please see the example Tasks.py and config file in the /demo folder: