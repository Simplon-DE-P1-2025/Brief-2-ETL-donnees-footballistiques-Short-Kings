"""
Constantes pour le mapping des équipes de football.

Ce module centralise toutes les données de référence pour la normalisation
des noms d'équipes à travers les différents datasets de la Coupe du Monde.

Sources:
- FIFA World Ranking (github.com/cnc8/fifa-world-ranking)
- FIFA World Cup Archives
"""

# =============================================================================
# ÉQUIPES HISTORIQUES ET LEURS SUCCESSEURS FIFA
# Ces équipes n'existent plus dans le classement FIFA actuel
# Format: "Équipe dissoute": (année_dissolution, "successeur_FIFA", "confédération")
#
# NOTE: FRG (Allemagne de l'Ouest) n'est PAS dans cette liste car selon les règles
# FIFA/UEFA, la RFA est la continuité juridique de l'Allemagne actuelle.
# Les matchs de la RFA sont donc attribués à "Germany", pas à une entité séparée.
# Seule la RDA (GDR) reste une entité historique distincte.
# =============================================================================

HISTORICAL_TEAMS = {
    # Europe (UEFA)
    "Soviet Union": (1991, "Russia", "UEFA"),
    "Yugoslavia": (2003, "Serbia", "UEFA"),
    "Czechoslovakia": (1993, "Czech Republic", "UEFA"),
    "Serbia-Montenegro": (2006, "Serbia", "UEFA"),
    "GDR": (1990, "Germany", "UEFA"),  # Allemagne de l'Est - reste séparée
    "Saarland": (1956, "Germany", "UEFA"),  # Protectorat de la Sarre
    "Irish Free State": (1936, "Republic of Ireland", "UEFA"),

    # Afrique (CAF)
    "Zaire": (1997, "Congo DR", "CAF"),
    "Dahomey": (1975, "Benin", "CAF"),
    "Upper Volta": (1984, "Burkina Faso", "CAF"),
    "Rhodesia": (1980, "Zimbabwe", "CAF"),

    # Asie (AFC)
    "Dutch East Indies": (1945, "Indonesia", "AFC"),
    "North Yemen": (1990, "Yemen", "AFC"),
    "South Yemen": (1990, "Yemen", "AFC"),
    "South Vietnam": (1976, "Vietnam", "AFC"),

    # Amérique (CONCACAF / CONMEBOL)
    "Dutch Guyana": (1975, "Suriname", "CONMEBOL"),
    "Dutch Antilles": (2010, None, "CONCACAF"),  # Dissous, pas de successeur unique

    # Océanie (OFC)
    "Western Samoa": (1997, "Samoa", "OFC"),
}

# =============================================================================
# ÉQUIPES MANQUANTES DU CLASSEMENT FIFA 2020
# Ces équipes existent mais ne sont pas dans le fichier FIFA téléchargé
# (membres FIFA suspendus, équipes non classées, etc.)
# =============================================================================

ADDITIONAL_TEAMS = {
    # Océanie (OFC) - membres non classés en 2020
    "Cook Islands": "OFC",
    "Tuvalu": "OFC",  # ne peut pas participer à la coupe du monde mais membre associé de l'OFC
    "Tonga": "OFC",

    # Autres équipes potentiellement manquantes
    "Turks and Caicos": "CONCACAF",  # Turks and Caicos Islands
}

# =============================================================================
# PLACEHOLDERS À EXCLURE (pas des équipes réelles)
# Ces valeurs apparaissent dans les données brutes pour les matchs à venir
# ou les phases de poules non encore jouées
# =============================================================================

PLACEHOLDERS = {
    # Numéros de positions
    "1", "2", "3", "4", "5", "6", "7", "8",
    # Lettres de groupes
    "A", "B", "C", "D",
    # Identifiants de poules
    "A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2",
    "E1", "E2", "F1", "F2", "G1", "G2", "H1", "H2",
    # Marqueurs de progression
    "WINNER X", "WINNER Y", "LOSER X", "LOSER Y",
}

# =============================================================================
# MAPPING DES ALIASES VERS NOMS STANDARDS (NOMS FIFA)
# Chaque variante de nom est mappée explicitement vers le nom FIFA officiel
# Format : "nom_brut" -> "nom_standard_FIFA"
# =============================================================================

ALIASES_MAPPING = {
    # -------------------------------------------------------------------------
    # Corrections d'encodage (caractères corrompus)
    # -------------------------------------------------------------------------
    "C�te d'Ivoire": "Côte d'Ivoire",
    "Cï¿½te d'Ivoire": "Côte d'Ivoire",
    'rn">Bosnia and Herzegovina': "Bosnia and Herzegovina",
    '"rn"">Bosnia and Herzegovina"': "Bosnia and Herzegovina",

    # -------------------------------------------------------------------------
    # Variantes avec noms locaux (extraites du dataset 1930-2010)
    # Format original : "NomAnglais (NomLocal)" -> "Nom FIFA"
    # -------------------------------------------------------------------------
    "Afghanistan (افغانستان)": "Afghanistan",
    "Albania (Shqipëri)": "Albania",
    "Algeria (الجزائر)": "Algeria",
    "Armenia (Հdelays)": "Armenia",
    "Armenia (Հdelays)": "Armenia",
    "Austria (Österreich)": "Austria",
    "Azerbaijan (Azərbaycan)": "Azerbaijan",
    "Bahrain (البحرين)": "Bahrain",
    "Bangladesh (বাংলাদেশ)": "Bangladesh",
    "Belarus (Беларусь)": "Belarus",
    "Belgium (België)": "Belgium",
    "Benin (Bénin)": "Benin",
    "Bosnia-Herzegovina (Bosna i Hercegovina)": "Bosnia and Herzegovina",
    "Brazil (Brasil)": "Brazil",
    "Brunei (بروني)": "Brunei Darussalam",
    "Bulgaria (България)": "Bulgaria",
    "Cambodia (កម្ពុជា)": "Cambodia",
    "Cameroon (Cameroun)": "Cameroon",
    "Cape Verde (Cabo Verde)": "Cabo Verde",
    "Central African Republic (Centrafrique)": "Central African Republic",
    "Chad (Tchad / تشاد)": "Chad",
    "China (中国)": "China PR",
    "Comoros (جزر القمر)": "Comoros",
    "Croatia (Hrvatska)": "Croatia",
    "Cyprus (Κύπρος)": "Cyprus",
    "Czech Republic (Česká Republika)": "Czech Republic",
    "Czechoslovakia (Československo)": "Czechoslovakia",
    "D.R. Congo (R.D. Congo)": "Congo DR",
    "Denmark (Danmark)": "Denmark",
    "Djibouti (جيبوتي)": "Djibouti",
    "Dominican Republic (República Dominicana)": "Dominican Republic",
    "Dutch Antilles (Nederlandse Antillen)": "Dutch Antilles",
    "Dutch East Indies (Nederlands-Indië)": "Dutch East Indies",
    "Dutch Guyana (Nederlands Guyana)": "Dutch Guyana",
    "East Timor (Timor-Leste)": "Timor-Leste",
    "Egypt (مصر)": "Egypt",
    "Equatorial Guinea (Guinea Ecuatorial)": "Equatorial Guinea",
    "Eritrea (ኤርትራ / إرتريا)": "Eritrea",
    "Estonia (Eesti)": "Estonia",
    "Ethiopia (ኢትዮⵒያ)": "Ethiopia",
    "Ethiopia (ኢትዮⵒ)": "Ethiopia",
    "Ethiopia (ኢትዮጵያ)": "Ethiopia",

    # -------------------------------------------------------------------------
    # ALLEMAGNE - Règles FIFA/UEFA
    # FRG (RFA) est la continuité juridique de l'Allemagne actuelle
    # Tous les matchs de la RFA sont attribués à "Germany"
    # GDR (RDA) reste une entité historique distincte
    # -------------------------------------------------------------------------
    "FRG (BRD / Westdeutschland)": "Germany",
    "FRG": "Germany",
    "West Germany": "Germany",
    "Allemagne de l'Ouest": "Germany",
    "BRD": "Germany",
    "Westdeutschland": "Germany",
    "GDR (DDR / Ostdeutschland)": "GDR",
    "East Germany": "GDR",
    "Allemagne de l'Est": "GDR",
    "DDR": "GDR",
    "Ostdeutschland": "GDR",
    "Germany (Deutschland)": "Germany",

    "Faroe Islands (Føroyar)": "Faroe Islands",
    "Finland (Suomi)": "Finland",
    "Georgia (საქართველო)": "Georgia",
    "Greece (Ελλάδα)": "Greece",
    "Guinea (Guinée)": "Guinea",
    "Guinea-Bissau (Guiné-Bissau)": "Guinea-Bissau",
    "Haiti (Haïti)": "Haiti",
    "Hong Kong (香港)": "Hong Kong",
    "Hungary (Magyarország)": "Hungary",
    "Iceland (Ísland)": "Iceland",
    "India (भारत)": "India",
    "Iran (ایران)": "IR Iran",
    "Iraq (العراق)": "Iraq",
    "Ireland (Éire)": "Republic of Ireland",
    "Irish Free State (Saorstát Éireann)": "Irish Free State",
    "Israel (ישראל)": "Israel",
    "Italy (Italia)": "Italy",
    "Ivory Coast (Côte d'Ivoire)": "Côte d'Ivoire",
    "Japan (日本)": "Japan",
    "Jordan (الأردن)": "Jordan",
    "Kazakhstan (Қазақстан)": "Kazakhstan",
    "Kuwait (الكويت)": "Kuwait",
    "Kyrgyzstan (Кыргызстан)": "Kyrgyz Republic",
    "Laos (ນລາວ)": "Laos",
    "Latvia (Latvija)": "Latvia",
    "Lebanon (لبنان)": "Lebanon",
    "Libya (ليبيا)": "Libya",
    "Lithuania (Lietuva)": "Lithuania",
    "Luxembourg (Lëtzebuerg)": "Luxembourg",
    "Macao (澳门)": "Macau",
    "Macedonia (Македонија)": "North Macedonia",
    "Madagascar (Madagasikara)": "Madagascar",
    "Malawi (Malaŵi)": "Malawi",
    "Malaysia (مليسيا)": "Malaysia",
    "Maldives (Divehi Rājjēge)": "Maldives",
    "Mauritania (موريتانيا)": "Mauritania",
    "Mexico (México)": "Mexico",
    "Mongolia (Монгол Улс)": "Mongolia",
    "Montenegro (Црна Гора)": "Montenegro",
    "Morocco (المغرب)": "Morocco",
    "Mozambique (Moçambique)": "Mozambique",
    "Myanmar (ြမန်မာ)": "Myanmar",
    "Nepal (नेपाल)": "Nepal",
    "Netherlands (Nederland)": "Netherlands",
    "New Caledonia (Nouvelle-Calédonie)": "New Caledonia",
    "New Zealand (Aotearoa)": "New Zealand",
    "North Korea (조선)": "Korea DPR",
    "North Yemen (اليمن)": "North Yemen",
    "Northern Ireland (Ulster)": "Northern Ireland",
    "Norway (Norge)": "Norway",
    "Oman (عمان)": "Oman",
    "Pakistan (پاکستان)": "Pakistan",
    "Palestine (فلسطين)": "Palestine",
    "Panama (Panamá)": "Panama",
    "Papua New Guinea (Papua Niugini)": "Papua New Guinea",
    "Peru (Perú)": "Peru",
    "Philippines (Pilipinas)": "Philippines",
    "Poland (Polska)": "Poland",
    "Qatar (قطر)": "Qatar",
    "Romania (România)": "Romania",
    "Russia (Россия)": "Russia",
    "Saudi Arabia (العربية السعودية)": "Saudi Arabia",
    "Senegal (Sénégal)": "Senegal",
    "Serbia (Србија)": "Serbia",
    "Serbia-Montenegro (Србија и Црна Гора)": "Serbia-Montenegro",
    "Singapore (新加坡)": "Singapore",
    "Slovakia (Slovensko)": "Slovakia",
    "Slovenia (Slovenija)": "Slovenia",
    "Somalia (Soomaaliya)": "Somalia",
    "South Africa (Suid-Afrika)": "South Africa",
    "South Korea (한국)": "Korea Republic",
    "South Vietnam (Việt Nam)": "South Vietnam",
    "South Yemen (اليمن)": "South Yemen",
    "Soviet Union (СССР)": "Soviet Union",
    "Spain (España)": "Spain",
    "Sri Lanka (ශ්රී ලංකාව)": "Sri Lanka",
    "Sudan (السودان)": "Sudan",
    "Surinam (Suriname)": "Suriname",
    "Swaziland (Swatini)": "Swaziland",
    "Sweden (Sverige)": "Sweden",
    "Switzerland (Schweiz / Suisse)": "Switzerland",
    "Syria (سوريا)": "Syria",
    "Taiwan (台湾)": "Chinese Taipei",
    "Tajikistan (Точикистон)": "Tajikistan",
    "Thailand (ประเทศไทย)": "Thailand",
    "Tunisia (تونس)": "Tunisia",
    "Turkey (Türkiye)": "Turkey",
    "Turkmenistan (Türkmenistan)": "Turkmenistan",
    "Ukraine (Україна)": "Ukraine",
    "United Arab Emirates (الإمارات العربية المتحدة)": "United Arab Emirates",
    "Upper Volta (Haute-Volta)": "Upper Volta",
    "Uzbekistan (Ўзбекистон)": "Uzbekistan",
    "Vietnam (Việt Nam)": "Vietnam",
    "Wales (Cymru)": "Wales",
    "Yemen (اليمن)": "Yemen",
    "Yugoslavia (Југославија)": "Yugoslavia",
    "Zaire (Zaïre)": "Zaire",

    # -------------------------------------------------------------------------
    # Aliases spéciaux (noms alternatifs utilisés dans certains datasets)
    # -------------------------------------------------------------------------
    "IR Iran": "IR Iran",
    "Iran": "IR Iran",
    "Korea Republic": "Korea Republic",
    "South Korea": "Korea Republic",

    # -------------------------------------------------------------------------
    # Aliases manquants identifiés lors de la validation
    # -------------------------------------------------------------------------
    "Antigua": "Antigua and Barbuda",
    "Guayana": "Guyana",
    "Saint Kitts & Nevis": "St. Kitts and Nevis",
    "Saint Lucia": "St. Lucia",
    "Saint Vincent & The Grenadines": "St. Vincent / Grenadines",
    "São Tomé e Príncipe": "São Tomé and Príncipe",
    "United states": "USA",
    "Cote d'Ivoire": "Côte d'Ivoire",
    "Serbia and Montenegro": "Serbia-Montenegro",
    "KOREA REPUBLIC": "Korea Republic",
}

# Version lowercase pour recherche insensible à la casse
ALIASES_MAPPING_LOWER = {k.lower(): v for k, v in ALIASES_MAPPING.items()}
