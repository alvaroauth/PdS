from src.core import board
from src.core import auth


def run():
    issue1 = board.create_issue(
        email="jose@mail.com",
        title="Mi computadora no funciona.",
        description="Mi departamente me compró una nueva computadora y necesito configurarla con todos mis emails y documentos de mi vieja computadora.",
        status="new",
    )
    issue2 = board.create_issue(
        email="maria@mail.com",
        title="No puedo obtener mis emails.",
        description="Estoy tratando de acceder a mi correo desde casa, pero no puedo obtenerlos. Estoy tratando con Outlook en mi casa pero en la oficina tengo Thunderbird.",
        status="in_progress",
    )
    issue3 = board.create_issue(
        email="ruben@mail.com",
        title="No puedo imprimir",
        description="Cada vez que trato de imprimir mi presentación el programa se cierra. Esto sólo me pasa con PowerPoint en Word puedo imprimir. Ya me aseguré que la impresora está prendida. Tengo una HP LaserJet 5.",
        status="done",
    )

    label1 = board.create_label(
        title="Urgente",
        description="Issues que tienen que resolverse dentro de 24hs",
    )
    label2 = board.create_label(
        title="Importante",
        description="Issues de alta prioridad",
    )
    label3 = board.create_label(
        title="Soporte",
        description="Issues relacionados con soporte técnico",
    )
    label4 = board.create_label(
        title="Ventas",
        description="Issues relacionado con el área de ventas",
    )

    fede = auth.create_user(email="fede@mail.com", password="1234")
    agus = auth.create_user(email="agus@mail.com", password="1234")
    miguel = auth.create_user(email="miguel@mail.com", password="1234")

    board.assign(issue1, fede)
    board.assign(issue2, agus)
    board.assign(issue3, miguel)

    board.assing_labels(issue1, [label1, label2])
    board.assing_labels(issue2, [label3, label4])
    board.assing_labels(issue3, [label1, label4])

    m1 = board.create_musician(
        name="Pappo",
        description="Norberto Aníbal Napolitano (La Paternal, Buenos Aires; 10 de marzo de 1950 - Luján, Buenos Aires; 25 de febrero de 2005), popularmente conocido como Pappo, fue un músico, guitarrista, cantante y compositor argentino.",
    )
    m2 = board.create_musician(
        name="Luca",
        description="Luca George Prodan (Roma, 17 de mayo de 1953 – Buenos Aires, 22 de diciembre de 1987) fue un músico ítalo-escocés quien a comienzos de los años ochenta se radicó en Argentina, donde formó el grupo de rock Sumo.",
    )
    m3 = board.create_musician(
        name="Spinetta",
        description="Luis Alberto Spinetta (Buenos Aires, 23 de enero de 1950 - Ibídem, 8 de febrero de 2012), conocido como El Flaco o simplemente por su apellido, fue un multifacético artista argentino, cantante, guitarrista, poeta, escritor, filósofo, artista plástico, dibujante y compositor, considerado uno de los más importantes y respetados músicos en Hispanoamérica.",
    )
    m4 = board.create_musician(
        name="Mollo",
        description="Ricardo Jorge Mollo (Pergamino, Buenos Aires; 17 de agosto de 1957) es un músico argentino conocido por formar parte de dos bandas del movimiento de rock argentino: fue guitarrista de Sumo en los años 1980 y actualmente es el guitarrista, vocalista y líder de Divididos.\n\nEs considerado uno de los mejores músicos y compositores del rock argentino. Se destaca también por sus virtuosismo con la guitarra, donde es particularmente conocido por su versión del solo de «Voodoo Child» de Jimi Hendrix, que ha interpretado con su guitarra usando sus dientes o algún objeto arrojado por el público como por ejemplo: zanahorias, zapatillas, ojotas, pelotas de tenis, o bastones para ciegos. Es reconocido también por un trato amistoso y personal hacia su público.[cita requerida]\n\nEn la edición argentina de la revista Rolling Stone del mes de septiembre de 2012, Ricardo Mollo ocupó la segunda posición en el ranking de Los cien mejores guitarristas del rock argentino, después de Pappo y antes de David Lebón.",
    )
    m5 = board.create_musician(
        name="xss",
        description="Acá hay un XSS guardado en la DB <script>alert(\"XSS!!! \"+document.cookie)</script>",
    )
    m6 = board.create_musician(
        name="Dillom",
        description="Dylan León Masa (Balvanera, 5 de diciembre de 2000), más conocido por su nombre artístico Dillom, es un rapero, compositor y productor discográfico argentino.\nEn 2018 saltó a la fama con su canción \"Drippin\", la cual él mismo produjo, a la que siguieron \"Superglue\", junto al músico Ill Quentín, y su sesión con Bizarrap. Es considerado uno de los referentes del nuevo trap argentino. En 2021, lanzó su álbum debut Post mortem, nominado a Mejor álbum de música urbana en los Premios Carlos Gardel.",
    )
    m7 = board.create_musician(
        name="Wos",
        description="Valentín Oliva (Buenos Aires, 23 de enero de 1998), conocido artísticamente como WOS (estilizado como WOS o WOS DS3), es un rapero, freestyler, cantante y actor argentino.\r\n\r\nSurgió en la escena de las batallas de rap entre freestylers, y fue campeón en varias ocasiones de la competencia argentina El Quinto Escalón, que lo impulsó a ser uno de los artistas urbanos más reconocidos del país. Además fue campeón de la FMS Argentina 2018 y del torneo internacional de Red Bull Batalla de los Gallos 2018, al vencer al rapero Aczino en Buenos Aires, tras haber sido subcampeón la edición pasada frente al mismo en México.\r\n\r\nTras su éxito en las batallas de rap, decidió iniciar su carrera musical. En 2018 lanzó su primer sencillo, \"Púrpura\", un trap agresivo. En 2019 lanzó su primer álbum de estudio, Caravana, cuyo sencillo de presentación, \"Canguro\", se colocó entre los 10 primeros puestos de las listas argentinas por varias semanas, y gracias al cual logró ganar tres Premios Gardel por mejor nuevo artista, mejor álbum/canción urbana y canción del año. También logró ser nominado para los premios Latin Grammy, por mejor nuevo artista. En 2020, sacó el EP Tres puntos suspensivos. En 2021, lanzó su segundo álbum de estudio, Oscuro éxtasis.",
    )