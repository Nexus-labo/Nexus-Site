/* NexusLab : petit script sans dépendance.
   Menu mobile, apparition au défilement (désactivée si « mouvement réduit »), année du pied de page. */
(function () {
  "use strict";
  document.documentElement.classList.remove("no-js");

  /* Menu mobile */
  var toggle = document.querySelector(".nav-toggle");
  var panel = document.querySelector(".nav-panel");
  if (toggle && panel) {
    var setOpen = function (open) {
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? toggle.dataset.labelClose : toggle.dataset.labelOpen);
      panel.setAttribute("data-open", open ? "true" : "false");
    };
    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });
    panel.addEventListener("click", function (e) {
      if (e.target.closest("a")) { setOpen(false); }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { setOpen(false); }
    });
  }

  /* Apparition au défilement */
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  /* souris ou trackpad : les effets de survol ne sont activés que là (pas au doigt) */
  var canHover = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  var items = document.querySelectorAll(".reveal");
  if (!reduced && "IntersectionObserver" in window && items.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add("is-visible"); });
  }


  /* Réseau 3D de l'accueil : des points reliés dans un volume, vus en perspective.
     Version allégée et sûre :
     - la caméra ne pivote que de quelques degrés, aucun point ne peut passer derrière elle
       (les tailles restent bornées, plus de cercles géants ni d'erreur qui fige l'animation) ;
     - les liens sont regroupés par intensité et tracés en une dizaine de passes au lieu de milliers ;
     - les halos corail sont dessinés une fois puis réutilisés (aucun dégradé recalculé à chaque image) ;
     - nombre de points et résolution adaptés à l'écran, 60 images par seconde au maximum ;
     - rendu figé si « mouvement réduit », en pause quand l'onglet est caché ou l'accueil hors écran. */
  var canvas = document.querySelector(".hero-canvas");
  if (canvas && canvas.getContext) {
    var ctx = canvas.getContext("2d", { alpha: true });
    var finePointer = canHover;
    var nodes = [], proj = [], order = [], W = 0, H = 0, dpr = 1, raf = 0, running = false, visible = true;
    var NAVY = "29, 29, 31", CORAL = "255, 95, 87";
    var BX = 0, BY = 0, BZ = 0, F = 1, LINK = 200, LINK2 = LINK * LINK;
    var mouse = { x: 0, y: 0, sx: -9999, sy: -9999, on: false };
    var cam = { yaw: 0, pitch: 0 };
    var BUCKETS = 6, segNavy = [], segCoral = [];
    /* signaux qui circulent le long des liens, ondes au toucher ou au clic */
    var adj = [], pulses = [], ripples = [], nextPulse = 0, lastT = 0;
    var MAXP = finePointer ? 7 : 5;
    for (var bi = 0; bi < BUCKETS; bi++) { segNavy.push([]); segCoral.push([]); }

    /* halo corail pré-dessiné */
    var glow = document.createElement("canvas"); glow.width = glow.height = 64;
    (function () {
      var g = glow.getContext("2d"), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
      gr.addColorStop(0, "rgba(" + CORAL + ",0.55)"); gr.addColorStop(1, "rgba(" + CORAL + ",0)");
      g.fillStyle = gr; g.fillRect(0, 0, 64, 64);
    })();

    var spawn = function () {
      var v = 0.16;
      return {
        x: (Math.random() * 2 - 1) * BX, y: (Math.random() * 2 - 1) * BY, z: (Math.random() * 2 - 1) * BZ,
        vx: (Math.random() * 2 - 1) * v, vy: (Math.random() * 2 - 1) * v, vz: (Math.random() * 2 - 1) * v,
        coral: Math.random() < 0.07, t: Math.random() * 6.28
      };
    };
    var resize = function () {
      var r = canvas.getBoundingClientRect();
      if (!r.width || !r.height) { return; }
      W = r.width; H = r.height;
      /* plafond de pixels : au-delà, la tablette ou le téléphone peine */
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      var budget = finePointer ? 3.2e6 : 1.8e6;
      if (W * H * dpr * dpr > budget) { dpr = Math.max(1, Math.sqrt(budget / (W * H))); }
      canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      var oldBX = BX || 1, oldBY = BY || 1;
      BX = W * 0.56; BY = H * 0.56; BZ = Math.min(W, H) * 0.42;
      F = Math.max(W, H) * 1.15;
      LINK = Math.max(150, Math.min(250, Math.min(W, H) * 0.3)); LINK2 = LINK * LINK;
      var max = finePointer ? 140 : 110;
      var count = Math.max(40, Math.min(max, Math.round(W * H / 9500)));
      for (var i = 0; i < nodes.length; i++) { nodes[i].x *= BX / oldBX; nodes[i].y *= BY / oldBY; }
      while (nodes.length < count) { nodes.push(spawn()); }
      nodes.length = count; proj.length = count; order.length = 0;
    };

    var project = function () {
      var cy = Math.cos(cam.yaw), sy = Math.sin(cam.yaw), cp = Math.cos(cam.pitch), sp = Math.sin(cam.pitch);
      for (var i = 0; i < nodes.length; i++) {
        var n = nodes[i];
        var x1 = n.x * cy + n.z * sy, z1 = -n.x * sy + n.z * cy;
        var y2 = n.y * cp - z1 * sp, z2 = n.y * sp + z1 * cp;
        var s = F / Math.max(F * 0.45, F + z2);          /* jamais derrière la caméra */
        if (s > 1.9) { s = 1.9; }
        var near = Math.max(0, Math.min(1, 0.5 - z2 / (2 * BZ)));
        var p = proj[i] || (proj[i] = {});
        p.x = W / 2 + x1 * s; p.y = H / 2 + y2 * s; p.s = s; p.near = near; p.n = n; p.z = z2;
      }
    };

    var draw = function (time) {
      ctx.clearRect(0, 0, W, H);
      var i, j, a, b, pa, pb, dx, dy, dz, d2, k, depth, lvl, list;
      for (i = 0; i < BUCKETS; i++) { segNavy[i].length = 0; segCoral[i].length = 0; }
      for (i = 0; i < nodes.length; i++) { if (adj[i]) { adj[i].length = 0; } else { adj[i] = []; } }
      /* liens : calculés dans l'espace 3D, classés par intensité */
      for (i = 0; i < nodes.length; i++) {
        a = nodes[i]; pa = proj[i];
        for (j = i + 1; j < nodes.length; j++) {
          b = nodes[j];
          dx = a.x - b.x; if (dx > LINK || dx < -LINK) { continue; }
          dy = a.y - b.y; if (dy > LINK || dy < -LINK) { continue; }
          dz = a.z - b.z; d2 = dx * dx + dy * dy + dz * dz;
          if (d2 < LINK2) {
            pb = proj[j];
            depth = (pa.near + pb.near) / 2;
            k = (1 - Math.sqrt(d2) / LINK) * (0.25 + 0.75 * depth);
            lvl = Math.min(BUCKETS - 1, (k * BUCKETS) | 0);
            list = (a.coral || b.coral) ? segCoral[lvl] : segNavy[lvl];
            list.push(pa.x, pa.y, pb.x, pb.y);
            adj[i].push(j); adj[j].push(i);
          }
        }
      }
      for (lvl = 0; lvl < BUCKETS; lvl++) {
        var w = (lvl + 0.5) / BUCKETS;
        ctx.lineWidth = 0.5 + 0.9 * w;
        for (var c = 0; c < 2; c++) {
          list = c ? segCoral[lvl] : segNavy[lvl];
          if (!list.length) { continue; }
          ctx.strokeStyle = "rgba(" + (c ? CORAL : NAVY) + "," + (0.05 + 0.36 * w * w).toFixed(3) + ")";
          ctx.beginPath();
          for (i = 0; i < list.length; i += 4) { ctx.moveTo(list[i], list[i + 1]); ctx.lineTo(list[i + 2], list[i + 3]); }
          ctx.stroke();
        }
      }
      /* signaux : une lueur corail qui parcourt le lien, avec sa traînée */
      ctx.lineWidth = 1.6;
      for (i = 0; i < pulses.length; i++) {
        var pu = pulses[i], A = proj[pu.a], B = proj[pu.b];
        var px = A.x + (B.x - A.x) * pu.t, py = A.y + (B.y - A.y) * pu.t;
        ctx.strokeStyle = "rgba(" + CORAL + ",0.55)";
        ctx.beginPath(); ctx.moveTo(A.x, A.y); ctx.lineTo(px, py); ctx.stroke();
        ctx.drawImage(glow, px - 13, py - 13, 26, 26);
        ctx.fillStyle = "rgb(" + CORAL + ")";
        ctx.beginPath(); ctx.arc(px, py, 2.4, 0, 6.2832); ctx.fill();
      }
      /* ondes : un anneau qui s'élargit depuis le doigt ou le clic */
      for (i = 0; i < ripples.length; i++) {
        var rp = ripples[i], kk = Math.min(1, (time - rp.t0) / 1100), ease = 1 - Math.pow(1 - kk, 3);
        ctx.strokeStyle = "rgba(" + CORAL + "," + (0.35 * (1 - kk)).toFixed(3) + ")";
        ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.arc(rp.x, rp.y, 12 + ease * rp.max, 0, 6.2832); ctx.stroke();
      }
      /* liens vers la souris (ordinateur uniquement) */
      if (mouse.on) {
        ctx.lineWidth = 1;
        for (i = 0; i < proj.length; i++) {
          var q = proj[i];
          dx = q.x - mouse.sx; dy = q.y - mouse.sy; d2 = dx * dx + dy * dy;
          if (d2 < 180 * 180) {
            k = 1 - Math.sqrt(d2) / 180;
            ctx.strokeStyle = "rgba(" + CORAL + "," + (k * (0.2 + 0.4 * q.near)).toFixed(3) + ")";
            ctx.beginPath(); ctx.moveTo(q.x, q.y); ctx.lineTo(mouse.sx, mouse.sy); ctx.stroke();
          }
        }
      }
      /* points : du plus lointain au plus proche, couleur unie */
      if (order.length !== proj.length) { order = proj.slice(); }
      order.sort(function (u, v) { return v.z - u.z; });
      for (i = 0; i < order.length; i++) {
        var o = order[i], r = (1.1 + 2.6 * o.near) * o.s, hover = 0;
        if (o.x < -40 || o.x > W + 40 || o.y < -40 || o.y > H + 40) { continue; }
        if (mouse.on) { dx = o.x - mouse.sx; dy = o.y - mouse.sy; hover = Math.max(0, 1 - Math.sqrt(dx * dx + dy * dy) / 180); }
        if (o.n.coral) {
          var gs = r * 4 * (1 + 0.25 * Math.sin(time / 900 + o.n.t));
          ctx.globalAlpha = 0.35 + 0.45 * o.near;
          ctx.drawImage(glow, o.x - gs, o.y - gs, gs * 2, gs * 2);
          ctx.globalAlpha = 1;
          ctx.fillStyle = "rgba(" + CORAL + "," + (0.5 + 0.5 * o.near).toFixed(3) + ")";
          r = r * 1.2 + hover * 2;
        } else {
          ctx.fillStyle = hover > 0
            ? "rgba(" + CORAL + "," + (0.35 + 0.6 * hover).toFixed(3) + ")"
            : "rgba(" + NAVY + "," + (0.2 + 0.65 * o.near).toFixed(3) + ")";
          r = r + hover * 1.5;
        }
        var fl = o.n.flash ? Math.max(0, 1 - (time - o.n.flash) / 550) : 0;
        if (fl > 0) {
          ctx.globalAlpha = fl; ctx.drawImage(glow, o.x - r * 5, o.y - r * 5, r * 10, r * 10); ctx.globalAlpha = 1;
          ctx.fillStyle = "rgba(" + CORAL + "," + (0.5 + 0.5 * fl).toFixed(3) + ")";
          r = r + fl * 1.5;
        }
        ctx.beginPath(); ctx.arc(o.x, o.y, r, 0, 6.2832); ctx.fill();
      }
      if (mouse.on) {
        ctx.drawImage(glow, mouse.sx - 24, mouse.sy - 24, 48, 48);
        ctx.fillStyle = "rgb(" + CORAL + ")";
        ctx.beginPath(); ctx.arc(mouse.sx, mouse.sy, 3.5, 0, 6.2832); ctx.fill();
      }
    };

    var launch = function (from, hops, time) {
      var list = adj[from];
      if (!list || !list.length || pulses.length >= MAXP + 4) { return; }
      pulses.push({ a: from, b: list[(Math.random() * list.length) | 0], t: 0, hops: hops });
      nodes[from].flash = time;
    };
    var movePulses = function (time, dt) {
      if (time > nextPulse && pulses.length < MAXP) {
        nextPulse = time + 500 + Math.random() * 700;
        /* départ de préférence depuis un point proche de la caméra, plus visible */
        var best = -1, bn = -1;
        for (var s = 0; s < 6; s++) {
          var c = (Math.random() * nodes.length) | 0;
          if (proj[c] && adj[c] && adj[c].length && proj[c].near > bn) { bn = proj[c].near; best = c; }
        }
        if (best >= 0) { launch(best, 3 + ((Math.random() * 4) | 0), time); }
      }
      for (var i = pulses.length - 1; i >= 0; i--) {
        var pu = pulses[i], A = proj[pu.a], B = proj[pu.b];
        if (!A || !B || !adj[pu.a] || adj[pu.a].indexOf(pu.b) < 0) { pulses.splice(i, 1); continue; }   /* lien rompu */
        var len = Math.max(20, Math.sqrt((B.x - A.x) * (B.x - A.x) + (B.y - A.y) * (B.y - A.y)));
        pu.t += dt * 0.32 / len;
        if (pu.t >= 1) {
          nodes[pu.b].flash = time;
          var nx = adj[pu.b] ? adj[pu.b].filter(function (n) { return n !== pu.a; }) : [];
          if (--pu.hops > 0 && nx.length) { pu.a = pu.b; pu.b = nx[(Math.random() * nx.length) | 0]; pu.t = 0; }
          else { pulses.splice(i, 1); }
        }
      }
      for (var r = ripples.length - 1; r >= 0; r--) {
        var rp = ripples[r], age = time - rp.t0, rad = 12 + (1 - Math.pow(1 - Math.min(1, age / 1100), 3)) * rp.max;
        /* les points touchés par l'anneau s'allument au passage */
        for (var n = 0; n < proj.length; n++) {
          var q = proj[n], d = Math.sqrt((q.x - rp.x) * (q.x - rp.x) + (q.y - rp.y) * (q.y - rp.y));
          if (Math.abs(d - rad) < 14 && q.near > 0.35 && !q.n.rip && (!q.n.flash || time - q.n.flash > 500)) { q.n.rip = rp.t0; q.n.flash = time; }
        }
        if (age > 1100) { ripples.splice(r, 1); }
      }
    };
    var poke = function (x, y) {
      var time = performance.now();
      ripples.push({ x: x, y: y, t0: time, max: Math.min(320, Math.max(W, H) * 0.28) });
      for (var z = 0; z < nodes.length; z++) { nodes[z].rip = 0; }
      if (ripples.length > 3) { ripples.shift(); }
      /* les trois points les plus proches envoient chacun un signal */
      var near = proj.map(function (q, i) { return { i: i, d: (q.x - x) * (q.x - x) + (q.y - y) * (q.y - y) }; })
        .sort(function (u, v) { return u.d - v.d; }).slice(0, 3);
      near.forEach(function (c) { launch(c.i, 4, time); });
    };

    var last = 0, lastDraw = 0;
    var step = function (time) {
      raf = window.requestAnimationFrame(step);           /* toujours replanifié en premier : la boucle ne peut pas mourir */
      if (time - lastDraw < 15) { return; }                /* 60 images par seconde au maximum */
      lastDraw = time;
      var dt = last ? Math.min(48, time - last) : 16; last = time;
      var f = dt / 16.67;
      for (var i = 0; i < nodes.length; i++) {
        var n = nodes[i];
        n.x += n.vx * f; n.y += n.vy * f; n.z += n.vz * f;
        if (n.x < -BX) { n.x = BX; } else if (n.x > BX) { n.x = -BX; }
        if (n.y < -BY) { n.y = BY; } else if (n.y > BY) { n.y = -BY; }
        if (n.z < -BZ) { n.z = -BZ; n.vz = -n.vz; } else if (n.z > BZ) { n.z = BZ; n.vz = -n.vz; }
      }
      /* caméra : oscillation lente et parallaxe souris, angles bornés */
      var ty = Math.sin(time * 0.00011) * 0.2 + mouse.x * 0.12;
      var tp = Math.cos(time * 0.00008) * 0.08 + mouse.y * 0.08;
      var ease = 1 - Math.pow(0.94, f);
      cam.yaw += (ty - cam.yaw) * ease;
      cam.pitch += (tp - cam.pitch) * ease;
      try { project(); movePulses(time, dt); draw(time); } catch (err) { /* une image ratée ne bloque pas les suivantes */ }
    };
    var start = function () { if (!running && !reduced && visible && !document.hidden && W) { running = true; last = 0; lastDraw = 0; raf = window.requestAnimationFrame(step); } };
    var stop = function () { running = false; window.cancelAnimationFrame(raf); };

    resize(); if (W) { project(); draw(0); }
    /* sur mobile, la barre d'adresse change la hauteur au défilement : on ignore ces petites variations */
    var rt = 0, lastW = W, lastH = H;
    window.addEventListener("resize", function () {
      clearTimeout(rt);
      rt = setTimeout(function () {
        var r = canvas.getBoundingClientRect();
        if (Math.abs(r.width - lastW) < 1 && Math.abs(r.height - lastH) < 140) { return; }
        lastW = r.width; lastH = r.height;
        resize(); project(); draw(performance.now());
      }, 150);
    });
    /* la taille réelle de l'accueil peut changer après le premier affichage (police chargée, texte qui passe
       sur une ligne de plus sur téléphone) : sans ce suivi, le dessin restait étiré jusqu'au prochain redimensionnement */
    if ("ResizeObserver" in window) {
      var roT = 0;
      new ResizeObserver(function () {
        cancelAnimationFrame(roT);
        roT = requestAnimationFrame(function () {
          var r = canvas.getBoundingClientRect();
          if (Math.abs(r.width - W) < 1 && Math.abs(r.height - H) < 1) { return; }
          lastW = r.width; lastH = r.height;
          resize(); project(); draw(performance.now());
        });
      }).observe(canvas);
    }
    var hero = canvas.parentNode;
    /* toucher (ou cliquer) dans l'accueil : une onde part du doigt, sans gêner le défilement */
    hero.addEventListener("pointerdown", function (e) {
      if (reduced || e.target.closest("a, button, input, textarea, label")) { return; }
      var r = canvas.getBoundingClientRect();
      poke(e.clientX - r.left, e.clientY - r.top);
    }, { passive: true });
    if (finePointer) {
      hero.addEventListener("pointermove", function (e) {
        if (e.pointerType !== "mouse") { return; }
        var r = canvas.getBoundingClientRect();
        mouse.sx = e.clientX - r.left; mouse.sy = e.clientY - r.top;
        mouse.x = (mouse.sx / W) * 2 - 1; mouse.y = (mouse.sy / H) * 2 - 1;
        mouse.on = true;
      });
      hero.addEventListener("pointerleave", function () { mouse.on = false; mouse.x = 0; mouse.y = 0; });
    }
    document.addEventListener("visibilitychange", function () { if (document.hidden) { stop(); } else { start(); } });
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (en) { visible = en[0].isIntersecting; if (visible) { start(); } else { stop(); } }).observe(hero);
    }
    start();
  }

  /* Barre de navigation : plus marquée dès qu'on a défilé */
  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 24); };
    window.addEventListener("scroll", onScroll, { passive: true }); onScroll();
  }

  /* Projets : la carte s'incline en 3D vers la souris, une lumière corail suit le curseur
     et allume le contour à l'endroit le plus proche ; la capture glisse en sens inverse (profondeur).
     Tout est lissé image par image et revient à plat en douceur.
     Au doigt (téléphone, tablette), la carte reste à plat : pas d'inclinaison ni de contour. */
  if (canHover) document.querySelectorAll(".project").forEach(function (card) {
    var tx = 0.5, ty = 0.5, cx = 0.5, cy = 0.5, on = 0, ton = 0, praf = 0;
    var shot = card.querySelector(".work-shot img") || card.querySelector("img");
    var frame = function () {
      cx += (tx - cx) * 0.14; cy += (ty - cy) * 0.14; on += (ton - on) * 0.1;
      var rx = (0.5 - cy) * 7 * on, ry = (cx - 0.5) * 9 * on;
      card.style.transform = "perspective(1100px) rotateX(" + rx.toFixed(2) + "deg) rotateY(" + ry.toFixed(2) + "deg) translate3d(0," + (-6 * on).toFixed(2) + "px,0)";
      card.style.setProperty("--mx", (cx * 100).toFixed(2) + "%");
      card.style.setProperty("--my", (cy * 100).toFixed(2) + "%");
      card.style.setProperty("--on", on.toFixed(3));
      if (shot) { shot.style.transform = "scale(" + (1 + 0.05 * on).toFixed(4) + ") translate3d(" + ((0.5 - cx) * 14 * on).toFixed(2) + "px," + ((0.5 - cy) * 10 * on).toFixed(2) + "px,0)"; }
      var still = Math.abs(tx - cx) < 0.001 && Math.abs(ty - cy) < 0.001 && Math.abs(ton - on) < 0.002;
      if (still && ton === 0) { card.style.transform = ""; }
      praf = still ? 0 : requestAnimationFrame(frame);
    };
    var kick = function () { if (!praf) { praf = requestAnimationFrame(frame); } };
    var point = function (e) {
      var r = card.getBoundingClientRect();
      tx = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width));
      ty = Math.max(0, Math.min(1, (e.clientY - r.top) / r.height));
    };
    card.addEventListener("pointerenter", function (e) { point(e); cx = tx; cy = ty; ton = 1; card.classList.add("is-on"); kick(); });
    card.addEventListener("pointermove", function (e) { point(e); kick(); });
    card.addEventListener("pointerleave", function () { tx = 0.5; ty = 0.5; ton = 0; card.classList.remove("is-on"); kick(); });
    card.addEventListener("focus", function () { tx = 0.5; ty = 0.2; ton = 1; card.classList.add("is-on"); kick(); });
    card.addEventListener("blur", function () { tx = 0.5; ty = 0.5; ton = 0; card.classList.remove("is-on"); kick(); });
    if (reduced) { frame = function () { card.style.setProperty("--on", ton); praf = 0; }; }
  });

  /* Accueil : « lien » bascule en glitch vers « nexus » au survol (au toucher sur mobile).
     Les lettres se brouillent quelques images, puis se posent ; la largeur du mot suit en douceur. */
  document.querySelectorAll(".glitch").forEach(function (el) {
    var text = el.querySelector(".glitch-text");
    var word = el.dataset.word, alt = el.dataset.alt;
    var current = word, raf = 0;
    var CHARS = "nexusl!<>/#*_01%&?";
    var measure = function (str) {
      var probe = text.cloneNode(true);
      probe.textContent = str;
      probe.style.position = "absolute"; probe.style.visibility = "hidden";
      el.appendChild(probe);
      var w = probe.getBoundingClientRect().width;
      el.removeChild(probe);
      return w;
    };
    var setShown = function (str) { text.textContent = str; el.setAttribute("data-shown", str); };
    setShown(word);

    var swap = function (target) {
      if (current === target) { return; }
      current = target;
      el.classList.toggle("is-alt", target === alt);
      if (reduced) { setShown(target); return; }
      cancelAnimationFrame(raf);
      el.style.width = el.getBoundingClientRect().width + "px";
      void el.offsetWidth;
      el.style.width = measure(target) + "px";
      el.classList.remove("is-glitching"); void el.offsetWidth; el.classList.add("is-glitching");
      var start = performance.now(), DUR = 420;
      var frame = function (now) {
        var k = Math.min(1, (now - start) / DUR);
        var settled = Math.floor(k * target.length);
        var out = "";
        for (var i = 0; i < target.length; i++) {
          out += i < settled ? target[i] : CHARS[(Math.random() * CHARS.length) | 0];
        }
        setShown(k < 1 ? out : target);
        if (k < 1) { raf = requestAnimationFrame(frame); }
        else { el.classList.remove("is-glitching"); el.style.width = ""; }
      };
      raf = requestAnimationFrame(frame);
    };

    /* Easter egg : « nexus » s'affiche un instant, puis le mot redevient « lien » tout seul.
       Il faut quitter le mot et revenir pour le relancer. */
    var timer = 0, armed = true;
    var play = function () {
      if (!armed) { return; }
      armed = false;
      swap(alt);
      clearTimeout(timer);
      timer = setTimeout(function () { swap(word); }, 1500);
    };
    var rearm = function () { armed = true; };
    el.addEventListener("pointerenter", function (e) { if (e.pointerType !== "touch") { play(); } });
    el.addEventListener("pointerleave", function (e) { if (e.pointerType !== "touch") { rearm(); } });
    el.addEventListener("focus", play);
    el.addEventListener("blur", rearm);
    el.addEventListener("touchstart", function () { rearm(); play(); }, { passive: true });
  });


  /* Montagnes de l'accueil : chaque plan bouge à sa vitesse (souris et défilement), effet de profondeur. */
  var alps = document.querySelectorAll(".hero-alps .alps-layer");
  if (alps.length && !reduced) {
    var heroEl = document.querySelector(".hero");
    var mx = 0, tx = 0, araf = 0;
    var paint = function () {
      mx += (tx - mx) * 0.08;
      var sy = Math.min(window.scrollY, window.innerHeight);
      alps.forEach(function (g) {
        var d = parseFloat(g.getAttribute("data-depth")) || 0;
        g.style.transform = "translate3d(" + (mx * d * -18).toFixed(2) + "px," + (sy * (1.1 - d) * -0.12).toFixed(2) + "px,0)";
      });
      araf = Math.abs(tx - mx) > 0.001 ? requestAnimationFrame(paint) : 0;
    };
    var kick = function () { if (!araf) { araf = requestAnimationFrame(paint); } };
    heroEl.addEventListener("pointermove", function (e) { tx = (e.clientX / window.innerWidth) * 2 - 1; kick(); });
    heroEl.addEventListener("pointerleave", function () { tx = 0; kick(); });
    window.addEventListener("scroll", kick, { passive: true });
  }

  /* La preuve par notre site : poids, temps de chargement, fichiers et cookies mesurés en direct. */
  var proof = document.querySelector(".proof");
  if (proof && window.performance && performance.getEntriesByType) {
    var fmt = function (n, dec) { return new Intl.NumberFormat("fr-CH", { minimumFractionDigits: dec || 0, maximumFractionDigits: dec || 0 }).format(n); };
    var measure = function () {
      var nav = performance.getEntriesByType("navigation")[0];
      var res = performance.getEntriesByType("resource");
      var bytes = 0;
      [nav].concat(res).forEach(function (r) { if (r) { bytes += Math.max(r.transferSize || 0, r.encodedBodySize || 0); } });
      var time = nav && nav.loadEventEnd > 0 ? nav.loadEventEnd : (nav ? nav.domContentLoadedEventEnd : 0);
      return {
        kb: bytes / 1000,
        time: time / 1000,
        req: res.length + 1,
        cookies: document.cookie ? document.cookie.split(";").length : 0
      };
    };
    var countUp = function (el, to, dec) {
      if (!el) { return; }
      if (reduced) { el.textContent = fmt(to, dec); return; }
      var t0 = performance.now(), D = 1400;
      var f = function (now) {
        var k = Math.min(1, (now - t0) / D), e = 1 - Math.pow(1 - k, 4);
        el.textContent = fmt(to * e, dec);
        if (k < 1) { requestAnimationFrame(f); }
      };
      requestAnimationFrame(f);
    };
    var shown = false;
    var show = function () {
      if (shown) { return; } shown = true;
      var m;
      try { m = measure(); } catch (err) { m = { kb: 0 }; }
      if (!m.kb || !isFinite(m.kb)) { proof.classList.add("no-measure"); return; }
      var median = window.innerWidth < 768 ? +proof.dataset.medianMobile : +proof.dataset.medianDesktop;
      countUp(proof.querySelector('[data-metric="kb"]'), m.kb, 0);
      countUp(proof.querySelector('[data-metric="time"]'), m.time, 2);
      countUp(proof.querySelector('[data-metric="req"]'), m.req, 0);
      countUp(proof.querySelector('[data-metric="cookies"]'), m.cookies, 0);
      countUp(proof.querySelector('[data-metric="ratio"]'), m.kb ? median / m.kb : 0, 0);
      proof.querySelector('[data-metric="kb-label"]').textContent = fmt(m.kb, 0) + " Ko";
      proof.querySelector('[data-metric="web-label"]').textContent = fmt(median, 0) + " Ko";
      requestAnimationFrame(function () {
        proof.querySelector('[data-bar="web"]').style.width = "100%";
        proof.querySelector('[data-bar="us"]').style.width = Math.max(1.2, Math.min(100, m.kb / median * 100)) + "%";
      });
    };
    var ready = function () {
      if ("IntersectionObserver" in window) {
        var po = new IntersectionObserver(function (en) { if (en[0].isIntersecting) { show(); po.disconnect(); } }, { threshold: 0.3 });
        po.observe(proof);
      } else { show(); }
    };
    if (document.readyState === "complete") { ready(); } else { window.addEventListener("load", function () { setTimeout(ready, 0); }); }
  }

  /* Méthode : un trait corail relie les étapes au fil du défilement, et allume chaque numéro au passage. */
  var steps = document.querySelector(".steps");
  if (steps) {
    var nums = steps.querySelectorAll(".step-num");
    var items2 = steps.querySelectorAll(".step");
    var line = document.createElement("div"); line.className = "steps-line"; line.setAttribute("aria-hidden", "true");
    var fill = document.createElement("span"); fill.className = "fill"; line.appendChild(fill);
    steps.insertBefore(line, steps.firstChild);
    var mode = "none", target = 0, cur = 0, lraf = 0, marks = [];
    var layout = function () {
      /* positions calculées sans les transformations (apparition, survol) pour rester stables */
      var c = Array.prototype.map.call(nums, function (n) {
        var x = n.offsetLeft + n.offsetWidth / 2, y = n.offsetTop + n.offsetHeight / 2, el = n.offsetParent;
        while (el && el !== steps) { x += el.offsetLeft; y += el.offsetTop; el = el.offsetParent; }
        return { x: x, y: y };
      });
      var sameY = c.every(function (p) { return Math.abs(p.y - c[0].y) < 3; });
      var sameX = c.every(function (p) { return Math.abs(p.x - c[0].x) < 3; });
      var a = c[0], b = c[c.length - 1];
      steps.classList.remove("is-vertical");
      if (sameY) {
        mode = "h"; line.className = "steps-line";
        line.style.cssText = "left:" + a.x + "px;top:" + (a.y - 1) + "px;width:" + (b.x - a.x) + "px;height:2px;display:block";
        marks = c.map(function (p) { return (p.x - a.x) / (b.x - a.x); });
      } else if (sameX) {
        mode = "v"; line.className = "steps-line vertical"; steps.classList.add("is-vertical");
        line.style.cssText = "left:" + (a.x - 1) + "px;top:" + a.y + "px;height:" + (b.y - a.y) + "px;width:2px;display:block";
        marks = c.map(function (p) { return (p.y - a.y) / (b.y - a.y); });
      } else { mode = "none"; line.style.display = "none"; items2.forEach(function (it) { it.classList.add("is-reached"); }); }
    };
    var render2 = function () {
      fill.style.transform = mode === "v" ? "scaleY(" + cur + ")" : "scaleX(" + cur + ")";
      if (mode !== "none") { items2.forEach(function (it, i) { it.classList.toggle("is-reached", cur >= marks[i] - 0.002); }); }
    };
    var loop = function () {
      cur += (target - cur) * 0.12;
      if (Math.abs(target - cur) < 0.0015) { cur = target; }
      render2();
      lraf = cur !== target ? requestAnimationFrame(loop) : 0;
    };
    var onScroll2 = function () {
      var r = steps.getBoundingClientRect(), vh = window.innerHeight;
      target = Math.max(0, Math.min(1, (vh * 0.78 - r.top) / (r.height + vh * 0.2)));
      if (reduced) { cur = target = 1; render2(); return; }
      if (!lraf) { lraf = requestAnimationFrame(loop); }
    };
    layout(); onScroll2();
    window.addEventListener("scroll", onScroll2, { passive: true });
    window.addEventListener("resize", function () { layout(); onScroll2(); });
    window.addEventListener("load", function () { layout(); onScroll2(); });
  }


  /* Ciel nocturne de la méthode : étoiles qui scintillent et, de temps en temps, une étoile filante. */
  var sky = document.querySelector(".night-sky");
  if (sky && sky.getContext) {
    var sc = sky.getContext("2d"), SW = 0, SH = 0, stars = [], shoot = null, nextShoot = 0, sraf = 0, son = false;
    var sizeSky = function () {
      var r = sky.getBoundingClientRect(), d = Math.min(window.devicePixelRatio || 1, 2);
      if (!r.width || !r.height) { return; }
      if (r.width * r.height * d * d > 2.4e6) { d = Math.max(1, Math.sqrt(2.4e6 / (r.width * r.height))); }
      SW = r.width; SH = r.height; sky.width = Math.round(SW * d); sky.height = Math.round(SH * d);
      sc.setTransform(d, 0, 0, d, 0, 0);
      var n = Math.min(canHover ? 420 : 220, Math.round(SW * SH / 3200));
      stars = [];
      for (var i = 0; i < n; i++) {
        var y = Math.pow(Math.random(), 1.6) * SH;            /* plus d'étoiles en haut du ciel */
        stars.push({ x: Math.random() * SW, y: y, r: Math.random() < 0.08 ? 1.3 + Math.random() * 0.7 : 0.35 + Math.random() * 0.8,
                     a: 0.35 + Math.random() * 0.6, s: 0.6 + Math.random() * 2.2, p: Math.random() * 6.28 });
      }
    };
    var drawSky = function (t) {
      sc.clearRect(0, 0, SW, SH);
      for (var i = 0; i < stars.length; i++) {
        var st = stars[i];
        var tw = reduced ? 1 : 0.65 + 0.35 * Math.sin(t / 1000 * st.s + st.p);
        sc.globalAlpha = st.a * tw * (1 - Math.max(0, (st.y / SH - 0.55) * 1.6));
        sc.fillStyle = st.r > 1.2 ? "#FFF6E3" : "#E5E5EA";
        sc.beginPath(); sc.arc(st.x, st.y, st.r, 0, 6.2832); sc.fill();
        if (st.r > 1.2) {
          sc.globalAlpha *= 0.25;
          sc.beginPath(); sc.arc(st.x, st.y, st.r * 3.2, 0, 6.2832); sc.fill();
        }
      }
      sc.globalAlpha = 1;
      if (shoot) {
        var k = (t - shoot.t0) / shoot.d;
        if (k >= 1) { shoot = null; }
        else {
          var hx = shoot.x + shoot.vx * k, hy = shoot.y + shoot.vy * k;
          var g = sc.createLinearGradient(hx, hy, hx - shoot.vx * 0.18, hy - shoot.vy * 0.18);
          var fade = Math.sin(k * Math.PI);
          g.addColorStop(0, "rgba(255,246,227," + (0.95 * fade).toFixed(3) + ")"); g.addColorStop(1, "rgba(255,246,227,0)");
          sc.strokeStyle = g; sc.lineWidth = 1.6; sc.lineCap = "round";
          sc.beginPath(); sc.moveTo(hx, hy); sc.lineTo(hx - shoot.vx * 0.18, hy - shoot.vy * 0.18); sc.stroke();
        }
      }
    };
    var lastSky = 0;
    var skyLoop = function (t) {
      sraf = requestAnimationFrame(skyLoop);
      if (t - lastSky < 32) { return; }                    /* le scintillement est lent : 30 images par seconde suffisent */
      lastSky = t;
      if (!shoot && t > nextShoot) {
        shoot = { x: SW * (0.15 + Math.random() * 0.6), y: SH * (0.05 + Math.random() * 0.25), vx: SW * (0.25 + Math.random() * 0.15) * (Math.random() < 0.5 ? -1 : 1), vy: SH * 0.22, t0: t, d: 900 + Math.random() * 500 };
        nextShoot = t + 5000 + Math.random() * 7000;
      }
      try { drawSky(t); } catch (err) { /* on continue */ }
    };
    var skyStart = function () { if (!son && !reduced && !document.hidden) { son = true; nextShoot = performance.now() + 2500; sraf = requestAnimationFrame(skyLoop); } };
    var skyStop = function () { son = false; cancelAnimationFrame(sraf); };
    sizeSky(); drawSky(0);
    if ("ResizeObserver" in window) {
      var skyR = 0;
      new ResizeObserver(function () {
        cancelAnimationFrame(skyR);
        skyR = requestAnimationFrame(function () {
          var r = sky.getBoundingClientRect();
          if (Math.abs(r.width - SW) < 1 && Math.abs(r.height - SH) < 40) { return; }
          sizeSky(); drawSky(performance.now());
        });
      }).observe(sky);
    }
    var skyT = 0, skyW = SW;
    window.addEventListener("resize", function () {
      clearTimeout(skyT);
      skyT = setTimeout(function () {
        if (Math.abs(sky.getBoundingClientRect().width - skyW) < 1) { return; }   /* barre d'adresse mobile : on ignore */
        skyW = sky.getBoundingClientRect().width; sizeSky(); drawSky(performance.now());
      }, 150);
    });
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (en) { if (en[0].isIntersecting) { skyStart(); } else { skyStop(); } }).observe(sky.parentNode);
    } else { skyStart(); }
    document.addEventListener("visibilitychange", function () { if (document.hidden) { skyStop(); } });
  }

  /* Outils sur mesure : un clic sur un exemple (ou sur le menu de la maquette) affiche l'écran correspondant */
  var mock = document.getElementById("outils-maquette");
  if (mock) {
    var toolBtns = document.querySelectorAll(".tool-btn, .mock-nav-btn");
    var screens = mock.querySelectorAll(".mock-screen");
    var narrow = window.matchMedia("(max-width: 960px)");
    var showTool = function (key) {
      if (mock.getAttribute("data-tool") === key) { return; }
      mock.setAttribute("data-tool", key);
      toolBtns.forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.tool === key ? "true" : "false"); });
      screens.forEach(function (s) { s.hidden = s.dataset.screen !== key; });
    };
    toolBtns.forEach(function (b) {
      b.addEventListener("click", function () {
        showTool(b.dataset.tool);
        // Sur mobile, la maquette est sous la liste : on la fait venir à l'écran
        if (narrow.matches && b.classList.contains("tool-btn")) {
          mock.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "start" });
        }
      });
    });
  }

  /* Année courante */
  var year = document.querySelector("[data-year]");
  if (year) { year.textContent = String(new Date().getFullYear()); }
})();
