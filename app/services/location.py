from sqlalchemy import select
from app.orm import get_session
from app.orm.models.locations import Location

def get_location_id(marker: str) -> int|None:
    location_id = None
    with get_session() as session:
        location_id = session.scalar(
            select(Location.id)
            .where(Location.marker == marker)
        )
        print(f"location in with block: {location_id}")

    print(f"location outside: {location_id}")
    return location_id
