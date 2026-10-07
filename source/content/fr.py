# -*- coding: utf-8 -*-
# Contenu français du site NexusLab. Une seule source pour tous les textes.
# Règles : pas de tiret cadratin ni demi-cadratin, apostrophes typographiques,
# typographie romande (espace insécable avant le deux-points, rien avant ? et !).

LANG = "fr"
LOCALE = "fr_CH"
PREFIX = ""  # racine du site pour le français

# Adresse e-mail NexusLab : formulaire, mentions légales, protection des données.
CONTACT_EMAIL = "nexuslab.mpa@gmail.com"

NBSP = " "

meta = {
    "title": "NexusLab, sites web et outils digitaux pour les PME de Suisse romande",
    "description": "NexusLab crée des sites web simples et des outils digitaux pour les PME et les indépendants de Suisse romande. Une équipe basée en Valais, un seul client à la fois, une offre écrite avant de commencer. Formules à partir de CHF 690.",
    "og_title": "NexusLab, le lien entre votre métier et le digital",
    "og_description": "Sites web et outils digitaux pour les PME de Suisse romande. Un seul client à la fois, des prix clairs, une équipe que vous pouvez appeler.",
    "lang_label": "Français",
    "lang_short": "FR",
}

brand = {
    "name": "NexusLab",
    "wordmark": "nexus",
    "signature": "Le lien entre votre métier et le digital.",
    "domain": "nexus-lab.ch",
    "phone_display": "+41 79 737 87 92",
    "phone_tel": "+41797378792",
    "whatsapp": "https://wa.me/41797378792",
    "form_email": CONTACT_EMAIL,
    "form_subject": "Nouveau message depuis nexus-lab.ch",
    "form_autoresponse": "Bonjour, nous avons bien reçu votre message et nous vous répondons rapidement, en général dans les 24 heures. À bientôt, l’équipe NexusLab.",
    "region": "Valais, Suisse romande",
}

nav = {
    "skip": "Aller au contenu",
    "menu_open": "Ouvrir le menu",
    "menu_close": "Fermer le menu",
    "links": [
        ("#offres", "Ce qu’on fait"),
        ("#methode", "Comment on travaille"),
        ("#equipe", "L’équipe"),
        ("#realisations", "Réalisations"),
        ("#contact", "Contact"),
    ],
    "cta": "Parler de votre projet",
    "lang_title": "Changer de langue",
}

hero = {
    "eyebrow": "Sites web et outils digitaux pour les PME de Suisse romande",
    "title": "Le lien entre votre métier et le digital.",
    # Au survol, ce mot bascule en glitch vers le second : « Le nexus entre votre métier et le digital. »
    "title_glitch": ("lien", "nexus"),
    "lede": "NexusLab crée des sites et des outils simples pour les PME et les indépendants de Suisse romande. Une équipe que vous pouvez appeler, un seul client à la fois, et une offre écrite avant de commencer.",
    "cta_primary": "Parler de votre projet",
    "cta_secondary": "Voir les formules",
    "facts": [
        ("Un seul client à la fois", "pour vous consacrer toute notre attention"),
        ("Une offre écrite", "le contenu, le prix et le délai, noir sur blanc"),
        ("Basés en Valais", "actifs dans toute la Suisse romande"),
    ],
    "art_label": "Motif décoratif : des points reliés entre eux",
}

offers = {
    "tag": "Ce qu’on fait",
    "title": "Nos formules",
    "intro": "La plupart des projets commencent par l’une de ces trois formules. Les montants affichés sont des prix de départ, pas des forfaits : le prix final dépend de ce que vous voulez y mettre, et on vous l’écrit avant de commencer.",
    "from": "À partir de",
    "per_month": "par mois",
    "featured_label": "Notre conseil",
    "cards": [
        {
            "name": "Essentiel",
            "price": "CHF 690",
            "period": "",
            "text": "Une seule page avec l’essentiel : vos prestations, vos horaires, des photos, le plan d’accès et un bouton pour vous appeler. On met aussi à jour votre fiche Google.",
            "items": [
                "Une page, pensée d’abord pour le téléphone",
                "Fiche Google à jour",
                "Contact WhatsApp et appel direct",
                "Mise en ligne comprise",
            ],
            "featured": False,
        },
        {
            "name": "Standard",
            "price": "CHF 1’200",
            "period": "",
            "text": "Un site de trois à cinq pages. Vous pouvez changer vous-même la carte, les tarifs ou les actualités. Selon votre métier, on ajoute la réservation ou la prise de rendez-vous en ligne.",
            "items": [
                "Trois à cinq pages",
                "Contenu que vous modifiez vous-même",
                "Rendez-vous ou réservation en ligne",
                "Textes et photos retravaillés avec vous",
            ],
            "featured": True,
        },
        {
            "name": "Suivi",
            "price": "CHF 30",
            "period": "par mois",
            "text": "Après la mise en ligne, on fait les changements à votre place : nouvelles photos, horaires, textes. Sans engagement de durée.",
            "items": [
                "Modifications sur demande",
                "Nouvelles photos et nouveaux textes",
                "Site maintenu à jour",
                "Sans engagement",
            ],
            "featured": False,
        },
    ],
    "note": "Prix de départ, pas des prix fixes. Le montant final dépend de votre projet et figure dans une offre écrite, avant tout engagement. Nom de domaine et hébergement en plus (environ CHF 100 à 200 par an).",
    "more_title": "Un autre besoin?",
    "more_text": "Fiche Google, présence Instagram, outil pour vos factures ou vos horaires : parlons-en, on vous dira franchement si on peut le faire.",
    "more_cta": "Voir les outils sur mesure",
}

tools = {
    "tag": "Sur mesure",
    "title": "On ne fait pas que des sites.",
    "intro": "Si une tâche vous prend trop de temps chaque semaine, on peut souvent en faire un outil. Un tableau Excel qui déborde, des factures faites à la main, des horaires envoyés par WhatsApp : dites-nous ce qui vous ralentit, on vous propose quelque chose de fait pour votre entreprise.",
    "examples": [
        ("Factures et devis", "Créer une facture avec QR-facture en quelques clics, suivre qui a payé et qui est en retard."),
        ("Planning des équipes", "Les horaires et les remplacements au même endroit, consultables sur le téléphone de chacun."),
        ("Tableau de bord", "Vos chiffres importants sur un seul écran : ventes, clients, rendez-vous."),
        ("Suivi des clients et des chantiers", "Toutes les infos d’un client ou d’un chantier dans une seule fiche, documents compris."),
        ("Gestion RH", "Absences, vacances, documents des collaborateurs, sans courir après les papiers."),
        ("Autre chose", "Votre besoin n’est pas dans la liste? Décrivez-le-nous. Si on ne sait pas le faire, on vous le dit."),
    ],
    "proof": "On utilise déjà un outil de ce genre chez Lugon Assèchement : factures avec QR-facture, devis, suivi des paiements et documents classés par client.",
    "price": "Prix sur devis, selon l’outil.",
    "cta": "Décrire mon besoin",
    "mock_title": "Factures",
    "mock_nav": ["Tableau de bord", "Factures", "Devis", "Clients", "Documents"],
    "mock_rows": [
        ("F-2026-041", "Boulangerie du Bourg", "CHF 480.00", "paid"),
        ("F-2026-042", "Garage des Alpes", "CHF 1’250.00", "wait"),
        ("F-2026-043", "Cabinet Rive Droite", "CHF 360.00", "late"),
        ("F-2026-044", "Atelier Bois & Co", "CHF 2’140.00", "paid"),
    ],
    "mock_status": {"paid": "Payée", "wait": "En attente", "late": "En retard"},
    "mock_new": "Nouvelle facture",
    "mock_total": "Encaissé ce mois",
    "mock_total_value": "CHF 2’620",
    "mock_note": "Exemple d’interface, données fictives.",
}

method = {
    "tag": "",
    "title": "Comment ça se passe concrètement?",
    "steps": [
        ("Échange", "On se rencontre, chez vous ou à distance, et vous nous expliquez ce dont vous avez besoin."),
        ("Offre écrite", "Vous recevez une offre avec le contenu, le prix et le délai. Rien ne commence sans votre accord."),
        ("Maquette", "On vous montre à quoi ressemblera le site avant de le construire. Vous pouvez demander des changements."),
        ("Mise en ligne", "Le site est publié et on vous montre comment modifier vos textes et vos photos."),
    ],
    "aside": "De votre côté, il nous faudra votre logo, quelques photos et vos textes ou vos horaires. Si vous n’avez pas tout, on vous aide à le préparer.",
    "principles_title": "Trois règles qu’on s’est fixées",
    "principles": [
        ("Un seul client à la fois", "On ne commence un nouveau projet qu’une fois le précédent livré. Si on est déjà pris, vous rejoignez la liste d’attente et on vous donne une date."),
        ("Le site est à vous", "Nom de domaine et hébergement compris, il vous coûte environ CHF 100 à 200 par an, et vous n’êtes lié à aucun abonnement chez nous."),
        ("On répond nous-mêmes", "Trois personnes, un numéro. Vous parlez à ceux qui font votre site, pas à un service client."),
    ],
}

team = {
    "tag": "",
    "title": "On est trois, à Sierre.",
    # Photo d'équipe : déposer site/assets/img/equipe-800.webp et equipe-1400.webp (format 16:9),
    # elle s'affiche automatiquement en haut de la section.
    "photo_alt": "Patrick, Mehdi et Arno, l’équipe de NexusLab",
    "members": [
        ("Patrick Lugon", "pilote les projets et s’occupe du design. C’est lui que vous aurez au téléphone.", "PL"),
        ("Mehdi Chouchane", "développe les sites et les outils, et tient les comptes du projet.", "MC"),
        ("Arno Blatter", "rencontre les entreprises et suit les clients après la mise en ligne.", "AB"),
    ],
    "roles": ["Chef de projet et direction artistique", "Création et développement", "Relation client et suivi"],
    "text": "Nous sommes étudiants en économie d’entreprise à la HES-SO Valais-Wallis, en filière Business Team Academy : on apprend en menant de vrais projets avec de vraies entreprises. NexusLab est porté par Vardena, la coopérative de notre classe, et chaque mandat passe par un contrat.",
}

work = {
    "tag": "Réalisation",
    "visit": "Voir le site",
    "soon": "En préparation",
    "case": {
        "name": "Lugon Assèchement Sàrl",
        "meta": "Assèchement et dégâts des eaux, Martigny",
        "intro": "C’est l’entreprise familiale de Patrick, et notre premier terrain d’essai.",
        "url": "https://lugon-assechement.ch",
        "url_label": "lugon-assechement.ch",
        "image": "lugon-site",
        "image_alt": "Page d’accueil du site de Lugon Assèchement, avec son titre et son bouton d’appel d’urgence",
        "blocks": [
            ("Le problème", "L’entreprise payait un abonnement d’annuaire en ligne coûteux, pour une page qui ne lui appartenait pas."),
            ("Ce qu’on a fait", "Un site en français, en allemand et en anglais, pensé pour les urgences : le numéro est visible partout et l’appel se lance en un geste. Référencement local en Valais, formulaire de contact, questions fréquentes et pages légales."),
            ("Le résultat", "Le site a remplacé l’abonnement d’annuaire. Il appartient à l’entreprise et ne coûte plus que l’hébergement et le nom de domaine."),
        ],
        # Chiffre clé optionnel, affiché en grand s'il est rempli (ex. : ("CHF 1’200", "économisés par an")).
        "figure": None,
    },
    "next": "Prochain projet : le site de Vardena, la coopérative de notre classe.",
    "yours": "Le vôtre pourrait suivre.",
    "yours_cta": "Parlons-en",
}

proof = {
    "tag": "",
    "title": "Ce que pèse cette page",
    "intro": "On applique à notre propre site ce qu’on propose à nos clients. Les chiffres ci-contre sont mesurés à l’instant, dans votre navigateur : un site léger s’ouvre vite, même avec une connexion moyenne, et Google tient compte de la vitesse.",
    "unavailable": "Mesure indisponible dans ce navigateur.",
    "term_title": "nexus-lab.ch · mesure en direct",
    "command": "mesurer cette-page",
    "weight": "Poids de la page",
    "time": "Chargée en",
    "requests": "Fichiers chargés",
    "cookies": "Cookies déposés",
    "compare_us": "Cette page",
    "compare_web": "Page médiane du web",
    "ratio": "fois plus légère que la page d’accueil médiane du web",
    "source": "Source : HTTP Archive, Web Almanac 2025, chapitre Page Weight (pages d’accueil, juillet 2025).",
    "source_url": "https://almanac.httparchive.org/en/2025/page-weight",
    "median_desktop_kb": 2862,
    "median_mobile_kb": 2559,
}

faq = {
    "tag": "",
    "title": "Questions fréquentes",
    "aside": "Une autre question? Appelez-nous, c’est souvent plus rapide.",
    "items": [
        ("Combien coûte un site?",
         "Un site d’une page coûte à partir de CHF 690, un site complet à partir de CHF 1’200. Le prix exact dépend de ce que vous voulez y mettre, et il est écrit avant de commencer. Le nom de domaine et l’hébergement coûtent en plus environ CHF 100 à 200 par an."),
        ("Combien de temps ça prend?",
         "En général, trois à six semaines entre notre premier échange et la mise en ligne, selon la formule et le temps qu’il vous faut pour nous transmettre vos contenus."),
        ("Est-ce que je peux modifier mon site moi-même?",
         "Oui, avec la formule Standard, pour la carte, les tarifs ou les actualités. Si vous préférez ne pas y toucher, la formule Suivi s’en charge."),
        ("Et si j’ai déjà un site?",
         "On regarde ce qui existe avec vous. Parfois quelques corrections suffisent, parfois il vaut mieux repartir de zéro. On vous le dit avant de proposer quoi que ce soit."),
        ("Vous êtes étudiants : qu’est-ce que ça change pour moi?",
         "Des prix accessibles et une équipe disponible. Chaque mandat passe par un contrat et l’école suit nos projets. Et vous aidez trois jeunes à apprendre leur métier avec de vrais clients."),
    ],
}

contact = {
    "tag": "Contact",
    "title": "Vous avez un projet en tête?",
    "questions": [
        "Qu’aimeriez-vous que vos clients voient en premier?",
        "Pour quand en avez-vous besoin?",
        "Qui s’occupera de mettre le contenu à jour?",
    ],
    "no_answers": "Pas besoin d’avoir déjà les réponses : on en parle ensemble.",
    "whatsapp": "Écrire sur WhatsApp",
    "call": "Appeler",
    "reply_time": "On vous répond en général dans les 24 heures.",
    "form": {
        "title": "Ou laissez-nous un message",
        "name": "Votre nom",
        "company": "Votre entreprise",
        "optional": "facultatif",
        "email": "Votre e-mail",
        "phone": "Votre téléphone",
        "message": "Votre message",
        "message_placeholder": "Dites-nous en quelques mots ce que vous cherchez.",
        "submit": "Envoyer",
        "privacy": "Vos coordonnées servent uniquement à vous répondre.",
        "privacy_link": "Protection des données",
    },
}

footer = {
    "signature": "Le lien entre votre métier et le digital.",
    "nav_title": "Le site",
    "legal_title": "Informations",
    "lang_title": "Langues",
    "legal_links": [
        ("mentions-legales/", "Mentions légales"),
        ("protection-donnees/", "Protection des données"),
    ],
    "about": "NexusLab est un projet de la coopérative Vardena, Business Team Academy, HES-SO Valais-Wallis.",
    "made": "Conçu et développé en Valais, Suisse.",
    "copyright": "NexusLab",
}

thanks = {
    "title": "Merci, votre message est bien parti.",
    "text": "On vous répond en général dans les 24 heures. En attendant, vous pouvez aussi nous écrire sur WhatsApp.",
    "back": "Retour au site",
    "meta_title": "Message envoyé",
}

notfound = {
    "title": "Cette page n’existe pas.",
    "text": "Le lien est peut-être ancien, ou l’adresse contient une faute de frappe.",
    "back": "Retour à l’accueil",
    "meta_title": "Page introuvable",
}

legal = {
    "meta_title": "Mentions légales",
    "title": "Mentions légales",
    "updated": "Dernière mise à jour : octobre 2026.",
    "back": "Retour à l’accueil",
    "sections": [
        ("Éditeur du site",
         "<p>NexusLab<br>Projet de Vardena, coopérative en cours de constitution, Team Company de la Business Team Academy, HES-SO Valais-Wallis</p>"
         "<p>c/o HES-SO Valais-Wallis, Business Team Academy<br>Route de Sous-Géronde 87<br>3960 Sierre<br>Suisse</p>"
         "<p>Téléphone : <a href=\"tel:+41797378792\">+41 79 737 87 92</a><br>E-mail : <a href=\"mailto:" + CONTACT_EMAIL + "\">" + CONTACT_EMAIL + "</a></p>"
         "<p>Responsables du contenu : Patrick Lugon, Mehdi Chouchane et Arno Blatter.</p>"
         "<p>Vardena sera inscrite au registre du commerce du canton du Valais lors de sa constitution. Son numéro d’identification des entreprises (IDE) figurera ici dès qu’il sera attribué. D’ici là, aucun contrat n’est conclu au nom de NexusLab sans une offre écrite.</p>"),
        ("Hébergement",
         "<p>Le site est hébergé par Netlify, Inc., San Francisco, États-Unis (<a href=\"https://www.netlify.com\" rel=\"noopener\" target=\"_blank\">netlify.com</a>).</p>"),
        ("Propriété intellectuelle",
         "<p>Les textes, le logo, les illustrations et la mise en page de ce site appartiennent à NexusLab. Toute reproduction, même partielle, demande notre accord écrit. La police de caractères Manrope est utilisée sous licence SIL Open Font License.</p>"
         "<p>Les marques, logos et contenus des entreprises présentées dans nos réalisations restent la propriété de leurs titulaires.</p>"),
        ("Responsabilité",
         "<p>Nous mettons tout en œuvre pour que les informations de ce site soient exactes et à jour. Elles sont données à titre indicatif : les prix affichés sont des points de départ, et seule une offre écrite nous engage. Nous ne répondons pas du contenu des sites externes vers lesquels nous renvoyons.</p>"),
        ("Crédits",
         "<p>Site conçu et réalisé par NexusLab.</p>"),
    ],
}

privacy = {
    "meta_title": "Protection des données",
    "title": "Protection des données",
    "updated": "Dernière mise à jour : octobre 2026.",
    "back": "Retour à l’accueil",
    "intro": "<p>Cette page explique quelles données sont traitées quand vous visitez nexus-lab.ch, et pourquoi. Elle s’appuie sur la loi fédérale sur la protection des données (LPD), en vigueur depuis le 1er septembre 2023. En résumé : ce site ne vous suit pas, et les seules données que nous recevons sont celles que vous nous envoyez.</p>",
    "sections": [
        ("Responsable du traitement",
         "<p>NexusLab, projet de Vardena, coopérative en cours de constitution, Team Company de la Business Team Academy, HES-SO Valais-Wallis. Adresse : c/o HES-SO Valais-Wallis, Business Team Academy, Route de Sous-Géronde 87, 3960 Sierre. Contact : <a href=\"tel:+41797378792\">+41 79 737 87 92</a>, <a href=\"mailto:" + CONTACT_EMAIL + "\">" + CONTACT_EMAIL + "</a>.</p>"),
        ("Aucun suivi, aucun cookie",
         "<p>Ce site n’utilise ni cookies, ni Google Analytics, ni aucun autre outil de mesure d’audience ou de publicité. Nous ne déposons rien sur votre appareil et nous ne suivons pas votre navigation. C’est pourquoi vous ne voyez pas de bandeau de cookies.</p>"),
        ("Hébergement et journaux techniques",
         "<p>Le site est hébergé par Netlify, Inc., San Francisco, États-Unis. Comme tout hébergeur, Netlify peut enregistrer des journaux techniques (adresse IP, type de navigateur, pages demandées, heure de la visite) pour assurer la sécurité et le bon fonctionnement du service, pendant une durée limitée. Ces données peuvent être traitées hors de Suisse. Les règles de Netlify sont décrites dans sa <a href=\"https://www.netlify.com/privacy/\" rel=\"noopener\" target=\"_blank\">politique de confidentialité</a>.</p>"),
        ("Formulaire de contact",
         "<p>Quand vous utilisez le formulaire, les données que vous saisissez (nom, entreprise, e-mail, téléphone, message) nous sont transmises par e-mail via le service FormSubmit (formsubmit.co). FormSubmit est un service externe : il reçoit vos données et nous les fait suivre par e-mail. Le message arrive ensuite dans notre boîte Gmail (Google). Ces deux prestataires peuvent traiter les données hors de Suisse, notamment aux États-Unis. Nous utilisons vos données uniquement pour vous répondre et, si vous le souhaitez, pour préparer une offre. Elles ne sont ni vendues ni transmises à d’autres tiers. Nous les conservons le temps de nos échanges, puis au plus douze mois après le dernier contact.</p>"),
        ("WhatsApp et téléphone",
         "<p>Si vous nous écrivez sur WhatsApp, les règles de confidentialité de WhatsApp (Meta) s’appliquent à cet échange. Nous ne conservons vos coordonnées que pour le suivi de votre demande.</p>"),
        ("Polices de caractères et contenus externes",
         "<p>La police Manrope est hébergée sur nos propres serveurs : aucune requête n’est envoyée à Google Fonts. Ce site ne charge aucun contenu provenant de réseaux sociaux. Les liens vers les sites de nos clients mènent à des sites indépendants, soumis à leurs propres règles.</p>"),
        ("Vos droits",
         "<p>Vous pouvez à tout moment demander quelles données nous détenons sur vous, les faire corriger ou les faire effacer. Il suffit de nous écrire aux coordonnées ci-dessus. Vous pouvez aussi vous adresser au Préposé fédéral à la protection des données et à la transparence (PFPDT).</p>"),
        ("Modifications",
         "<p>Si notre façon de traiter les données change, par exemple si nous ajoutons un outil de mesure d’audience, nous mettons cette page à jour avant de l’activer.</p>"),
    ],
}
