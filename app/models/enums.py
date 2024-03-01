from enum import Enum, unique


@unique
class UserRole(Enum):
    CLIENT = "client"
    THERAPIST = "therapist"


@unique
class SessionFormat(Enum):
    FACE = "Face to Face"
    AUDIO = "Audio Call"
    VIDEO = "Video Call"


@unique
class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non-binary"
