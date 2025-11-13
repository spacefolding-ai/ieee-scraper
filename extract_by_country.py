#!/usr/bin/env python3
"""
Extract authors by country from the academic-only dataset.
Groups Germany, Switzerland, and Austria under DACH.
"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def extract_country_from_affiliation(affiliation):
    """
    Extract country from affiliation string.
    Returns standardized country name.
    """
    if not affiliation:
        return "Unknown"
    
    aff_lower = affiliation.lower()
    
    # Country patterns - comprehensive list
    country_patterns = {
        'Germany': [
            'germany', 'deutschland', 'berlin', 'munich', 'münchen', 'hamburg',
            'frankfurt', 'cologne', 'köln', 'stuttgart', 'düsseldorf', 'dortmund',
            'essen', 'leipzig', 'dresden', 'hannover', 'nuremberg', 'nürnberg',
            'duisburg', 'bochum', 'wuppertal', 'bielefeld', 'bonn', 'münster',
            'karlsruhe', 'mannheim', 'augsburg', 'wiesbaden', 'mönchengladbach',
            'gelsenkirchen', 'aachen', 'braunschweig', 'chemnitz', 'kiel',
            'halle', 'magdeburg', 'freiburg', 'krefeld', 'mainz', 'lübeck',
            'oberhausen', 'erfurt', 'rostock', 'kassel', 'hagen', 'potsdam',
            'saarbrücken', 'hamm', 'ludwigshafen', 'mülheim', 'oldenburg',
            'osnabrück', 'leverkusen', 'heidelberg', 'darmstadt', 'paderborn',
            'regensburg', 'würzburg', 'ingolstadt', 'göttingen', 'ulm',
            'heilbronn', 'pforzheim', 'wolfsburg', 'bottrop', 'recklinghausen',
            'erlangen', 'siegen', 'passau', 'offenbach', 'clausthal'
        ],
        'Switzerland': [
            'switzerland', 'schweiz', 'suisse', 'svizzera', 'zurich', 'zürich',
            'geneva', 'genève', 'basel', 'lausanne', 'bern', 'berne',
            'winterthur', 'lucerne', 'luzern', 'lugano', 'biel', 'thun',
            'bellinzona', 'sion', 'neuchâtel', 'aarau', 'chur', 'fribourg',
            'schaffhausen', 'zug', 'montreux', 'vevey', 'eth', 'epfl'
        ],
        'Austria': [
            'austria', 'österreich', 'vienna', 'wien', 'graz', 'linz',
            'salzburg', 'innsbruck', 'klagenfurt', 'villach', 'wels',
            'st. pölten', 'dornbirn', 'steyr', 'wiener neustadt', 'feldkirch',
            'bregenz', 'leonding', 'klosterneuburg', 'baden', 'wolfsberg',
            'leoben', 'krems', 'traun', 'amstetten', 'lustenau'
        ],
        'United Kingdom': [
            'u.k.', 'uk', 'united kingdom', 'england', 'scotland', 'wales',
            'northern ireland', 'london', 'manchester', 'birmingham', 'leeds',
            'glasgow', 'liverpool', 'newcastle', 'sheffield', 'bristol',
            'edinburgh', 'belfast', 'leicester', 'coventry', 'bradford',
            'nottingham', 'kingston', 'southampton', 'plymouth', 'reading',
            'cambridge', 'oxford', 'brighton', 'bournemouth', 'swindon',
            'portsmouth', 'warwick', 'huddersfield', 'canterbury', 'bath',
            'york', 'durham', 'exeter', 'cardiff', 'swansea', 'aberdeen',
            'dundee', 'inverness', 'stirling', 'strathclyde', 'imperial',
            'loughborough', 'cranfield'
        ],
        'France': [
            'france', 'paris', 'marseille', 'lyon', 'toulouse', 'nice',
            'nantes', 'strasbourg', 'montpellier', 'bordeaux', 'lille',
            'rennes', 'reims', 'saint-étienne', 'toulon', 'grenoble',
            'dijon', 'angers', 'nîmes', 'villeurbanne', 'clermont-ferrand',
            'le mans', 'aix-en-provence', 'brest', 'tours', 'amiens',
            'limoges', 'annecy', 'perpignan', 'besançon', 'metz',
            'orléans', 'rouen', 'mulhouse', 'caen', 'nancy', 'versailles',
            'gif-sur-yvette', 'saclay', 'palaiseau', 'orsay'
        ],
        'Italy': [
            'italy', 'italia', 'rome', 'roma', 'milan', 'milano', 'naples',
            'napoli', 'turin', 'torino', 'palermo', 'genoa', 'genova',
            'bologna', 'florence', 'firenze', 'bari', 'catania', 'venice',
            'venezia', 'verona', 'messina', 'padua', 'padova', 'trieste',
            'brescia', 'prato', 'parma', 'modena', 'reggio', 'perugia',
            'livorno', 'cagliari', 'foggia', 'ferrara', 'salerno',
            'ravenna', 'rimini', 'pisa', 'bergamo', 'trento', 'vicenza',
            'terni', 'forlì', 'pescara', 'lecce', 'udine', 'ancona'
        ],
        'Spain': [
            'spain', 'españa', 'madrid', 'barcelona', 'valencia', 'seville',
            'sevilla', 'zaragoza', 'málaga', 'malaga', 'murcia', 'palma',
            'las palmas', 'bilbao', 'alicante', 'córdoba', 'cordoba',
            'valladolid', 'vigo', 'gijón', 'hospitalet', "l'hospitalet",
            'vitoria', 'la coruña', 'coruña', 'granada', 'elche',
            'oviedo', 'badalona', 'cartagena', 'terrassa', 'jerez',
            'sabadell', 'móstoles', 'santa cruz', 'pamplona', 'almería',
            'leganés', 'san sebastián', 'donostia', 'burgos', 'albacete',
            'santander', 'castellón', 'alcalá', 'logroño', 'badajoz',
            'salamanca', 'huelva', 'tarragona', 'león', 'cádiz',
            'upc', 'catalonia', 'catalunya', 'basque', 'euskadi'
        ],
        'Netherlands': [
            'netherlands', 'holland', 'amsterdam', 'rotterdam', 'the hague',
            'utrecht', 'eindhoven', 'tilburg', 'groningen', 'almere',
            'breda', 'nijmegen', 'enschede', 'haarlem', 'arnhem',
            'zaanstad', 'amersfoort', 'apeldoorn', 's-hertogenbosch',
            'hoofddorp', 'maastricht', 'leiden', 'dordrecht', 'zoetermeer',
            'delft', 'enschede', 'wageningen', 'twente'
        ],
        'Belgium': [
            'belgium', 'belgique', 'belgië', 'brussels', 'bruxelles',
            'antwerp', 'antwerpen', 'ghent', 'gent', 'charleroi', 'liège',
            'luik', 'bruges', 'brugge', 'namur', 'leuven', 'mons',
            'mechelen', 'aalst', 'la louvière', 'kortrijk', 'hasselt',
            'ostend', 'oostende', 'genk', 'seraing', 'verviers', 'lier'
        ],
        'Sweden': [
            'sweden', 'sverige', 'stockholm', 'gothenburg', 'göteborg',
            'malmö', 'uppsala', 'västerås', 'örebro', 'linköping',
            'helsingborg', 'jönköping', 'norrköping', 'lund', 'umeå',
            'gävle', 'borås', 'eskilstuna', 'södertälje', 'karlstad',
            'täby', 'växjö', 'halmstad', 'sundsvall', 'luleå', 'trollhättan',
            'östersund', 'borlänge', 'falun', 'kalmar', 'kristianstad',
            'karlskrona', 'skellefteå', 'kth', 'chalmers', 'kista'
        ],
        'Norway': [
            'norway', 'norge', 'oslo', 'bergen', 'trondheim', 'stavanger',
            'drammen', 'fredrikstad', 'kristiansand', 'sandnes', 'tromsø',
            'sarpsborg', 'skien', 'ålesund', 'sandefjord', 'haugesund',
            'tønsberg', 'moss', 'porsgrunn', 'bodø', 'arendal', 'hamar',
            'ytrebygda', 'larvik', 'halden', 'askøy', 'ntnu', 'sintef'
        ],
        'Denmark': [
            'denmark', 'danmark', 'copenhagen', 'københavn', 'aarhus',
            'odense', 'aalborg', 'frederiksberg', 'esbjerg', 'randers',
            'kolding', 'horsens', 'vejle', 'roskilde', 'herning',
            'hørsholm', 'silkeborg', 'næstved', 'fredericia', 'viborg',
            'køge', 'holstebro', 'taastrup', 'slagelse', 'hillerød',
            'dtu', 'lyngby'
        ],
        'Finland': [
            'finland', 'suomi', 'helsinki', 'espoo', 'tampere', 'vantaa',
            'oulu', 'turku', 'jyväskylä', 'lahti', 'kuopio', 'pori',
            'kouvola', 'joensuu', 'lappeenranta', 'hämeenlinna', 'vaasa',
            'seinäjoki', 'rovaniemi', 'mikkeli', 'kotka', 'salo',
            'porvoo', 'kokkola', 'hyvinkää', 'aalto', 'vtt'
        ],
        'Poland': [
            'poland', 'polska', 'warsaw', 'warszawa', 'kraków', 'krakow',
            'łódź', 'lodz', 'wrocław', 'wroclaw', 'poznań', 'poznan',
            'gdańsk', 'gdansk', 'szczecin', 'bydgoszcz', 'lublin',
            'katowice', 'białystok', 'bialystok', 'gdynia', 'częstochowa',
            'czestochowa', 'radom', 'sosnowiec', 'toruń', 'torun',
            'kielce', 'gliwice', 'zabrze', 'bytom', 'olsztyn',
            'rzeszów', 'rzeszow', 'bielsko-biała', 'ruda śląska',
            'rybnik', 'tychy', 'dąbrowa górnicza', 'elbląg', 'płock',
            'opole', 'gorzów wielkopolski', 'politechnika', 'agh'
        ],
        'Czech Republic': [
            'czech', 'czechia', 'ceska', 'prague', 'praha', 'brno',
            'ostrava', 'plzeň', 'liberec', 'olomouc', 'české budějovice',
            'hradec králové', 'ústí nad labem', 'pardubice', 'havířov',
            'zlín', 'kladno', 'most', 'opava', 'frýdek-místek', 'karviná',
            'jihlava', 'teplice', 'karlovy vary', 'děčín', 'chomutov'
        ],
        'Portugal': [
            'portugal', 'lisbon', 'lisboa', 'porto', 'oporto', 'amadora',
            'braga', 'setúbal', 'coimbra', 'queluz', 'funchal', 'cacém',
            'vila nova de gaia', 'loures', 'évora', 'rio de mouro',
            'odivelas', 'aveiro', 'amora', 'corroios', 'barreiro',
            'seixal', 'agualva-cacém', 'guimarães', 'faro', 'almada',
            'portimão', 'maia', 'póvoa de varzim', 'matosinhos', 'viseu'
        ],
        'Greece': [
            'greece', 'hellas', 'ελλάδα', 'athens', 'athina', 'αθήνα',
            'thessaloniki', 'thessalonica', 'θεσσαλονίκη', 'patras',
            'πάτρα', 'heraklion', 'ηράκλειο', 'larissa', 'λάρισα',
            'volos', 'βόλος', 'rhodes', 'ρόδος', 'ioannina', 'ιωάννινα',
            'chania', 'χανιά', 'chalcis', 'χαλκίδα', 'agrinio', 'αγρίνιο',
            'kalamata', 'καλαμάτα', 'kavala', 'καβάλα', 'serres', 'σέρρες',
            'drama', 'δράμα', 'komotini', 'κομοτηνή', 'katerini', 'κατερίνη',
            'xanthi', 'ξάνθη', 'lamia', 'λαμία', 'alexandroupoli',
            'αλεξανδρούπολη', 'kozani', 'κοζάνη', 'trikala', 'τρίκαλα',
            'veria', 'βέροια', 'ntua', 'ntu athens', 'aristotle'
        ],
        'Ireland': [
            'ireland', 'éire', 'dublin', 'cork', 'limerick', 'galway',
            'waterford', 'drogheda', 'dundalk', 'swords', 'bray',
            'navan', 'ennis', 'kilkenny', 'carlow', 'tralee', 'newbridge',
            'naas', 'athlone', 'portlaoise', 'mullingar', 'wexford',
            'balbriggan', 'letterkenny', 'celbridge', 'sligo', 'clonmel',
            'greystones', 'malahide', 'trinity', 'ucd', 'nuig'
        ],
        'Turkey': [
            'turkey', 'türkiye', 'turkiye', 'istanbul', 'ankara', 'izmir',
            'bursa', 'adana', 'gaziantep', 'konya', 'antalya', 'kayseri',
            'mersin', 'eskişehir', 'diyarbakır', 'samsun', 'denizli',
            'şanlıurfa', 'adapazarı', 'malatya', 'kahramanmaraş', 'erzurum',
            'van', 'batman', 'elâzığ', 'icel', 'kocaeli', 'manisa',
            'sivas', 'gebze', 'balıkesir', 'tarsus', 'kütahya', 'trabzon',
            'çorum', 'corlu', 'adıyaman', 'osmaniye', 'kırıkkale', 'antakya',
            'aydın', 'iskenderun', 'uşak', 'aksaray', 'afyon', 'isparta',
            'inönü', 'kastamonu', 'tokat', 'edirne', 'btu', 'metu', 'itu',
            'bogazici', 'boğaziçi', 'middle east technical', 'technical university'
        ],
        'Romania': [
            'romania', 'românia', 'bucharest', 'bucurești', 'cluj-napoca',
            'cluj', 'timișoara', 'timisoara', 'iași', 'iasi', 'constanța',
            'constanta', 'craiova', 'brașov', 'brasov', 'galați', 'galati',
            'ploiești', 'ploiesti', 'oradea', 'brăila', 'braila', 'arad',
            'pitești', 'pitesti', 'sibiu', 'bacău', 'bacau', 'târgu mureș',
            'tirgu mures', 'baia mare', 'buzău', 'buzau', 'satu mare',
            'botoșani', 'botosani', 'piatra neamț', 'piatra neamt',
            'râmnicu vâlcea', 'rimnicu vilcea', 'suceava', 'drobeta-turnu severin',
            'focșani', 'focsani', 'târgoviște', 'targoviste', 'târgu jiu',
            'tirgu jiu', 'tulcea', 'politehnica'
        ],
        'Hungary': [
            'hungary', 'magyarország', 'budapest', 'debrecen', 'szeged',
            'miskolc', 'pécs', 'győr', 'nyíregyháza', 'kecskemét',
            'székesfehérvár', 'szombathely', 'szolnok', 'tatabánya',
            'kaposvár', 'érd', 'veszprém', 'békéscsaba', 'zalaegerszeg',
            'sopron', 'eger', 'nagykanizsa', 'dunakeszi', 'hódmezővásárhely',
            'szentendre', 'bme', 'eötvös', 'eotvos'
        ],
        'Croatia': [
            'croatia', 'hrvatska', 'zagreb', 'split', 'rijeka', 'osijek',
            'zadar', 'pula', 'slavonski brod', 'karlovac', 'varaždin',
            'varazdin', 'šibenik', 'sibenik', 'sisak', 'velika gorica',
            'dubrovnik', 'bjelovar', 'koprivnica', 'vinkovci', 'sveučilište'
        ],
        'Serbia': [
            'serbia', 'srbija', 'belgrade', 'beograd', 'novi sad', 'niš',
            'nis', 'kragujevac', 'subotica', 'zrenjanin', 'pančevo',
            'pancevo', 'čačak', 'cacak', 'kruševac', 'krusevac', 'kraljevo',
            'smederevo', 'leskovac', 'užice', 'uzice', 'vranje', 'valjevo',
            'novi pazar', 'šabac', 'sabac', 'sombor', 'požarevac',
            'pozarevac', 'pirot', 'zaječar', 'zajecar', 'kikinda',
            'sremska mitrovica', 'jagodina', 'vršac', 'vrsac'
        ],
        'Slovenia': [
            'slovenia', 'slovenija', 'ljubljana', 'maribor', 'celje',
            'kranj', 'velenje', 'koper', 'novo mesto', 'ptuj',
            'trbovlje', 'kamnik', 'jesenice', 'nova gorica', 'domžale',
            'domzale', 'škofja loka', 'skofja loka', 'nova mesto',
            'slovenj gradec', 'murska sobota', 'izola', 'postojna'
        ],
        'Bulgaria': [
            'bulgaria', 'българия', 'sofia', 'софия', 'plovdiv', 'пловдив',
            'varna', 'варна', 'burgas', 'бургас', 'ruse', 'русе',
            'stara zagora', 'pleven', 'sliven', 'dobrich', 'shumen',
            'pernik', 'haskovo', 'yambol', 'pazardzhik', 'blagoevgrad',
            'veliko tarnovo', 'vratsa', 'gabrovo', 'asenovgrad', 'vidin',
            'kazanlak', 'kyustendil', 'kardzhali', 'montana', 'dimitrovgrad'
        ],
        'Slovakia': [
            'slovakia', 'slovensko', 'bratislava', 'košice', 'kosice',
            'prešov', 'presov', 'žilina', 'zilina', 'nitra', 'banská bystrica',
            'banska bystrica', 'trnava', 'martin', 'trenčín', 'trencin',
            'poprad', 'prievidza', 'zvolen', 'považská bystrica',
            'povazska bystrica', 'nové zámky', 'nove zamky', 'michalovce',
            'spišská nová ves', 'spiska nova ves', 'komárno', 'komarno',
            'levice', 'humenné', 'humenne', 'bardejov', 'lučenec', 'lucenec'
        ],
        'Lithuania': [
            'lithuania', 'lietuva', 'vilnius', 'kaunas', 'klaipėda',
            'klaipeda', 'šiauliai', 'siauliai', 'panevėžys', 'panevezys',
            'alytus', 'marijampolė', 'marijampole', 'mažeikiai', 'mazeikiai',
            'jonava', 'utena', 'kėdainiai', 'kedainiai', 'telšiai', 'telsiai',
            'ukmergė', 'ukmerge', 'tauragė', 'taurage', 'plungė', 'plunge',
            'kretinga', 'šilutė', 'silute', 'radviliškis', 'radviliskis',
            'palanga', 'gargždai', 'gargzdai', 'druskininkai', 'ktu', 'vtu'
        ],
        'Latvia': [
            'latvia', 'latvija', 'riga', 'rīga', 'daugavpils', 'liepāja',
            'liepaja', 'jelgava', 'jūrmala', 'jurmala', 'ventspils',
            'rēzekne', 'rezekne', 'valmiera', 'jēkabpils', 'jekabpils',
            'ogre', 'tukums', 'salaspils', 'cēsis', 'cesis', 'kuldīga',
            'kuldiga', 'olaine', 'saldus', 'talsi', 'dobele', 'bauska',
            'sigulda', 'madona', 'aizkraukle', 'ludza', 'alūksne', 'aluksne'
        ],
        'Estonia': [
            'estonia', 'eesti', 'tallinn', 'tartu', 'narva', 'pärnu',
            'parnu', 'kohtla-järve', 'kohtla-jarve', 'viljandi', 'rakvere',
            'maardu', 'sillamäe', 'sillamae', 'kuressaare', 'võru', 'voru',
            'valga', 'haapsalu', 'jõhvi', 'johvi', 'paide', 'keila',
            'kiviõli', 'tapa', 'põlva', 'polva', 'türi', 'turi', 'elva',
            'saue', 'rapla', 'ttu', 'taltech'
        ],
        'Iceland': [
            'iceland', 'ísland', 'island', 'reykjavik', 'reykjavík',
            'kópavogur', 'kopavogur', 'hafnarfjörður', 'hafnarfjordur',
            'akureyri', 'reykjanesbær', 'reykjanesbaer', 'garðabær',
            'gardabaer', 'mosfellsbær', 'mosfellsbaer', 'árborg', 'arborg',
            'akranes', 'fjarðabyggð', 'fjardabyggd', 'vestmannaeyjar',
            'selfoss', 'sauðárkrókur', 'saudarkrokur'
        ],
        'Luxembourg': [
            'luxembourg', 'luxemburg', 'lëtzebuerg', 'luxembourg-ville',
            'esch-sur-alzette', 'differdange', 'dudelange', 'ettelbruck',
            'diekirch', 'wiltz', 'echternach', 'rumelange', 'grevenmacher',
            'uni.lu', 'luxembourg institute'
        ],
        'Malta': [
            'malta', 'valletta', 'birkirkara', 'mosta', 'qormi',
            'żabbar', 'zabbar', 'sliema', 'naxxar', 'san pawl il-baħar',
            'san pawl il-bahar', 'victoria', 'rabat', 'marsaskala',
            'attard', 'paola', 'tarxien', 'pietà', 'pieta', 'hamrun',
            'university of malta', 'um.edu.mt'
        ],
        'Cyprus': [
            'cyprus', 'κύπρος', 'kypros', 'kıbrıs', 'nicosia', 'lefkosia',
            'λευκωσία', 'limassol', 'lemesos', 'λεμεσός', 'larnaca',
            'larnaka', 'λάρνακα', 'famagusta', 'ammochostos', 'αμμόχωστος',
            'paphos', 'pafos', 'πάφος', 'kyrenia', 'keryneia', 'κερύνεια',
            'morphou', 'güzelyurt', 'μόρφου', 'protaras', 'ayia napa',
            'paralimni', 'university of cyprus', 'ucy.ac.cy', 'cut.ac.cy'
        ],
        'Bosnia and Herzegovina': [
            'bosnia', 'herzegovina', 'bosna', 'hercegovina', 'sarajevo',
            'banja luka', 'tuzla', 'zenica', 'mostar', 'bijeljina',
            'brčko', 'brcko', 'bihać', 'bihac', 'prijedor', 'trebinje',
            'travnik', 'doboj', 'cazin', 'gradačac', 'gradacac', 'gradiška',
            'gradiska', 'konjic', 'gračanica', 'gracanica', 'ilijaš', 'ilijas',
            'ius.edu.ba', 'unsa.ba', 'etf.unsa.ba'
        ],
        'Montenegro': [
            'montenegro', 'crna gora', 'podgorica', 'nikšić', 'niksic',
            'pljevlja', 'bijelo polje', 'cetinje', 'bar', 'herceg novi',
            'berane', 'budva', 'ulcinj', 'tivat', 'rožaje', 'rozaje',
            'kotor', 'danilovgrad', 'mojkovac', 'plav', 'kolašin', 'kolasin',
            'žabljak', 'zabljak', 'plužine', 'pluzine', 'šavnik', 'savnik',
            'andrijevica', 'gusinje', 'petnjica', 'ucg.ac.me'
        ],
        'North Macedonia': [
            'macedonia', 'north macedonia', 'македонија', 'makedonija',
            'skopje', 'скопје', 'bitola', 'битола', 'kumanovo', 'куманово',
            'prilep', 'прилеп', 'tetovo', 'тетово', 'veles', 'велес',
            'ohrid', 'охрид', 'gostivar', 'гостивар', 'štip', 'štip',
            'струмица', 'strumnica', 'kavadarci', 'кавадарци', 'kočani',
            'кочани', 'kičevo', 'кичево', 'struga', 'струга', 'radoviš',
            'радовиш', 'gevgelija', 'гевгелија', 'debar', 'дебар'
        ],
        'Albania': [
            'albania', 'shqipëri', 'shqiperi', 'tirana', 'tiranë', 'tirane',
            'durrës', 'durres', 'vlorë', 'vlore', 'elbasan', 'shkodër',
            'shkoder', 'fier', 'korçë', 'korce', 'berat', 'lushnjë',
            'lushnje', 'kavajë', 'kavaje', 'patos', 'laç', 'lac',
            'kukës', 'kukes', 'lezhë', 'lezhe', 'pogradec', 'gjirokastër',
            'gjirokaster', 'sarandë', 'sarande', 'krujë', 'kruje',
            'university of tirana', 'upt.al'
        ]
    }
    
    # Check patterns
    for country, patterns in country_patterns.items():
        for pattern in patterns:
            if pattern in aff_lower:
                return country
    
    return "Unknown"

def extract_domain(email):
    """Extract domain from email"""
    if '@' in email:
        return email.split('@')[1].lower()
    return ''

def main():
    # File paths
    input_path = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/european_authors_with_emails_academic_only.json')
    output_dir = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country')
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    print("="*80)
    print("Extracting Authors by Country")
    print("="*80)
    
    # Load data
    print(f"\nLoading: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_authors = len(data['authors'])
    print(f"Total authors: {total_authors}")
    
    # Group authors by country
    by_country = defaultdict(list)
    
    for author_id, author_data in data['authors'].items():
        affiliation = author_data.get('primary_affiliation', '')
        country = extract_country_from_affiliation(affiliation)
        by_country[country].append((author_id, author_data))
    
    # Combine DACH countries
    dach_authors = []
    dach_authors.extend(by_country.pop('Germany', []))
    dach_authors.extend(by_country.pop('Switzerland', []))
    dach_authors.extend(by_country.pop('Austria', []))
    
    if dach_authors:
        by_country['DACH'] = dach_authors
    
    # Print statistics
    print(f"\n{'='*80}")
    print("Countries detected:")
    print(f"{'='*80}")
    
    sorted_countries = sorted(by_country.items(), key=lambda x: len(x[1]), reverse=True)
    
    for country, authors in sorted_countries:
        count = len(authors)
        percentage = (count / total_authors) * 100
        print(f"  {country:30s}: {count:4d} authors ({percentage:5.1f}%)")
    
    # Save individual country files
    print(f"\n{'='*80}")
    print("Creating country-specific JSON files...")
    print(f"{'='*80}")
    
    saved_files = []
    
    for country, authors in sorted_countries:
        # Create filename
        filename = f"european_authors_{country.lower().replace(' ', '_')}.json"
        filepath = output_dir / filename
        
        # Prepare data structure
        country_data = {
            'metadata': {
                'dataset_name': f'European Authors - {country}',
                'description': f'Academic authors from {country} with institutional emails',
                'created_date': datetime.now().isoformat(),
                'source': 'european_authors_with_emails_academic_only.json',
                'country': country,
                'total_authors': len(authors),
                'filters_applied': [
                    'European affiliations only',
                    'Institutional emails only',
                    'No HubSpot duplicates',
                    'No commercial domains',
                    f'Country: {country}'
                ],
                'notes': []
            },
            'authors': {}
        }
        
        # Add note for DACH
        if country == 'DACH':
            country_data['metadata']['notes'].append(
                'DACH includes Germany, Switzerland, and Austria'
            )
        
        # Add authors to structure
        for author_id, author_data in authors:
            country_data['authors'][author_id] = author_data
        
        # Save file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(country_data, f, indent=2, ensure_ascii=False)
        
        saved_files.append((country, len(authors), filepath))
        print(f"  ✓ Saved {country:30s}: {len(authors):4d} authors -> {filename}")
    
    # Create summary file
    summary_file = output_dir / 'countries_summary.json'
    summary_data = {
        'metadata': {
            'created_date': datetime.now().isoformat(),
            'source': 'european_authors_with_emails_academic_only.json',
            'total_authors': total_authors,
            'total_countries': len(sorted_countries)
        },
        'countries': [
            {
                'country': country,
                'author_count': len(authors),
                'percentage': round((len(authors) / total_authors) * 100, 2),
                'filename': f"european_authors_{country.lower().replace(' ', '_')}.json"
            }
            for country, authors in sorted_countries
        ]
    }
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n  ✓ Saved summary: countries_summary.json")
    
    # Final summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Total authors processed:  {total_authors}")
    print(f"Countries detected:       {len(sorted_countries)}")
    print(f"Files created:            {len(saved_files) + 1}")
    print(f"\nOutput directory: {output_dir}")
    print(f"\nTop 10 Countries by Author Count:")
    for i, (country, authors) in enumerate(sorted_countries[:10], 1):
        print(f"  {i:2d}. {country:30s}: {len(authors):4d} authors")
    
    print(f"\n{'='*80}")
    print("✓ Country extraction completed successfully!")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()

