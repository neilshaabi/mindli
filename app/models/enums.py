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
    MALE = "Male"
    FEMALE = "Female"
    NON_BINARY = "Non-Binary"
