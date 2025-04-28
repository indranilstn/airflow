from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
from app.orm import get_session
from app.orm.models.contacts import Contact
from app.orm.models.contact_assoc import ContactAssoc
from app.orm.models.contact_master import ContactMaster, ContactAssocType

async def add_contact(name: str|None, email: str|None, phone: str|None) -> int|None:
    # Validate input (at least one of email or phone should be provided)
    if not email and not phone:
        raise ValueError("At least one of email or phone must be provided")

    contact_id = None
    contact = Contact(name=name, email=email, phone=phone)
    with get_session() as session:
        try:
            session.add(contact)
            session.flush()
            contact_id = contact.id

        except IntegrityError:
            contact_id = session.scalar(
                select(Contact.id).where(
                    Contact.name == name,
                    Contact.email == email,
                    Contact.phone == phone,
                )
            )

        if not contact_id:
            raise ValueError("Invalid contact information")

        master_email_id = None
        master_phone_id = None
        if email:
            master_email_id = session.scalar(select(Contact.id).where(ContactMaster.value == email))
            if not master_email_id:
                try:
                    master_email_id = session.scalar(
                        insert(ContactMaster)
                        .values(value=email, type=ContactAssocType.EMAIL)
                        .returning(ContactMaster.id)
                    )
                    session.flush()

                except IntegrityError:
                    master_email_id = session.scalar(select(Contact.id).where(ContactMaster.value == email))

        if phone:
            master_phone_id = session.scalar(select(ContactMaster.id).where(ContactMaster.value == phone))
            if not master_phone_id:
                try:
                    master_phone_id = session.scalar(
                        insert(ContactMaster)
                        .values(value=phone, type=ContactAssocType.PHONE)
                        .returning(ContactMaster.id)
                    )
                    session.flush()

                except IntegrityError:
                    master_phone_id = session.scalar(select(ContactMaster.id).where(ContactMaster.value == phone))

        for master_id in [master_email_id, master_phone_id]:
            if master_id:
                try:
                    session.execute(
                        insert(ContactAssoc)
                        .values(master_id=master_id, contact_id=contact_id)
                    )

                except IntegrityError:
                    continue

        session.commit()

    return contact_id, master_email_id or master_phone_id, master_phone_id if master_email_id else None
