import sys
import os
import asyncio

# 1. PATH FIX
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from passlib.context import CryptContext
from backend.core.database import engine, Base
from backend.db.models import User, UserRole, Classroom, ClassStatus

# Setup Password Hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

async def init_db():
    print("🔄 Initializing Database...")
    
    # 2. Reset Tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Tables Created.")

    # 3. Create Users & Classes
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.asyncio import AsyncSession
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Create Teacher
        teacher = User(
            id="teacher-123",
            username="teacher",
            full_name="Dr. Serious Teacher",
            hashed_password=get_password_hash("123"),
            role=UserRole.TEACHER
        )
        
        # Create Student
        student = User(
            id="student-456",
            username="student",
            full_name="Alex Student",
            hashed_password=get_password_hash("123"),
            role=UserRole.STUDENT
        )

        session.add(teacher)
        session.add(student)
        
        # ⚡ NEW: Create the Default Class (So Discussions.jsx works immediately)
        physics_class = Classroom(
            id="physics-101",
            title="Physics: Thermodynamics",
            code="PHY101",
            teacher_id="teacher-123",
            status=ClassStatus.LIVE
        )
        session.add(physics_class)

        await session.commit()
            
    print("✅ Users Seeded: 'student' and 'teacher' (Password: 123)")
    print("✅ Class Seeded: 'Physics: Thermodynamics' (ID: physics-101)")
    print("🚀 Database 'vlink.db' is ready!")

if __name__ == "__main__":
    try:
        asyncio.run(init_db())
    except ModuleNotFoundError as e:
        print(f"❌ Error: {e}")