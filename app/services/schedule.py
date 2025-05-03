from datetime import datetime, date, time, timedelta
from sqlalchemy import text
from ..orm import get_session
from ..orm.models.schedule import ScheduleType

DEFAULT_INTERVAL_MINUTES = 30
STAFF_ADVISORY_KEY = "StaffLock-"
LOCATION_ADVISORY_KEY = "LocationLock-"

def get_free_slots(location: int, target_date: date) -> list:
    result = []

    with get_session() as session:
        result = session.scalars(
            text("SELECT get_free_slots(:id_location, :target_date, :slot_interval)"),
            {
                'id_location': location,
                'target_date': target_date,
                'slot_interval': timedelta(minutes=DEFAULT_INTERVAL_MINUTES),
            }
        ).all()

    return result

def get_free_staff(
    location: int,
    target_date: date,
    target_start: time,
    target_end: time|None = None,
) -> list:
    if not target_end:
        target_end = (datetime.combine(datetime.today(), target_start) + timedelta(minutes=DEFAULT_INTERVAL_MINUTES)).time()

    result = []
    with get_session() as session:
        result = session.scalars(
            text("SELECT get_free_staff(:id_location, :target_date, :target_start, :target_end)"),
            {
                'id_location': location,
                'target_date': target_date,
                'target_start': target_start,
                'target_end': target_end,
            }
        ).all()

    return result

def book_appointment(
    location: int,
    target_date: date,
    target_start: time,
    target_end: time|None = None,
) -> int|None:
    if not target_end:
        target_end = (datetime.combine(datetime.today(), target_start) + timedelta(minutes=DEFAULT_INTERVAL_MINUTES)).time()

    result = None
    with get_session() as session:
        result = session.scalar(
            text("SELECT book_free_staff(:location_id, :target_date, :target_start, :target_end)"),
            {
                'location_id': location,
                'target_date': target_date,
                'target_start': target_start,
                'target_end': target_end,
            }
        )

    return result

def add_staff_schedule(
    staff_id: int,
    target_start: datetime,
    target_end: datetime,
    schedule_type: ScheduleType = ScheduleType.OUT_OF_OFFICE,
    rrule: str|None = None,
) -> int|None:
    result = None
    with get_session() as session:
        result = session.scalar(
            text("SELECT add_schedule(:schedule_type, :target_start, :target_end, :id_staff, NULL, :repeat_rule)"),
            {
                'schedule_type': schedule_type,
                'target_start': target_start,
                'target_end': target_end,
                'id_staff': staff_id,
                'repeat_rule': rrule,
            }
        )

    return result

def add_location_schedule(
    location_id: int,
    target_start: datetime,
    target_end: datetime,
    rrule: str|None = None,
) -> int|None:
    result = None
    with get_session() as session:
        result = session.scalar(
            text("SELECT add_schedule(:schedule_type, :target_start, :target_end, NULL, :id_location, :repeat_rule)"),
            {
                'schedule_type': ScheduleType.LOCATION,
                'target_start': target_start,
                'target_end': target_end,
                'id_location': location_id,
                'repeat_rule': rrule,
            }
        )

    return result

def add_holiday(
    target_start: datetime,
    target_end: datetime,
    rrule: str|None = None,
) -> int|None:
    result = None
    with get_session() as session:
        result = session.scalar(
            text("SELECT add_schedule(:schedule_type, :target_start, :target_end, NULL, NULL, :repeat_rule)"),
            {
                'schedule_type': ScheduleType.HOLIDAY,
                'target_start': target_start,
                'target_end': target_end,
                'repeat_rule': rrule,
            }
        )

    return result

def check_booking_conflict(
    target_start: datetime,
    target_end: datetime,
    id_staff: int|None,
    id_location: int|None,
) -> list:
    result = []
    with get_session() as session:
        result = session.scalars(
            text("SELECT check_conflict(:target_start, :target_end, :id_staff, :id_location)"),
            {
                'target_start': target_start,
                'target_end': target_end,
                'id_staff': id_staff,
                'id_location': id_location,
            }
        ).all()

    return result
