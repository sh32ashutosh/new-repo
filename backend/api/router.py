from fastapi import APIRouter
from backend.api.endpoints import auth, dashboard, classes

api_router = APIRouter()

# 1. Auth Routes
# URL: /api/auth/login
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# 2. Dashboard Routes
# URL: /api/dashboard
api_router.include_router(dashboard.router, tags=["dashboard"])

# 3. Classroom Management Routes
# URLs: /api/classes/create, /api/classes/join, /api/classes/{id}
api_router.include_router(classes.router, prefix="/classes", tags=["classes"])