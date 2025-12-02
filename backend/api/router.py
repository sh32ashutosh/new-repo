from fastapi import APIRouter

# 🔄 UPDATED IMPORTS: backend -> backend
# Ensure your folder structure matches this (backend/api/endpoints/...)
from backend.api.endpoints import auth
from backend.api.endpoints import dashboard
from backend.api.endpoints import classes
from backend.api.endpoints import assignments
from backend.api.endpoints import files
from backend.api.endpoints import discussions
from backend.api.endpoints import live_classroom
from backend.api.endpoints import profile

api_router = APIRouter()

# 1. Auth Routes (The Hardcoded Login Logic lives here)
# URL: /api/auth/login/access-token
# ✅ NEW (Matches Frontend URL: /api/login/access-token)
api_router.include_router(auth.router, prefix="", tags=["auth"])

# 2. Dashboard Routes
# URL: /api/dashboard
api_router.include_router(dashboard.router,prefix="/dashboard", tags=["dashboard"])

# 3. Classroom Management
# URLs: /api/classes/create, /api/classes/join, /api/classes/{id}
api_router.include_router(classes.router, prefix="/classes", tags=["classes"])

# 4. Assignments
# URLs: /api/assignments/create, /api/assignments/{id}/submit
api_router.include_router(assignments.router, prefix="/assignments", tags=["assignments"])

# 5. Files
# URLs: /api/files/upload, /api/files/download/{id}
api_router.include_router(files.router, prefix="/files", tags=["files"])

# 6. Discussions
# URLs: /api/discussions/create, /api/discussions/class/{id}
api_router.include_router(discussions.router, prefix="/discussions", tags=["discussions"])

# 7. Live Classroom Status
# URLs: /api/live/{id}/start, /api/live/{id}/end
api_router.include_router(live_classroom.router, prefix="/live", tags=["live_classroom"])

# 8. Profile & Preferences
# URLs: /api/profile, /api/profile/preferences
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])