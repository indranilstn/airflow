from app.orm.models.service_requests import ServiceRequest, ServiceRequestType

_dag_map: dict = {
    ServiceRequestType.SCHEDULE_EMAIL_DELIVERY: 'some_dag_id',
}

def find_service(request: ServiceRequest) -> str|None:
    request_type = request.type
    return _dag_map.get(request_type)

