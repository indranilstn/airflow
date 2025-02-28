import os
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy import MetaData, insert, select
from sqlalchemy.exc import IntegrityError

from include.sql.tables.locations import get_locations_model
from include.sql.tables.contacts import get_contacts_model
from include.sql.tables.events import get_events_model
from include.sql.tables.contact_master import get_contact_master_model, ContactAssocType
from include.sql.tables.contact_assoc import get_contact_assoc_model
from include.sql.tables.lead_journey import get_journey_model

def process_event(event_id: int):
    """Post-process the event

    Raises:
        Exception: Non-existent location,
    """

    engine = (
        PostgresHook(postgres_conn_id=os.environ['APP__DATABASE__CONN_ID'])
            .get_sqlalchemy_engine()
    )

    sql_meta = MetaData()
    events = get_events_model(metadata=sql_meta)
    contacts = get_contacts_model(metadata=sql_meta)
    locations = get_locations_model(metadata=sql_meta)
    contact_master = get_contact_master_model(metadata=sql_meta)
    contact_assoc = get_contact_assoc_model(metadata=sql_meta)
    lead_journey = get_journey_model(metadata=sql_meta)

    select_stmt = select(
        events.c.type,
        events.c.location_marker.label("marker"),
        contacts.c.id,
        contacts.c.name,
        contacts.c.email,
        contacts.c.phone,
    ).join(
        contacts,
        events.c.contact_id == contacts.c.id,
    ).where(
        events.c.id == event_id
    )

    location_id = None
    master_email = None
    master_phone = None
    with engine.connect() as conn:
        row = conn.execute(select_stmt).first()
        location_id = conn.execute(select(locations.c.id).where(locations.c.marker == row['marker'])).scalar()
        if not location_id:
            raise Exception("Location not found")

        print(f"location id: {location_id}")
        # TODO: use ThreadPoolExecutor
        if row['email']:
            try:
                master_email = conn.execute(select(contact_master.c.id).where(contact_master.c.value == row['email'])).scalar()
            except Exception as e:
                print(type(e))
                raise

            if not master_email:
                result = conn.execute(insert(contact_master).returning(contact_master.c.id), [{
                    'value': row['email'],
                    'type': ContactAssocType.EMAIL,
                }])
                master_email = result.scalar()

        if row['phone']:
            master_phone = conn.execute(select(contact_master.c.id).where(contact_master.c.value == row['phone'])).scalar()
            if not master_phone:
                result = conn.execute(insert(contact_master).returning(contact_master.c.id), [{
                    'value': row['phone'],
                    'type': ContactAssocType.PHONE,
                }])
                master_phone = result.scalar()

        transaction = conn.begin()
        for master_id in [master_email, master_phone]:
            if master_id:
                try:
                    conn.execute(insert(contact_assoc), [{
                        'master_id': master_id,
                        'contact_id': row['id'],
                    }])

                except IntegrityError:
                    continue

                except: #noqa
                    transaction.rollback()
                    raise

        transaction.commit()

        try:
            conn.execute(insert(lead_journey), [{
                'event_id': event_id,
                'location_id': location_id,
                'contact_master_id': master_email or master_phone,
            }])

        except IntegrityError:
            pass
