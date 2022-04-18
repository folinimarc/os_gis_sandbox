FROM alpine:3.15.3

# Datastories are copied from datastories_img to a shared volume in entrypoint.sh.
COPY ./datastories /datastories_img

# Copy entrypoint and make excutable
COPY entrypoint.sh /
RUN chmod 0700 /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
