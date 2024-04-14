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


@unique
class AppointmentStatus(Enum):
    SCHEDULED = "Scheduled"
    CANCELED = "Canceled"
    COMPLETED = "Completed"
    CONFIRMED = "Confirmed"
    RESCHEDULED = "Rescheduled"
    NO_SHOW = "No Show"
