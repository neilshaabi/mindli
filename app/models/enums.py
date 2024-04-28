from enum import Enum, unique


@unique
class EmailSubject(Enum):
    EMAIL_VERIFICATION = "Email Verification"
    PASSWORD_RESET = "Password Reset"
    APPOINTMENT_SCHEDULED_CLIENT = "Appointment Scheduled"
    APPOINTMENT_SCHEDULED_THERAPIST = "Confirm New Appointment"
    PAYMENT_FAILED_CLIENT = "Payment Failed"
    APPOINTMENT_CONFIRMED_CLIENT = "Appointment Confirmed"
    APPOINTMENT_RESCHEDULED = "Appointment Rescheduled"
    APPOINTMENT_CANCELLED = "Appointment Cancelled"
    APPOINTMENT_NO_SHOW_CLIENT = "Missed Appointment"


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
class Occupation(Enum):
    ARTS = "Arts and Entertainment"
    EDUCATION = "Education"
    FINANCE = "Finance"
    HEALTHCARE = "Healthcare"
    IT = "IT/Technology"
    STUDENT = "Student"
    UNEMPLOYED = "Unemployed"
    OTHER = "Other"


@unique
class ReferralSource(Enum):
    INTERNET = "Internet"
    FRIEND_FAMILY = "Friend/family"
    HEALTHCARE_PROVIDER = "Healthcare provider"
    SOCIAL_MEDIA = "Social media"
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
    PSYCHOMETRICS = "Psychometrics"


@unique
class AppointmentStatus(Enum):
    SCHEDULED = "Scheduled"
    CONFIRMED = "Confirmed"
    COMPLETED = "Completed"
    RESCHEDULED = "Rescheduled"
    CANCELLED = "Cancelled"
    NO_SHOW = "No Show"


@unique
class PaymentStatus(Enum):
    PENDING = "Pending"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
