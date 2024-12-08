from sqlalchemy.orm import Session
from db.models import Service


def add_service(service_name: str, session: Session) -> bool:
    existing_service = session.query(Service).filter_by(name=service_name).first()
    if existing_service:
        return False
    new_service = Service(name=service_name)
    session.add(new_service)
    session.commit()
    return True



def delete_service(service_name: str, session: Session) -> bool:
    """Видаляє послугу з бази даних. Повертає True, якщо успішно."""
    service = session.query(Service).filter_by(name=service_name).first()
    if not service:
        return False
    session.delete(service)
    session.commit()
    return True


def get_all_services(session: Session) -> list[str]:
    """Повертає список усіх послуг."""
    services = session.query(Service).all()
    return [service.name for service in services]
