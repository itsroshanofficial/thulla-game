"""Original, family-friendly comedy lines (Roman script).

lang: "pa" = Punjabi, "ur" = Urdu, "en" = English (mixed style is fine).
All lines are original and target no protected or sensitive personal traits.
Add your own lines here, or drop recordings in assets/audio/<line id>.mp3
(see assets/audio/README.md).
"""
CATEGORIES = ("thulla", "surprise", "teasing", "commentary", "victory", "defeat", "random")

_RAW = {
    "thulla": [
        ("pa", "Oye hoye hoye! Thulla pai gaya!"),
        ("pa", "Haye oye, thulla ho gaya, hun chaa pi lo!"),
        ("ur", "Lo ji, thulla aa gaya, ab sab ki khair nahi!"),
        ("pa", "Oho ji, patte hi paltay gaye!"),
        ("en", "Thulla alert! Everybody stay calm, ya nahi!"),
        ("pa", "Hun ki karoge puttar? Thulla tay aa gaya!"),
        ("ur", "Yeh kya hua bhai, thulla ho gaya!"),
        ("pa", "Wah ji wah, pattay vi bewafa nikle!"),
    ],
    "surprise": [
        ("pa", "Haye oye, ki ho gaya!"),
        ("pa", "Oho ji, game hi palat gayi!"),
        ("ur", "Arre waah, yeh to socha hi nahi tha!"),
        ("en", "Plot twist! Even the cards are shocked."),
        ("pa", "Ni main mar gayi, eh ki kar ditta!"),
        ("ur", "Hayyy, dil ruk gaya mera!"),
        ("pa", "Oye, eh tay kamaal ho gaya!"),
    ],
    "teasing": [
        ("pa", "Chal puttar, hun teri vaari!"),
        ("pa", "Bach ke veere, bach ke!"),
        ("ur", "Aaj to tumhari baari lag gayi lagti hai!"),
        ("en", "Somebody's hand is looking very heavy right now."),
        ("pa", "Pattay gin lo, kitthe ja rahe ho?"),
        ("ur", "Itna tension mat lo, sirf cards hain!"),
        ("pa", "Oye hoye, chehra dekho, rang ud gaya!"),
    ],
    "commentary": [
        ("pa", "Hun khedan di vaari ayi aa!"),
        ("ur", "Chaal chalo, jaldi karo, chai thandi ho rahi hai!"),
        ("en", "And the next move is coming up, hold your breath!"),
        ("pa", "Sambhal ke khedna, bade tej banday ne!"),
        ("pa", "Game garam ho rahi aa, dhyan naal!"),
        ("ur", "Maidan garam hai, patte tayyar hain!"),
        ("en", "Shuffle done, let the drama begin!"),
    ],
    "victory": [
        ("pa", "Balle balle, ki khedya ae!"),
        ("pa", "Shava shava! Jit gaye, jit gaye!"),
        ("ur", "Wah wah, kya baat hai, kamaal kar diya!"),
        ("en", "Victory! Somebody call the dhol wala!"),
        ("pa", "Oye hoye, bachda reh gaya, badshahan!"),
        ("ur", "Mubarak ho, aap to bach gaye!"),
        ("pa", "Chak de phatte, safe ho gaye!"),
    ],
    "defeat": [
        ("pa", "Oho, hun chaa te mithai tere hisaab ch!"),
        ("ur", "Afsos, aaj kismat ne saath nahi diya!"),
        ("en", "Oh no. The Thulla title has found a new owner."),
        ("pa", "Koi gal nai puttar, agli vaari vekhange!"),
        ("pa", "Haye, thulla tay tere naal chipak gaya!"),
        ("ur", "Koi baat nahi, agli baar zaroor jeetenge!"),
        ("en", "Better luck next round, champion of the cards!"),
    ],
    "random": [
        ("pa", "Oye, kise ne chai banayi?"),
        ("ur", "Bhai, kya zabardast game hai!"),
        ("en", "Fun fact: cards cannot hear your complaints."),
        ("pa", "Ajj tay maza hi aa gaya!"),
        ("pa", "Dil kardaa ae ik hor game laiye!"),
        ("ur", "Samosa kahan hai, game ke saath chahiye!"),
        ("en", "Remember: it is only a game. A very serious game."),
    ],
}

LINES = {
    cat: [{"id": f"{cat}_{i:02d}", "category": cat, "lang": lang, "text": text}
          for i, (lang, text) in enumerate(items)]
    for cat, items in _RAW.items()
}
LANGUAGES = {"pa": "Punjabi", "ur": "Urdu", "en": "English"}
