from fastapi import APIRouter
# Using explicit imports
from backend.api.endpoints import auth
from backend.api.endpoints import dashboard
from backend.api.endpoints import classes
from backend.api.endpoints import assignments
from backend.api.endpoints import files
from backend.api.endpoints import discussions
from backend.api.endpoints import live_classroom
from backend.api.endpoints import profile
from backend.api.endpoints import utils # <-- New Import

api_router = APIRouter()

# 1. Auth Routes
api_router.include_router(auth.router, prefix="/login", tags=["auth"])

# 2. Dashboard Routes
api_router.include_router(dashboard.router, tags=["dashboard"])

# 3. Classroom Management
api_router.include_router(classes.router, prefix="/classes", tags=["classes"])

# 4. Assignments
api_router.include_router(assignments.router, prefix="/assignments", tags=["assignments"])

# 5. Files
api_router.include_router(files.router, prefix="/files", tags=["files"])

# 6. Discussions
api_router.include_router(discussions.router, prefix="/discussions", tags=["discussions"])

# 7. Live Classroom Status
api_router.include_router(live_classroom.router, prefix="/live", tags=["live_classroom"])

# 8. Profile
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
from fastapi import APIRouter
# Using explicit imports
from backend.api.endpoints import auth
from backend.api.endpoints import dashboard
from backend.api.endpoints import classes
from backend.api.endpoints import assignments
from backend.api.endpoints import files
from backend.api.endpoints import discussions
from backend.api.endpoints import live_classroom
from backend.api.endpoints import profile
from backend.api.endpoints import utils 

api_router = APIRouter()

# 1. Auth Routes
# CHANGED: Removed prefix="/login" because auth.py already has @router.post("/login")
# Final URL: /api/login
api_router.include_router(auth.router, tags=["auth"])

# 2. Dashboard Routes
api_router.include_router(dashboard.router, tags=["dashboard"])

# 3. Classroom Management
# Final URL: /api/classes/create
api_router.include_router(classes.router, prefix="/classes", tags=["classes"])

# 4. Assignments
api_router.include_router(assignments.router, prefix="/assignments", tags=["assignments"])

# 5. Files
api_router.include_router(files.router, prefix="/files", tags=["files"])

# 6. Discussions
api_router.include_router(discussions.router, prefix="/discussions", tags=["discussions"])

# 7. Live Classroom Status
api_router.include_router(live_classroom.router, prefix="/live", tags=["live_classroom"])

# 8. Profile
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])

# 9. Utilities (Video Proxy)
api_router.include_router(utils.router, tags=["utils"])
# 9. Utilities (Video Proxy)
# URL: /api/stream-proxy?url=...
api_router.include_router(utils.router, tags=["utils"])