from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Role, Permission, UserRole, RolePermission, User, CreateRoleRequest, AssignRolesRequest
from dependencies import get_current_user

rbac_router = APIRouter(tags=["RBAC"])

# Permission mapping per role
ROLE_PERMISSIONS_MAP = {
    "admin":              ["upload", "edit", "delete", "view"],
    "financial analyst":  ["upload", "edit"],
    "auditor":            ["review"],
    "client":             ["view"],
}

def admin_only(current_user=Depends(get_current_user)):
    if current_user.get("role") not in ("admin", "Admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@rbac_router.post("/roles/create")
def create_role(
    request: CreateRoleRequest,
    db: Session = Depends(get_db),
    admin=Depends(admin_only)
):
    existing = db.query(Role).filter(Role.name == request.name.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Role '{request.name}' already exists")

    new_role = Role(name=request.name.lower())
    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    return {
        "message": "Role created successfully",
        "id": new_role.id,
        "name": new_role.name
    }


@rbac_router.post("/users/assign-role")
def assign_role(
    request: AssignRolesRequest,
    db: Session = Depends(get_db),
    admin=Depends(admin_only)
):
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = db.query(Role).filter(Role.id == request.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Avoid duplicate assignment
    existing = db.query(UserRole).filter(
        UserRole.user_id == request.user_id,
        UserRole.role_id == request.role_id
    ).first()

    if not existing:
        user_role = UserRole(user_id=request.user_id, role_id=request.role_id)
        db.add(user_role)

    # Always sync user.role field
    user.role = role.name
    db.commit()

    return {
        "message": "Role assigned successfully",
        "user_id": request.user_id,
        "user_email": user.email,
        "role_assigned": role.name
    }


@rbac_router.get("/users/{user_id}/roles")
def get_user_roles(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_roles = db.query(UserRole).filter(UserRole.user_id == user_id).all()
    role_names = []
    for ur in user_roles:
        role = db.query(Role).filter(Role.id == ur.role_id).first()
        if role:
            role_names.append({"id": role.id, "name": role.name})

    return {
        "user_id": user_id,
        "email": user.email,
        "roles": role_names
    }



# see permissionn with user_id
@rbac_router.get("/users/{user_id}/permissions")
def get_user_permissions(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role_name = user.role or ""
    permissions = ROLE_PERMISSIONS_MAP.get(role_name.lower(), [])

    return {
        "user_id": user_id,
        "email": user.email,
        "role": role_name,
        "permissions": permissions
    }
