"""Catálogo oficial CIE-10 (Clasificación Internacional de Enfermedades, 10.ª revisión)
en español, optimizado para consulta clínica y recuperación léxica/semántica.
"""
from __future__ import annotations

# Catálogo exhaustivo de afecciones frecuentes en atención ambulatoria, emergencias y hospitalización
CATALOGO_CIE10 = [
    # Sistema Circulatorio
    {
        "codigo": "I10",
        "descripcion": "Hipertensión esencial (primaria)",
        "capitulo": "IX. Enfermedades del sistema circulatorio",
        "sinonimos": ["hta", "hipertension arterial", "presion alta", "crisis hipertensiva", "hipertension arterial esencial"],
    },
    {
        "codigo": "I20.9",
        "descripcion": "Angina de pecho, no especificada",
        "capitulo": "IX. Enfermedades del sistema circulatorio",
        "sinonimos": ["angina de pecho", "angina", "dolor precordial isquemico", "sindrome coronario"],
    },
    {
        "codigo": "I21.9",
        "descripcion": "Infarto agudo del miocardio, sin otra especificación",
        "capitulo": "IX. Enfermedades del sistema circulatorio",
        "sinonimos": ["iam", "infarto agudo de miocardio", "infarto", "ataque cardiaco", "necrosis miocardica"],
    },
    {
        "codigo": "I50.9",
        "descripcion": "Insuficiencia cardíaca, no especificada",
        "capitulo": "IX. Enfermedades del sistema circulatorio",
        "sinonimos": ["icc", "insuficiencia cardiaca congestiva", "falla cardiaca", "descompensacion cardiaca"],
    },
    {
        "codigo": "I64",
        "descripcion": "Accidente vascular encefálico agudo, no especificado como hemorrágico o isquémico",
        "capitulo": "IX. Enfermedades del sistema circulatorio",
        "sinonimos": ["acv", "evc", "ictus", "derrame cerebral", "isquemia cerebral", "accidente cerebrovascular"],
    },

    # Sistema Endocrino y Metabólico
    {
        "codigo": "E11.9",
        "descripcion": "Diabetes mellitus tipo 2, sin mención de complicación",
        "capitulo": "IV. Enfermedades endocrinas, nutricionales y metabólicas",
        "sinonimos": ["dm2", "diabetes mellitus tipo 2", "diabetes tipo ii", "dmnid", "diabetes del adulto", "hiperglicemia cronica"],
    },
    {
        "codigo": "E10.9",
        "descripcion": "Diabetes mellitus tipo 1, sin mención de complicación",
        "capitulo": "IV. Enfermedades endocrinas, nutricionales y metabólicas",
        "sinonimos": ["dm1", "diabetes mellitus tipo 1", "dmid", "diabetes juvenil", "diabetes insulinodependiente"],
    },
    {
        "codigo": "E03.9",
        "descripcion": "Hipotiroidismo, no especificado",
        "capitulo": "IV. Enfermedades endocrinas, nutricionales y metabólicas",
        "sinonimos": ["hipotiroidismo", "tiroides hipoactiva", "deficiencia tiroidea"],
    },
    {
        "codigo": "E66.9",
        "descripcion": "Obesidad, no especificada",
        "capitulo": "IV. Enfermedades endocrinas, nutricionales y metabólicas",
        "sinonimos": ["obesidad", "sobrepeso grado iii", "exceso ponderal severo"],
    },
    {
        "codigo": "E78.5",
        "descripcion": "Hiperlipidemia, no especificada",
        "capitulo": "IV. Enfermedades endocrinas, nutricionales y metabólicas",
        "sinonimos": ["dislipidemia", "hipercolesterolemia", "trigliceridos altos", "colesterol elevado"],
    },

    # Sistema Respiratorio
    {
        "codigo": "J00",
        "descripcion": "Rinofaringitis aguda [resfriado común]",
        "capitulo": "X. Enfermedades del sistema respiratorio",
        "sinonimos": ["resfriado comun", "catarro comun", "rinitis aguda", "gripe leve", "rinofaringitis"],
    },
    {
        "codigo": "J02.9",
        "descripcion": "Faringitis aguda, no especificada",
        "capitulo": "X. Enfermedades del sistema respiratorio",
        "sinonimos": ["faringitis", "odinofagia aguda", "dolor de garganta infeccioso", "faringoamigdalitis"],
    },
    {
        "codigo": "J06.9",
        "descripcion": "Infección aguda de las vías respiratorias superiores, no especificada",
        "capitulo": "X. Enfermedades del sistema respiratorio",
        "sinonimos": ["ira", "infeccion respiratoria alta", "infeccion de vias respiratorias superiores"],
    },
    {
        "codigo": "J18.9",
        "descripcion": "Neumonía, no especificada",
        "capitulo": "X. Enfermedades del sistema respiratorio",
        "sinonimos": ["neumonia", "nac", "neumonia adquirida en la comunidad", "infeccion pulmonar", "consolidacion pulmonar"],
    },
    {
        "codigo": "J20.9",
        "descripcion": "Bronquitis aguda, no especificada",
        "capitulo": "X. Enfermedades del sistema respiratorio",
        "sinonimos": ["bronquitis aguda", "cuadro bronquial agudo", "bronquitis"],
    },
    {
        "codigo": "J44.9",
        "descripcion": "Enfermedad pulmonar obstructiva crónica, no especificada",
        "capitulo": "X. Enfermedades del sistema respiratorio",
        "sinonimos": ["epoc", "enfermedad pulmonar obstructiva cronica", "enfisema", "bronquitis cronica"],
    },
    {
        "codigo": "J45.9",
        "descripcion": "Asma, no especificada",
        "capitulo": "X. Enfermedades del sistema respiratorio",
        "sinonimos": ["asma bronquial", "crisis asmatica", "broncoespasmo", "asma"],
    },

    # Sistema Digestivo
    {
        "codigo": "K29.7",
        "descripcion": "Gastritis, no especificada",
        "capitulo": "XI. Enfermedades del sistema digestivo",
        "sinonimos": ["gastritis", "dolor epigastrico", "epigastralgia", "gastropatia", "ardor estomacal"],
    },
    {
        "codigo": "K21.9",
        "descripcion": "Enfermedad del reflujo gastroesofágico sin esofagitis",
        "capitulo": "XI. Enfermedades del sistema digestivo",
        "sinonimos": ["erge", "reflujo gastroesofagico", "acidez estomacal", "pirosis"],
    },
    {
        "codigo": "K35.8",
        "descripcion": "Otras apendicitis agudas y las no especificadas",
        "capitulo": "XI. Enfermedades del sistema digestivo",
        "sinonimos": ["apendicitis aguda", "apendicitis", "cuadro apendicular", "fosa iliaca derecha dolor"],
    },
    {
        "codigo": "K80.2",
        "descripcion": "Cálculo de la vesícula biliar sin colecistitis",
        "capitulo": "XI. Enfermedades del sistema digestivo",
        "sinonimos": ["colelitiasis", "calculos biliares", "litiasis vesicular", "piedras en la vesicula"],
    },
    {
        "codigo": "K40.9",
        "descripcion": "Hernia inguinal unilateral o no especificada, sin obstrucción ni gangrena",
        "capitulo": "XI. Enfermedades del sistema digestivo",
        "sinonimos": ["hernia inguinal", "hernia de ingle", "defecto herniario inguinal"],
    },

    # Sistema Genitourinario
    {
        "codigo": "N39.0",
        "descripcion": "Infección del tracto urinario, sitio no especificado",
        "capitulo": "XIV. Enfermedades del sistema genitourinario",
        "sinonimos": ["itu", "ivu", "infeccion de vias urinarias", "cistitis", "disuria infecciosa", "bacteriuria"],
    },
    {
        "codigo": "N20.0",
        "descripcion": "Cálculo del riñón",
        "capitulo": "XIV. Enfermedades del sistema genitourinario",
        "sinonimos": ["litiasis renal", "nefrolitiasis", "calculos renales", "colico nefritico", "piedras en rinon"],
    },
    {
        "codigo": "N18.9",
        "descripcion": "Enfermedad renal crónica, no especificada",
        "capitulo": "XIV. Enfermedades del sistema genitourinario",
        "sinonimos": ["erc", "insuficiencia renal cronica", "falla renal cronica", "enfermedad renal"],
    },

    # Infecciosas y Parasitarias
    {
        "codigo": "A09",
        "descripcion": "Diarrea y gastroenteritis de presunto origen infeccioso",
        "capitulo": "I. Ciertas enfermedades infecciosas y parasitarias",
        "sinonimos": ["eda", "gastroenteritis aguda", "diarrea aguda", "enfermedad diarreica aguda", "gastroenterocolitis"],
    },
    {
        "codigo": "B34.9",
        "descripcion": "Infección viral, no especificada",
        "capitulo": "I. Ciertas enfermedades infecciosas y parasitarias",
        "sinonimos": ["sindrome viral", "virosis", "infeccion viral inespecifica", "cuadro viral agudo"],
    },

    # Osteomuscular y Tejido Conjuntivo
    {
        "codigo": "M54.5",
        "descripcion": "Lumbago no especificado",
        "capitulo": "XIII. Enfermedades del sistema osteomuscular y del tejido conjuntivo",
        "sinonimos": ["lumbalgia", "dolor lumbar", "lumbago", "lumbalgia mecanica", "dolor de espalda baja"],
    },
    {
        "codigo": "M19.9",
        "descripcion": "Artrosis, no especificada",
        "capitulo": "XIII. Enfermedades del sistema osteomuscular y del tejido conjuntivo",
        "sinonimos": ["osteoartritis", "artrosis", "desgaste articular", "gonartrosis", "coxartrosis"],
    },

    # Síntomas, Signos y Hallazgos Anormales (Capítulo XVIII)
    {
        "codigo": "R10.4",
        "descripcion": "Otros dolores abdominales y los no especificados",
        "capitulo": "XVIII. Síntomas, signos y hallazgos anormales clínicos y de laboratorio",
        "sinonimos": ["dolor abd", "dolor abdominal", "abdomen doloroso", "dolor de vientre", "malestar abdominal"],
    },
    {
        "codigo": "R50.9",
        "descripcion": "Fiebre, no especificada",
        "capitulo": "XVIII. Síntomas, signos y hallazgos anormales clínicos y de laboratorio",
        "sinonimos": ["fiebre", "sindrome febril", "alza termica", "pirexia", "temperatura elevada"],
    },
    {
        "codigo": "R51",
        "descripcion": "Cefalea",
        "capitulo": "XVIII. Síntomas, signos y hallazgos anormales clínicos y de laboratorio",
        "sinonimos": ["cefalea", "dolor de cabeza", "jaqueca", "migrana"],
    },
    {
        "codigo": "R05",
        "descripcion": "Tos",
        "capitulo": "XVIII. Síntomas, signos y hallazgos anormales clínicos y de laboratorio",
        "sinonimos": ["tos seca", "tos productiva", "acceso de tos", "tos persistente"],
    },
    {
        "codigo": "R07.4",
        "descripcion": "Dolor en el pecho, no especificado",
        "capitulo": "XVIII. Síntomas, signos y hallazgos anormales clínicos y de laboratorio",
        "sinonimos": ["dolor precordial", "dolor toracico", "toracodinia", "opresion toracica"],
    },
    {
        "codigo": "R53",
        "descripcion": "Malestar y fatiga",
        "capitulo": "XVIII. Síntomas, signos y hallazgos anormales clínicos y de laboratorio",
        "sinonimos": ["astenia", "adinamia", "fatiga", "malestar general", "debilidad"],
    },

    # Traumatismos y Causas Externas
    {
        "codigo": "T14.9",
        "descripcion": "Traumatismo, no especificado",
        "capitulo": "XIX. Traumatismos, envenenamientos y algunas otras consecuencias de causas externas",
        "sinonimos": ["trauma", "traumatismo", "contusion", "golpe directo", "politraumatismo leve"],
    },
]


def buscar_en_catalogo(codigo: str) -> dict | None:
    cod = codigo.strip().upper()
    for item in CATALOGO_CIE10:
        if item["codigo"].upper() == cod:
            return item
    return None
