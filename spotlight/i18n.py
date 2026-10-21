"""i18n translations for SPOTLIGHT canonical answers.

Covers the 4 original beats (kids, movie, sports, news) in Spanish (es) and Hindi (hi).
Translations are static and human-written — no runtime translation API needed.
"""

from spotlight.models import AnswerPayload, BeatId

SUPPORTED_LANGS = ["en", "es", "hi"]

# beat_id -> lang -> field translations
TRANSLATIONS = {
    BeatId.KIDS: {
        "es": {
            "title": "Por qué el cielo es azul",
            "subtitle": "EXPLICACIÓN FAMILIAR PARA LEER EN VOZ ALTA",
            "verdict_badge": "LISTO PARA LEER EN VOZ ALTA",
            "primary_explanation": (
                "¡La luz del sol nos parece blanca, pero en secreto está hecha de todos "
                "los colores del arcoíris juntos! Cuando llega a la Tierra, las diminutas "
                "partículas del aire chocan con la luz azul y la esparcen por todo el cielo. "
                "Como la luz azul rebota más que los otros colores, el cielo entero brilla "
                "con ese hermoso manto azul."
            ),
            "key_details": [
                "La luz solar contiene todos los colores del arcoíris viajando juntos.",
                "La luz azul viaja en ondas cortas que rebotan fácilmente en el aire.",
                "Los científicos llaman a este rebote 'dispersión de Rayleigh'.",
            ],
        },
        "hi": {
            "title": "आसमान नीला क्यों है",
            "subtitle": "परिवार के साथ ज़ोर से पढ़ने हेतु",
            "verdict_badge": "पढ़ने के लिए तैयार",
            "primary_explanation": (
                "सूरज की रोशनी हमें सफ़ेद दिखती है, लेकिन असल में वह इंद्रधनुष के सभी "
                "रंगों से मिलकर बनी है! जब यह धरती पर पहुँचती है, तो हवा के छोटे-छोटे कण "
                "नीली रोशनी से टकराकर उसे पूरे आसमान में बिखेर देते हैं। क्योंकि नीली रोशनी "
                "बाकी रंगों से ज़्यादा उछलती है, पूरा आसमान खूबसूरत नीली चादर से चमक उठता है!"
            ),
            "key_details": [
                "सूरज की रोशनी में इंद्रधनुष के सभी रंग एक साथ यात्रा करते हैं।",
                "नीली रोशनी छोटी तरंगों में चलती है जो हवा में आसानी से उछलती हैं।",
                "वैज्ञानिक इस कोमल उछाल को 'रेले प्रकीर्णन' कहते हैं।",
            ],
        },
    },
    BeatId.MOVIE: {
        "es": {
            "title": "Tarjeta de actualización: Director Vance",
            "subtitle": "INTELIGENCIA DE PERSONAJES Y CONTEXTO",
            "verdict_badge": "ALERTA DE AGENTE REBELDE",
            "primary_explanation": (
                "Ese es el Director Vance, exjefe de la unidad encubierta de Operaciones "
                "Cibernéticas. Hace diez minutos, en los muelles, traicionó a su propio equipo "
                "y robó la llave maestra biométrica. La sala está furiosa porque las puertas "
                "acaban de iniciar un bloqueo total: sin el cifrado de Vance, todos quedarán "
                "atrapados en menos de 15 minutos."
            ),
            "key_details": [
                "Personaje: Director Vance (exjefe convertido en corredor del mercado negro).",
                "Contexto: dio coordenadas falsas a la agente Rossi a las 01:02:18.",
                "Apuesta inmediata: sin la llave física, la central se autopurga a las 01:30:00.",
            ],
        },
        "hi": {
            "title": "कैच-अप कार्ड: निदेशक वेंस",
            "subtitle": "पात्र जानकारी और समयरेखा संदर्भ",
            "verdict_badge": "दगाबाज़ एजेंट अलर्ट",
            "primary_explanation": (
                "यह निदेशक वेंस हैं, गुप्त साइबर ऑपरेशंस इकाई के पूर्व प्रमुख। दस मिनट पहले "
                "बंदरगाह पर उन्होंने अपनी ही टीम को धोखा दिया और बायोमेट्रिक मास्टर साइफर चुरा "
                "लिया। कमरा गुस्से में है क्योंकि दरवाज़ों ने अभी हार्ड लॉकआउट शुरू कर दिया है — "
                "वेंस के साइफर के बिना 15 मिनट में सभी अंदर फँस जाएँगे।"
            ),
            "key_details": [
                "पात्र: निदेशक वेंस (पूर्व डिवीजन प्रमुख, अब काला-बाज़ार दलाल)।",
                "संदर्भ: 01:02:18 पर एजेंट रॉसी को झूठे निर्देशांक दिए।",
                "तत्काल दांव: भौतिक कुंजी के बिना 01:30:00 पर बेस मेनफ्रेम स्वयं मिट जाएगा।",
            ],
        },
    },
    BeatId.SPORTS: {
        "es": {
            "title": "Decisión arbitral: Entrada temeraria",
            "subtitle": "REVISIÓN VAR Y REGLAS DEL JUEGO",
            "verdict_badge": "TIRO LIBRE DIRECTO + TARJETA AMARILLA",
            "primary_explanation": (
                "En el 74:12, el centrocampista defensor hizo una entrada deslizante tardía "
                "por detrás, con los tacos por delante, alcanzando el tobillo derecho del "
                "atacante antes de tocar el balón. El árbitro detuvo el juego de inmediato "
                "por poner en peligro la seguridad."
            ),
            "key_details": [
                "Regla oficial: Ley 12 de la IFAB — tiro libre directo por entrada temeraria o con fuerza excesiva.",
                "Sanción: tarjeta amarilla confirmada por la entrada imprudente.",
                "Análisis: cero contacto con el balón; la trayectoria atrapó la pierna de apoyo del rival.",
            ],
        },
        "hi": {
            "title": "रेफरी का फैसला: लापरवाह टैकल",
            "subtitle": "VAR और खेल नियम समीक्षा",
            "verdict_badge": "डायरेक्ट फ्री किक + पीला कार्ड",
            "primary_explanation": (
                "74:12 पर रक्षात्मक मिडफील्डर ने पीछे से देर से स्लाइडिंग टैकल किया, गेंद को "
                "छुए बिना हमलावर के दाहिने टखने पर स्टड्स से प्रहार किया। सुरक्षा को खतरे में "
                "डालने के कारण रेफरी ने तुरंत खेल रोक दिया।"
            ),
            "key_details": [
                "आधिकारिक नियम: IFAB नियम 12 — लापरवाह या अत्यधिक बल वाले टैकल पर डायरेक्ट फ्री किक।",
                "अनुशासनात्मक कार्रवाई: लापरवाह टैकल के लिए पीला कार्ड।",
                "रिप्ले विश्लेषण: गेंद से कोई संपर्क नहीं; विरोधी के पैर पर सीधा प्रहार।",
            ],
        },
    },
    BeatId.NEWS: {
        "es": {
            "title": "Verificación: Alunizaje del Apolo 11",
            "subtitle": "AUDITORÍA CIENTÍFICA IMPARCIAL",
            "verdict_badge": "VERIFICADO: VERDADERO",
            "primary_explanation": (
                "VERDADERO. El 20 de julio de 1969, la misión Apolo 11 aterrizó en el Mar de "
                "la Tranquilidad en la Luna. Neil Armstrong y Buzz Aldrin caminaron sobre la "
                "superficie lunar, instalaron reflectores láser que los observatorios aún usan, "
                "y trajeron 21.5 kilos de rocas lunares verificadas por instituciones de más de 40 países."
            ),
            "key_details": [
                "Evidencia directa: los reflectores láser del Apolo 11 siguen devolviendo pulsos a la Tierra.",
                "Artefactos físicos: 382 kg de material lunar analizado por geoquímicos de todo el mundo.",
                "Rastreo global: el observatorio Jodrell Bank (Reino Unido) confirmó la telemetría en tiempo real.",
            ],
        },
        "hi": {
            "title": "तथ्य-जाँच: अपोलो 11 का चंद्र अवतरण",
            "subtitle": "निष्पक्ष वैज्ञानिक ऑडिट",
            "verdict_badge": "सत्यापित: सत्य",
            "primary_explanation": (
                "सत्यापित सत्य। 20 जुलाई 1969 को अपोलो 11 मिशन चंद्रमा के शांति सागर में "
                "सफलतापूर्वक उतरा। नील आर्मस्ट्रांग और बज़ एल्ड्रिन चंद्र सतह पर चले, लेज़र "
                "परावर्तक स्थापित किए जो वेधशालाएँ आज भी उपयोग करती हैं, और 21.5 किलोग्राम "
                "चंद्र चट्टानें लाए जिनकी 40 से अधिक देशों के संस्थानों ने पुष्टि की।"
            ),
            "key_details": [
                "प्रत्यक्ष प्रमाण: अपोलो 11 के लेज़र परावर्तक आज भी पृथ्वी पर संकेत भेजते हैं।",
                "भौतिक अवशेष: 382 किलोग्राम चंद्र सामग्री का विश्व भर के वैज्ञानिकों ने विश्लेषण किया।",
                "वैश्विक निगरानी: जोड्रेल बैंक वेधशाला (यूके) ने रीयल-टाइम टेलीमेट्री की पुष्टि की।",
            ],
        },
    },
}


def translate_answer(answer: AnswerPayload, lang: str) -> AnswerPayload:
    """Return a copy of the answer with translated display fields.

    Only applies to canonical answers for beats with translations.
    Falls back to the original (English) for anything untranslated.
    """
    if lang == "en" or not answer.is_canonical:
        return answer
    beat_map = TRANSLATIONS.get(answer.beat_id)
    if not beat_map:
        return answer
    t = beat_map.get(lang)
    if not t:
        return answer
    data = answer.model_dump()
    for field in ("title", "subtitle", "verdict_badge", "primary_explanation", "key_details"):
        if field in t:
            data[field] = t[field]
    return AnswerPayload(**data)
