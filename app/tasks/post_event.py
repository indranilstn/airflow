from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from app.orm import get_session
from app.orm.models.locations import Location
from app.orm.models.contacts import Contact
from app.orm.models.events import Event
from app.orm.models.lead_journey import LeadJourney
from . import AppContext

def process_event(context: AppContext) -> AppContext:
    """Post-process the event

    Raises:
        Exception: Non-existent location,
    """

    data = context.get("data", None)
    event_id = data.get("event_id") if data else None
    if not event_id:
        raise Exception("Event not found")

    primary_master_id = data.get("primary_master")
    secondary_master_id = data.get("secondary_master")
    if not primary_master_id:
        raise Exception("Primary contact information not found")

    select_stmt = select(
        Event.type,
        Event.location_marker.label("marker"),
        Contact.id,
        Contact.name,
        Contact.email,
        Contact.phone,
    ).where(
        Event.id == event_id
    )

    location_id = None
    with get_session(context=context) as session:
        row = session.execute(select_stmt).first()

        location_id = session.scalar(select(Location.id).where(Location.marker == row['marker']))
        if not location_id:
            raise Exception("Location not found")

        print(f"location id: {location_id}")

        try:
            session.execute(
                insert(LeadJourney)
                .values(
                    event_id=event_id,
                    location_id=location_id,
                    primary_master_id=primary_master_id,
                    secondary_master_id=secondary_master_id,
                )
            )
            session.commit()

        except IntegrityError:
            pass

    context['data'] = None
    return context
