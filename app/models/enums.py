from enum import Enum, unique


@unique
class UserRole(Enum):
    CLIENT = "client"
    THERAPIST = "therapist"


@unique
class SessionFormat(Enum):
    FACE = "Face to face"
    AUDIO = "Audio call"
    VIDEO = "Video call"


@unique
class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non-binary"
