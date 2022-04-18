#!/bin/sh


if $HOME_IS_PERSISTED
then
    # Upon container start copy overwrite existing files on shared volume. Files which are
    # not in conflict will remain, giving user the chance to just copy and rename to persist changes.
    cp -rT /assets/tutorial_notebooks_img /home/tutorial_notebooks
    # Copy readme explaining persistence and overwrite procedure.
    cp /assets/_README.md /home/_README.md
fi

# Run the CMD as the main container process
exec "$@"
