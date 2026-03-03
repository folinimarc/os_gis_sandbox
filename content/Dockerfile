FROM alpine:3.15.3

# Build a lightweight data image. Content seeding into shared volumes is
# orchestrated by docker compose (content service entrypoint in compose.yml).
COPY ./copy_to_image/content_root /content_img
