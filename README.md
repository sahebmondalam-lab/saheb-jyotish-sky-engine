# Saheb Jyotish Sky Engine · সাহেব জ্যোতিষ স্কাই ইঞ্জিন · साहेब ज्योतिष स्काई इंजन

**Open Vedic astrology (Jyotish) + sky engine. Kundli, planets, nakshatra, panchang, dasha, forecast, in English, বাংলা and हिन्दी. Built so AI assistants can use it too.**

Created by **Saheb Mondal (সাহেব মন্ডল / साहेब मंडल)** · License: **CC BY-NC-SA 4.0** (open, credit required, no commercial use, changes must stay open)

> ⚠️ Jyotish is a traditional belief system, not proven science. Planet positions are computed astronomy (checkable); the readings and forecasts are traditional interpretations for culture and fun. Don't use them for medical, legal, financial or safety decisions.
> ⚠️ জ্যোতিষ ঐতিহ্যগত বিশ্বাস, প্রমাণিত বিজ্ঞান নয়। গ্রহের অবস্থান গাণিতিকভাবে গণনা করা (যাচাই করা যায়); ফলাফল ও পূর্বাভাস ঐতিহ্যগত ব্যাখ্যা। চিকিৎসা, আইন, অর্থ বা নিরাপত্তার সিদ্ধান্তে ভরসা করবেন না।
> ⚠️ ज्योतिष एक पारंपरिक विश्वास-प्रणाली है, प्रमाणित विज्ञान नहीं। ग्रहों की स्थिति गणना से निकाली गई है (जाँची जा सकती है); फल और भविष्यवाणी पारंपरिक व्याख्याएँ हैं। चिकित्सा, कानून, पैसे या सुरक्षा के फ़ैसलों में इन पर भरोसा न करें।

---

## English

### What it does
Give a birth date, time and place (or just any date) and it prints:
- **Core signs**: Lagna (ascendant), Moon sign (Janma Rashi), birth Nakshatra + pada, Sun sign, plus Western signs
- **Planet positions** (sidereal Lahiri and tropical): Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu, with house, nakshatra, speed, retrograde, exalted/debilitated/own sign
- **Rashi chart** (South-Indian layout in plain text)
- **Panchang**: tithi, nakshatra, yoga, karana, vara, moon phase, sunrise/sunset, Rahu Kaal, Yamaganda, Gulika, Abhijit and Brahma Muhurta
- **Yogas and doshas**: Gajakesari, Budhaditya, Pancha Mahapurusha, Kemadruma, Mangal dosha, Kaal Sarp, ...
- **Vimshottari Dasha**: current Mahadasha and Antardasha with dates and themes
- **Future forecast**: Saturn, Jupiter and Rahu sign changes with dates and houses from your Moon, plus **Sade Sati / Dhaiya** windows
- **Sky on any date** (`sky` command): where every planet and nakshatra was or will be at that moment
- **Numerology**: Mulank and Bhagyank
- Output in **English, Bengali, Hindi**, or all together; **JSON** for programs and AI

### Why you can trust the numbers
All positions come from published open algorithms (NASA/JPL planetary elements, Meeus lunar series, Espenak-Meeus Delta-T, Lahiri ayanamsa); see [docs/SOURCES.md](docs/SOURCES.md). Automated tests check known sankrantis, new/full moons, ingress dates and a published chart. [docs/ACCURACY.md](docs/ACCURACY.md) lists what is checked, what is **not yet** (a live comparison with NASA/JPL Horizons; a script for it is included), and the expected error.

### Install and run
Needs only Python 3.9+. No other packages (on Windows: `pip install tzdata`). Pure Python, so it should also run in Termux (not yet tested there).

```bash
git clone https://github.com/sahebmondalam-lab/saheb-jyotish-sky-engine
cd saheb-jyotish-sky-engine

# Birth chart + dasha + 5-year forecast
python3 -m jyotish kundli --date 1995-08-15 --time 14:30 --place kolkata --name "Your Name" --lang all

# The sky at any moment (planets, nakshatra, moon phase)
python3 -m jyotish sky --date 2026-11-16 --time 10:00 --place kolkata --lang hi

# Panchang for a day
python3 -m jyotish panchang --date 2026-11-16 --place kolkata --lang en
# everything that happens in the sky on one day: Purnima/Amavasya moments, Sankranti, retrograde turns, tithi/nakshatra/yoga timeline
python3 -m jyotish day --date 1992-01-27 --place kolkata --lang all

# Any place on Earth: latitude, longitude (EAST positive), timezone
python3 -m jyotish kundli --date 1990-01-05 --time 06:10 --lat 23.81 --lon 90.41 --tz Asia/Dhaka --lang bn

# Exact JSON for apps and AI
python3 -m jyotish kundli --date 1995-08-15 --time 14:30 --place kolkata --years 10 --json
```

`--lang en | bn | hi | both (en+bn, default) | all (en+bn+hi)` · `--years N` forecast window · `--now YYYY-MM-DD` pretend date · `python3 -m jyotish places` lists built-in cities.

Library use:
```python
from jyotish import api
data = api.kundli("1995-08-15", "14:30", place="kolkata")      # JSON-ready dict, names in en/bn/hi
print(data["moon_sign"]["sign"]["hi"], data["dasha"]["current"])
```

Run the tests: `python3 -m unittest discover -s tests -v`

### Use it from AI assistants
Give an AI this repository link and ask it to install it. Tools that can run commands (Claude Code, Codex, Cursor agents, Gemini CLI...) clone it, read [AGENTS.md](AGENTS.md) and then answer birth-date questions from exact calculation. Apps with MCP support can add it as a tool server: `jyotish mcp`. Plain chat windows that cannot run code or install anything cannot do this; for those, run the command yourself and paste the result. Full guide with honest limits: [docs/AI.md](docs/AI.md).

### Known limits
Accurate for 1800-2050. Rahu/Ketu use the mean node. Lahiri ayanamsa only. Birth time must be exact for the Lagna. The engine knows the sky, not what happened in the world on a day. Details in [docs/ACCURACY.md](docs/ACCURACY.md).

---

## বাংলা

### কী করে
জন্মতারিখ, সময় আর জায়গা (বা শুধু যেকোনো তারিখ) দিলে এটা দেখায়:
- **মূল রাশি**: লগ্ন, জন্মরাশি (চন্দ্ররাশি), জন্মনক্ষত্র ও পাদ, সূর্যরাশি, সঙ্গে পাশ্চাত্য রাশি
- **গ্রহস্থিতি** (নিরয়ন লাহিড়ী ও সায়ন): সূর্য, চন্দ্র, মঙ্গল, বুধ, বৃহস্পতি, শুক্র, শনি, রাহু, কেতু; ভাব, নক্ষত্র, গতি, বক্রী, উচ্চ/নীচ/স্বক্ষেত্র
- **রাশিচক্র** (দক্ষিণ ভারতীয় ছক, টেক্সটে)
- **পঞ্চাঙ্গ**: তিথি, নক্ষত্র, যোগ, করণ, বার, চাঁদের দশা, সূর্যোদয়-সূর্যাস্ত, রাহুকাল, যমগণ্ড, গুলিকা, অভিজিৎ ও ব্রাহ্ম মুহূর্ত
- **যোগ ও দোষ**: গজকেশরী, বুধাদিত্য, পঞ্চমহাপুরুষ, কেমদ্রুম, মঙ্গল দোষ, কালসর্প ইত্যাদি
- **বিংশোত্তরী দশা**: চলতি মহাদশা ও অন্তর্দশা, তারিখ ও বিষয়-সহ
- **ভবিষ্যৎ পূর্বাভাস**: শনি, বৃহস্পতি ও রাহুর রাশি বদলের তারিখ, চন্দ্র থেকে কোন ভাবে আছে, এবং **সাড়েসাতি / ঢাইয়া**-র সময়সীমা
- **যেকোনো তারিখের আকাশ** (`sky` কমান্ড): ওই মুহূর্তে প্রতিটা গ্রহ আর নক্ষত্র কোথায় ছিল বা থাকবে
- **সংখ্যাতত্ত্ব**: মূলাঙ্ক ও ভাগ্যাঙ্ক
- আউটপুট **ইংরেজি, বাংলা, হিন্দি** (আলাদা বা একসাথে), আর প্রোগ্রাম ও AI-এর জন্য **JSON**

### সংখ্যাগুলো কেন ভরসাযোগ্য
সব গণনা প্রকাশিত ওপেন অ্যালগরিদম থেকে (NASA/JPL গ্রহ-উপাত্ত, মিউসের চন্দ্র-সিরিজ, লাহিড়ী অয়নাংশ ইত্যাদি); [docs/SOURCES.md](docs/SOURCES.md) দেখো। অটো-টেস্টে জানা সংক্রান্তি, অমাবস্যা-পূর্ণিমা, রাশি বদলের তারিখ আর একটা প্রকাশিত কুণ্ডলী মেলানো হয়। কী যাচাই হয়েছে, কী **এখনও হয়নি** (NASA/JPL Horizons-এর সাথে লাইভ তুলনা, তার স্ক্রিপ্ট দেওয়া আছে), আর ভুলের আনুমানিক মাপ [docs/ACCURACY.md](docs/ACCURACY.md)-এ আছে।

### চালানোর নিয়ম
শুধু Python 3.9+ লাগবে, আর কোনো প্যাকেজ নয় (Windows-এ `pip install tzdata`)। উপরের English অংশের কমান্ডগুলোই চালা। বাংলায় আউটপুট চাইলে `--lang bn`, তিন ভাষায় চাইলে `--lang all`। প্রোগ্রামের জন্য নিখুঁত তথ্য চাইলে `--json`।

### AI অ্যাসিস্ট্যান্ট থেকে ব্যবহার
কোনো AI-কে এই রিপোর লিংক দিয়ে ইনস্টল করতে বললে, যে টুল কমান্ড চালাতে পারে (Claude Code, Codex, Cursor, Gemini CLI ইত্যাদি) সে রিপো নামিয়ে [AGENTS.md](AGENTS.md) পড়ে নিজে হিসাব চালিয়ে জন্মতারিখের উত্তর দেবে। MCP-সমর্থক অ্যাপে টুল হিসেবেও যোগ করা যায়: `jyotish mcp`। শুধু চ্যাট-উইন্ডো, যেখানে কোড চালানো বা ইনস্টল করা যায় না, সেখানে এটা সম্ভব নয়; তখন কমান্ড নিজে চালিয়ে ফল চ্যাটে পেস্ট করতে হবে। বিস্তারিত ও সীমাবদ্ধতা: [docs/AI.md](docs/AI.md)।

### সীমাবদ্ধতা
১৮০০-২০৫০ সালের মধ্যে নির্ভুল। রাহু-কেতু গড় নোড ধরে। শুধু লাহিড়ী অয়নাংশ। লগ্নের জন্য জন্মসময় একদম ঠিক লাগবে। ইঞ্জিন আকাশের অবস্থা জানে, কোনো দিনে দুনিয়ায় কী ঘটেছিল তা জানে না। বিস্তারিত [docs/ACCURACY.md](docs/ACCURACY.md)-এ।

---

## हिन्दी

### यह क्या करता है
जन्म की तारीख़, समय और स्थान (या सिर्फ़ कोई भी तारीख़) देने पर यह दिखाता है:
- **मुख्य राशियाँ**: लग्न, जन्मराशि (चंद्र राशि), जन्म नक्षत्र और चरण, सूर्य राशि, साथ में पाश्चात्य राशियाँ
- **ग्रह स्थिति** (निरयण लाहिड़ी और सायन): सूर्य, चंद्र, मंगल, बुध, गुरु, शुक्र, शनि, राहु, केतु; भाव, नक्षत्र, गति, वक्री, उच्च/नीच/स्वराशि
- **राशि चक्र** (दक्षिण भारतीय शैली, टेक्स्ट में)
- **पंचांग**: तिथि, नक्षत्र, योग, करण, वार, चंद्र कला, सूर्योदय-सूर्यास्त, राहुकाल, यमगंड, गुलिका, अभिजित और ब्रह्म मुहूर्त
- **योग और दोष**: गजकेसरी, बुधादित्य, पंचमहापुरुष, केमद्रुम, मंगल दोष, कालसर्प आदि
- **विंशोत्तरी दशा**: चल रही महादशा और अंतर्दशा, तारीख़ों और विषय के साथ
- **भविष्य का पूर्वानुमान**: शनि, गुरु और राहु के राशि बदलने की तारीख़ें, चंद्र से कौन-से भाव में हैं, और **साढ़ेसाती / ढैया** का समय
- **किसी भी तारीख़ का आकाश** (`sky` कमांड): उस क्षण हर ग्रह और नक्षत्र कहाँ था या होगा
- **अंक ज्योतिष**: मूलांक और भाग्यांक
- आउटपुट **अंग्रेज़ी, बांग्ला, हिन्दी** (अलग-अलग या एक साथ), और प्रोग्राम व AI के लिए **JSON**

### संख्याओं पर भरोसा क्यों
सारी गणना प्रकाशित खुले एल्गोरिद्म से होती है (NASA/JPL ग्रह-तत्व, मीयस की चंद्र श्रृंखला, लाहिड़ी अयनांश आदि); देखें [docs/SOURCES.md](docs/SOURCES.md)। ऑटो-टेस्ट में ज्ञात संक्रांतियाँ, अमावस्या-पूर्णिमा, राशि बदलने की तारीख़ें और एक प्रकाशित कुंडली मिलाई जाती है। क्या जाँचा गया, क्या **अभी नहीं** (NASA/JPL Horizons से सीधी तुलना, उसकी स्क्रिप्ट दी गई है), और अनुमानित त्रुटि [docs/ACCURACY.md](docs/ACCURACY.md) में है।

### चलाने का तरीका
सिर्फ़ Python 3.9+ चाहिए, कोई और पैकेज नहीं (Windows पर `pip install tzdata`)। ऊपर English भाग के कमांड ही चलाएँ। हिन्दी आउटपुट के लिए `--lang hi`, तीनों भाषाओं के लिए `--lang all`, और प्रोग्राम के लिए सटीक डेटा `--json` से।

```bash
python3 -m jyotish kundli --date 1995-08-15 --time 14:30 --place kolkata --lang hi
python3 -m jyotish sky --date 2026-11-16 --time 10:00 --place delhi --lang hi
python3 -m jyotish panchang --date 2026-11-16 --place delhi --lang hi
```

### AI असिस्टेंट से उपयोग
किसी AI को यह रिपॉज़िटरी का लिंक देकर इंस्टॉल करने को कहें। जो टूल कमांड चला सकते हैं (Claude Code, Codex, Cursor, Gemini CLI आदि) वे इसे डाउनलोड करके [AGENTS.md](AGENTS.md) पढ़ते हैं और जन्म-तारीख़ के सवालों का जवाब सटीक गणना से देते हैं। MCP-समर्थित ऐप में इसे टूल सर्वर की तरह भी जोड़ा जा सकता है: `jyotish mcp`। सिर्फ़ चैट विंडो, जहाँ कोड चलाना या इंस्टॉल करना संभव नहीं, वहाँ यह नहीं हो सकता; तब कमांड खुद चलाकर नतीजा चैट में चिपकाएँ। विस्तार और सीमाएँ: [docs/AI.md](docs/AI.md)।

### सीमाएँ
1800-2050 के बीच सटीक। राहु-केतु औसत नोड माने गए हैं। सिर्फ़ लाहिड़ी अयनांश। लग्न के लिए जन्म-समय बिल्कुल सही चाहिए। इंजन आकाश की स्थिति जानता है, यह नहीं कि किसी दिन दुनिया में क्या हुआ। विवरण [docs/ACCURACY.md](docs/ACCURACY.md) में।

---

## License / লাইসেন্স / लाइसेंस

**CC BY-NC-SA 4.0** — see [LICENSE](LICENSE), [NOTICE](NOTICE) and [AUTHORS](AUTHORS).

- ✅ Use, run, study, modify, share · ব্যবহার, চালানো, পড়া, পরিবর্তন, শেয়ার করা যাবে · उपयोग, चलाना, पढ़ना, बदलना, साझा करना ठीक है
- 📛 Author credit **Saheb Mondal** and the project name must stay · "সাহেব মন্ডল" ও প্রজেক্টের নাম রাখতে হবে · "साहेब मंडल" और प्रोजेक्ट का नाम रखना होगा
- 🔓 Any changed version must be open source under the same licence · পরিবর্তিত সংস্করণও একই লাইসেন্সে ওপেন সোর্স করতে হবে · बदला हुआ संस्करण भी इसी लाइसेंस में ओपन सोर्स करना होगा
- 🚫 No commercial use or selling · টাকা কামানো বা বিক্রি করা যাবে না · व्यावसायिक उपयोग या बिक्री नहीं

Contributions are welcome and are accepted under the same licence. · অবদান স্বাগত, একই লাইসেন্সে গৃহীত হবে। · योगदान का स्वागत है, इसी लाइसेंस के तहत स्वीकार होगा।
