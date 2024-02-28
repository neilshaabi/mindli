from enum import Enum, unique


@unique
class UserRole(Enum):
    CLIENT = "client"
    THERAPIST = "therapist"


@unique
class SessionFormat(Enum):
    FACE = "face_to_face"
    AUDIO = "audio_call"
    VIDEO = "video_call"


@unique
class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non-binary"
