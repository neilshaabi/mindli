from enum import Enum, unique


@unique
class EmailSubject(Enum):
    EMAIL_VERIFICATION = "Email verification"
    PASSWORD_RESET = "Password reset"
    APPOINTMENT_SCHEDULED_CLIENT = (
        "Appointment scheduled and awaiting therapist confirmation"
    )
    APPOINTMENT_SCHEDULED_THERAPIST = (
        "New appointment scheduled and awaiting confirmation"
    )
    PAYMENT_FAILED_CLIENT = "Payment failed"


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


@unique
class PaymentStatus(Enum):
    PENDING = "Pending"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
