import enum
import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Enum, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.core.database import Base


def gen_uuid():
    return str(uuid.uuid4())


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
    id = Column(String, primary_key=True, index=True, default=gen_uuid)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)

    enrollments = relationship("Enrollment", back_populates="student")
    created_classes = relationship("Classroom", back_populates="teacher")
    submissions = relationship("Submission", back_populates="student")
    posts = relationship("Discussion", back_populates="author")
    replies = relationship("DiscussionReply", back_populates="author")


class Classroom(Base):
    __tablename__ = "classrooms"
    id = Column(String, primary_key=True, index=True, default=gen_uuid)
    title = Column(String, index=True)
    code = Column(String, unique=True, index=True)
    teacher_id = Column(String, ForeignKey("users.id"))
    status = Column(Enum(ClassStatus), default=ClassStatus.UPCOMING)

    teacher = relationship("User", back_populates="created_classes")
    students = relationship("Enrollment", back_populates="classroom")
    assignments = relationship("Assignment", back_populates="classroom")
    files = relationship("FileResource", back_populates="classroom")
    discussions = relationship("Discussion", back_populates="classroom")
    live_chunks = relationship("LiveChunk", back_populates="classroom")
    events = relationship("EventLog", back_populates="classroom")


class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    classroom_id = Column(String, ForeignKey("classrooms.id"))

    student = relationship("User", back_populates="enrollments")
    classroom = relationship("Classroom", back_populates="students")


class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(String, primary_key=True, index=True, default=gen_uuid)
    title = Column(String)
    description = Column(Text, nullable=True)
    due_date = Column(String, nullable=True)
    classroom_id = Column(String, ForeignKey("classrooms.id"))

    classroom = relationship("Classroom", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment")


class Submission(Base):
    __tablename__ = "submissions"
    id = Column(String, primary_key=True, index=True, default=gen_uuid)
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
    id = Column(String, primary_key=True, index=True, default=gen_uuid)
    classroom_id = Column(String, ForeignKey("classrooms.id"))
    filename = Column(String)
    file_path = Column(String)
    file_size = Column(String)
    file_type = Column(String)
    is_offline_ready = Column(Boolean, default=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    classroom = relationship("Classroom", back_populates="files")


class Discussion(Base):
    __tablename__ = "discussions"
    id = Column(String, primary_key=True, index=True, default=gen_uuid)
    classroom_id = Column(String, ForeignKey("classrooms.id"))
    user_id = Column(String, ForeignKey("users.id"))
    title = Column(String, nullable=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    classroom = relationship("Classroom", back_populates="discussions")
    author = relationship("User", back_populates="posts")
    replies = relationship("DiscussionReply", back_populates="discussion")


class DiscussionReply(Base):
    __tablename__ = "discussion_replies"
    id = Column(String, primary_key=True, index=True, default=gen_uuid)
    discussion_id = Column(String, ForeignKey("discussions.id"))
    author_id = Column(String, ForeignKey("users.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    discussion = relationship("Discussion", back_populates="replies")
    author = relationship("User", back_populates="replies")


# Audio cache index table for frontend offline/Audio caching metadata
class AudioCache(Base):
    __tablename__ = "audio_cache"
    id = Column(String, primary_key=True, index=True, default=gen_uuid)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    duration_ms = Column(Integer, nullable=True)
    sample_rate = Column(Integer, nullable=True)
    indexed_at = Column(DateTime, default=datetime.utcnow)
    classroom_id = Column(String, ForeignKey("classrooms.id"), nullable=True)

    classroom = relationship("Classroom")


# --- NEW: Live streaming metadata tables ---

class LiveChunk(Base):
    """
    Stores individual audio/video chunk metadata persisted from socket.io stream.
    The backend writes chunk binary files under uploads/live_audio or uploads/live_video.
    """
    __tablename__ = "live_chunks"
    id = Column(String, primary_key=True, index=True, default=gen_uuid)
    classroom_id = Column(String, ForeignKey("classrooms.id"), nullable=False)
    sender_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    seq = Column(Integer, nullable=False, index=True)  # sequence number
    timestamp_ms = Column(Integer, nullable=True)  # unix ms timestamp from client
    
    # "audio" or "video" - Added to support x264 video streaming
    chunk_type = Column(String, default="audio", nullable=False) 
    
    codec = Column(String, nullable=True)  # e.g., "opus", "h264"
    file_path = Column(String, nullable=True)  # stored chunk file path
    file_size = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    classroom = relationship("Classroom", back_populates="live_chunks")


class EventLog(Base):
    """
    Generic event logging table for pen strokes, coordinates, slide switches, custom signaling.
    payload is JSON to be flexible.
    """
    __tablename__ = "event_logs"
    id = Column(String, primary_key=True, index=True, default=gen_uuid)
    classroom_id = Column(String, ForeignKey("classrooms.id"), nullable=False)
    sender_id = Column(String, ForeignKey("users.id"), nullable=True)
    event_type = Column(String, nullable=False)  # e.g., "pen", "coords", "slide", "control"
    payload = Column(JSON, nullable=True)  # JSON blob with details
    created_at = Column(DateTime, default=datetime.utcnow)

    classroom = relationship("Classroom", back_populates="events")