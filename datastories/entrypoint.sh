#!/bin/sh

# Upon container start copy overwrite existing files on shared volume. Files which are
# not in conflict will remain, giving user the chance to just copy and rename to persist changes.
cp -rT /datastories_img /shared_datastories
