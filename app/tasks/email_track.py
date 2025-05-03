import re
from os import getenv
# from langchain.globals import set_verbose, set_debug
from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.documents import Document
from langchain_community.document_transformers import Html2TextTransformer

from sqlalchemy import select #, desc
from pydantic import BaseModel, Field
from app.services.emails.base_email import EmailService as BaseService
from app.services.emails.gmail import Gmail as GmailService
from app.services.emails.raw_email import RawEmailHandler
from app.services.contact import add_contact
from app.services.location import get_location_id
from app.orm.models.tracking_email import TrackerEmail
from app.orm.models.events import Event, EventType
from app.orm import get_session
from . import AppContext, set_app_context

USER_EMAIL = "indranil@softechnation.com"
INFO_PATTERN = r"indranil\+([^\+]+)\+([^\+@]+).*@softechnation.com"

class _SourceStruct(BaseModel):
    """Extract source from email subject"""
    source: str|None = Field(default=None, description="source of the email")

class _OutputStruct(_SourceStruct):
    """Extract data from email body"""

    name: str|None = Field(default=None, description="name of the prospect")
    email: str|None = Field(default=None, description="email address of the prospect")
    phone: str|None = Field(default=None, description="phone number of the prospect")
    location: str|None = Field(default=None, description="building the prospect is interested in")
    unit: str|None = Field(default=None, description="bedroom unit the prospect is interested in as '1 Bedroom', '2 Bedroom', '3 Bedroom', '4 Bedroom' or '4+ Bedroom'")
    address: str|None = Field(default=None, description="address of the building in standard US or Canadian format")
    movein: str|None = Field(defalt=None, description="desired move-in date")
    request: str|None = Field(default=None, description="summarize any request from prospect")

def get_service(user_email: str = "", *, file_path: str = "") -> BaseService|None:
    """Initiate and authenticate appropriate service"""

    if file_path:
        service = RawEmailHandler()
        service.file_path = file_path
    else:
        service = GmailService()

    email = user_email or USER_EMAIL if not file_path else None

    return service if service.authenticate(email) else None

def fetch_email(service: BaseService) -> int:
    tracker_id = None
    with get_session() as session:
        for headers, body in service.get_emails(1):
            msg_id = headers.get('Message-ID') or headers.get('Message-Id') or None
            header_str = str(headers)

            if re.search(r"indranil\+[^@]+@softechnation.com", header_str):
                tracker = TrackerEmail(headers=headers, body=body, msg_id=msg_id)
                session.add(tracker)
                session.flush()

                tracker_id = tracker.id

        session.commit()

    return tracker_id

def parse_email(tracking_id: int) -> AppContext:
    """Parse user information in the email body

    Raises:
        ValueError: on invalid email format
        Exception: on missing prospect email address
    """

    contact_id = None
    event_id = None
    app_context = None
    primary_master_id = None
    secondary_master_id = None

    def prepare_text(body_text: str|list) -> list:
        return [body_text] if isinstance(body_text, str) else body_text

    with get_session() as session:
        tracker = session.scalar(
            select(TrackerEmail)
            .where(TrackerEmail.id == tracking_id)
            # .order_by(desc(TrackerEmail.id))
            # .limit(1)
        )

        flat_headers = ", ".join(list(tracker.headers.values()))
        matched = re.search(INFO_PATTERN, flat_headers)

        client = None
        location = None
        if matched:
            client = matched.group(1)
            location = matched.group(2)

        if not (client and location):
            raise Exception("Client and/or Location not found")

        session.set_client(client)

        prospect = None
        body = tracker.body
        for part in body:
            output = None
            if isinstance(part, str):
                body_text = prepare_text(body[part])
                match part:
                    case "text/plain":
                        output = _parse_text_body(body_text)

                    case "text/html":
                        output = _parse_html_body(body_text)

            else:
                if "text/plain" in part:
                    output = _parse_text_body(prepare_text(part['text/plain']))

                if "text/html" in part:
                    output = _parse_html_body(prepare_text(part['text/html']))

            if output and output.email:
                prospect = output
                break

        if not prospect:
            raise ValueError("Invalid email format")

        name_from_header = None
        email_from_header = None
        if not prospect.email and "Reply-To" in tracker.headers:
            # Unicode-compatible pattern for name and email address
            pattern = r"(?P<name>[\w\s\u0080-\uFFFF]+)?\s*(<(?P<email>[^>]+)>|(?P<email_only>[^@\s]+@[^@\s]+))?"
            matched = re.search(pattern, tracker.headers['Reply-To'])

            if matched:
                name_from_header = matched.group("name") and matched.group("name").strip() or None
                email_from_header = (
                    (matched.group("email") and matched.group("email").strip())
                    or
                    (matched.group("email_only") and matched.group("email_only").strip())
                    or
                    None
                )

            if not email_from_header:
                raise Exception("Prospect email address not found")

            prospect.email = email_from_header
            if not prospect.name and name_from_header:
                prospect.name = name_from_header

        source_from_header = None
        if not prospect.source and "Subject" in tracker.headers:
            source_from_header = _ask_ai_source(tracker.headers['Subject'])
            if source_from_header:
                prospect.source = source_from_header

        app_context = AppContext(client=client, data={})
        set_app_context(app_context)

        try:
            contact_id, primary_master_id, secondary_master_id = add_contact(prospect.name, prospect.email, prospect.phone)

        except ValueError:
            raise ValueError(f"Invalid contact information in tracker email: {tracker.id}")

        print(f"Location found in parse_email: {location}")
        location_id = get_location_id(location)

        event = Event(
            type=EventType.EMAIL,
            contact_id=contact_id,
            source=prospect.source,
            unit_type=prospect.unit,
            location_id=location_id,
            data={'location': prospect.location, 'address': prospect.address},
        )

        session.add(event)
        session.flush()

        event_id = event.id

        session.commit()

    if app_context:
        app_context['data'] = {
            'event_id': event_id,
            'location_id': location_id,
            'primary_master': primary_master_id,
            'secondary_master': secondary_master_id,
        }

    return app_context

def _parse_text_body(content: list[str]) -> _OutputStruct|None:
    for body in content:
        output = _ask_ai(body) if body else None
        print(output)

        if output and output.email:
            return output

    return None

def _parse_html_body(content: list[str]) -> _OutputStruct|None:
    docs = [Document(page_content=html_text) for html_text in content]

    html2text = Html2TextTransformer()
    html_docs = html2text.transform_documents(docs)
    content_list = [html_doc.page_content for html_doc in html_docs]
    # print(content_list)

    return _parse_text_body(content_list)

def _ask_ai(content: str) -> _OutputStruct:
    """Extract user information"""

    print(content)
    # set_debug(True)
    parser = PydanticOutputParser(pydantic_object=_OutputStruct)
    prompt_template = ChatPromptTemplate([
        ("system", "You are an email parser. Wrap the output in `json` tags\n{format_instructions}"),
        ("user", "Extract the prospect information in the format provided, from the following email: {body}"),
    ]).partial(format_instructions=parser.get_format_instructions())

    api_key = getenv('GOOGLE_GEMINI_API_KEY')
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.0,
        max_retries=2,
        google_api_key=api_key,
    )

    # llm = ChatOpenAI(
    #     model="gpt-4o-mini",
    #     temperature=0,
    #     max_tokens=None,
    #     timeout=None,
    #     max_retries=2,
    # )

    chain = prompt_template | llm | parser
    result = chain.invoke({'body': content})

    if result.unit:
        unit = result.unit.strip().split()
        result.unit = f"{unit[0]} Bedroom"

    return result

def _ask_ai_source(content: str) -> str|None:
    """Extract source information from email subject"""

    # set_debug(True)
    parser = PydanticOutputParser(pydantic_object=_SourceStruct)
    prompt_template = ChatPromptTemplate([
        ("system", "You are an email parser. Wrap the output in `json` tags\n{format_instructions}"),
        ("user", "Extract the source of the email from the subject line: {subject}"),
    ]).partial(format_instructions=parser.get_format_instructions())

    api_key = getenv('GOOGLE_GEMINI_API_KEY')
    gllm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.1,
        max_retries=2,
        google_api_key=api_key,
    )

    chain = prompt_template | gllm | parser
    result = chain.invoke({'subject': content})

    return result.source


def test():
    output = _ask_ai(
        """You have received a PadMapper lead.


The following lead is interested in 1371 Harwood Stree: 1 Bed 1 Bath (https://post.spmailtechno.com/f/a/hbb92DJPoexyb_wQM8JXVA~~/AAPDZgA~/RgRoXzCvP0ReaHR0cHM6Ly93d3cucGFkbWFwcGVyLmNvbS9idWlsZGluZ3MvcDQ5MjE1My9hcGFydG1lbnRzLWF0LTEzNzEtaGFyd29vZC1zdC12YW5jb3V2ZXItYmMtdjZlLTFzNlcDc3BjQgpmda-rfGYfYQODUh1tZXRjYXAtNzc2NjVAbGlmdGluc2lnaHRzLmNvbVgEAAAAAA~~)
Meg Ryan
meg@megryan.ca (mailto:meg@megryan.ca)
(778) 838-3697 (tel:7788383697)
Hi,

I found your listing on PadMapper and I'm interested in coming to see it: https://www.padmapper.com/buildings/p492153/apartments-at-1371-harwood-st-vancouver-bc-v6e-1s6

Can you please let me know if it's still available, and when I might be able to view it?

Thanks"""
    )
    print(output)

    output = _ask_ai_source("Your lead from Kijiji")
    print(output)
