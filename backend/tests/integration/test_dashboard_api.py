"""Integration tests for dashboard endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dashboard_today(auth_client: AsyncClient):
    resp = await auth_client.get("/api/v1/dashboard/today")
    assert resp.status_code == 200
    data = resp.json()
    assert "date" in data
    assert "habits" in data
    assert "scores" in data
    assert "active_quests" in data


@pytest.mark.asyncio
async def test_dashboard_week(auth_client: AsyncClient):
    resp = await auth_client.get("/api/v1/dashboard/week")
    assert resp.status_code == 200
    data = resp.json()
    assert "start_date" in data
    assert "end_date" in data
    assert "habits" in data


@pytest.mark.asyncio
async def test_dashboard_month(auth_client: AsyncClient):
    resp = await auth_client.get("/api/v1/dashboard/month")
    assert resp.status_code == 200
    data = resp.json()
    assert "month" in data
    assert "year" in data
    assert "days" in data
    assert len(data["days"]) >= 28


@pytest.mark.asyncio
async def test_stats(auth_client: AsyncClient):
    resp = await auth_client.get("/api/v1/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "scores" in data
    assert "total_aura" in data
    assert len(data["scores"]) == 6


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
