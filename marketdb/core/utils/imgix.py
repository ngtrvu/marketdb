def ensure_imgix(photo_path):
    if not photo_path:
        return

    imgix_host = "https://stag-media.imgix.net"
    gcs_host = "https://stag_media.storage.googleapis.com"
    return photo_path.replace(gcs_host, imgix_host)
