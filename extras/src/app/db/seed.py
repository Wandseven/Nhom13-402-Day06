"""Seed clinics data into the database."""
import asyncio
import json
from pathlib import Path
from sqlalchemy import text
from app.db.database import engine, Base, async_session
from app.models.clinic import Clinic


DATA_DIR = Path(__file__).parent.parent / "data"


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        # Check if already seeded
        result = await session.execute(text("SELECT COUNT(*) FROM clinics"))
        count = result.scalar()
        if count > 0:
            print(f"Database already has {count} clinics. Skipping seed.")
            return

        with open(DATA_DIR / "clinics.json", "r", encoding="utf-8") as f:
            clinics_data = json.load(f)

        for c in clinics_data:
            session.add(Clinic(**c))

        await session.commit()
        print(f"Seeded {len(clinics_data)} clinics successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
