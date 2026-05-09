from datetime import datetime

from utils.auth import get_password_hash


def _demo_employees(now: datetime):
    return [
        {
            "id": "1",
            "name": "María García López",
            "position": "Tech Lead",
            "department": "Tecnología",
            "email": "maria@empresa.com",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Maria",
            "evaluations": {"superior": 90, "subordinados": 88, "companeros": 85, "cliente": 92},
            "kpis_score": 88,
            "eval_360_score": 89,
            "category": "A",
            "created_at": now,
        },
        {
            "id": "2",
            "name": "Juan Rodríguez",
            "position": "Senior Developer",
            "department": "Desarrollo",
            "email": "juan@empresa.com",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Juan",
            "evaluations": {"superior": 82, "subordinados": 80, "companeros": 78},
            "kpis_score": 82,
            "eval_360_score": 80,
            "category": "B1",
            "created_at": now,
        },
        {
            "id": "3",
            "name": "Laura Sánchez",
            "position": "Sales Manager",
            "department": "Ventas",
            "email": "laura@empresa.com",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Laura",
            "evaluations": {"superior": 75, "companeros": 80},
            "kpis_score": 72,
            "eval_360_score": 77,
            "category": "B2",
            "created_at": now,
        },
        {
            "id": "4",
            "name": "Carlos Mendoza",
            "position": "Developer",
            "department": "Tecnología",
            "email": "carlos@empresa.com",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Carlos",
            "evaluations": {"superior": 88, "companeros": 85},
            "kpis_score": 85,
            "eval_360_score": 87,
            "category": "A",
            "created_at": now,
        },
        {
            "id": "5",
            "name": "Ana Martínez",
            "position": "Junior Developer",
            "department": "Tecnología",
            "email": "ana@empresa.com",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Ana",
            "evaluations": {"superior": 70, "companeros": 75},
            "kpis_score": 68,
            "eval_360_score": 72,
            "category": "B2",
            "created_at": now,
        },
        {
            "id": "6",
            "name": "Roberto Fernández",
            "position": "Operations Manager",
            "department": "Operaciones",
            "email": "roberto@empresa.com",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Roberto",
            "evaluations": {"superior": 78, "subordinados": 76},
            "kpis_score": 80,
            "eval_360_score": 77,
            "category": "B1",
            "created_at": now,
        },
        {
            "id": "7",
            "name": "Patricia Ruiz",
            "position": "Sales Representative",
            "department": "Ventas",
            "email": "patricia@empresa.com",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Patricia",
            "evaluations": {"superior": 65},
            "kpis_score": 60,
            "eval_360_score": 65,
            "category": "C1",
            "created_at": now,
        },
        {
            "id": "8",
            "name": "Diego Morales",
            "position": "Product Manager",
            "department": "Producto",
            "email": "diego@empresa.com",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Diego",
            "evaluations": {"superior": 85, "companeros": 82},
            "kpis_score": 84,
            "eval_360_score": 83,
            "category": "B1",
            "created_at": now,
        },
    ]


def _demo_users(now: datetime):
    return [
        {
            "id": "admin-1",
            "email": "admin@empresa.com",
            "name": "Admin Usuario",
            "hashed_password": get_password_hash("admin123"),
            "role": "admin",
            "employee_id": None,
            "department": "Administración",
            "position": "Administrador",
            "is_active": True,
            "created_at": now,
        },
        {
            "id": "1",
            "email": "maria@empresa.com",
            "name": "María García López",
            "hashed_password": get_password_hash("maria123"),
            "role": "admin",
            "employee_id": "1",
            "department": "Tecnología",
            "position": "Tech Lead",
            "is_active": True,
            "created_at": now,
        },
        {
            "id": "2",
            "email": "juan@empresa.com",
            "name": "Juan Rodríguez",
            "hashed_password": get_password_hash("juan123"),
            "role": "empleado",
            "employee_id": "2",
            "department": "Desarrollo",
            "position": "Senior Developer",
            "is_active": True,
            "created_at": now,
        },
    ]


async def ensure_demo_seed_data(db):
    users_count = await db.users.count_documents({})
    if users_count > 0:
        return {"seeded": False, "reason": "users_exist"}

    now = datetime.now()

    employees_count = await db.employees.count_documents({})
    inserted_employees = 0
    if employees_count == 0:
        employees = _demo_employees(now)
        if employees:
            await db.employees.insert_many(employees)
            inserted_employees = len(employees)

    users = _demo_users(now)
    await db.users.insert_many(users)

    return {
        "seeded": True,
        "users_inserted": len(users),
        "employees_inserted": inserted_employees,
    }
