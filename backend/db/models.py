from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from backend.core.database import Base

# --- ENUMS ---
class UserRole(str, enum.Enum):
    TEACHER = "teacher"
    STUDENT = "student"
    ADMIN = "admin"

class ClassStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    LIVE = "live"
    COMPLETED = "completed"

class SubmissionStatus(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    GRADED = "graded"
    LATE = "late"

def generate_uuid():
    return str(uuid.uuid4())

# --- CORE TABLES ---

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    
    # Relationships
    created_classes = relationship("Classroom", back_populates="teacher", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="student")
    discussions = relationship("Discussion", back_populates="author")
    replies = relationship("DiscussionReply", back_populates="author")

class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    title = Column(String(100), nullable=False)
    code = Column(String(6), unique=True, index=True, nullable=False)
    teacher_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(ClassStatus), default=ClassStatus.UPCOMING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    teacher = relationship("User", back_populates="created_classes")
    students = relationship("Enrollment", back_populates="classroom", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="classroom", cascade="all, delete-orphan")
    files = relationship("FileResource", back_populates="classroom", cascade="all, delete-orphan")
    discussions = relationship("Discussion", back_populates="classroom", cascade="all, delete-orphan")

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    classroom_id = Column(String(36), ForeignKey("classrooms.id"), nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("User", back_populates="enrollments")
    classroom = relationship("Classroom", back_populates="students")

# --- LMS TABLES ---

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    classroom_id = Column(String(36), ForeignKey("classrooms.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    total_points = Column(Integer, default=100)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    classroom = relationship("Classroom", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment", cascade="all, delete-orphan")

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    assignment_id = Column(String(36), ForeignKey("assignments.id"), nullable=False)
    student_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=True) # Text submission or URL
    file_url = Column(String(500), nullable=True)
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.PENDING)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    grade = Column(Integer, nullable=True)

    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User", back_populates="submissions")

class FileResource(Base):
    __tablename__ = "files"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    classroom_id = Column(String(36), ForeignKey("classrooms.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False) # Local path or S3 URL
    file_size = Column(String(20)) # e.g. "2MB"
    file_type = Column(String(50)) # e.g. "application/pdf"
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    is_offline_ready = Column(Boolean, default=False) # For PWA caching

    classroom = relationship("Classroom", back_populates="files")

class Discussion(Base):
    __tablename__ = "discussions"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    classroom_id = Column(String(36), ForeignKey("classrooms.id"), nullable=False)
    author_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    classroom = relationship("Classroom", back_populates="discussions")
    author = relationship("User", back_populates="discussions")
    replies = relationship("DiscussionReply", back_populates="discussion", cascade="all, delete-orphan")

class DiscussionReply(Base):
    __tablename__ = "discussion_replies"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    discussion_id = Column(String(36), ForeignKey("discussions.id"), nullable=False)
    author_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    discussion = relationship("Discussion", back_populates="replies")
    author = relationship("User", back_populates="replies")