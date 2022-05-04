If this text looks spartanic and hard to read, right-click here and select "Show
Markdown Preview"!

***

# Hey there friend - A minute of reading might save you a day of headaches!

## Avoid losing your work
Existing files and folders of this Sandbox might be reset to their original
state upon Sandbox restart. **Only files and folders you create are safe** and
will be persisted across Sandbox restarts. This also applies to files you create
inside existing folders, because we do not replace whole folder contents but
rather reset on a file-per-file basis inside each folder recursively.

If you want to build upon an existing script just **copy and rename before**
starting your work! Believe me, this will save you headache down the road!


## Customize the Python environment
Every time the Sandbox is started, it is initialized with a default set of
packages listed in _requirements-base.txt_. If you want to add additional
packages or change the version of existing ones, add it to
_requirements-override.txt_, which is a normal PIP requirements file, and then
restart the Sandbox. At each startup the added packages will be installed on top
of the base environments. The more packages you add the longer the startup time
will become due to this installation procedure, so be patient.

> _Good to know:_ If the behavior is not what you expected, you can start the
> Sandbox using simply `docker compose up` ignoring the detached (-d) flag. This
will show you the logs of the jupyterlabgeoenv-container which includes the
output from the above command, for example that a package was not found due to a
typo.

## How to activate JupyterLab extensions
JupyterLab is a modular environment and hundreds of great extensions exist. Two
ways exist how to install and activate such extensions and this Sandbox only
supports the newer approach whereby an extension is installed via PIP just like
every other Python package. If you find an extension you want to install, look
out for the installation instruction using `pip install` and add the extension
name to _requirements-override.txt_. On next Sandbox restart the extension will
be installed and ready.
