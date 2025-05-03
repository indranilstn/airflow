from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from app.orm import get_session
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

    location_id = data.get("location_id")
    with get_session(context=context) as session:
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

    # context['data'] = None
    return context
