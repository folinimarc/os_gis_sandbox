FROM alpine:3.15.3

# Datastories are copied from datastories_img to a shared volume in entrypoint.sh.
COPY ./datastories /datastories_img

COPY entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
