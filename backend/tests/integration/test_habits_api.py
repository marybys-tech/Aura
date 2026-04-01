"""Integration tests for habit CRUD endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_habit(auth_client: AsyncClient):
    resp = await auth_client.post("/api/v1/habits", json={
        "title": "Read 30 minutes",
        "category": "intelligence",
        "schedule_type": "daily",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Read 30 minutes"
    assert data["category"] == "intelligence"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_habit_specific_days(auth_client: AsyncClient):
    resp = await auth_client.post("/api/v1/habits", json={
        "title": "Call a friend",
        "category": "sociality",
        "schedule_type": "specific_days",
        "schedule_days": [1, 3, 5],
    })
    assert resp.status_code == 201
    assert resp.json()["schedule_days"] == [1, 3, 5]


@pytest.mark.asyncio
async def test_create_habit_invalid_category(auth_client: AsyncClient):
    resp = await auth_client.post("/api/v1/habits", json={
        "title": "Bad habit",
        "category": "nonexistent",
        "schedule_type": "daily",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_habits(auth_client: AsyncClient):
    resp = await auth_client.get("/api/v1/habits")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_update_habit(auth_client: AsyncClient):
    # Create first
    create_resp = await auth_client.post("/api/v1/habits", json={
        "title": "To update",
        "category": "stamina",
        "schedule_type": "daily",
    })
    habit_id = create_resp.json()["id"]

    # Update
    resp = await auth_client.patch(f"/api/v1/habits/{habit_id}", json={"title": "Updated title"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated title"


@pytest.mark.asyncio
async def test_delete_habit_soft(auth_client: AsyncClient):
    create_resp = await auth_client.post("/api/v1/habits", json={
        "title": "To delete",
        "category": "wellness",
        "schedule_type": "daily",
    })
    habit_id = create_resp.json()["id"]

    resp = await auth_client.delete(f"/api/v1/habits/{habit_id}")
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


@pytest.mark.asyncio
async def test_unauthenticated_access(client: AsyncClient):
    resp = await client.get("/api/v1/habits")
    assert resp.status_code in (401, 403)
