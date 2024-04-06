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

@unique
class TherapistTitle(Enum):
    THERAPIST = "Therapist"
    PSYCHOLOGIST = "Psychologist"
    COACH = "Coach"

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