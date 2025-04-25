from os import getenv
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from app.orm import get_pg_session
from app.orm.models.locations import Location
from app.orm.models.contacts import Contact
from app.orm.models.events import Event
from app.orm.models.contact_master import ContactMaster, ContactAssocType
from app.orm.models.contact_assoc import ContactAssoc
from app.orm.models.lead_journey import LeadJourney
from . import AppContext

def process_event(context: AppContext) -> AppContext:
    """Post-process the event

    Raises:
        Exception: Non-existent location,
    """

    data = context.get("data", None)
    event_id = data.get("event_id", None) if data else None
    if not event_id:
        raise Exception("Event not found")

    postgres_conn_id=getenv('APP__DATABASE__CONN_ID')

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
    master_email_id = None
    master_phone_id = None
    with get_pg_session(connection_id=postgres_conn_id, context=context) as session:
        row = session.execute(select_stmt).first()

        location_id = session.scalar(select(Location.id).where(Location.marker == row['marker']))
        if not location_id:
            raise Exception("Location not found")

        print(f"location id: {location_id}")
        # TODO: use ThreadPoolExecutor
        if row['email']:
            try:
                master_email_id = session.scalar(select(Contact.id).where(ContactMaster.value == row['email']))
            except Exception as e:
                print(type(e))
                raise

            if not master_email_id:
                master_email_id = session.scalar(
                    insert(ContactMaster)
                    .values(value=row['email'], type=ContactAssocType.EMAIL)
                    .returning(ContactMaster.id)
                )

        if row['phone']:
            master_phone_id = session.scalar(select(ContactMaster.id).where(ContactMaster.value == row['phone']))
            if not master_phone_id:
                master_phone_id = session.scalar(
                    insert(ContactMaster)
                    .values(value=row['phone'], type=ContactAssocType.PHONE)
                    .returning(ContactMaster.id)
                )

        with session.begin():
            for master_id in [master_email_id, master_phone_id]:
                if master_id:
                    try:
                        session.execute(
                            insert(ContactAssoc)
                            .values(master_id=master_id, contact_id=row['id'])
                        )

                    except IntegrityError:
                        continue

            try:
                session.execute(
                    insert(LeadJourney)
                    .values(
                        event_id=event_id,
                        location_id=location_id,
                        primary_master_id=master_email_id or master_phone_id,
                        secondary_master_id=master_phone_id if master_email_id else None,
                    )
                )

            except IntegrityError:
                pass

    context['data'] = None
    return context