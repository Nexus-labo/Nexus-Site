# Site NexusLab (nexus-lab.ch), version 1

Site statique, une page à sections, trois langues prévues (FR en ligne, DE et EN à générer une fois les textes validés). Déploiement par zip sur Netlify, comme le site Lugon.

## Les deux dossiers

- `site/` : le site prêt à mettre en ligne. C'est ce dossier (son contenu, pas le dossier lui-même) qu'on zippe et qu'on dépose sur Netlify.
- `source/` : les textes, les gabarits et les outils qui fabriquent `site/`. On ne modifie jamais `site/` à la main, on modifie `source/` et on reconstruit.

## Modifier un texte

1. Ouvrir `source/content/fr.py`. Tous les textes du site français sont là, section par section.
2. Reconstruire le site : dans un terminal, `python3 source/build.py`.
3. Vérifier `site/index.html` dans un navigateur, puis zipper et déposer sur Netlify.

Le script refuse de construire si un jeton de gabarit n'a pas de texte, ce qui évite de publier une page avec un trou.

## Ajouter une langue

1. Copier `source/content/fr.py` en `source/content/de.py` (ou `en.py`), traduire les textes, mettre `LANG = "de"` et `LOCALE = "de_CH"`.
2. Dans `source/build.py`, ajouter la langue à `LANGS` : `LANGS = ["fr", "de", "en"]`.
3. Reconstruire. Les sous-dossiers `/de/` et `/en/`, les balises hreflang, le sélecteur de langue, le sitemap et les pages légales traduites se créent tout seuls.

## Mettre en ligne sur Netlify

1. Zipper le contenu de `site/` (le fichier `index.html` doit être à la racine du zip).
2. Sur app.netlify.com, déposer le zip sur le site NexusLab (ou créer le site la première fois avec « Add new site », puis « Deploy manually »).
3. Relier le domaine nexus-lab.ch dans « Domain management » (Netlify indique les enregistrements DNS à mettre chez le bureau d'enregistrement). Le certificat HTTPS est automatique.

## Le formulaire de contact

Il passe par FormSubmit (formsubmit.co), sans serveur. Au premier message envoyé, FormSubmit envoie un e-mail de confirmation à l'adresse configurée : il faut cliquer sur le lien pour activer le formulaire, sinon rien n'arrive. L'adresse se change dans `source/content/fr.py`, variable `CONTACT_EMAIL` en haut du fichier (pour le moment nexuslab.mpa@gmail.com, l’e-mail commun NexusLab). Protection anti-spam : champ piège (`_honey`) et captcha de FormSubmit. Page de retour : `/merci/`.

## Photo de l’équipe

Déposer deux fichiers WebP au format 16:9 dans `site/assets/img/` : `equipe-800.webp` et `equipe-1400.webp`, puis reconstruire. La photo s’affiche automatiquement en haut de la section équipe ; sans fichier, la section reste en texte.

## Chiffre clé de l’étude de cas Lugon

Dans `source/content/fr.py`, champ `work > case > figure`, par exemple `("CHF 1’200", "économisés par an")`. Laisser `None` tant qu’on n’a pas le vrai chiffre.

## Images et icônes

- `source/tools/make_icons.py` fabrique les favicons et l'image de partage (`assets/img/og-image.png`, celle qui s'affiche quand on partage le lien sur WhatsApp ou LinkedIn).
- `source/tools/shot.js` prend une capture d'écran d'un site (sert pour les vignettes de réalisations). Les captures sont ensuite converties en WebP, en deux tailles, dans `site/assets/img/`.
- Les images sont des fichiers séparés, en WebP, chargées à la demande (`loading="lazy"`), jamais intégrées dans le HTML.

## Ce que le site fait déjà

- Manrope hébergée sur le site (pas d'appel à Google Fonts), couleurs centralisées en haut de `style.css`.
- Balises title et description, canonical, hreflang, Open Graph avec image, données structurées schema.org (entreprise, site, FAQ).
- Pages mentions légales et protection des données (nLPD), aucun cookie, aucun suivi.
- Mouvement réduit respecté, navigation au clavier, lien d'évitement, contrastes AA.
- Sitemap, robots.txt, manifeste, en-têtes de sécurité Netlify (`_headers`), page 404.

## À vérifier avant la mise en ligne

- Mentions légales : faire confirmer l’adresse « c/o Business Team Academy » par l’école, puis ajouter le numéro IDE de Vardena dès sa constitution.
- Formulaire : au premier message, cliquer sur le lien d’activation FormSubmit reçu sur nexuslab.mpa@gmail.com.
- Accord de François Lugon pour montrer le site Lugon Assèchement en réalisation.
- Accord de Mehdi et Arno sur les textes, les rôles affichés et les prix « dès CHF ».
- Textes DE et EN à générer après validation du français.
