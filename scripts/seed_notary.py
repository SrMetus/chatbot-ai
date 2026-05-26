"""Seed the faq_cache with the 20 most common notary Q&A for Chilean notaries.

Usage:
    python scripts/seed_notary.py <client_id>

This script will:
    1. Connect to the database
    2. Generate embeddings for each question using the local model
    3. Insert/update FAQ entries for the given client
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.faq_cache import FaqCache
from app.models.client import Client
from app.core.embeddings import generate_embedding

FAQ_DATA = [
    {
        "question": "Cuanto cuesta una escritura publica",
        "answer": (
            "El costo de una escritura pública varía según el monto de la operación. "
            "Para propiedades sobre 1.000 UF, el arancel es de aproximadamente 0,2% del valor. "
            "Escrituras simples como poderes o certificados tienen un costo fijo de $20.000 a $50.000 CLP."
        ),
    },
    {
        "question": "Que documentos necesito para hacer una compraventa de propiedad",
        "answer": (
            "Para una compraventa de propiedad necesitas: cédula de identidad vigente, "
            "certificado de dominio vigente (emitido por el Conservador, máximo 30 días), "
            "certificado de hipotecas y gravámenes, rol de avalúo fiscal, "
            "y el comprobante de pago de contribuciones del año en curso."
        ),
    },
    {
        "question": "Cual es el horario de atencion de la notaria",
        "answer": (
            "Nuestro horario de atención es de lunes a viernes de 09:00 a 18:00 horas, "
            "y sábados de 10:00 a 13:00 horas. La notaría permanece cerrada los días "
            "festivos y feriados irremplazables."
        ),
    },
    {
        "question": "Donde esta ubicada la notaria",
        "answer": (
            "Nuestra notaría está ubicada en calle Prat 456, oficina 302, "
            "Valparaíso. Estamos a media cuadra de la Plaza Sotomayor, "
            "con estacionamiento de pago en el edificio."
        ),
    },
    {
        "question": "Como puedo hacer un poder notarial",
        "answer": (
            "Para hacer un poder notarial debes asistir personalmente a la notaría "
            "con tu cédula de identidad vigente. El poder puede ser simple (sin facultades "
            "especiales) o amplio (con facultades de administración y disposición). "
            "El costo aproximado es de $15.000 a $30.000 CLP según el tipo."
        ),
    },
    {
        "question": "Cuanto tiempo demora una escritura",
        "answer": (
            "Una escritura pública simple se puede otorgar el mismo día si todos los "
            "documentos están en orden. Escrituras complejas (compraventas, hipotecas) "
            "pueden demorar de 2 a 5 días hábiles por la revisión de antecedentes."
        ),
    },
    {
        "question": "Que servicios ofrece la notaria",
        "answer": (
            "Ofrecemos: escrituras públicas, poderes notariales, certificados (vigencia, "
            "supervivencia), legalización de documentos, protocolización de instrumentos, "
            "contratos de arrendamiento, constitución de sociedades, "
            "matrimonios civiles y autenticación de firmas."
        ),
    },
    {
        "question": "Necesito visa para firmar una escritura",
        "answer": (
            "No necesitas visa. Solo debes presentar tu cédula de identidad vigente. "
            "Para extranjeros, se acepta el pasaporte vigente o el DNI para ciudadanos "
            "de países del Mercosur. En algunos casos se requiere el RUT provisorio."
        ),
    },
    {
        "question": "Cuanto cuesta un certificado de vigencia",
        "answer": (
            "El certificado de vigencia de firma tiene un costo de $5.000 CLP. "
            "El certificado de vigencia de escritura cuesta aproximadamente $8.000 CLP. "
            "Ambos se emiten el mismo día."
        ),
    },
    {
        "question": "Como legalizar un documento",
        "answer": (
            "Para legalizar un documento debes: 1) Firmar ante el notario, "
            "2) El notario certifica tu identidad y la fecha de firma, "
            "3) Si es para uso en el extranjero, puede requerir Apostilla de La Haya. "
            "El costo de legalización es de aproximadamente $10.000 CLP por documento."
        ),
    },
    {
        "question": "Que es la apostilla de la Haya",
        "answer": (
            "La Apostilla de la Haya es un certificado que autentica documentos "
            "públicos para uso en países miembros del Convenio de La Haya. "
            "Chile es parte del convenio desde 2016. Se tramita en la notaría "
            "o en el Ministerio de Relaciones Exteriores."
        ),
    },
    {
        "question": "Como constituir una sociedad en la notaria",
        "answer": (
            "Para constituir una sociedad necesitas: cédula de identidad de todos los socios, "
            "definir el tipo social (SpA, EIRL, Ltda.), el capital aportado, "
            "el giro comercial y el domicilio. La escritura de constitución tiene un costo "
            "aproximado de $150.000 a $300.000 CLP según la complejidad."
        ),
    },
    {
        "question": "Puedo firmar una escritura si estoy fuera del pais",
        "answer": (
            "Sí, puedes firmar a través de un poder especial otorgado ante un "
            "cónsul chileno o ante notario del país donde te encuentres, con la "
            "apostilla correspondiente. También es posible mediante firma electrónica "
            "avanzada si el sistema lo permite."
        ),
    },
    {
        "question": "Que necesito para casarme por lo civil en la notaria",
        "answer": (
            "Para el matrimonio civil necesitas: cédula de identidad vigente de ambos "
            "contrayentes, certificado de nacimiento, declaración de testigos (2 por cada uno), "
            "y el pago de la hora notarial. El costo total es de aproximadamente $100.000 CLP "
            "e incluye la ceremonia y el certificado de matrimonio."
        ),
    },
    {
        "question": "Cuanto cuesta una hipoteca",
        "answer": (
            "La escritura de hipoteca tiene un costo que varía entre 0,1% y 0,3% "
            "del monto hipotecado, más un cargo fijo de $30.000 CLP por gastos "
            "administrativos. Se requiere la tasación del inmueble y el certificado "
            "de dominio vigente."
        ),
    },
    {
        "question": "Como tramitar una herencia en la notaria",
        "answer": (
            "Para tramitar una herencia necesitas: certificado de defunción, "
            "certificado de dominio de los bienes del causante, certificado de "
            "matrimonio o nacimiento según corresponda, y cédula de identidad "
            "de todos los herederos. La escritura de posesión efectiva demora "
            "aproximadamente 15 a 30 días."
        ),
    },
    {
        "question": "Que es la protocolizacion de documentos",
        "answer": (
            "La protocolización es el proceso mediante el cual se incorpora un "
            "documento al protocolo del notario, dándole fecha cierta y carácter "
            "de instrumento público. Se usa para contratos privados, sentencias "
            "judiciales y actas de asamblea. El costo varía según la extensión."
        ),
    },
    {
        "question": "Como autenticar una firma",
        "answer": (
            "Para autenticar una firma debes presentarte personalmente en la notaría "
            "con tu cédula de identidad vigente. El notario verificará tu identidad "
            "y estampará un sello de autenticación. El costo es de $3.000 a $5.000 "
            "CLP por firma. No es necesario que el documento esté en papel de la notaría."
        ),
    },
    {
        "question": "Que es el certificado de dominio vigente",
        "answer": (
            "El certificado de dominio vigente es un documento emitido por el "
            "Conservador de Bienes Raíces que acredita quién es el dueño actual "
            "de una propiedad. Tiene una vigencia de 30 días hábiles y es "
            "requisito indispensable para toda compraventa o hipoteca. "
            "Su costo es de aproximadamente $8.000 a $15.000 CLP."
        ),
    },
    {
        "question": "Puedo hacer tramites sin cita previa",
        "answer": (
            "Sí, puedes asistir sin cita previa en nuestro horario de atención. "
            "Sin embargo, para escrituras complejas como compraventas o constituciones "
            "de sociedad, recomendamos agendar una cita para asegurar disponibilidad "
            "del notario y agilizar el proceso."
        ),
    },
]


def seed_faqs(client_id: int) -> int:
    session = SessionLocal()

    client = session.query(Client).filter(Client.id == client_id).first()
    if not client:
        print(f"Error: Client with id {client_id} not found.")
        session.close()
        sys.exit(1)

    count = 0
    for item in FAQ_DATA:
        question = item["question"]
        answer = item["answer"]

        embedding = generate_embedding(question)

        existing = (
            session.query(FaqCache)
            .filter(
                FaqCache.client_id == client_id,
                FaqCache.question.ilike(question),
            )
            .first()
        )

        if existing:
            existing.answer = answer
            existing.embedding = embedding
        else:
            faq = FaqCache(
                client_id=client_id,
                question=question,
                answer=answer,
                embedding=embedding,
            )
            session.add(faq)

        count += 1

    session.commit()
    session.close()
    return count


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/seed_notary.py <client_id>")
        sys.exit(1)

    client_id = int(sys.argv[1])
    total = seed_faqs(client_id)
    print(f"Seeded {total} FAQ entries for client {client_id}.")
