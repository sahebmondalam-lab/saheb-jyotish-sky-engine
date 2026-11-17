# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Names and traditional text in English and Bengali. Every entry is (English, Bengali)."""

RASHI = [
    ("Mesha (Aries)", "মেষ"), ("Vrishabha (Taurus)", "বৃষ"), ("Mithuna (Gemini)", "মিথুন"),
    ("Karka (Cancer)", "কর্কট"), ("Simha (Leo)", "সিংহ"), ("Kanya (Virgo)", "কন্যা"),
    ("Tula (Libra)", "তুলা"), ("Vrishchika (Scorpio)", "বৃশ্চিক"), ("Dhanu (Sagittarius)", "ধনু"),
    ("Makara (Capricorn)", "মকর"), ("Kumbha (Aquarius)", "কুম্ভ"), ("Meena (Pisces)", "মীন"),
]
RASHI_SHORT = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", "Tula", "Vrishchika",
               "Dhanu", "Makara", "Kumbha", "Meena"]
WESTERN = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio",
           "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
RASHI_LORD = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars",
              "Jupiter", "Saturn", "Saturn", "Jupiter"]

PLANET = {
    "Sun": ("Sun (Surya)", "সূর্য"), "Moon": ("Moon (Chandra)", "চন্দ্র"),
    "Mars": ("Mars (Mangal)", "মঙ্গল"), "Mercury": ("Mercury (Budha)", "বুধ"),
    "Jupiter": ("Jupiter (Guru)", "বৃহস্পতি"), "Venus": ("Venus (Shukra)", "শুক্র"),
    "Saturn": ("Saturn (Shani)", "শনি"), "Rahu": ("Rahu (North Node)", "রাহু"),
    "Ketu": ("Ketu (South Node)", "কেতু"),
}
PLANET_ABBR = {"Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me", "Jupiter": "Ju",
               "Venus": "Ve", "Saturn": "Sa", "Rahu": "Ra", "Ketu": "Ke"}

NAKSHATRA = [
    ("Ashwini", "অশ্বিনী"), ("Bharani", "ভরণী"), ("Krittika", "কৃত্তিকা"), ("Rohini", "রোহিণী"),
    ("Mrigashira", "মৃগশিরা"), ("Ardra", "আর্দ্রা"), ("Punarvasu", "পুনর্বসু"), ("Pushya", "পুষ্যা"),
    ("Ashlesha", "অশ্লেষা"), ("Magha", "মঘা"), ("Purva Phalguni", "পূর্বফাল্গুনী"),
    ("Uttara Phalguni", "উত্তরফাল্গুনী"), ("Hasta", "হস্তা"), ("Chitra", "চিত্রা"), ("Swati", "স্বাতী"),
    ("Vishakha", "বিশাখা"), ("Anuradha", "অনুরাধা"), ("Jyeshtha", "জ্যেষ্ঠা"), ("Mula", "মূলা"),
    ("Purva Ashadha", "পূর্বাষাঢ়া"), ("Uttara Ashadha", "উত্তরাষাঢ়া"), ("Shravana", "শ্রবণা"),
    ("Dhanishta", "ধনিষ্ঠা"), ("Shatabhisha", "শতভিষা"), ("Purva Bhadrapada", "পূর্বভাদ্রপদ"),
    ("Uttara Bhadrapada", "উত্তরভাদ্রপদ"), ("Revati", "রেবতী"),
]
NAKSHATRA_TEXT = [
    ("Swift, healing, pioneering", "দ্রুতগতি, নিরাময়ী, অগ্রগামী"),
    ("Intense, disciplined, bears responsibility", "তীব্র, সংযমী, দায়িত্ব বহনকারী"),
    ("Sharp, purifying, outspoken", "ধারালো, শুদ্ধিকারী, স্পষ্টভাষী"),
    ("Creative, attractive, fertile", "সৃজনশীল, আকর্ষণীয়, উর্বর"),
    ("Searching, curious, gentle", "অন্বেষী, কৌতূহলী, কোমল"),
    ("Stormy, transformative, deeply emotional", "ঝঞ্ঝাময়, রূপান্তরকারী, গভীর আবেগপ্রবণ"),
    ("Renewing, optimistic, returns after setbacks", "নবায়নশীল, আশাবাদী, ধাক্কার পর ফিরে আসে"),
    ("Nourishing, protective, traditionally very auspicious", "পুষ্টিদায়ী, রক্ষক, ঐতিহ্যগতভাবে অত্যন্ত শুভ"),
    ("Shrewd, intuitive, hypnotic", "চতুর, সহজাতবোধসম্পন্ন, সম্মোহনী"),
    ("Regal, proud of ancestry, authoritative", "রাজকীয়, পূর্বপুরুষের গর্ব, কর্তৃত্বশীল"),
    ("Pleasure-loving, creative, generous", "আমুদে, সৃজনশীল, উদার"),
    ("Dependable, helpful, steady in friendship", "নির্ভরযোগ্য, সহায়ক, বন্ধুত্বে স্থির"),
    ("Skilful with the hands, resourceful, witty", "হাতের কাজে দক্ষ, কৌশলী, রসিক"),
    ("Artistic, striking, loves craftsmanship", "শিল্পীমন, নজরকাড়া, কারুকাজ ভালোবাসে"),
    ("Independent, flexible like the wind", "স্বাধীন, হাওয়ার মতো নমনীয়"),
    ("Goal-driven, determined, strongly ambitious", "লক্ষ্যমুখী, দৃঢ়, তীব্র উচ্চাকাঙ্ক্ষী"),
    ("Devoted, friendly, succeeds through cooperation", "নিবেদিত, বন্ধুবৎসল, সহযোগিতায় সাফল্য"),
    ("Senior, protective, strong sense of status", "জ্যেষ্ঠ, রক্ষক, মর্যাদাবোধ প্রবল"),
    ("Root-seeker, investigative, breaks down to rebuild", "মূল-সন্ধানী, অনুসন্ধিৎসু, ভেঙে নতুন করে গড়ে"),
    ("Invincible, persuasive, enthusiastic", "অপরাজেয়, প্রভাবশালী, উদ্যমী"),
    ("Principled, lasting victory, patient", "নীতিনিষ্ঠ, স্থায়ী জয়, ধৈর্যশীল"),
    ("Listener, learner, a natural connector", "শ্রোতা, শিক্ষার্থী, সেতুবন্ধনকারী"),
    ("Rhythmic, prosperous, ambitious", "ছন্দময়, সমৃদ্ধ, উচ্চাকাঙ্ক্ষী"),
    ("Healer-minded, private, independent thinker", "নিরাময়ী মন, অন্তর্মুখী, স্বাধীনচিন্তক"),
    ("Intense, idealistic, transformative", "তীব্র, আদর্শবাদী, রূপান্তরকারী"),
    ("Deep, calm, wise and charitable", "গভীর, শান্ত, প্রাজ্ঞ ও দানশীল"),
    ("Gentle, nurturing, protector of travellers", "কোমল, লালনকারী, পথিকের রক্ষক"),
]

# Vimshottari order and years
DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18,
               "Jupiter": 16, "Saturn": 19, "Mercury": 17}
DASHA_TEXT = {
    "Ketu": ("Detachment, spiritual searching, sudden changes; letting go of what no longer serves.",
             "অনাসক্তি, আধ্যাত্মিক অন্বেষণ, আকস্মিক পরিবর্তন; যা আর কাজে লাগে না তা ছেড়ে দেওয়ার সময়।"),
    "Venus": ("Relationships, comfort, arts, money matters and enjoyment come to the fore.",
              "সম্পর্ক, আরাম, শিল্প, অর্থ ও উপভোগের বিষয়গুলো সামনে আসে।"),
    "Sun": ("Career status, authority, father-figures, health and self-confidence are in focus.",
            "কর্মজীবনের মর্যাদা, কর্তৃত্ব, পিতৃস্থানীয়দের সাথে সম্পর্ক, স্বাস্থ্য ও আত্মবিশ্বাস গুরুত্ব পায়।"),
    "Moon": ("Emotions, home, mother, public dealings and peace of mind are emphasised.",
             "আবেগ, গৃহ, মা, জনসংযোগ ও মনের শান্তি প্রাধান্য পায়।"),
    "Mars": ("Energy, courage, property, siblings and conflict; good for bold action, needs patience.",
             "শক্তি, সাহস, সম্পত্তি, ভাইবোন ও সংঘাত; সাহসী পদক্ষেপের পক্ষে ভালো, তবে ধৈর্য দরকার।"),
    "Rahu": ("Ambition, foreign links, technology and unconventional paths; confusion if rushed.",
             "উচ্চাকাঙ্ক্ষা, বিদেশ-যোগ, প্রযুক্তি ও অপ্রচলিত পথ; তাড়াহুড়ো করলে বিভ্রান্তিও আসে।"),
    "Jupiter": ("Growth, learning, children, wisdom and fortune; generally expanding and supportive.",
                "বৃদ্ধি, শিক্ষা, সন্তান, প্রজ্ঞা ও ভাগ্য; সাধারণত প্রসারণ ও সহায়তার সময়।"),
    "Saturn": ("Hard work, discipline, delays and responsibility; rewards come slowly but last.",
               "কঠোর পরিশ্রম, শৃঙ্খলা, বিলম্ব ও দায়িত্ব; ফল আসে ধীরে, কিন্তু টেকে।"),
    "Mercury": ("Communication, business, studies, skills and travel are highlighted.",
                "যোগাযোগ, ব্যবসা, পড়াশোনা, দক্ষতা ও ভ্রমণ গুরুত্ব পায়।"),
}

RASHI_TEXT = [
    ("Energetic, courageous and direct; a natural starter who dislikes waiting.",
     "উদ্যমী, সাহসী ও স্পষ্টবক্তা; কাজ শুরু করতে ভালোবাসে, অপেক্ষা পছন্দ করে না।"),
    ("Steady, patient and practical; loves comfort, good food and loyalty.",
     "স্থির, ধৈর্যশীল ও বাস্তববাদী; আরাম, ভালো খাবার আর বিশ্বস্ততা ভালোবাসে।"),
    ("Curious, witty and adaptable; quick with words and ideas.",
     "কৌতূহলী, রসিক ও মানিয়ে নিতে পটু; কথায় ও ভাবনায় চটপটে।"),
    ("Caring, emotional and protective; strongly attached to home and family.",
     "যত্নশীল, আবেগপ্রবণ ও রক্ষাকারী; ঘর ও পরিবারের প্রতি গভীর টান।"),
    ("Confident, generous and proud; a natural leader who wants recognition.",
     "আত্মবিশ্বাসী, উদার ও আত্মমর্যাদাবান; জন্মগত নেতা, স্বীকৃতি চায়।"),
    ("Analytical, careful and service-minded; notices details others miss.",
     "বিশ্লেষণী, সতর্ক ও সেবামনস্ক; অন্যের চোখ এড়ানো খুঁটিনাটি ধরে ফেলে।"),
    ("Balanced, fair-minded and artistic; seeks harmony and partnership.",
     "ভারসাম্যপ্রিয়, ন্যায়বোধসম্পন্ন ও শিল্পমনস্ক; সম্প্রীতি ও সঙ্গ খোঁজে।"),
    ("Intense, determined and private; deep emotions and strong willpower.",
     "তীব্র, দৃঢ়সংকল্প ও অন্তর্মুখী; গভীর আবেগ আর প্রবল ইচ্ছাশক্তি।"),
    ("Optimistic, freedom-loving and philosophical; drawn to travel and learning.",
     "আশাবাদী, স্বাধীনচেতা ও দার্শনিক; ভ্রমণ ও শেখার দিকে টান।"),
    ("Disciplined, ambitious and responsible; builds slowly but lasts long.",
     "শৃঙ্খলাপরায়ণ, উচ্চাকাঙ্ক্ষী ও দায়িত্বশীল; ধীরে গড়ে, কিন্তু টেকে অনেকদিন।"),
    ("Independent, inventive and humanitarian; thinks differently from the crowd.",
     "স্বাধীন, উদ্ভাবনী ও মানবদরদি; ভিড়ের চেয়ে আলাদা করে ভাবে।"),
    ("Compassionate, imaginative and intuitive; sensitive to others' feelings.",
     "করুণাময়, কল্পনাপ্রবণ ও সহজাতবোধসম্পন্ন; অন্যের অনুভূতির প্রতি সংবেদনশীল।"),
]

# ---- panchang names
TITHI = [("Pratipada", "প্রতিপদ"), ("Dwitiya", "দ্বিতীয়া"), ("Tritiya", "তৃতীয়া"), ("Chaturthi", "চতুর্থী"),
         ("Panchami", "পঞ্চমী"), ("Shashthi", "ষষ্ঠী"), ("Saptami", "সপ্তমী"), ("Ashtami", "অষ্টমী"),
         ("Navami", "নবমী"), ("Dashami", "দশমী"), ("Ekadashi", "একাদশী"), ("Dwadashi", "দ্বাদশী"),
         ("Trayodashi", "ত্রয়োদশী"), ("Chaturdashi", "চতুর্দশী")]
TITHI_FULL = ("Purnima (Full Moon)", "পূর্ণিমা")
TITHI_NEW = ("Amavasya (New Moon)", "অমাবস্যা")
PAKSHA = {"shukla": ("Shukla Paksha (waxing)", "শুক্লপক্ষ"), "krishna": ("Krishna Paksha (waning)", "কৃষ্ণপক্ষ")}

YOGA = [("Vishkambha", "বিষ্কম্ভ"), ("Priti", "প্রীতি"), ("Ayushman", "আয়ুষ্মান"), ("Saubhagya", "সৌভাগ্য"),
        ("Shobhana", "শোভন"), ("Atiganda", "অতিগণ্ড"), ("Sukarma", "সুকর্মা"), ("Dhriti", "ধৃতি"),
        ("Shula", "শূল"), ("Ganda", "গণ্ড"), ("Vriddhi", "বৃদ্ধি"), ("Dhruva", "ধ্রুব"),
        ("Vyaghata", "ব্যাঘাত"), ("Harshana", "হর্ষণ"), ("Vajra", "বজ্র"), ("Siddhi", "সিদ্ধি"),
        ("Vyatipata", "ব্যতীপাত"), ("Variyana", "বরীয়ান"), ("Parigha", "পরিঘ"), ("Shiva", "শিব"),
        ("Siddha", "সিদ্ধ"), ("Sadhya", "সাধ্য"), ("Shubha", "শুভ"), ("Shukla", "শুক্ল"),
        ("Brahma", "ব্রহ্ম"), ("Indra", "ইন্দ্র"), ("Vaidhriti", "বৈধৃতি")]

KARANA_MOVABLE = [("Bava", "বব"), ("Balava", "বালব"), ("Kaulava", "কৌলব"), ("Taitila", "তৈতিল"),
                  ("Gara", "গর"), ("Vanija", "বণিজ"), ("Vishti (Bhadra)", "বিষ্টি (ভদ্রা)")]
KARANA_FIXED = {0: ("Kimstughna", "কিংস্তুঘ্ন"), 57: ("Shakuni", "শকুনি"),
                58: ("Chatushpada", "চতুষ্পদ"), 59: ("Naga", "নাগ")}

VARA = [("Sunday (Ravivar)", "রবিবার"), ("Monday (Somvar)", "সোমবার"), ("Tuesday (Mangalvar)", "মঙ্গলবার"),
        ("Wednesday (Budhvar)", "বুধবার"), ("Thursday (Guruvar)", "বৃহস্পতিবার"),
        ("Friday (Shukravar)", "শুক্রবার"), ("Saturday (Shanivar)", "শনিবার")]
VARA_LORD = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

MOON_PHASE = [("New Moon", "অমাবস্যার কাছাকাছি নতুন চাঁদ"), ("Waxing Crescent", "শুক্লপক্ষের বাঁকা চাঁদ"),
              ("First Quarter", "শুক্লপক্ষের অর্ধচন্দ্র"), ("Waxing Gibbous", "শুক্লপক্ষের স্ফীত চাঁদ"),
              ("Full Moon", "পূর্ণিমার কাছাকাছি পূর্ণ চাঁদ"), ("Waning Gibbous", "কৃষ্ণপক্ষের স্ফীত চাঁদ"),
              ("Last Quarter", "কৃষ্ণপক্ষের অর্ধচন্দ্র"), ("Waning Crescent", "কৃষ্ণপক্ষের ক্ষীণ চাঁদ")]

DIGNITY = {"exalted": ("exalted", "উচ্চস্থ"), "debilitated": ("debilitated", "নীচস্থ"),
           "own": ("own sign", "স্বক্ষেত্রী"), "neutral": ("", "")}
EXALT = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5, "Jupiter": 3, "Venus": 11, "Saturn": 6}
DEBIL = {k: (v + 6) % 12 for k, v in EXALT.items()}
OWN = {"Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5], "Jupiter": [8, 11],
       "Venus": [1, 6], "Saturn": [9, 10]}

NUMEROLOGY = {
    1: ("Sun", "Leader, independent, ambitious", "নেতা, স্বাধীন, উচ্চাকাঙ্ক্ষী"),
    2: ("Moon", "Sensitive, cooperative, imaginative", "সংবেদনশীল, সহযোগী, কল্পনাপ্রবণ"),
    3: ("Jupiter", "Expressive, optimistic, a teacher at heart", "প্রকাশক্ষম, আশাবাদী, মনে মনে শিক্ষক"),
    4: ("Rahu", "Practical, hard-working, with an unconventional streak", "বাস্তববাদী, পরিশ্রমী, কিছুটা অপ্রচলিত"),
    5: ("Mercury", "Quick, versatile, loves change and trade", "চটপটে, বহুমুখী, পরিবর্তন ও বাণিজ্য ভালোবাসে"),
    6: ("Venus", "Loving, artistic, responsible for family", "স্নেহশীল, শিল্পমনস্ক, পরিবারের প্রতি দায়িত্বশীল"),
    7: ("Ketu", "Reflective, research-minded, private", "চিন্তাশীল, গবেষণামনস্ক, অন্তর্মুখী"),
    8: ("Saturn", "Persistent, disciplined, late but steady rewards", "অধ্যবসায়ী, শৃঙ্খলাপরায়ণ, দেরিতে কিন্তু স্থির ফল"),
    9: ("Mars", "Brave, energetic, protective, humanitarian", "সাহসী, প্রাণবন্ত, রক্ষক, মানবদরদি"),
}

YOGA_TEXT = {
    "gajakesari": (("Gajakesari Yoga", "গজকেশরী যোগ"),
                   ("Jupiter in a kendra (1/4/7/10) from the Moon: traditionally gives good reputation, wisdom and support.",
                    "চন্দ্র থেকে কেন্দ্রে (১/৪/৭/১০) বৃহস্পতি: ঐতিহ্যগতভাবে সুনাম, প্রজ্ঞা ও সহায়তা দেয়।")),
    "budhaditya": (("Budhaditya Yoga", "বুধাদিত্য যোগ"),
                   ("Sun and Mercury in the same sign: sharp intellect and communication skill.",
                    "সূর্য ও বুধ একই রাশিতে: তীক্ষ্ণ বুদ্ধি ও যোগাযোগ দক্ষতা।")),
    "chandra_mangala": (("Chandra-Mangala Yoga", "চন্দ্র-মঙ্গল যোগ"),
                        ("Moon and Mars in the same sign: drive for earning and enterprise; emotions can run hot.",
                         "চন্দ্র ও মঙ্গল একই রাশিতে: উপার্জন ও উদ্যোগের তাগিদ; আবেগে তীব্রতাও থাকতে পারে।")),
    "ruchaka": (("Ruchaka Yoga (Mahapurusha)", "রুচক যোগ (মহাপুরুষ)"),
                ("Mars strong in a kendra: courage, leadership, physical strength.",
                 "কেন্দ্রে বলবান মঙ্গল: সাহস, নেতৃত্ব, শারীরিক বল।")),
    "bhadra": (("Bhadra Yoga (Mahapurusha)", "ভদ্র যোগ (মহাপুরুষ)"),
               ("Mercury strong in a kendra: intellect, eloquence, business sense.",
                "কেন্দ্রে বলবান বুধ: বুদ্ধি, বাগ্মিতা, ব্যবসায়িক বোধ।")),
    "hamsa": (("Hamsa Yoga (Mahapurusha)", "হংস যোগ (মহাপুরুষ)"),
              ("Jupiter strong in a kendra: wisdom, ethics, respect from others.",
               "কেন্দ্রে বলবান বৃহস্পতি: প্রজ্ঞা, নীতিবোধ, অন্যের শ্রদ্ধা।")),
    "malavya": (("Malavya Yoga (Mahapurusha)", "মালব্য যোগ (মহাপুরুষ)"),
                ("Venus strong in a kendra: comfort, charm, artistic gifts.",
                 "কেন্দ্রে বলবান শুক্র: আরাম, আকর্ষণ, শিল্পপ্রতিভা।")),
    "shasha": (("Shasha Yoga (Mahapurusha)", "শশ যোগ (মহাপুরুষ)"),
               ("Saturn strong in a kendra: discipline, endurance, authority earned by long effort.",
                "কেন্দ্রে বলবান শনি: শৃঙ্খলা, ধৈর্য, দীর্ঘ পরিশ্রমে অর্জিত কর্তৃত্ব।")),
    "kemadruma": (("Kemadruma (possible)", "কেমদ্রুম (সম্ভাব্য)"),
                  ("No planet beside the Moon (apart from Sun/nodes): phases of loneliness or insecurity are said to be possible; many traditional cancellations exist.",
                   "চন্দ্রের আশেপাশে (সূর্য ও রাহু-কেতু বাদে) কোনো গ্রহ নেই: নিঃসঙ্গতা বা নিরাপত্তাহীনতার পর্ব আসতে পারে বলা হয়; ঐতিহ্যে অনেক শর্তে এর দোষ কেটে যায়।")),
    "mangal_dosha": (("Mangal (Kuja) Dosha", "মঙ্গল দোষ (কুজ দোষ)"),
                     ("Mars in house 1/4/7/8/12 from the Lagna: traditionally checked in marriage matching; its effect is debated and often cancelled.",
                      "লগ্ন থেকে ১/৪/৭/৮/১২ ভাবে মঙ্গল: বিয়ের মিলানে ঐতিহ্যগতভাবে দেখা হয়; এর ফল নিয়ে মতভেদ আছে এবং অনেক ক্ষেত্রে দোষ কাটে।")),
    "kaal_sarp": (("Kaal Sarp Yoga", "কালসর্প যোগ"),
                  ("All seven planets lie between Rahu and Ketu: traditionally read as a life of sharp swings and late success.",
                   "সাত গ্রহই রাহু ও কেতুর মাঝখানে: ঐতিহ্যে উত্থান-পতনময় জীবন ও দেরিতে সাফল্য বোঝায়।")),
}

SADE_SATI_TEXT = {
    12: ("Sade Sati - first phase (Saturn in 12th from Moon): expenses, sleep and inner restlessness are emphasised.",
         "সাড়েসাতি - প্রথম ধাপ (চন্দ্র থেকে ১২শ রাশিতে শনি): খরচ, ঘুম ও মনের অস্থিরতা বেশি টের পাওয়া যায়।"),
    1: ("Sade Sati - peak phase (Saturn over the natal Moon sign): tests of patience, health and responsibilities.",
        "সাড়েসাতি - মধ্য ধাপ (জন্মরাশির উপর শনি): ধৈর্য, স্বাস্থ্য ও দায়িত্বের পরীক্ষা।"),
    2: ("Sade Sati - last phase (Saturn in 2nd from Moon): money and family matters need care; relief approaches.",
        "সাড়েসাতি - শেষ ধাপ (চন্দ্র থেকে ২য় রাশিতে শনি): অর্থ ও পরিবারে যত্ন দরকার; স্বস্তি এগিয়ে আসছে।"),
    4: ("Dhaiya / Kantaka Shani (Saturn in 4th from Moon): pressure on home, peace of mind and property.",
        "ঢাইয়া / কণ্টক শনি (চন্দ্র থেকে ৪র্থ রাশিতে শনি): গৃহ, মনের শান্তি ও সম্পত্তিতে চাপ।"),
    8: ("Dhaiya / Ashtama Shani (Saturn in 8th from Moon): health and sudden events call for caution.",
        "ঢাইয়া / অষ্টম শনি (চন্দ্র থেকে ৮ম রাশিতে শনি): স্বাস্থ্য ও আকস্মিক ঘটনায় সতর্কতা দরকার।"),
}

# Gochar: traditional favourable houses counted from the natal Moon sign
GOCHAR_GOOD = {
    "Saturn": {3, 6, 11}, "Jupiter": {2, 5, 7, 9, 11}, "Rahu": {3, 6, 10, 11}, "Ketu": {3, 6, 11},
}
GOCHAR_TEXT = {
    True: ("traditionally favourable", "ঐতিহ্যগতভাবে অনুকূল"),
    False: ("traditionally needs care", "ঐতিহ্যগতভাবে সতর্কতার সময়"),
}

DISCLAIMER = (
    "Jyotish is a traditional belief system, not a proven science. The astronomical positions here are "
    "computed (and checkable); the readings and 'predictions' are traditional interpretations for "
    "reflection and entertainment. Do not use them for medical, legal, financial or safety decisions.",
    "জ্যোতিষ একটি ঐতিহ্যগত বিশ্বাসব্যবস্থা, প্রমাণিত বিজ্ঞান নয়। এখানে গ্রহ-নক্ষত্রের অবস্থান গণনা করা "
    "(এবং যাচাই করা যায়), কিন্তু ফলাফল ও 'ভবিষ্যদ্বাণী' ঐতিহ্যগত ব্যাখ্যা, ভাবনা ও বিনোদনের জন্য। "
    "চিকিৎসা, আইন, অর্থ বা নিরাপত্তার সিদ্ধান্তে এর ওপর ভরসা করবেন না।",
)

CREDIT = ("Saheb Jyotish Sky Engine - created by Saheb Mondal (CC BY-NC-SA 4.0)",
          "সাহেব জ্যোতিষ স্কাই ইঞ্জিন - নির্মাতা সাহেব মন্ডল (CC BY-NC-SA 4.0)")

# Built-in place table (name -> lat, lon_east, IANA timezone). Use --lat/--lon/--tz for any other place.
PLACES = {
    "kolkata": (22.5726, 88.3639, "Asia/Kolkata"), "howrah": (22.5958, 88.2636, "Asia/Kolkata"),
    "siliguri": (26.7271, 88.3953, "Asia/Kolkata"), "durgapur": (23.5204, 87.3119, "Asia/Kolkata"),
    "asansol": (23.6739, 86.9524, "Asia/Kolkata"), "delhi": (28.6139, 77.2090, "Asia/Kolkata"),
    "mumbai": (19.0760, 72.8777, "Asia/Kolkata"), "chennai": (13.0827, 80.2707, "Asia/Kolkata"),
    "bengaluru": (12.9716, 77.5946, "Asia/Kolkata"), "hyderabad": (17.3850, 78.4867, "Asia/Kolkata"),
    "pune": (18.5204, 73.8567, "Asia/Kolkata"), "ahmedabad": (23.0225, 72.5714, "Asia/Kolkata"),
    "jaipur": (26.9124, 75.7873, "Asia/Kolkata"), "lucknow": (26.8467, 80.9462, "Asia/Kolkata"),
    "patna": (25.5941, 85.1376, "Asia/Kolkata"), "varanasi": (25.3176, 82.9739, "Asia/Kolkata"),
    "guwahati": (26.1445, 91.7362, "Asia/Kolkata"), "agartala": (23.8315, 91.2868, "Asia/Kolkata"),
    "bhubaneswar": (20.2961, 85.8245, "Asia/Kolkata"), "dhaka": (23.8103, 90.4125, "Asia/Dhaka"),
    "chittagong": (22.3569, 91.7832, "Asia/Dhaka"), "kathmandu": (27.7172, 85.3240, "Asia/Kathmandu"),
    "london": (51.5074, -0.1278, "Europe/London"), "new york": (40.7128, -74.0060, "America/New_York"),
}

# Moon-phase moments (elongation 0 / 90 / 180 / 270 degrees), used by the day-events report
PHASE_EVENT = [("New Moon (Amavasya)", "অমাবস্যা (নতুন চাঁদ)"), ("First Quarter Moon", "শুক্লপক্ষের অর্ধচন্দ্র (প্রথম চতুর্থাংশ)"),
               ("Full Moon (Purnima)", "পূর্ণিমা"), ("Last Quarter Moon", "কৃষ্ণপক্ষের অর্ধচন্দ্র (শেষ চতুর্থাংশ)")]


_IST = "Asia/Kolkata"
PLACES.update({
    # India
    "chennai": (13.0827, 80.2707, _IST), "surat": (21.1702, 72.8311, _IST), "kanpur": (26.4499, 80.3319, _IST),
    "agra": (27.1767, 78.0081, _IST), "nagpur": (21.1458, 79.0882, _IST), "indore": (22.7196, 75.8577, _IST),
    "bhopal": (23.2599, 77.4126, _IST), "ranchi": (23.3441, 85.3096, _IST), "raipur": (21.2514, 81.6296, _IST),
    "chandigarh": (30.7333, 76.7794, _IST), "amritsar": (31.6340, 74.8723, _IST), "kochi": (9.9312, 76.2673, _IST),
    "thiruvananthapuram": (8.5241, 76.9366, _IST), "dehradun": (30.3165, 78.0322, _IST), "shimla": (31.1048, 77.1734, _IST),
    "srinagar": (34.0837, 74.7973, _IST), "imphal": (24.8170, 93.9368, _IST), "shillong": (25.5788, 91.8933, _IST),
    "gangtok": (27.3389, 88.6065, _IST), "puducherry": (11.9416, 79.8083, _IST), "visakhapatnam": (17.6868, 83.2185, _IST),
    "coimbatore": (11.0168, 76.9558, _IST), "madurai": (9.9252, 78.1198, _IST), "mysuru": (12.2958, 76.6394, _IST),
    "jamshedpur": (22.8046, 86.2029, _IST), "dhanbad": (23.7957, 86.4304, _IST), "cuttack": (20.4625, 85.8830, _IST),
    "kharagpur": (22.3460, 87.2320, _IST), "baharampur": (24.1048, 88.2517, _IST), "malda": (25.0108, 88.1411, _IST),
    "cooch behar": (26.3452, 89.4482, _IST), "jalpaiguri": (26.5167, 88.7333, _IST), "darjeeling": (27.0410, 88.2663, _IST),
    "bardhaman": (23.2324, 87.8615, _IST), "krishnanagar": (23.4058, 88.4850, _IST),
    # South Asia
    "khulna": (22.8456, 89.5403, "Asia/Dhaka"), "rajshahi": (24.3745, 88.6042, "Asia/Dhaka"), "sylhet": (24.8949, 91.8687, "Asia/Dhaka"),
    "colombo": (6.9271, 79.8612, _IST), "karachi": (24.8607, 67.0011, "Asia/Karachi"), "lahore": (31.5497, 74.3436, "Asia/Karachi"),
    "islamabad": (33.6844, 73.0479, "Asia/Karachi"),
    # world
    "singapore": (1.3521, 103.8198, "Asia/Singapore"), "kuala lumpur": (3.1390, 101.6869, "Asia/Kuala_Lumpur"),
    "dubai": (25.2048, 55.2708, "Asia/Dubai"), "riyadh": (24.7136, 46.6753, "Asia/Riyadh"), "doha": (25.2854, 51.5310, "Asia/Qatar"),
    "bangkok": (13.7563, 100.5018, "Asia/Bangkok"), "tokyo": (35.6762, 139.6503, "Asia/Tokyo"),
    "beijing": (39.9042, 116.4074, "Asia/Shanghai"), "shanghai": (31.2304, 121.4737, "Asia/Shanghai"),
    "hong kong": (22.3193, 114.1694, "Asia/Hong_Kong"), "sydney": (-33.8688, 151.2093, "Australia/Sydney"),
    "melbourne": (-37.8136, 144.9631, "Australia/Melbourne"), "auckland": (-36.8485, 174.7633, "Pacific/Auckland"),
    "paris": (48.8566, 2.3522, "Europe/Paris"), "berlin": (52.5200, 13.4050, "Europe/Berlin"), "rome": (41.9028, 12.4964, "Europe/Rome"),
    "madrid": (40.4168, -3.7038, "Europe/Madrid"), "moscow": (55.7558, 37.6173, "Europe/Moscow"), "istanbul": (41.0082, 28.9784, "Europe/Istanbul"),
    "cairo": (30.0444, 31.2357, "Africa/Cairo"), "nairobi": (-1.2921, 36.8219, "Africa/Nairobi"),
    "johannesburg": (-26.2041, 28.0473, "Africa/Johannesburg"), "lagos": (6.5244, 3.3792, "Africa/Lagos"),
    "toronto": (43.6532, -79.3832, "America/Toronto"), "chicago": (41.8781, -87.6298, "America/Chicago"),
    "los angeles": (34.0522, -118.2437, "America/Los_Angeles"), "san francisco": (37.7749, -122.4194, "America/Los_Angeles"),
    "houston": (29.7604, -95.3698, "America/Chicago"), "mexico city": (19.4326, -99.1332, "America/Mexico_City"),
    "sao paulo": (-23.5505, -46.6333, "America/Sao_Paulo"), "buenos aires": (-34.6037, -58.3816, "America/Argentina/Buenos_Aires"),
})
# alternative spellings, old names, and Bengali / Hindi names
PLACE_ALIASES = {
    "calcutta": "kolkata", "কলকাতা": "kolkata", "कोलकाता": "kolkata", "bombay": "mumbai", "মুম্বই": "mumbai", "মুম্বাই": "mumbai", "मुंबई": "mumbai",
    "madras": "chennai", "চেন্নাই": "chennai", "चेन्नई": "chennai", "bangalore": "bengaluru", "बेंगलुरु": "bengaluru", "বেঙ্গালুরু": "bengaluru",
    "new delhi": "delhi", "দিল্লি": "delhi", "দিল্লী": "delhi", "दिल्ली": "delhi", "benares": "varanasi", "banaras": "varanasi", "काशी": "varanasi",
    "वाराणसी": "varanasi", "বারাণসী": "varanasi", "dacca": "dhaka", "ঢাকা": "dhaka", "ढाका": "dhaka", "chattogram": "chittagong", "চট্টগ্রাম": "chittagong",
    "trivandrum": "thiruvananthapuram", "cochin": "kochi", "mysore": "mysuru", "vizag": "visakhapatnam", "pondicherry": "puducherry",
    "শিলিগুড়ি": "siliguri", "হাওড়া": "howrah", "দুর্গাপুর": "durgapur", "আসানসোল": "asansol", "লখনউ": "lucknow", "लखनऊ": "lucknow", "जयपुर": "jaipur",
    "पटना": "patna", "পাটনা": "patna", "गुवाहाटी": "guwahati", "গুয়াহাটি": "guwahati", "कानपुर": "kanpur", "आगरा": "agra", "भोपाल": "bhopal",
    "इंदौर": "indore", "नागपुर": "nagpur", "पुणे": "pune", "হায়দরাবাদ": "hyderabad", "हैदराबाद": "hyderabad", "কাঠমান্ডু": "kathmandu", "काठमांडू": "kathmandu",
    "বর্ধমান": "bardhaman", "burdwan": "bardhaman", "কৃষ্ণনগর": "krishnanagar", "দার্জিলিং": "darjeeling", "মালদা": "malda", "english bazar": "malda",
    "kolkata, india": "kolkata", "nyc": "new york", "new york city": "new york", "ny": "new york", "la": "los angeles", "sf": "san francisco",
}
