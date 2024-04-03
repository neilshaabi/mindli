from magic import Magic
from werkzeug.datastructures import FileStorage


def get_file_extension(file: FileStorage):
    # Determine file's MIME type
    file_stream = file.stream
    mime = Magic(mime=True)
    file_mime_type = mime.from_buffer(file_stream.read(2048))
    file_stream.seek(0)

    # Map MIME types to file extensions
    mime_extension_map = {
        "image/jpeg": "jpg",
        "image/png": "png",
    }

    # Default to '.unknown' if MIME type not recognized
    extension = mime_extension_map.get(file_mime_type, ".unknown")
    return extension
