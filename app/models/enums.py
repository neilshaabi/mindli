from enum import Enum, unique


@unique
class UserRole(Enum):
    CLIENT = "Client"
    THERAPIST = "Therapist"


@unique
class Gender(Enum):
    MALE = "Male"
    FEMALE = "Female"
    NON_BINARY = "Non-Binary"
    TRANSMASCULINE = "Transmasculine"
    TRANSFEMININE = "Transfeminine"
    AGENDER = "Agender"
    OTHER = "Other"
    PREFER_NOT_TO_SAY = "Prefer not to say"


@unique
class TherapyMode(Enum):
    IN_PERSON = "In Person"
    AUDIO = "Audio Call"
    VIDEO = "Video Call"


@unique
class TherapyType(Enum):
    INDIVIDUAL = "Individual"
    COUPLES = "Couples"
    FAMILY = "Family"
    PSYCHOMETRIC_TESTING = "Psychometric Testing"
