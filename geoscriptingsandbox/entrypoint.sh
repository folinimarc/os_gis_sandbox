#!/bin/sh

# Upon container start copy overwrite existing files on shared volume. Files which are
# not in conflict will remain, giving user the chance to just copy and rename to persist changes.
cp -rT /setup/tutorial_notebooks_img /home/tutorial_notebooks

# Run the CMD as the main container process
exec "$@"
