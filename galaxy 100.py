import math
import requests
import webbrowser
from urllib.parse import quote

print("==========================================")
print("             GALAXY 100")
print("       ASTRONOMICAL EXPLORER")
print("==========================================")

email = input("Please enter your email for login: ")
input("Please enter your password: ")

print("\nLogin successful!")


# ==========================================================
# SIMBAD FUNCTION
# ==========================================================

def search_simbad(object_name):

    print("\n==========================================")
    print("          SEARCHING SIMBAD...")
    print("==========================================")

    url = "https://simbad.cds.unistra.fr/simbad/sim-script"

    script = f"""
output console=off script=off
format object galaxy100 "%IDLIST(1)\\n%OTYPE(V)\\n%COO(A D;ICRS;J2000)\\n%COO(A D;GAL)\\n%SP\\n%PLX\\n%PM(A|D)\\n%RV\\n%Z\\n%FLUXLIST(U;B;V;R;I;J;H;K)"
query id {object_name}
"""

    try:

        response = requests.get(
            url,
            params={"script": script},
            timeout=15
        )

        if response.status_code != 200:

            print("\nSIMBAD request failed.")
            print("Status code:", response.status_code)
            return


        result = response.text.strip()


        # --------------------------------------------------
        # CHECK FOR NO RESULT
        # --------------------------------------------------

        if not result:

            print("\nSorry!")
            print("SIMBAD could not find this object.")
            return


        # --------------------------------------------------
        # REMOVE EMPTY LINES
        # --------------------------------------------------

        lines = []

        for line in result.splitlines():

            line = line.strip()

            if line:
                lines.append(line)


        # --------------------------------------------------
        # SOMETIMES SIMBAD RETURNS ERROR INFORMATION
        # --------------------------------------------------

        for line in lines:

            lower_line = line.lower()

            if "error" in lower_line and len(lines) <= 5:

                print("\nSIMBAD could not process this search.")
                print(line)

                return


        # --------------------------------------------------
        # PARSE THE RESULT
        # --------------------------------------------------

        object_id = "Not available"
        object_type = "Not available"
        coordinates = "Not available"
        galactic_coordinates = "Not available"
        spectral_type = "Not available"
        parallax = "Not available"
        proper_motion = "Not available"
        radial_velocity = "Not available"
        redshift = "Not available"

        magnitudes = {
            "U": "Not available",
            "B": "Not available",
            "V": "Not available",
            "R": "Not available",
            "I": "Not available",
            "J": "Not available",
            "H": "Not available",
            "K": "Not available"
        }


        # --------------------------------------------------
        # FIRST NINE MAIN FIELDS
        # --------------------------------------------------

        if len(lines) >= 1:
            object_id = lines[0]

        if len(lines) >= 2:
            object_type = lines[1]

        if len(lines) >= 3:
            coordinates = lines[2]

        if len(lines) >= 4:
            galactic_coordinates = lines[3]

        if len(lines) >= 5:
            spectral_type = lines[4]

        if len(lines) >= 6:
            parallax = lines[5]

        if len(lines) >= 7:
            proper_motion = lines[6]

        if len(lines) >= 8:
            radial_velocity = lines[7]

        if len(lines) >= 9:
            redshift = lines[8]


        # --------------------------------------------------
        # PHOTOMETRY
        # --------------------------------------------------

        for line in lines[9:]:

            parts = line.split()

            if len(parts) >= 2:

                filter_name = parts[0]

                if filter_name in magnitudes:

                    magnitudes[filter_name] = " ".join(parts[1:])


        # --------------------------------------------------
        # FRIENDLY USER INTERFACE
        # --------------------------------------------------

        print("\n==========================================")
        print("           SIMBAD SEARCH RESULT")
        print("==========================================")


        print("\n[ OBJECT IDENTIFICATION ]")
        print("------------------------------------------")

        print(f"{'Object':22}: {object_name}")
        print(f"{'Identifier':22}: {object_id}")
        print(f"{'Object type':22}: {object_type}")


        print("\n[ POSITION ]")
        print("------------------------------------------")

        print(f"{'RA / Dec':22}: {coordinates}")

        print(f"{'Galactic coordinates':22}: {galactic_coordinates}")


        print("\n[ STELLAR INFORMATION ]")
        print("------------------------------------------")

        print(f"{'Spectral type':22}: {spectral_type}")


        print("\n[ DISTANCE & MOTION ]")
        print("------------------------------------------")

        print(f"{'Parallax':22}: {parallax} mas")

        print(f"{'Proper motion':22}: {proper_motion}")

        print(f"{'Radial velocity':22}: {radial_velocity} km/s")

        print(f"{'Redshift':22}: {redshift}")


        print("\n[ MAGNITUDES / PHOTOMETRY ]")
        print("------------------------------------------")

        print(f"{'U':>22}: {magnitudes['U']}")
        print(f"{'B':>22}: {magnitudes['B']}")
        print(f"{'V':>22}: {magnitudes['V']}")
        print(f"{'R':>22}: {magnitudes['R']}")
        print(f"{'I':>22}: {magnitudes['I']}")
        print(f"{'J':>22}: {magnitudes['J']}")
        print(f"{'H':>22}: {magnitudes['H']}")
        print(f"{'K':>22}: {magnitudes['K']}")


        print("\n==========================================")
        print("DATA SOURCE")
        print("==========================================")

        print("SIMBAD Astronomical Database")
        print("Operated at CDS, Strasbourg, France")

        print("==========================================")


    except requests.exceptions.RequestException:

        print("\nCould not connect to SIMBAD.")
        print("Please check your internet connection.")


# ==========================================================
# NASA EXOPLANET ARCHIVE FUNCTION
# ==========================================================

def search_exoplanet(planet_name):

    print("\n==========================================")
    print("       SEARCHING EXOPLANET ARCHIVE")
    print("==========================================")

    url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"

    # Escape apostrophes so the object name stays inside the query string.
    safe_name = planet_name.strip().replace("'", "''")

    query = (
        "select pl_name, hostname, discoverymethod, disc_year, "
        "pl_rade, pl_bmasse, pl_bmassj, pl_orbper, pl_orbsmax, "
        "pl_eqt, sy_dist "
        "from pscomppars "
        f"where lower(pl_name) = lower('{safe_name}')"
    )

    try:

        response = requests.get(
            url,
            params={"query": query, "format": "json"},
            timeout=20
        )

        response.raise_for_status()
        data = response.json()

        if not data:

            print("\nNo exact match was found in the NASA Exoplanet Archive.")
            print("Check the planet name and try again.")
            return

        planet = data[0]

        def show_value(label, key, unit=""):
            value = planet.get(key)
            if value is None or value == "":
                value = "Not available in the archive"
            elif unit:
                value = f"{value} {unit}"
            print(f"{label:24}: {value}")

        print("\n==========================================")
        print("       EXOPLANET SEARCH RESULT")
        print("==========================================")
        show_value("Planet name", "pl_name")
        show_value("Host star", "hostname")
        show_value("Discovery method", "discoverymethod")
        show_value("Discovery year", "disc_year")
        print("\n[ PLANETARY PARAMETERS ]")
        print("------------------------------------------")
        show_value("Radius", "pl_rade", "Earth radii")
        show_value("Mass", "pl_bmasse", "Earth masses")
        show_value("Mass", "pl_bmassj", "Jupiter masses")
        show_value("Orbital period", "pl_orbper", "days")
        show_value("Orbital distance", "pl_orbsmax", "AU")
        show_value("Equilibrium temperature", "pl_eqt", "K")
        show_value("Distance from Earth", "sy_dist", "parsecs")

        print("\n==========================================")
        print("DATA SOURCE")
        print("==========================================")
        print("NASA Exoplanet Archive")
        print("California Institute of Technology (Caltech)")
        print("NASA Exoplanet Exploration Program")
        print("Table: Planetary Systems Composite Parameters (pscomppars)")
        print("==========================================")

    except requests.exceptions.RequestException as error:

        print("\nCould not connect to the NASA Exoplanet Archive.")
        print("Please check your internet connection and try again.")
        print("Details:", error)

    except (ValueError, TypeError, KeyError) as error:

        print("\nThe archive returned data that could not be processed.")
        print("Details:", error)


# ==========================================================
# NASA/JPL HORIZONS MOON SEARCH FUNCTION
# ==========================================================

def search_moon(moon_name):

    print("\n==========================================")
    print("      SEARCHING SOLAR SYSTEM MOONS")
    print("==========================================")

    url = "https://ssd.jpl.nasa.gov/api/horizons_lookup.api"

    # Known parent planets for common moons.
    # The API confirms whether the requested name is recognized by Horizons.
    parent_planets = {
        "moon": "Earth",
        "earth's moon": "Earth",
        "earths moon": "Earth",
        "luna": "Earth",
        "phobos": "Mars",
        "deimos": "Mars",
        "io": "Jupiter",
        "europa": "Jupiter",
        "ganymede": "Jupiter",
        "callisto": "Jupiter",
        "amalthea": "Jupiter",
        "titan": "Saturn",
        "enceladus": "Saturn",
        "rhea": "Saturn",
        "iapetus": "Saturn",
        "dione": "Saturn",
        "tethys": "Saturn",
        "mimas": "Saturn",
        "triton": "Neptune",
        "nereid": "Neptune",
        "proteus": "Neptune",
        "charon": "Pluto",
        "styx": "Pluto",
        "nix": "Pluto",
        "kerberos": "Pluto",
        "hydra": "Pluto",
        "miranda": "Uranus",
        "ariel": "Uranus",
        "umbriel": "Uranus",
        "titania": "Uranus",
        "oberon": "Uranus"
    }

    try:

        response = requests.get(
            url,
            params={"sstr": moon_name.strip(), "group": "sat"},
            timeout=15
        )

        response.raise_for_status()
        data = response.json()

        results = data.get("result", [])

        if not results:

            print("\nSorry! NASA/JPL Horizons did not find a matching natural satellite.")
            print("Try a recognized moon name, such as Europa, Titan, Ganymede, or Phobos.")
            print("A missing result does not prove that the object is not a moon;")
            print("it means this lookup did not return a match.")
            return

        print("\n==========================================")
        print("          MOON SEARCH RESULT")
        print("==========================================")

        for index, moon in enumerate(results, start=1):

            found_name = moon.get("name", "Not available")
            object_type = moon.get("type", "Not available")
            spkid = moon.get("spkid", "Not available")
            aliases = moon.get("alias", [])

            print(f"\nResult {index}")
            print("------------------------------------------")
            print(f"{'Moon / object name':24}: {found_name}")
            print(f"{'Object type':24}: {object_type}")
            print(f"{'Horizons SPK ID':24}: {spkid}")

            parent_planet = parent_planets.get(moon_name.strip().lower())
            if parent_planet:
                print(f"{'Parent planet':24}: {parent_planet}")
            else:
                print(f"{'Parent planet':24}: Not provided by this lookup")

            if aliases:
                print(f"{'Other identifiers':24}: {', '.join(str(alias) for alias in aliases)}")
            else:
                print(f"{'Other identifiers':24}: None listed")

        print("\n==========================================")
        print("DATA SOURCE")
        print("==========================================")
        print("NASA/JPL Horizons Lookup API")
        print("NASA Jet Propulsion Laboratory (JPL)")
        print("Search restricted to natural satellites (group=sat)")
        print("Note: this lookup provides object identification, not a complete physical-data catalogue.")
        print("==========================================")

    except requests.exceptions.RequestException as error:

        print("\nCould not connect to NASA/JPL Horizons.")
        print("Please check your internet connection and try again.")
        print("Details:", error)

    except (ValueError, TypeError, KeyError) as error:

        print("\nNASA/JPL Horizons returned data that could not be processed.")
        print("Details:", error)
# ==========================================================
# CONSTELLATION IMAGES
# ==========================================================



IAU_CODES = {
    "andromeda": "And", "antlia": "Ant", "apus": "Aps", "aquarius": "Aqr",
    "aquila": "Aql", "ara": "Ara", "aries": "Ari", "auriga": "Aur",
    "bootes": "Boo", "caelum": "Cae", "camelopardalis": "Cam", "cancer": "Cnc",
    "canesvenatici": "CVn", "canismajor": "CMa", "canisminor": "CMi",
    "capricornus": "Cap", "carina": "Car", "cassiopeia": "Cas",
    "centaurus": "Cen", "cepheus": "Cep", "cetus": "Cet", "chamaeleon": "Cha",
    "circinus": "Cir", "columba": "Col", "comaberenices": "Com",
    "coronaaustralis": "CrA", "coronaborealis": "CrB", "corvus": "Crv",
    "crater": "Crt", "crux": "Cru", "cygnus": "Cyg", "delphinus": "Del",
    "dorado": "Dor", "draco": "Dra", "equuleus": "Equ", "eridanus": "Eri",
    "fornax": "For", "gemini": "Gem", "grus": "Gru", "hercules": "Her",
    "horologium": "Hor", "hydra": "Hya", "hydrus": "Hyi", "indus": "Ind",
    "lacerta": "Lac", "leo": "Leo", "leominor": "LMi", "lepus": "Lep",
    "libra": "Lib", "lupus": "Lup", "lynx": "Lyn", "lyra": "Lyr",
    "mensa": "Men", "microscopium": "Mic", "monoceros": "Mon", "musca": "Mus",
    "norma": "Nor", "octans": "Oct", "ophiuchus": "Oph", "orion": "Ori",
    "pavo": "Pav", "pegasus": "Peg", "perseus": "Per", "phoenix": "Phe",
    "pictor": "Pic", "pisces": "Psc", "piscisaustrinus": "PsA",
    "puppis": "Pup", "pyxis": "Pyx", "reticulum": "Ret", "sagitta": "Sge",
    "sagittarius": "Sgr", "scorpius": "Sco", "sculptor": "Scl", "scutum": "Sct",
    "serpens": "Ser", "sextans": "Sex", "taurus": "Tau", "telescopium": "Tel",
    "triangulum": "Tri", "triangulumaustrale": "TrA", "tucana": "Tuc",
    "ursamajor": "UMa", "ursaminor": "UMi", "vela": "Vel", "virgo": "Vir",
    "volans": "Vol", "vulpecula": "Vul"
}

def open_constellation_image(constellation_name):
    key = constellation_name.strip().lower().replace(" ", "")
    
    if key not in IAU_CODES:
        print("Image not available for this constellation.")
    return
    
    code = IAU_CODES[key]
    image_url = f"https://en.wikipedia.org/wiki/{constellation_name.replace('_', '_').title()}_(constellation)"
    
    print("\nCONSTELLATION IMAGE")
    print("------------------------------------------")
    print("Opening official IAU constellation chart...")
    print(image_url)
    print("\nImage credit: International Astronomical Union (IAU) and Sky & Telescope.")
    print("License: CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/")
    
    webbrowser.open(image_url)


# ==========================================================
# CONSTELLATION SEARCH
# ==========================================================

def search_constellation(constellation_name):
    

    print("\n==========================================")
    print("       CONSTELLATION INFORMATION")
    print("==========================================")

    # Northern Hemisphere observing seasons are used as the default.
    constellation_info = {
        "andromeda": {
            "mythology": "Andromeda was a Greek princess chained to a rock as a sacrifice to a sea monster.",
            "ancient_usage": "Used in Greek star lore; its galaxy, M31, was known to ancient astronomers as a fuzzy patch.",
            "best_season": "Autumn",
            "best_time": "Evening",
            "hemisphere": "Northern Hemisphere; visible from both hemispheres",
            "major_stars": ["Alpheratz", "Mirach", "Almach", "Delta Andromedae"]
        },
        "antlia": {
            "mythology": "Named after the air pump, an 18th-century scientific instrument; it has no classical mythology.",
            "ancient_usage": "Created during the Age of Exploration to fill unmapped southern skies.",
            "best_season": "Spring",
            "best_time": "Late evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Alpha Antliae", "Epsilon Antliae", "Iota Antliae"]
        },
        "apus": {
            "mythology": "Represents the bird of paradise; it has no major Greek myth.",
            "ancient_usage": "Added by Dutch navigators to map the southern sky.",
            "best_season": "Southern winter",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Alpha Apodis", "Beta Apodis", "Gamma Apodis"]
        },
        "aquarius": {
            "mythology": "Associated with Ganymede, the cupbearer of the gods in Greek mythology.",
            "ancient_usage": "Linked with the rainy season and water in Babylonian and Greek traditions.",
            "best_season": "Autumn",
            "best_time": "Evening",
            "hemisphere": "Zodiac; visible from both hemispheres",
            "major_stars": ["Sadalsuud", "Sadalmelik", "Skat", "Albali"]
        },
        "aquila": {
            "mythology": "The eagle of Zeus, which carried Ganymede to Olympus.",
            "ancient_usage": "Important in Greek, Roman, and Indian traditions as a celestial bird.",
            "best_season": "Summer",
            "best_time": "Late evening",
            "hemisphere": "Equatorial; visible from both hemispheres",
            "major_stars": ["Altair", "Tarazed", "Alshain", "Zeta Aquilae"]
        },
        "ara": {
            "mythology": "Represents the altar used by the gods before the battle with the Titans.",
            "ancient_usage": "Known to the Greeks as a sacrificial altar.",
            "best_season": "Southern winter",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Beta Arae", "Alpha Arae", "Gamma Arae"]
        },
        "aries": {
            "mythology": "The golden ram that carried Phrixus to safety in Greek myth.",
            "ancient_usage": "Marked the vernal equinox in ancient times and was vital for calendars.",
            "best_season": "Autumn",
            "best_time": "Evening",
            "hemisphere": "Zodiac; visible from both hemispheres",
            "major_stars": ["Hamal", "Sheratan", "Mesarthim"]
        },
        "auriga": {
            "mythology": "Often identified as Erichthonius, a legendary charioteer, or Myrtilus.",
            "ancient_usage": "Represented a charioteer and was used for seasonal navigation.",
            "best_season": "Winter",
            "best_time": "Evening",
            "hemisphere": "Northern Hemisphere",
            "major_stars": ["Capella", "Menkalinan", "Mahasim", "Iota Aurigae"]
        },
        "bootes": {
            "mythology": "The herdsman or ploughman, sometimes linked with Icarius.",
            "ancient_usage": "Used to track seasons and guide agricultural activity.",
            "best_season": "Spring",
            "best_time": "Evening",
            "hemisphere": "Northern Hemisphere",
            "major_stars": ["Arcturus", "Izar", "Muphrid", "Seginus"]
        },
        "caelum": {
            "mythology": "Represents a sculptor’s chisel; no classical mythology.",
            "ancient_usage": "An 18th-century southern constellation created by Nicolas-Louis de Lacaille.",
            "best_season": "Southern summer",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Alpha Caeli", "Beta Caeli", "Gamma Caeli"]
        },
        "camelopardalis": {
            "mythology": "Represents a giraffe; it lacks ancient mythology.",
            "ancient_usage": "A relatively modern northern constellation introduced in the 17th century.",
            "best_season": "Winter",
            "best_time": "Late evening",
            "hemisphere": "Northern Hemisphere",
            "major_stars": ["Beta Camelopardalis", "Alpha Camelopardalis", "CS Camelopardalis"]
        },
        "cancer": {
            "mythology": "The crab sent by Hera to distract Hercules during his fight with the Hydra.",
            "ancient_usage": "A zodiac sign used for calendars and the summer solstice in antiquity.",
            "best_season": "Spring",
            "best_time": "Evening",
            "hemisphere": "Zodiac; visible from both hemispheres",
            "major_stars": ["Altarf", "Asellus Borealis", "Asellus Australis", "Tegmine"]
        },
        "canes_venatici": {
            "mythology": "Represents the hunting dogs of Boötes, Asterion and Chara.",
            "ancient_usage": "Created in the 17th century to separate stars formerly part of Ursa Major.",
            "best_season": "Spring",
            "best_time": "Evening",
            "hemisphere": "Northern Hemisphere",
            "major_stars": ["Cor Caroli", "Chara", "La Superba"]
        },
        "canis_major": {
            "mythology": "The great dog of Orion, often identified with Laelaps.",
            "ancient_usage": "Sirius was used by Egyptians to predict the Nile flood and by sailors for navigation.",
            "best_season": "Winter",
            "best_time": "Evening",
            "hemisphere": "Visible from both hemispheres; better in the Southern Hemisphere",
            "major_stars": ["Sirius", "Mirzam", "Wezen", "Adhara", "Aludra"]
        },
        "canis_minor": {
            "mythology": "The smaller dog of Orion, sometimes called Maera.",
            "ancient_usage": "Procyon was used in ancient calendars and navigation.",
            "best_season": "Winter",
            "best_time": "Evening",
            "hemisphere": "Northern Hemisphere; visible from both hemispheres",
            "major_stars": ["Procyon", "Gomeisa"]
        },
        "capricornus": {
            "mythology": "The sea-goat, linked to the god Pan or the goat Amalthea.",
            "ancient_usage": "A zodiac constellation used to mark the winter solstice in ancient times.",
            "best_season": "Autumn",
            "best_time": "Evening",
            "hemisphere": "Zodiac; visible from both hemispheres",
            "major_stars": ["Deneb Algedi", "Algedi", "Nashira", "Psi Capricorni"]
        },
        "carina": {
            "mythology": "Part of the ancient ship Argo Navis, the ship of Jason and the Argonauts.",
            "ancient_usage": "Canopus was a major navigation star for ancient sailors.",
            "best_season": "Southern summer",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Canopus", "Miaplacidus", "Avior", "Aspidiske"]
        },
        "cassiopeia": {
            "mythology": "Cassiopeia was the vain queen of Ethiopia, punished by being placed in the sky.",
            "ancient_usage": "A circumpolar guide for finding the North Star in northern skies.",
            "best_season": "Autumn and winter",
            "best_time": "Evening",
            "hemisphere": "Northern Hemisphere; circumpolar in many northern locations",
            "major_stars": ["Schedar", "Caph", "Gamma Cassiopeiae", "Ruchbah", "Segin"]
        },
        "centaurus": {
            "mythology": "Represents Chiron, the wise centaur and teacher of Greek heroes.",
            "ancient_usage": "Alpha Centauri was important for southern navigation and distance measurement.",
            "best_season": "Southern autumn",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Alpha Centauri", "Beta Centauri", "Mimosa", "Menkent"]
        },
        "cepheus": {
            "mythology": "Cepheus was the king of Ethiopia and husband of Cassiopeia.",
            "ancient_usage": "Its variable star Delta Cephei became the basis for measuring cosmic distances.",
            "best_season": "Autumn",
            "best_time": "Evening",
            "hemisphere": "Northern Hemisphere; circumpolar in many northern locations",
            "major_stars": ["Alderamin", "Alfirk", "Errai", "Zeta Cephei"]
        },
        "cetus": {
            "mythology": "The sea monster sent to punish Queen Cassiopeia and threaten Andromeda.",
            "ancient_usage": "Mira, its long-period variable star, was studied from ancient and early modern times.",
            "best_season": "Autumn and winter",
            "best_time": "Evening",
            "hemisphere": "Equatorial; visible from both hemispheres",
            "major_stars": ["Diphda", "Menkar", "Mira", "Kaffaljidhma"]
        },
        "chamaeleon": {
            "mythology": "Represents a chameleon; it has no classical mythology.",
            "ancient_usage": "Created by Dutch explorers to chart the far-southern sky.",
            "best_season": "Southern autumn",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Alpha Chamaeleontis", "Beta Chamaeleontis", "Gamma Chamaeleontis"]
        },
        "circinus": {
            "mythology": "Represents a pair of drafting compasses; no ancient mythology.",
            "ancient_usage": "An 18th-century scientific constellation created by Lacaille.",
            "best_season": "Southern autumn",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Alpha Circini", "Beta Circini", "Gamma Circini"]
        },
        "columba": {
            "mythology": "Often associated with Noah’s dove or the dove of Jason’s ship Argo.",
            "ancient_usage": "Created in the late 16th century from formerly unassigned southern stars.",
            "best_season": "Winter",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere; partly visible from northern latitudes",
            "major_stars": ["Phact", "Wazn", "Epsilon Columbae"]
        },
        "coma_berenices": {
            "mythology": "Represents the hair of Queen Berenice II of Egypt, offered to Aphrodite.",
            "ancient_usage": "Known as a faint star cluster region; important for galaxy research today.",
            "best_season": "Spring",
            "best_time": "Evening",
            "hemisphere": "Northern Hemisphere",
            "major_stars": ["Beta Comae Berenices", "Alpha Comae Berenices", "Gamma Comae Berenices"]
        },
        "corona_australis": {
            "mythology": "A southern crown, associated with the crown of Sagittarius or a laurel wreath.",
            "ancient_usage": "Known to Greek and Roman astronomers as the Southern Crown.",
            "best_season": "Southern winter",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Alphecca Meridiana", "Beta Coronae Australis", "Gamma Coronae Australis"]
        },
        "corona_borealis": {
            "mythology": "The crown of Ariadne, given by Dionysus after she helped Theseus.",
            "ancient_usage": "Recognized by many cultures as a crown or circle of stars.",
            "best_season": "Summer",
            "best_time": "Evening",
            "hemisphere": "Northern Hemisphere",
            "major_stars": ["Alphecca", "Nusakan", "Theta Coronae Borealis"]
        },
        "corvus": {
            "mythology": "The crow of Apollo, punished for reporting falsely about a water nymph.",
            "ancient_usage": "Used by sailors and farmers as a seasonal marker.",
            "best_season": "Spring",
            "best_time": "Evening",
            "hemisphere": "Equatorial; visible from both hemispheres",
            "major_stars": ["Gienah", "Algorab", "Kraz", "Minkar"]
        },
        "crater": {
            "mythology": "The cup of Apollo, associated with the crow and Hydra myth.",
            "ancient_usage": "Represented a drinking cup in Greek and Roman star lore.",
            "best_season": "Spring",
            "best_time": "Evening",
            "hemisphere": "Equatorial; visible from both hemispheres",
            "major_stars": ["Delta Crateris", "Beta Crateris", "Gamma Crateris"]
        },
        "crux": {
            "mythology": "The Southern Cross; important in many southern cultures and Christian symbolism.",
            "ancient_usage": "A key navigation constellation for Southern Hemisphere sailors.",
            "best_season": "Southern autumn",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere; not visible from most northern locations",
            "major_stars": ["Acrux", "Mimosa", "Gacrux", "Imai", "Ginan"]
        },
        "cygnus": {
            "mythology": "The swan, often identified with Zeus or the musician Cycnus.",
            "ancient_usage": "Deneb was used in seasonal calendars and navigation.",
            "best_season": "Summer and early autumn",
            "best_time": "Late evening",
            "hemisphere": "Northern Hemisphere",
            "major_stars": ["Deneb", "Sadr", "Gienah", "Delta Cygni", "Albireo"]
        },
        "delphinus": {
            "mythology": "The dolphin that saved the poet Arion or helped Poseidon find Amphitrite.",
            "ancient_usage": "A small but ancient Greek constellation.",
            "best_season": "Summer and autumn",
            "best_time": "Evening",
            "hemisphere": "Northern Hemisphere",
            "major_stars": ["Beta Delphini", "Alpha Delphini", "Gamma Delphini"]
        },
        "dorado": {
            "mythology": "Represents the dolphinfish or mahi-mahi; no classical mythology.",
            "ancient_usage": "Created during Dutch southern-sky expeditions; contains the Large Magellanic Cloud.",
            "best_season": "Southern summer",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Alpha Doradus", "Beta Doradus", "Gamma Doradus"]
        },
        "draco": {
            "mythology": "The dragon Ladon, guardian of the golden apples in the Garden of the Hesperides.",
            "ancient_usage": "Thuban was the pole star around 2700 BCE and may have been used in pyramid alignment.",
            "best_season": "Summer",
            "best_time": "Evening",
            "hemisphere": "Northern Hemisphere; circumpolar in many northern locations",
            "major_stars": ["Eltanin", "Rastaban", "Grumium", "Thuban"]
        },
        "equuleus": {
            "mythology": "The little horse or foal; its exact mythological identity is uncertain.",
            "ancient_usage": "One of the 48 constellations recorded by Ptolemy.",
            "best_season": "Autumn",
            "best_time": "Evening",
            "hemisphere": "Northern Hemisphere",
            "major_stars": ["Kitalpha", "Delta Equulei", "Gamma Equulei"]
        },
        "eridanus": {
            "mythology": "The heavenly river, often linked to the River Eridanus or the path of Phaethon.",
            "ancient_usage": "Achernar marked the southern end of the celestial river for navigators.",
            "best_season": "Winter",
            "best_time": "Evening",
            "hemisphere": "Equatorial; visible from both hemispheres",
            "major_stars": ["Achernar", "Cursa", "Zaurak", "Rana"]
        },
        "fornax": {
            "mythology": "Represents a chemical furnace; it has no ancient mythology.",
            "ancient_usage": "Created by Lacaille in the 18th century for southern sky mapping.",
            "best_season": "Autumn and winter",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Alpha Fornacis", "Beta Fornacis", "Nu Fornacis"]
        },
        "gemini": {
            "mythology": "The twins Castor and Pollux, sons of Leda in Greek mythology.",
            "ancient_usage": "A zodiac constellation used in calendars and navigation.",
            "best_season": "Winter",
            "best_time": "Evening",
            "hemisphere": "Zodiac; visible from both hemispheres",
            "major_stars": ["Pollux", "Castor", "Alhena", "Wasat", "Mebsuta"]
        },
        "grus": {
            "mythology": "The crane; created during European southern-sky mapping.",
            "ancient_usage": "A modern constellation with no direct ancient mythology.",
            "best_season": "Southern spring",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Alnair", "Tiaki", "Delta Gruis", "Gamma Gruis"]
        },
        "hercules": {
            "mythology": "The Greek hero Heracles, famous for completing the Twelve Labours.",
            "ancient_usage": "Recognized in antiquity as the Kneeler; used in seasonal star lore.",
            "best_season": "Summer",
            "best_time": "Evening",
            "hemisphere": "Northern Hemisphere",
            "major_stars": ["Kornephoros", "Zeta Herculis", "Pi Herculis", "Sarin"]
        },
        "horologium": {
            "mythology": "Represents a pendulum clock; no classical mythology.",
            "ancient_usage": "Created by Lacaille to commemorate scientific instruments.",
            "best_season": "Southern summer",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Alpha Horologii", "Beta Horologii", "R Horologii"]
        },
        "hydra": {
            "mythology": "The many-headed water serpent defeated by Hercules.",
            "ancient_usage": "One of the largest ancient constellations; used as a seasonal marker.",
            "best_season": "Spring",
            "best_time": "Evening",
            "hemisphere": "Equatorial; visible from both hemispheres",
            "major_stars": ["Alphard", "Gamma Hydrae", "Zeta Hydrae", "Nu Hydrae"]
        },
        "hydrus": {
            "mythology": "The lesser water snake; no major Greek myth.",
            "ancient_usage": "Created by Dutch navigators to distinguish it from Hydra.",
            "best_season": "Southern spring",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Beta Hydri", "Alpha Hydri", "Gamma Hydri"]
        },
        "indus": {
            "mythology": "Represents an Indian or native person holding arrows; created during southern mapping.",
            "ancient_usage": "A 16th-century southern constellation with no classical mythology.",
            "best_season": "Southern spring",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Alpha Indi", "Beta Indi", "Delta Indi"]
        },
        "lacerta": {
            "mythology": "The lizard; created by Johannes Hevelius in the 17th century.",
            "ancient_usage": "A modern constellation with no ancient mythology.",
            "best_season": "Autumn",
            "best_time": "Evening",
            "hemisphere": "Northern Hemisphere",
            "major_stars": ["Alpha Lacertae", "Beta Lacertae", "Roe 47"]
        },
        "leo": {
            "mythology": "The Nemean Lion, killed by Hercules as his first labour.",
            "ancient_usage": "A zodiac constellation linked to the summer solstice in ancient times.",
            "best_season": "Spring",
            "best_time": "Evening",
            "hemisphere": "Zodiac; visible from both hemispheres",
            "major_stars": ["Regulus", "Denebola", "Algieba", "Zosma", "Chertan"]
        },
        "leo_minor": {
            "mythology": "The lesser lion; created by Johannes Hevelius.",
            "ancient_usage": "A modern faint northern constellation with no ancient mythology.",
            "best_season": "Spring",
            "best_time": "Evening",
            "hemisphere": "Northern Hemisphere",
            "major_stars": ["Praecipua", "Beta Leonis Minoris", "21 Leonis Minoris"]
        },
        "lepus": {
            "mythology": "The hare chased by Orion’s dogs across the sky.",
            "ancient_usage": "Known to Greek and Roman astronomers as the Hare.",
            "best_season": "Winter",
            "best_time": "Evening",
            "hemisphere": "Equatorial; visible from both hemispheres",
            "major_stars": ["Arneb", "Nihal", "Gamma Leporis", "Mu Leporis"]
        },
        "libra": {
            "mythology": "The scales of justice, associated with Astraea or the claws of Scorpius.",
            "ancient_usage": "A zodiac constellation used for equinox and legal-symbolic traditions.",
            "best_season": "Summer",
            "best_time": "Evening",
            "hemisphere": "Zodiac; visible from both hemispheres",
            "major_stars": ["Zubenelgenubi", "Zubeneschamali", "Brachium"]
        },
        "lupus": {
            "mythology": "The wolf, sometimes connected to the centaur’s sacrifice in Greek lore.",
            "ancient_usage": "Known to Ptolemy as the Beast; used in early southern star charts.",
            "best_season": "Southern autumn",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Alpha Lupi", "Beta Lupi", "Gamma Lupi", "Delta Lupi"]
        },
        "lynx": {
            "mythology": "The lynx; named because only sharp-eyed observers could see its faint stars.",
            "ancient_usage": "Created by Hevelius in the 17th century.",
            "best_season": "Winter and spring",
            "best_time": "Late evening",
            "hemisphere": "Northern Hemisphere",
            "major_stars": ["Alpha Lyncis", "38 Lyncis", "12 Lyncis"]
        },
        "lyra": {
            "mythology": "The lyre of Orpheus, placed in the sky after his death.",
            "ancient_usage": "Vega was a former northern pole star and remains a major navigation reference.",
            "best_season": "Summer",
            "best_time": "Evening",
            "hemisphere": "Northern Hemisphere",
            "major_stars": ["Vega", "Sheliak", "Sulafat", "Delta Lyrae"]
        },
        "mensa": {
            "mythology": "Named after Table Mountain in South Africa; no classical mythology.",
            "ancient_usage": "Created by Lacaille during his southern sky survey.",
            "best_season": "Southern summer",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Alpha Mensae", "Beta Mensae", "Gamma Mensae"]
        },
        "microscopium": {
            "mythology": "Represents the microscope; no classical mythology.",
            "ancient_usage": "An 18th-century scientific constellation created by Lacaille.",
            "best_season": "Southern spring",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Gamma Microscopii", "Alpha Microscopii", "Epsilon Microscopii"]
        },
        "monoceros": {
            "mythology": "The unicorn; its mythology is uncertain but often linked to the unicorn of legend.",
            "ancient_usage": "A relatively late constellation, formally established in the 17th century.",
            "best_season": "Winter",
            "best_time": "Evening",
            "hemisphere": "Equatorial; visible from both hemispheres",
            "major_stars": ["Beta Monocerotis", "Alpha Monocerotis", "Gamma Monocerotis"]
        },
        "musca": {
            "mythology": "The fly; originally called Apis, the bee.",
            "ancient_usage": "Created by Dutch navigators for southern sky charts.",
            "best_season": "Southern autumn",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Alpha Muscae", "Beta Muscae", "Delta Muscae"]
        },
        "norma": {
            "mythology": "Represents a carpenter’s square or level; no ancient mythology.",
            "ancient_usage": "Created by Lacaille as part of his instrument-based southern constellations.",
            "best_season": "Southern winter",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Gamma Normae", "Eta Normae", "Delta Normae"]
        },
        "octans": {
            "mythology": "Represents the octant, a navigation instrument; no classical mythology.",
            "ancient_usage": "Contains the south celestial pole and was vital for southern navigation.",
            "best_season": "All year from far-southern latitudes",
            "best_time": "Any clear night",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Sigma Octantis", "Beta Octantis", "Nu Octantis"]
        },
        "ophiuchus": {
            "mythology": "Asclepius, the healer who could revive the dead and was placed in the sky by Zeus.",
            "ancient_usage": "Associated with medicine and healing in Greek tradition.",
            "best_season": "Summer",
            "best_time": "Evening",
            "hemisphere": "Equatorial; visible from both hemispheres",
            "major_stars": ["Rasalhague", "Cebalrai", "Kornephoros", "Yed Prior"]
        },
        "orion": {
            "mythology": "Orion was a mighty Greek hunter placed among the stars after his death.",
            "ancient_usage": "Used worldwide for seasonal calendars, navigation, and agricultural timing.",
            "best_season": "Winter",
            "best_time": "Evening",
            "hemisphere": "Equatorial; visible from both hemispheres",
            "major_stars": ["Betelgeuse", "Rigel", "Bellatrix", "Mintaka", "Alnilam", "Alnitak", "Saiph", "Meissa"]
        },
        "pavo": {
            "mythology": "The peacock, associated with Hera’s sacred bird.",
            "ancient_usage": "Created by Dutch explorers during southern sky mapping.",
            "best_season": "Southern winter",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Peacock", "Beta Pavonis", "Delta Pavonis"]
        },
        "pegasus": {
            "mythology": "The winged horse Pegasus, born from Medusa’s blood.",
            "ancient_usage": "Its Great Square helped ancient observers locate autumn stars.",
            "best_season": "Autumn",
            "best_time": "Evening",
            "hemisphere": "Northern Hemisphere",
            "major_stars": ["Markab", "Scheat", "Algenib", "Enif", "Matar"]
        },
        "perseus": {
            "mythology": "Perseus, the hero who killed Medusa and rescued Andromeda.",
            "ancient_usage": "Algol, its eclipsing variable star, was known as the Demon Star.",
            "best_season": "Autumn and winter",
            "best_time": "Evening",
            "hemisphere": "Northern Hemisphere",
            "major_stars": ["Mirfak", "Algol", "Zeta Persei", "Epsilon Persei"]
        },
        "phoenix": {
            "mythology": "The phoenix, the mythical bird reborn from ashes.",
            "ancient_usage": "Created by Dutch navigators; no direct ancient Greek mythology.",
            "best_season": "Southern spring",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Ankaa", "Beta Phoenicis", "Gamma Phoenicis"]
        },
        "pictor": {
            "mythology": "The painter’s easel; no classical mythology.",
            "ancient_usage": "Created by Lacaille as part of his scientific southern constellations.",
            "best_season": "Southern summer",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Alpha Pictoris", "Beta Pictoris", "Gamma Pictoris"]
        },
        "pisces": {
            "mythology": "Two fish connected by a cord, often linked to Aphrodite and Eros escaping Typhon.",
            "ancient_usage": "Contains the vernal equinox point in the current astronomical epoch.",
            "best_season": "Autumn",
            "best_time": "Evening",
            "hemisphere": "Zodiac; visible from both hemispheres",
            "major_stars": ["Alrescha", "Eta Piscium", "Gamma Piscium", "Omega Piscium"]
        },
        "piscis_austrinus": {
            "mythology": "The southern fish that swallowed the water poured by Aquarius.",
            "ancient_usage": "Fomalhaut was an important navigation and calendar star.",
            "best_season": "Autumn",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere; partly visible from northern latitudes",
            "major_stars": ["Fomalhaut", "Beta Piscis Austrini", "Delta Piscis Austrini"]
        },
        "puppis": {
            "mythology": "The stern of the Argo Navis, the ship of Jason and the Argonauts.",
            "ancient_usage": "Part of the ancient great ship constellation used in maritime lore.",
            "best_season": "Winter",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere; partly visible from northern latitudes",
            "major_stars": ["Naos", "Pi Puppis", "Rho Puppis", "Tau Puppis"]
        },
        "pyxis": {
            "mythology": "The mariner’s compass; originally part of the ship Argo Navis.",
            "ancient_usage": "Created in the 18th century from stars of the ancient Argo.",
            "best_season": "Spring",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Alpha Pyxidis", "Beta Pyxidis", "Gamma Pyxidis"]
        },
        "reticulum": {
            "mythology": "Represents a reticle, the crosshair in a telescope eyepiece.",
            "ancient_usage": "Created by Lacaille for scientific instrument symbolism.",
            "best_season": "Southern summer",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Alpha Reticuli", "Beta Reticuli", "Gamma Reticuli"]
        },
        "sagitta": {
            "mythology": "The arrow of Apollo, Heracles, or Eros, depending on the tradition.",
            "ancient_usage": "One of Ptolemy’s original 48 constellations.",
            "best_season": "Summer",
            "best_time": "Evening",
            "hemisphere": "Northern Hemisphere",
            "major_stars": ["Gamma Sagittae", "Delta Sagittae", "Alpha Sagittae"]
        },
        "sagittarius": {
            "mythology": "The archer, usually identified as the centaur Chiron aiming his bow.",
            "ancient_usage": "Marks the direction of the galactic centre; important in many cultural calendars.",
            "best_season": "Summer",
            "best_time": "Evening",
            "hemisphere": "Zodiac; visible from both hemispheres; better in the Southern Hemisphere",
            "major_stars": ["Kaus Australis", "Nunki", "Ascella", "Kaus Media", "Kaus Borealis"]
        },
        "scorpius": {
            "mythology": "The scorpion that killed Orion; Zeus placed both in the sky but at opposite sides.",
            "ancient_usage": "Antares was used in ancient calendars and as a marker of the summer season.",
            "best_season": "Summer",
            "best_time": "Evening",
            "hemisphere": "Zodiac; visible from both hemispheres; better in the Southern Hemisphere",
            "major_stars": ["Antares", "Acrab", "Dschubba", "Fang", "Shaula", "Lesath"]
        },
        "sculptor": {
            "mythology": "Represents a sculptor’s workshop; no classical mythology.",
            "ancient_usage": "Created by Lacaille in the 18th century.",
            "best_season": "Autumn",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Alpha Sculptoris", "Beta Sculptoris", "Gamma Sculptoris"]
        },
        "scutum": {
            "mythology": "Sobieski’s Shield, named after the Polish king John III Sobieski.",
            "ancient_usage": "Created in the 17th century; no ancient mythology.",
            "best_season": "Summer",
            "best_time": "Evening",
            "hemisphere": "Equatorial; visible from both hemispheres",
            "major_stars": ["Alpha Scuti", "Beta Scuti", "Zeta Scuti"]
        },
        "serpens": {
            "mythology": "The serpent held by Ophiuchus, the healer.",
            "ancient_usage": "Uniquely divided into Serpens Caput and Serpens Cauda; tied to healing myths.",
            "best_season": "Summer",
            "best_time": "Evening",
            "hemisphere": "Equatorial; visible from both hemispheres",
            "major_stars": ["Unukalhai", "Alpha Serpentis", "Eta Serpentis", "Mu Serpentis"]
        },
        "sextans": {
            "mythology": "Represents the sextant, a navigation instrument; no classical mythology.",
            "ancient_usage": "Created by Johannes Hevelius in the 17th century.",
            "best_season": "Spring",
            "best_time": "Evening",
            "hemisphere": "Equatorial; visible from both hemispheres",
            "major_stars": ["Alpha Sextantis", "Beta Sextantis", "Gamma Sextantis"]
        },
        "taurus": {
            "mythology": "The bull, often identified as Zeus transformed to abduct Europa.",
            "ancient_usage": "The Pleiades and Hyades were used for agricultural calendars and navigation.",
            "best_season": "Autumn and winter",
            "best_time": "Evening",
            "hemisphere": "Zodiac; visible from both hemispheres",
            "major_stars": ["Aldebaran", "Elnath", "Alcyone", "Zeta Tauri", "Theta Tauri"]
        },
        "telescopium": {
            "mythology": "Represents the telescope; no classical mythology.",
            "ancient_usage": "Created by Lacaille to honour modern astronomy.",
            "best_season": "Southern winter",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Alpha Telescopii", "Beta Telescopii", "Delta Telescopii"]
        },
        "triangulum": {
            "mythology": "The triangle, associated with the Nile Delta or the island of Sicily.",
            "ancient_usage": "One of Ptolemy’s original constellations.",
            "best_season": "Autumn and winter",
            "best_time": "Evening",
            "hemisphere": "Northern Hemisphere",
            "major_stars": ["Mothallah", "Beta Trianguli", "Gamma Trianguli"]
        },
        "triangulum_australe": {
            "mythology": "The Southern Triangle; no detailed classical mythology.",
            "ancient_usage": "Known to early European navigators and southern cultures.",
            "best_season": "Southern winter",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Atria", "Beta Trianguli Australis", "Gamma Trianguli Australis"]
        },
        "tucana": {
            "mythology": "The toucan; created during Dutch southern-sky expeditions.",
            "ancient_usage": "Contains the Small Magellanic Cloud, important for modern research.",
            "best_season": "Southern spring",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Alpha Tucanae", "Beta Tucanae", "Gamma Tucanae"]
        },
        "ursa_major": {
            "mythology": "The Great Bear, often linked to Callisto, transformed by Zeus or Hera.",
            "ancient_usage": "The Big Dipper was used to find Polaris and for navigation.",
            "best_season": "Spring",
            "best_time": "Evening",
            "hemisphere": "Northern Hemisphere; circumpolar in many northern locations",
            "major_stars": ["Dubhe", "Merak", "Phecda", "Megrez", "Alioth", "Mizar", "Alkaid"]
        },
        "ursa_minor": {
            "mythology": "The Little Bear, linked to Arcas, son of Callisto.",
            "ancient_usage": "Polaris has been the primary northern navigation star for centuries.",
            "best_season": "All year in many northern locations",
            "best_time": "Any clear night",
            "hemisphere": "Northern Hemisphere only",
            "major_stars": ["Polaris", "Kochab", "Pherkad", "Yildun", "Epsilon Ursae Minoris"]
        },
        "vela": {
            "mythology": "The sails of the Argo Navis, the ship of Jason and the Argonauts.",
            "ancient_usage": "Part of the ancient great ship constellation used in navigation lore.",
            "best_season": "Southern summer",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Suhail", "Regor", "Alsephina", "Alsefina", "Markeb"]
        },
        "virgo": {
            "mythology": "The maiden, associated with Demeter, Persephone, Astraea, or Dike.",
            "ancient_usage": "Spica marked harvest seasons and was important in ancient calendars.",
            "best_season": "Spring",
            "best_time": "Evening",
            "hemisphere": "Zodiac; visible from both hemispheres",
            "major_stars": ["Spica", "Porrima", "Vindemiatrix", "Auva", "Zavijava"]
        },
        "volans": {
            "mythology": "The flying fish; created during Dutch southern-sky exploration.",
            "ancient_usage": "A modern southern constellation with no classical mythology.",
            "best_season": "Southern summer",
            "best_time": "Evening",
            "hemisphere": "Southern Hemisphere",
            "major_stars": ["Beta Volantis", "Alpha Volantis", "Gamma Volantis"]
        },
        "vulpecula": {
            "mythology": "The little fox; created by Johannes Hevelius.",
            "ancient_usage": "A modern northern constellation with no ancient mythology.",
            "best_season": "Summer and autumn",
            "best_time": "Evening",
            "hemisphere": "Northern Hemisphere",
            "major_stars": ["Anser", "Alpha Vulpeculae", "Herald"]
        }
    }

    constellation_name = constellation_name.strip().lower().replace(" ", "_")

    if constellation_name in constellation_info:
        info = constellation_info[constellation_name]

        print("\nConstellation:", constellation_name.replace("_", " ").title())
        print("Mythology:", info["mythology"])
        print("Ancient Usage:", info["ancient_usage"])
        print("Best Season:", info["best_season"])
        print("Best Time:", info["best_time"])
        print("Visibility:", info["hemisphere"])
        print("Major Stars:", ", ".join(info["major_stars"]))

        choice = input("\nDo you want to analyse the chart? (yes/no): ").strip().lower()

    if choice in ("yes", "y"):
        open_constellation_image(constellation_name)
    else:
        print("\nConstellation not found in Galaxy 100.")
        print("Available constellations:")
        print(", ".join(name.replace("_", " ").title() for name in constellation_info))
    



# ==========================================================
# MAIN GALAXY 100 LOOP
# ==========================================================

while True:

    print("\n==========================================")
    print("             MAIN MENU")
    print("==========================================")
    print("1. Planets & Dwarf Planets. {PRESS: 1}")
    print("2. Asteroids & Comets (NASA/JPL SBDB). {PRESS: 2}")
    print("3. Objects Outside the Solar System (SIMBAD). {PRESS: 3}")
    print("4. Exoplanet Search (NASA Exoplanet Archive). {PRESS: 4}")
    print("5. Solar System Moon Search (NASA/JPL Horizons). {PRESS: 5}")
    print("6. Constellations & Star Charts. {PRESS: 6}")
    print("7. Exit. {PRESS: 7}")
    
    choosen_celestial = input(
        "Enter a menu number or object name: "
    ).strip().lower()

    if choosen_celestial == "1":
        choosen_celestial = input(
            "\nEnter planet or dwarf planet name: "
        ).lower()

    elif choosen_celestial == "2":
        choosen_celestial = "asteroids and comets"

    elif choosen_celestial == "3":
        choosen_celestial = "object outside from solar system"

    elif choosen_celestial == "4":
        choosen_celestial = "exoplanets"

    elif choosen_celestial == "5":
        choosen_celestial = "moon search"

    elif choosen_celestial == "6":
        choosen_celestial = "constellations"

    elif choosen_celestial == "7":
        choosen_celestial = "exit"


    # ======================================================
    # EXIT
    # ======================================================

    if choosen_celestial == "exit":
        print("\n==========================================")
        print("       THANK YOU FOR USING GALAXY 100    ")
        print("==========================================")
        break


    # ======================================================
    # NASA / JPL API
    # ======================================================

    if choosen_celestial == "asteroids and comets":

        object_name = input(
            "\nEnter an asteroid, comet or small body name: "
        )

        url = "https://ssd-api.jpl.nasa.gov/sbdb.api"

        try:

            response = requests.get(
                url,
                params={"sstr": object_name},
                timeout=10
            )

            data = response.json()


            # ------------------------------------------------
            # ONE OBJECT FOUND
            # ------------------------------------------------

            if "object" in data:

                print("\n==========================================")
                print("          NASA/JPL OBJECT RESULT")
                print("==========================================")

                print(
                    f"{'Full name':22}: "
                    f"{data['object'].get('fullname', 'Not available')}"
                )

                print(
                    f"{'Object type':22}: "
                    f"{data['object'].get('kind', 'Not available')}"
                )


                if "orbit_class" in data["object"]:

                    print(
                        f"{'Orbit class':22}: "
                        f"{data['object']['orbit_class'].get('name', 'Not available')}"
                    )


                if "neo" in data["object"]:

                    print(
                        f"{'Near-Earth Object':22}: "
                        f"{data['object']['neo']}"
                    )


                if "pha" in data["object"]:

                    print(
                        f"{'Potentially Hazardous':22}: "
                        f"{data['object']['pha']}"
                    )


                # --------------------------------------------
                # ORBIT INFORMATION
                # --------------------------------------------

                if "orbit" in data:

                    print("\n[ ORBIT INFORMATION ]")

                    for element in data["orbit"]["elements"]:

                        if element["name"] == "per":

                            print(
                                f"{'Orbital period':22}: "
                                f"{element['value']} {element['units']}"
                            )

                        elif element["name"] == "a":

                            print(
                                f"{'Semi-major axis':22}: "
                                f"{element['value']} {element['units']}"
                            )

                        elif element["name"] == "e":

                            print(
                                f"{'Eccentricity':22}: "
                                f"{element['value']}"
                            )

                        elif element["name"] == "q":

                            print(
                                f"{'Perihelion distance':22}: "
                                f"{element['value']} {element['units']}"
                            )

                        elif element["name"] == "ad":

                            print(
                                f"{'Aphelion distance':22}: "
                                f"{element['value']} {element['units']}"
                            )


                print("\n------------------------------------------")
                print("DATA SOURCE")
                print("------------------------------------------")
                print("NASA/JPL Small-Body Database (SBDB) API")
                print("NASA/JPL Solar System Dynamics")
                print("------------------------------------------")


            # ------------------------------------------------
            # MULTIPLE OBJECTS FOUND
            # ------------------------------------------------

            elif "list" in data:

                print("\nMultiple objects were found.")

                print("\nPlease choose one of these:")

                for item in data["list"]:

                    print(
                        "-",
                        item.get(
                            "name",
                            item.get(
                                "pdes",
                                "Unknown"
                            )
                        )
                    )


            # ------------------------------------------------
            # ERROR MESSAGE
            # ------------------------------------------------

            elif "message" in data:

                print("\nSorry!")
                print(data["message"])


            # ------------------------------------------------
            # UNKNOWN RESPONSE
            # ------------------------------------------------

            else:

                print("\nSorry!")
                print("The object could not be found.")


        except requests.exceptions.RequestException:

            print("\nInternet connection error.")
            print("Please check your internet connection.")


        except ValueError:

            print("\nThe API returned invalid data.")


        continue


    # ==========================================================
    # SIMBAD ASTRONOMICAL DATABASE
    # ==========================================================



    # ======================================================
    # CONSTELLATION SEARCH
    # ======================================================

    if choosen_celestial == "constellations":

        object_name = input(
            "\nEnter a constellation name (example: Orion): "
        )

        search_constellation(object_name)

        continue


    # ======================================================
    # NASA/JPL HORIZONS MOON SEARCH
    # ======================================================

    if choosen_celestial == "moon search":

        object_name = input(
            "\nEnter a Solar System moon name (example: Europa): "
        )

        search_moon(object_name)

        continue


    # ======================================================
    # NASA EXOPLANET ARCHIVE
    # ======================================================

    if choosen_celestial == "exoplanets":

        object_name = input(
            "\nEnter the exact exoplanet name (example: Kepler-452 b): "
        )

        search_exoplanet(object_name)

        continue


    if choosen_celestial == "object outside from solar system":

        object_name = input(
            "\nEnter an astronomical object name: "
        )

        search_simbad(object_name)

        continue


    # ==========================================================
    # MERCURY
    # ==========================================================

    if choosen_celestial == "mercury":

        print("\n==========================================")
        print("                MERCURY")
        print("==========================================")
        print("BASIC INFORMATION")
        print("------------------------------------------")

        print("Diameter: 4,879 km")
        print("Mass: 3.3011 × 10^23 kg")
        print("Gravity: 3.70 m/s²")
        print("Average temperature: 167°C")
        print("Year length: 88 Earth days")
        print("Sidereal day: 58.6 Earth days")
        print("Solar day: 176 Earth days")
        print("Moons: 0")
        print("Escape velocity: 4.25 km/s")
        print("Atmosphere: Extremely thin exosphere")
        print("Surface: Rocky and heavily cratered")

        while True:

            print("\n[ CALCULATOR ]")
            calculator = input(
                "What do you want to calculate? "
                "(weight / escape velocity / age / "
                "distance / years / solar days / sidereal days / "
                "change): "
            ).lower()

            if calculator == "change":
                break

            elif calculator == "weight":

                weight = float(
                    input("Enter your Earth weight in kg: ")
                )

                answer = weight * 3.70 / 9.81

                print(
                    "Your weight on Mercury:",
                    answer,
                    "kg"
                )

            elif calculator == "escape velocity":

                print(
                    "Mercury escape velocity: 4.25 km/s"
                )

            elif calculator == "age":

                age = float(
                    input("Enter your age on Earth: ")
                )

                answer = age * 365.25 / 87.97

                print(
                    "Your age on Mercury:",
                    answer,
                    "Mercury years"
                )

            elif calculator == "distance":

                print(
                    "Average distance from Sun: 57.9 million km"
                )
                print(
                    "In miles: about 36 million miles"
                )
                print("In AU: 0.387 AU")

            elif calculator == "years":

                years = float(
                    input("Enter Earth years: ")
                )

                answer = years * 365.25 / 87.97

                print("Mercury years:", answer)

            elif calculator == "solar days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 176

                print("Mercury solar days:", answer)

            elif calculator == "sidereal days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 58.6

                print(
                    "Mercury sidereal days:",
                    answer
                )

            else:

                print("Invalid calculator option.")

        continue


    # ==========================================================
    # VENUS
    # ==========================================================

    elif choosen_celestial == "venus":

        print("\n==========================================")
        print("                 VENUS")
        print("==========================================")

        print("Diameter: 12,104 km")
        print("Mass: 4.8675 × 10^24 kg")
        print("Gravity: 8.87 m/s²")
        print("Average temperature: 464°C")
        print("Year length: 224.7 Earth days")
        print("Sidereal day: 243 Earth days")
        print("Solar day: 116.75 Earth days")
        print("Moons: 0")
        print("Escape velocity: 10.36 km/s")
        print("Atmosphere: Mostly carbon dioxide and nitrogen")
        print("Surface: Rocky, volcanic and mountainous")

        while True:

            print("\n[ CALCULATOR ]")
            calculator = input(
                "What do you want to calculate? "
                "(weight / escape velocity / age / "
                "distance / years / solar days / sidereal days / "
                "change): "
            ).lower()

            if calculator == "change":
                break

            elif calculator == "weight":

                weight = float(
                    input("Enter your Earth weight in kg: ")
                )

                answer = weight * 8.87 / 9.81

                print(
                    "Your weight on Venus:",
                    answer,
                    "kg"
                )

            elif calculator == "escape velocity":

                print(
                    "Venus escape velocity: 10.36 km/s"
                )

            elif calculator == "age":

                age = float(
                    input("Enter your age on Earth: ")
                )

                answer = age * 365.25 / 224.7

                print(
                    "Your age on Venus:",
                    answer,
                    "Venus years"
                )

            elif calculator == "distance":

                print(
                    "Average distance from Sun: 108.2 million km"
                )
                print(
                    "In miles: about 67.2 million miles"
                )
                print("In AU: 0.723 AU")

            elif calculator == "years":

                years = float(
                    input("Enter Earth years: ")
                )

                answer = years * 365.25 / 224.7

                print("Venus years:", answer)

            elif calculator == "solar days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 116.75

                print("Venus solar days:", answer)

            elif calculator == "sidereal days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 243

                print(
                    "Venus sidereal days:",
                    answer
                )

            else:

                print("Invalid calculator option.")

        continue


    # ==========================================================
    # EARTH
    # ==========================================================

    elif choosen_celestial == "earth":

        print("\n==========================================")
        print("                 EARTH")
        print("==========================================")

        print("Diameter: 12,742 km")
        print("Mass: 5.972 × 10^24 kg")
        print("Gravity: 9.81 m/s²")
        print("Average temperature: 15°C")
        print("Year length: 365.25 days")
        print("Sidereal day: 23h 56m")
        print("Solar day: 24 hours")
        print("Moons: 1")
        print("Escape velocity: 11.19 km/s")
        print("Atmosphere: Mostly nitrogen and oxygen")
        print("Surface: Rock, water and soil")

        while True:

            print("\n[ CALCULATOR ]")
            calculator = input(
                "What do you want to calculate? "
                "(weight / escape velocity / age / "
                "distance / years / solar days / sidereal days / "
                "change): "
            ).lower()

            if calculator == "change":
                break

            elif calculator == "weight":

                weight = float(
                    input("Enter your Earth weight in kg: ")
                )

                print(
                    "Your weight on Earth:",
                    weight,
                    "kg"
                )

            elif calculator == "escape velocity":

                print(
                    "Earth escape velocity: 11.19 km/s"
                )

            elif calculator == "age":

                age = float(
                    input("Enter your age on Earth: ")
                )

                print(
                    "Your age on Earth:",
                    age,
                    "years"
                )

            elif calculator == "distance":

                print(
                    "Average distance from Sun: 149.6 million km"
                )
                print(
                    "In miles: about 93 million miles"
                )
                print("In AU: 1 AU")

            elif calculator == "years":

                years = float(
                    input("Enter Earth years: ")
                )

                print("Earth years:", years)

            elif calculator == "solar days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 1

                print(
                    "Earth solar days:",
                    answer
                )

            elif calculator == "sidereal days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 0.9973

                print(
                    "Earth sidereal days:",
                    answer
                )

            else:

                print("Invalid calculator option.")

        continue


    # ==========================================================
    # MARS
    # ==========================================================

    elif choosen_celestial == "mars":

        print("\n==========================================")
        print("                  MARS")
        print("==========================================")

        print("Diameter: 6,779 km")
        print("Mass: 6.4171 × 10^23 kg")
        print("Gravity: 3.71 m/s²")
        print("Average temperature: -63°C")
        print("Year length: 687 Earth days")
        print("Sidereal day: 24.6 hours")
        print("Solar day: 24.66 hours")
        print("Moons: 2")
        print("Escape velocity: 5.03 km/s")
        print("Atmosphere: Mostly carbon dioxide")
        print("Surface: Rocky, dusty and volcanic")

        while True:

            print("\n[ CALCULATOR ]")
            calculator = input(
                "What do you want to calculate? "
                "(weight / escape velocity / age / "
                "distance / years / solar days / sidereal days / "
                "change): "
            ).lower()

            if calculator == "change":
                break

            elif calculator == "weight":

                weight = float(
                    input("Enter your Earth weight in kg: ")
                )

                answer = weight * 3.71 / 9.81

                print(
                    "Your weight on Mars:",
                    answer,
                    "kg"
                )

            elif calculator == "escape velocity":

                print(
                    "Mars escape velocity: 5.03 km/s"
                )

            elif calculator == "age":

                age = float(
                    input("Enter your age on Earth: ")
                )

                answer = age * 365.25 / 686.98

                print(
                    "Your age on Mars:",
                    answer,
                    "Mars years"
                )

            elif calculator == "distance":

                print(
                    "Average distance from Sun: 227.9 million km"
                )
                print(
                    "In miles: about 141.6 million miles"
                )
                print("In AU: 1.524 AU")

            elif calculator == "years":

                years = float(
                    input("Enter Earth years: ")
                )

                answer = years * 365.25 / 686.98

                print("Mars years:", answer)

            elif calculator == "solar days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 1.0275

                print(
                    "Mars solar days:",
                    answer
                )

            elif calculator == "sidereal days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 1.026

                print(
                    "Mars sidereal days:",
                    answer
                )

            else:

                print("Invalid calculator option.")

        continue


    # ==========================================================
    # JUPITER
    # ==========================================================

    elif choosen_celestial == "jupiter":

        print("\n==========================================")
        print("                JUPITER")
        print("==========================================")
        print("BASIC INFORMATION")
        print("------------------------------------------")

        print("Diameter: 139,820 km")
        print("Mass: 1.898 × 10^27 kg")
        print("Gravity: 24.79 m/s²")
        print("Average temperature: -110°C")
        print("Year length: 11.86 Earth years")
        print("Sidereal day: 9.93 hours")
        print("Solar day: 9.93 hours")
        print("Moons: 95")
        print("Escape velocity: 59.5 km/s")
        print("Atmosphere: Mostly hydrogen and helium")
        print("Surface: No solid surface; gas giant")

        while True:

            print("\n[ CALCULATOR ]")
            calculator = input(
                "What do you want to calculate? "
                "(weight / escape velocity / age / "
                "distance / years / solar days / sidereal days / "
                "change): "
            ).lower()

            if calculator == "change":
                break

            elif calculator == "weight":

                weight = float(
                    input("Enter your Earth weight in kg: ")
                )

                answer = weight * 24.79 / 9.81

                print(
                    "Your weight on Jupiter:",
                    answer,
                    "kg"
                )

            elif calculator == "escape velocity":

                print(
                    "Jupiter escape velocity: 59.5 km/s"
                )

            elif calculator == "age":

                age = float(
                    input("Enter your age on Earth: ")
                )

                answer = age / 11.86

                print(
                    "Your age on Jupiter:",
                    answer,
                    "Jupiter years"
                )

            elif calculator == "distance":

                print(
                    "Average distance from Sun: 778.5 million km"
                )
                print(
                    "In miles: about 483.8 million miles"
                )
                print("In AU: 5.203 AU")

            elif calculator == "years":

                years = float(
                    input("Enter Earth years: ")
                )

                answer = years / 11.86

                print("Jupiter years:", answer)

            elif calculator == "solar days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 0.4135

                print(
                    "Jupiter solar days:",
                    answer
                )

            elif calculator == "sidereal days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 0.414

                print(
                    "Jupiter sidereal days:",
                    answer
                )

            else:

                print("Invalid calculator option.")

        continue


    # ==========================================================
    # SATURN
    # ==========================================================

    elif choosen_celestial == "saturn":

        print("\n==========================================")
        print("                SATURN")
        print("==========================================")
        print("BASIC INFORMATION")
        print("------------------------------------------")

        print("Diameter: 116,460 km")
        print("Mass: 5.683 × 10^26 kg")
        print("Gravity: 10.44 m/s²")
        print("Average temperature: -140°C")
        print("Year length: 29.45 Earth years")
        print("Sidereal day: about 10.7 hours")
        print("Solar day: about 10.7 hours")
        print("Moons: 274")
        print("Escape velocity: 35.5 km/s")
        print("Atmosphere: Mostly hydrogen and helium")
        print("Surface: No solid surface; gas giant")

        while True:

            print("\n[ CALCULATOR ]")
            calculator = input(
                "What do you want to calculate? "
                "(weight / escape velocity / age / "
                "distance / years / solar days / sidereal days / "
                "change): "
            ).lower()

            if calculator == "change":
                break

            elif calculator == "weight":

                weight = float(
                    input("Enter your Earth weight in kg: ")
                )

                answer = weight * 10.44 / 9.81

                print(
                    "Your weight on Saturn:",
                    answer,
                    "kg"
                )

            elif calculator == "escape velocity":

                print(
                    "Saturn escape velocity: 35.5 km/s"
                )

            elif calculator == "age":

                age = float(
                    input("Enter your age on Earth: ")
                )

                answer = age / 29.45

                print(
                    "Your age on Saturn:",
                    answer,
                    "Saturn years"
                )

            elif calculator == "distance":

                print(
                    "Average distance from Sun: 1.43 billion km"
                )
                print(
                    "In miles: about 886.7 million miles"
                )
                print("In AU: 9.537 AU")

            elif calculator == "years":

                years = float(
                    input("Enter Earth years: ")
                )

                answer = years / 29.45

                print("Saturn years:", answer)

            elif calculator == "solar days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 0.446

                print(
                    "Saturn solar days:",
                    answer
                )

            elif calculator == "sidereal days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 0.446

                print(
                    "Saturn sidereal days:",
                    answer
                )

            else:

                print("Invalid calculator option.")

        continue


    # ==========================================================
    # URANUS
    # ==========================================================

    elif choosen_celestial == "uranus":

        print("\n==========================================")
        print("                URANUS")
        print("==========================================")
        print("BASIC INFORMATION")
        print("------------------------------------------")

        print("Diameter: 50,724 km")
        print("Mass: 8.681 × 10^25 kg")
        print("Gravity: 8.69 m/s²")
        print("Average temperature: -195°C")
        print("Year length: 84 Earth years")
        print("Sidereal day: 17.2 hours")
        print("Solar day: about 17.2 hours")
        print("Moons: 28")
        print("Escape velocity: 21.3 km/s")
        print("Atmosphere: Hydrogen, helium and methane")
        print("Surface: No solid surface; ice giant")

        while True:

            print("\n[ CALCULATOR ]")
            calculator = input(
                "What do you want to calculate? "
                "(weight / escape velocity / age / "
                "distance / years / solar days / sidereal days / "
                "change): "
            ).lower()

            if calculator == "change":
                break

            elif calculator == "weight":

                weight = float(
                    input("Enter your Earth weight in kg: ")
                )

                answer = weight * 8.69 / 9.81

                print(
                    "Your weight on Uranus:",
                    answer,
                    "kg"
                )

            elif calculator == "escape velocity":

                print(
                    "Uranus escape velocity: 21.3 km/s"
                )

            elif calculator == "age":

                age = float(
                    input("Enter your age on Earth: ")
                )

                answer = age / 84

                print(
                    "Your age on Uranus:",
                    answer,
                    "Uranus years"
                )

            elif calculator == "distance":

                print(
                    "Average distance from Sun: 2.87 billion km"
                )
                print(
                    "In miles: about 1.78 billion miles"
                )
                print("In AU: 19.19 AU")

            elif calculator == "years":

                years = float(
                    input("Enter Earth years: ")
                )

                answer = years / 84

                print("Uranus years:", answer)

            elif calculator == "solar days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 0.716

                print(
                    "Uranus solar days:",
                    answer
                )

            elif calculator == "sidereal days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 0.718

                print(
                    "Uranus sidereal days:",
                    answer
                )

            else:

                print("Invalid calculator option.")

        continue


    # ==========================================================
    # NEPTUNE
    # ==========================================================

    elif choosen_celestial == "neptune":

        print("\n==========================================")
        print("                NEPTUNE")
        print("==========================================")
        print("BASIC INFORMATION")
        print("------------------------------------------")

        print("Diameter: 49,244 km")
        print("Mass: 1.024 × 10^26 kg")
        print("Gravity: 11.15 m/s²")
        print("Average temperature: -200°C")
        print("Year length: 164.8 Earth years")
        print("Sidereal day: 16.1 hours")
        print("Solar day: about 16.1 hours")
        print("Moons: 16")
        print("Escape velocity: 23.5 km/s")
        print("Atmosphere: Hydrogen, helium and methane")
        print("Surface: No solid surface; ice giant")

        while True:

            print("\n[ CALCULATOR ]")
            calculator = input(
                "What do you want to calculate? "
                "(weight / escape velocity / age / "
                "distance / years / solar days / sidereal days / "
                "change): "
            ).lower()

            if calculator == "change":
                break

            elif calculator == "weight":

                weight = float(
                    input("Enter your Earth weight in kg: ")
                )

                answer = weight * 11.15 / 9.81

                print(
                    "Your weight on Neptune:",
                    answer,
                    "kg"
                )

            elif calculator == "escape velocity":

                print(
                    "Neptune escape velocity: 23.5 km/s"
                )

            elif calculator == "age":

                age = float(
                    input("Enter your age on Earth: ")
                )

                answer = age / 164.8

                print(
                    "Your age on Neptune:",
                    answer,
                    "Neptune years"
                )

            elif calculator == "distance":

                print(
                    "Average distance from Sun: 4.50 billion km"
                )
                print(
                    "In miles: about 2.80 billion miles"
                )
                print("In AU: 30.07 AU")

            elif calculator == "years":

                years = float(
                    input("Enter Earth years: ")
                )

                answer = years / 164.8

                print("Neptune years:", answer)

            elif calculator == "solar days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 0.671

                print(
                    "Neptune solar days:",
                    answer
                )

            elif calculator == "sidereal days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 0.671

                print(
                    "Neptune sidereal days:",
                    answer
                )

            else:

                print("Invalid calculator option.")

        continue


    # ==========================================================
    # PLUTO
    # ==========================================================

    elif choosen_celestial == "pluto":

        print("\n==========================================")
        print("                 PLUTO")
        print("==========================================")

        print("Diameter: 2,377 km")
        print("Mass: 1.303 × 10^22 kg")
        print("Gravity: 0.62 m/s²")
        print("Average temperature: -229°C")
        print("Year length: 248 Earth years")
        print("Sidereal day: 6.39 Earth days")
        print("Solar day: 6.39 Earth days")
        print("Moons: 5")
        print("Escape velocity: 1.21 km/s")
        print("Atmosphere: Nitrogen, methane and carbon monoxide")
        print("Surface: Nitrogen ice, methane ice and water ice")

        while True:

            print("\n[ CALCULATOR ]")
            calculator = input(
                "What do you want to calculate? "
                "(weight / escape velocity / age / "
                "distance / years / solar days / sidereal days / "
                "change): "
            ).lower()

            if calculator == "change":
                break

            elif calculator == "weight":

                weight = float(
                    input("Enter your Earth weight in kg: ")
                )

                answer = weight * 0.62 / 9.81

                print(
                    "Your weight on Pluto:",
                    answer,
                    "kg"
                )

            elif calculator == "escape velocity":

                print(
                    "Pluto escape velocity: 1.21 km/s"
                )

            elif calculator == "age":

                age = float(
                    input("Enter your age on Earth: ")
                )

                answer = age / 248

                print(
                    "Your age on Pluto:",
                    answer,
                    "Pluto years"
                )

            elif calculator == "distance":

                print(
                    "Average distance from Sun: 5.91 billion km"
                )
                print(
                    "In miles: about 3.67 billion miles"
                )
                print("In AU: 39.48 AU")

            elif calculator == "years":

                years = float(
                    input("Enter Earth years: ")
                )

                answer = years / 248

                print("Pluto years:", answer)

            elif calculator == "solar days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 6.39

                print(
                    "Pluto solar days:",
                    answer
                )

            elif calculator == "sidereal days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 6.39

                print(
                    "Pluto sidereal days:",
                    answer
                )

            else:

                print("Invalid calculator option.")

        continue


    # ==========================================================
    # CERES
    # ==========================================================

    elif choosen_celestial == "ceres":

        print("\n==========================================")
        print("                 CERES")
        print("==========================================")

        print("Diameter: 939 km")
        print("Mass: 9.3835 × 10^20 kg")
        print("Gravity: 0.27 m/s²")
        print("Average temperature: about -105°C")
        print("Year length: 4.61 Earth years")
        print("Sidereal day: 9.07 hours")
        print("Solar day: about 9.07 hours")
        print("Moons: 0")
        print("Escape velocity: 0.51 km/s")
        print("Atmosphere: Extremely thin / temporary exosphere")
        print("Surface: Rocky with water ice and salts")

        while True:

            print("\n[ CALCULATOR ]")
            calculator = input(
                "What do you want to calculate? "
                "(weight / escape velocity / age / "
                "distance / years / solar days / sidereal days / "
                "change): "
            ).lower()

            if calculator == "change":
                break

            elif calculator == "weight":

                weight = float(
                    input("Enter your Earth weight in kg: ")
                )

                answer = weight * 0.27 / 9.81

                print(
                    "Your weight on Ceres:",
                    answer,
                    "kg"
                )

            elif calculator == "escape velocity":

                print(
                    "Ceres escape velocity: 0.51 km/s"
                )

            elif calculator == "age":

                age = float(
                    input("Enter your age on Earth: ")
                )

                answer = age / 4.61

                print(
                    "Your age on Ceres:",
                    answer,
                    "Ceres years"
                )

            elif calculator == "distance":

                print(
                    "Average distance from Sun: 413.7 million km"
                )
                print(
                    "In miles: about 257 million miles"
                )
                print("In AU: 2.77 AU")

            elif calculator == "years":

                years = float(
                    input("Enter Earth years: ")
                )

                answer = years / 4.61

                print("Ceres years:", answer)

            elif calculator == "solar days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 0.378

                print(
                    "Ceres solar days:",
                    answer
                )

            elif calculator == "sidereal days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 0.378

                print(
                    "Ceres sidereal days:",
                    answer
                )

            else:

                print("Invalid calculator option.")

        continue


    # ==========================================================
    # ERIS
    # ==========================================================

    elif choosen_celestial == "eris":

        print("\n==========================================")
        print("                  ERIS")
        print("==========================================")

        print("Diameter: about 2,326 km")
        print("Mass: 1.6466 × 10^22 kg")
        print("Gravity: about 0.82 m/s²")
        print("Average temperature: extremely cold")
        print("Year length: about 558 Earth years")
        print("Sidereal day: about 25.9 hours")
        print("Solar day: about 25.9 hours")
        print("Moons: 1")
        print("Escape velocity: about 1.38 km/s")
        print("Atmosphere: Extremely thin / uncertain")
        print("Surface: Mostly icy")

        while True:

            print("\n[ CALCULATOR ]")
            calculator = input(
                "What do you want to calculate? "
                "(weight / escape velocity / age / "
                "distance / years / solar days / sidereal days / "
                "change): "
            ).lower()

            if calculator == "change":
                break

            elif calculator == "weight":

                weight = float(
                    input("Enter your Earth weight in kg: ")
                )

                answer = weight * 0.82 / 9.81

                print(
                    "Your weight on Eris:",
                    answer,
                    "kg"
                )

            elif calculator == "escape velocity":

                print(
                    "Eris escape velocity: about 1.38 km/s"
                )

            elif calculator == "age":

                age = float(
                    input("Enter your age on Earth: ")
                )

                answer = age / 558

                print(
                    "Your age on Eris:",
                    answer,
                    "Eris years"
                )

            elif calculator == "distance":

                print(
                    "Average distance from Sun: about 10.1 billion km"
                )
                print(
                    "In miles: about 6.3 billion miles"
                )
                print("In AU: about 67.7 AU")

            elif calculator == "years":

                years = float(
                    input("Enter Earth years: ")
                )

                answer = years / 558

                print("Eris years:", answer)

            elif calculator == "solar days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 1.08

                print(
                    "Eris solar days:",
                    answer
                )

            elif calculator == "sidereal days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 1.08

                print(
                    "Eris sidereal days:",
                    answer
                )

            else:

                print("Invalid calculator option.")

        continue


    # ==========================================================
    # HAUMEA
    # ==========================================================

    elif choosen_celestial == "haumea":

        print("\n==========================================")
        print("                HAUMEA")
        print("==========================================")
        print("BASIC INFORMATION")
        print("------------------------------------------")

        print("Diameter: about 1,560 km")
        print("Mass: about 4.006 × 10^21 kg")
        print("Gravity: about 0.40 m/s²")
        print("Average temperature: about -241°C")
        print("Year length: about 284 Earth years")
        print("Sidereal day: about 3.9 hours")
        print("Solar day: about 3.9 hours")
        print("Moons: 2")
        print("Escape velocity: about 0.91 km/s")
        print("Atmosphere: No significant atmosphere")
        print("Surface: Mostly icy")

        while True:

            print("\n[ CALCULATOR ]")
            calculator = input(
                "What do you want to calculate? "
                "(weight / escape velocity / age / "
                "distance / years / solar days / sidereal days / "
                "change): "
            ).lower()

            if calculator == "change":
                break

            elif calculator == "weight":

                weight = float(
                    input("Enter your Earth weight in kg: ")
                )

                answer = weight * 0.40 / 9.81

                print(
                    "Your weight on Haumea:",
                    answer,
                    "kg"
                )

            elif calculator == "escape velocity":

                print(
                    "Haumea escape velocity: about 0.91 km/s"
                )

            elif calculator == "age":

                age = float(
                    input("Enter your age on Earth: ")
                )

                answer = age / 284

                print(
                    "Your age on Haumea:",
                    answer,
                    "Haumea years"
                )

            elif calculator == "distance":

                print(
                    "Average distance from Sun: about 6.45 billion km"
                )
                print(
                    "In miles: about 4.0 billion miles"
                )
                print("In AU: about 43.1 AU")

            elif calculator == "years":

                years = float(
                    input("Enter Earth years: ")
                )

                answer = years / 284

                print("Haumea years:", answer)

            elif calculator == "solar days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 0.163

                print(
                    "Haumea solar days:",
                    answer
                )

            elif calculator == "sidereal days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 0.163

                print(
                    "Haumea sidereal days:",
                    answer
                )

            else:

                print("Invalid calculator option.")

        continue


    # ==========================================================
    # MAKEMAKE
    # ==========================================================

    elif choosen_celestial == "makemake":

        print("\n==========================================")
        print("               MAKEMAKE")
        print("==========================================")

        print("Diameter: about 1,430 km")
        print("Mass: about 3.1 × 10^21 kg")
        print("Gravity: about 0.40 m/s²")
        print("Average temperature: about -240°C")
        print("Year length: about 305 Earth years")
        print("Sidereal day: about 22.8 hours")
        print("Solar day: about 22.8 hours")
        print("Moons: 1")
        print("Escape velocity: about 0.80 km/s")
        print("Atmosphere: Extremely thin / temporary")
        print("Surface: Icy with methane and nitrogen")

        while True:

            print("\n[ CALCULATOR ]")
            calculator = input(
                "What do you want to calculate? "
                "(weight / escape velocity / age / "
                "distance / years / solar days / sidereal days / "
                "change): "
            ).lower()

            if calculator == "change":
                break

            elif calculator == "weight":

                weight = float(
                    input("Enter your Earth weight in kg: ")
                )

                answer = weight * 0.40 / 9.81

                print(
                    "Your weight on Makemake:",
                    answer,
                    "kg"
                )

            elif calculator == "escape velocity":

                print(
                    "Makemake escape velocity: about 0.80 km/s"
                )

            elif calculator == "age":

                age = float(
                    input("Enter your age on Earth: ")
                )

                answer = age / 305

                print(
                    "Your age on Makemake:",
                    answer,
                    "Makemake years"
                )

            elif calculator == "distance":

                print(
                    "Average distance from Sun: about 6.85 billion km"
                )
                print(
                    "In miles: about 4.26 billion miles"
                )
                print("In AU: about 45.8 AU")

            elif calculator == "years":

                years = float(
                    input("Enter Earth years: ")
                )

                answer = years / 305

                print("Makemake years:", answer)

            elif calculator == "solar days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 0.95

                print(
                    "Makemake solar days:",
                    answer
                )

            elif calculator == "sidereal days":

                earth_days = float(
                    input("Enter Earth days: ")
                )

                answer = earth_days / 0.95

                print(
                    "Makemake sidereal days:",
                    answer
                )

            else:

                print("Invalid calculator option.")

        continue


    # ==========================================================
    # INVALID CELESTIAL OBJECT
    # ==========================================================

    else:

        print("\n==========================================")
        print("             INVALID OPTION")
        print("==========================================")
        print("That celestial object is not available")
        print("in GALAXY 100.")
        print("\nAvailable built-in objects:")
        print("------------------------------------------")
        print(
            "Mercury, Venus, Earth, Mars, Jupiter, Saturn,"
        )
        print(
            "Uranus, Neptune, Pluto, Ceres, Eris, Haumea, Makemake"
        )
        print("------------------------------------------")
        print("Use the main menu for:")
        print("Asteroids & Comets")
        print("Objects Outside the Solar System")