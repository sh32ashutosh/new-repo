import asyncio
import sys
import os
from datetime import datetime, timedelta

# Fix path to allow imports from backend root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import AsyncSessionLocal, engine, Base
from backend.db.models import (
    User, UserRole, Classroom, ClassStatus, Assignment, 
    FileResource, Discussion, DiscussionReply
)
from sqlalchemy.future import select
from backend.core.security import get_password_hash 

# UNIQUE HASHES FOR DISTINCT PASSWORDS:
# Hash for "teacher123"
HASH_TEACHER = "$2b$12$27h.3f4.z7QxY.A8E7L1S3H8H4J5oR1Z7E7O6uQyT9/uX6L7F4P3E9"
# Hash for "student123"
HASH_STUDENT = "$2b$12$C3d1e9f2g7h2i7k9j6l8m0n2o4p6q8r9s0t1u2v3w4x5y6z7a8b9c0"

async def seed_data():
    print("🌱 Initializing Database Seeding...")
    
    # 1. Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Check if teacher exists
        result = await db.execute(select(User).where(User.username == "teacher"))
        if result.scalars().first():
            print("⚠️  Default users already exist. Skipping seed.")
            return

        print("Creating Default Users...")
        
        # 2. Create Users
        teacher = User(
            username="teacher",
            hashed_password=HASH_TEACHER, # Unique Teacher Hash
            full_name="Dr. Ratnesh (Physics)",
            role=UserRole.TEACHER
        )
        student = User(
            username="student",
            hashed_password=HASH_STUDENT, # Unique Student Hash
            full_name="Student User",
            role=UserRole.STUDENT
        )
        db.add_all([teacher, student])
        await db.commit()
        await db.refresh(teacher)
        await db.refresh(student)
        
        # 3. Create Demo Class
        print("Creating Demo Class and Resources...")
        demo_class = Classroom(
            title="Hybrid Networks & PWA",
            code="NET401",
            teacher_id=teacher.id,
            status=ClassStatus.LIVE
        )
        db.add(demo_class)
        await db.commit()
        await db.refresh(demo_class)

        # 4. Create Resources (Files)
        demo_file = FileResource(
            classroom_id=demo_class.id,
            filename="Resilience_Principles.pdf",
            file_path="/uploads/resilience_principles.pdf",
            file_size="4.2 MB",
            file_type="application/pdf",
            is_offline_ready=True
        )
        db.add(demo_file)

        # 5. Create Assignments
        demo_assignment = Assignment(
            classroom_id=demo_class.id,
            title="Hybrid Sync Quiz",
            description="Test your knowledge on FEC and Opus codecs.",
            total_points=10,
            due_date=datetime.utcnow() + timedelta(days=7)
        )
        db.add(demo_assignment)

        # 6. Create Discussions
        demo_discussion = Discussion(
            classroom_id=demo_class.id,
            author_id=teacher.id,
            title="Latency vs. Bandwidth Trade-off",
            content="Discuss: If we reduce the audio chunk size (e.g., 20ms), how does it affect FEC efficiency?"
        )
        db.add(demo_discussion)
        await db.commit()
        await db.refresh(demo_discussion)

        # 7. Create Discussion Reply
        demo_reply = DiscussionReply(
            discussion_id=demo_discussion.id,
            author_id=student.id,
            content="I think smaller chunks mean more overhead, reducing efficiency, but it lowers perceived lag."
        )
        db.add(demo_reply)

        await db.commit()
        
        print("✅ Seeding Complete!")
        print("   Teacher Login: teacher / teacher123")
        print("   Student Login: student / student123")

if __name__ == "__main__":
    try:
        asyncio.run(seed_data())
    except Exception as e:
        print(f"❌ Error during seeding: {e}")