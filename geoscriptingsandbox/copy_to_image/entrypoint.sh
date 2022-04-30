#!/bin/sh


if $PERSISTENCE_NOTE_IN_HOME
then
    # Copy readme explaining persistence and overwrite procedure.
    cp /assets/_README.md /home/_README.md
fi

# Run the CMD as the main container process
exec "$@"
