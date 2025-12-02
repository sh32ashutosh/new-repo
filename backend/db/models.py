import enum
import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Enum, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.core.database import Base

# --- ENUMS ---
class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class ClassStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    LIVE = "live"
    COMPLETED = "completed"

class SubmissionStatus(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    GRADED = "graded"

# --- TABLES ---

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    
    enrollments = relationship("Enrollment", back_populates="student")
    created_classes = relationship("Classroom", back_populates="teacher")
    submissions = relationship("Submission", back_populates="student")
    posts = relationship("DiscussionPost", back_populates="author")

class Classroom(Base):
    __tablename__ = "classrooms"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    code = Column(String, unique=True, index=True)
    teacher_id = Column(String, ForeignKey("users.id"))
    status = Column(Enum(ClassStatus), default=ClassStatus.UPCOMING)
    
    teacher = relationship("User", back_populates="created_classes")
    students = relationship("Enrollment", back_populates="classroom")
    
    # ✅ FIX: Pointing to 'assignments' (plural) matches the Assignment table
    assignments = relationship("Assignment", back_populates="classroom")
    
    files = relationship("FileResource", back_populates="classroom")
    discussions = relationship("DiscussionPost", back_populates="classroom")

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    classroom_id = Column(String, ForeignKey("classrooms.id"))
    
    student = relationship("User", back_populates="enrollments")
    classroom = relationship("Classroom", back_populates="students")

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    due_date = Column(String, nullable=True)
    classroom_id = Column(String, ForeignKey("classrooms.id"))
    
    # ✅ FIX: Pointing to 'assignments' (plural) matches the Classroom table
    classroom = relationship("Classroom", back_populates="assignments")
    
    submissions = relationship("Submission", back_populates="assignment")

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(String, primary_key=True, index=True)
    assignment_id = Column(String, ForeignKey("assignments.id"))
    student_id = Column(String, ForeignKey("users.id"))
    file_url = Column(String, nullable=True)
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.PENDING)
    grade = Column(String, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User", back_populates="submissions")

class FileResource(Base):
    __tablename__ = "files"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    classroom_id = Column(String, ForeignKey("classrooms.id"))
    filename = Column(String)
    file_path = Column(String)
    file_size = Column(String)
    file_type = Column(String)
    is_offline_ready = Column(Boolean, default=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    classroom = relationship("Classroom", back_populates="files")

class DiscussionPost(Base):
    __tablename__ = "discussions"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    classroom_id = Column(String, ForeignKey("classrooms.id"))
    user_id = Column(String, ForeignKey("users.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    classroom = relationship("Classroom", back_populates="discussions")
    author = relationship("User", back_populates="posts")