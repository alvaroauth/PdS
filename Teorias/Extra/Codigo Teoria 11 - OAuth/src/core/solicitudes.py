"""Solicitudes en memoria: el foco de esta demo es el acceso, no la persistencia.

Se reinician al reiniciar el servidor. En el integrador vendrían del ORM.
"""

_SOLICITUDES = [
    {"id": 1, "servicio": "Pediatría", "fecha": "2026-10-20", "cantidad": 12, "estado": "pendiente"},
    {"id": 2, "servicio": "Consultorios", "fecha": "2026-10-21", "cantidad": 8, "estado": "pendiente"},
    {"id": 3, "servicio": "Pediatría", "fecha": "2026-10-22", "cantidad": 15, "estado": "aprobada"},
]


class SolicitudInexistente(Exception):
    pass


def listar():
    return _SOLICITUDES


def aprobar(solicitud_id):
    for solicitud in _SOLICITUDES:
        if solicitud["id"] == solicitud_id:
            solicitud["estado"] = "aprobada"
            return solicitud
    raise SolicitudInexistente()
