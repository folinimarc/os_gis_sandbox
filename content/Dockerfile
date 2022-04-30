FROM alpine:3.15.3

# All content in content_root is copied from content_img to a shared volume in
# entrypoint.sh. This ensures that the data is always reset (and updated in case
# of a new version of this data container) upon container start.
COPY ./copy_to_image/content_root /content_img

# Copy entrypoint and make excutable
COPY ./copy_to_image/entrypoint.sh /
RUN chmod 0700 /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
