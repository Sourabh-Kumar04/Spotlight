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
            "title": "Cary Grant",
            "subtitle": "CHARADA (1963) — PETER JOSHUA",
            "verdict_badge": "PRIMER PLANO DEL ELENCO",
            "primary_explanation": (
                "Ese es el legendario galán de Hollywood Cary Grant interpretando a Peter Joshua "
                "en el clásico de intriga 'Charada' (1963). En la película, interpreta a un encantador "
                "desconocido que ayuda a Regina Lampert (Audrey Hepburn) en París tras el asesinato de su "
                "esposo, cambiando continuamente de alias —Peter Joshua, Alexander Dyle, Adam Canfield y "
                "Carson Dyle— antes de revelarse finalmente como el agente del Tesoro Brian Cruikshank."
            ),
            "key_details": [
                "Película y Director: Charada (1963), dirigida por Stanley Donen.",
                "Protagonista: Cary Grant como el misterioso hombre que asiste a Reggie (Audrey Hepburn).",
                "Giro de identidades: Peter Joshua, Alexander Dyle, Adam Canfield y finalmente Brian Cruikshank.",
                "Dominio público: Pasó al dominio público de inmediato por la omisión del aviso de copyright.",
            ],
        },
        "hi": {
            "title": "कैरी ग्रांट",
            "subtitle": "शराड (1963) — पीटर जोशुआ",
            "verdict_badge": "कास्ट स्पॉटलाइट",
            "primary_explanation": (
                "यह हॉलीवुड के दिग्गज अभिनेता कैरी ग्रांट हैं, जो 1963 की क्लासिक मिस्ट्री थ्रिलर 'शराड' में "
                "पीटर जोशुआ की भूमिका निभा रहे हैं। फिल्म में, वह पेरिस में रेजिना लैम्बर्ट (ऑड्रे हेपबर्न) की "
                "मदद करने वाले एक आकर्षक अजनबी का किरदार निभाते हैं, जो लगातार अपनी पहचान बदलते हैं (पीटर जोशुआ, "
                "अलेक्जेंडर डाइल, एडम कैनफील्ड, कार्सन डाइल) और अंततः अमेरिकी ट्रेजरी एजेंट ब्रायन क्रुइकशैंक साबित होते हैं।"
            ),
            "key_details": [
                "फिल्म और निर्देशक: शराड (1963), स्टेनली डोनेन द्वारा निर्देशित।",
                "मुख्य अभिनेता: कैरी ग्रांट, ऑड्रे हेपबर्न की मदद करने वाले रहस्यमयी अजनबी के रूप में।",
                "पहचान का मोड़: पीटर जोशुआ, अलेक्जेंडर डाइल, एडम कैनफील्ड और अंततः ब्रायन क्रुइकशैंक।",
                "पब्लिक डोमेन: कॉपीराइट नोटिस छूट जाने के कारण यह फिल्म रिलीज़ होते ही पब्लिक डोमेन में आ गई थी।",
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
