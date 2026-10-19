"""Reglas de negocio del hospital: las decide nuestra app, no el proveedor."""


def clave_identidad(usuario):
    """Identidad externa estable: (issuer, subject). El email puede cambiar."""
    return f"{usuario['iss']}|{usuario['sub']}"


def puede_aprobar(usuario, jefes_de_servicio):
    return clave_identidad(usuario) in jefes_de_servicio
