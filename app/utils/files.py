from werkzeug.datastructures import FileStorage


def get_file_extension(file: FileStorage):
    # Extract MIME type from file
    file_mime_type = file.content_type

    # Map MIME types to file extensions
    mime_extension_map = {
        "image/jpeg": "jpg",
        "image/png": "png",
    }

    # Default to '.unknown' if MIME type not recognized
    extension = mime_extension_map.get(file_mime_type, ".unknown")
    return extension
