/* KÉT Sans specimen runtime. Data comes from data.js (generated from the built OTF). */
(() => {
  "use strict";
  const K = window.KET_SANS;
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
  const supported = new Set(K.codepoints);
  const byCp = new Map();
  for (const [name, g] of Object.entries(K.glyphs)) for (const u of g.u) byCp.set(u, name);
  const m = K.metrics;

  const has = (ch) => ch === "\n" || ch === " " || [...ch.normalize("NFC")].every((c) => supported.has(c.codePointAt(0)));

  // ------------------------------------------------------------ missing glyphs
  function markMissing(root) {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    for (const node of nodes) {
      if (node.parentElement.closest(".ket-missing")) continue;
      const text = node.nodeValue;
      if ([...text].every(has)) continue;
      const frag = document.createDocumentFragment();
      let run = "";
      for (const ch of text) {
        if (has(ch)) { run += ch; continue; }
        if (run) frag.append(run), (run = "");
        const span = document.createElement("span");
        span.className = "ket-missing";
        span.title = `Ngoài bảng chữ: U+${ch.codePointAt(0).toString(16).toUpperCase().padStart(4, "0")}`;
        span.textContent = ch;
        frag.append(span);
      }
      if (run) frag.append(run);
      node.replaceWith(frag);
    }
  }
  const refreshMissing = () => $$("[data-check]").forEach(markMissing);

  // ------------------------------------------------------------ overview
  function facts() {
    const st = K.system.masters.Regular.stroke;
    const ov = m.overshoot;
    const rows = [
      ["Phiên bản", `${K.version} — ${K.phase}`],
      ["Glyph", `${Object.keys(K.glyphs).length} glyph, ${K.codepoints.length} codepoint`],
      ["UPM / x-height / cap", `${m.unitsPerEm} / ${m.xHeight} (${(m.xHeight / m.unitsPerEm).toFixed(3)} em) / ${m.capHeight} (${(m.capHeight / m.unitsPerEm).toFixed(3)} em)`],
      ["Ascender / descender", `${m.ascender} / ${m.descender}`],
      ["Overshoot hoa / thường / vai", `${ov.capRound} / ${ov.lowercaseRound} / ${ov.arch}`],
      ["Stem hoa / thường", `${st.stemUpper} / ${st.stemLower}`],
      ["Nét ngang hoa / thường", `${st.barUpper} / ${st.barLower}`],
      ["Tròn hoa cạnh/đỉnh", `${st.roundUpperSide} / ${st.roundUpperTop}`],
      ["Tròn thường cạnh/đỉnh", `${st.roundLowerSide} / ${st.roundLowerTop}`],
      ["Line box", `${m.line.typoAscender} / ${m.line.typoDescender} (${((m.line.typoAscender - m.line.typoDescender) / m.unitsPerEm).toFixed(3)} em)`],
    ];
    $("#facts").innerHTML = rows.map(([k, v]) => `<tr><th>${k}</th><td>${v}</td></tr>`).join("");
    $("#identity").innerHTML = '<tr><th colspan="2">Đặc điểm nhận diện</th></tr>' +
      K.system.identity.map((t) => `<tr><th>${t.trait}</th><td>${t.rule}</td></tr>`).join("");
    $("#version").textContent = `v${K.version} · Light–Bold · ${K.phase.split(" — ")[0]}`;
  }

  // ------------------------------------------------------------ glyph grids
  function cell(ch) {
    const cp = ch.codePointAt(0);
    const ok = supported.has(cp);
    const el = document.createElement(ok ? "button" : "div");
    el.className = "cell" + (ok ? "" : " pending");
    el.innerHTML = `<span class="ch ${ok ? "ket" : ""}">${ch}</span><span class="cp">U+${cp.toString(16).toUpperCase().padStart(4, "0")}</span>`;
    if (ok) {
      el.type = "button";
      el.setAttribute("aria-pressed", "false");
      el.title = byCp.get(cp);
      el.addEventListener("click", () => showGlyph(byCp.get(cp), el));
    } else {
      el.title = "Ngoài bảng chữ";
    }
    return el;
  }
  function grids() {
    for (const g of $$("[data-grid]")) for (const ch of g.dataset.grid) g.append(cell(ch));
    const vowels = "aăâeêioôơuưyAĂÂEÊIOÔƠUƯY";
    const tones = ["", "̀", "́", "̉", "̃", "̣"];
    const vg = $("#viet-grid");
    for (const v of vowels) for (const t of tones) vg.append(cell((v + t).normalize("NFC")));
    vg.append(cell("đ"), cell("Đ"));
    const viet = new Set([...vowels].flatMap((v) => tones.map((t) => (v + t).normalize("NFC"))));
    const lg = $("#latin-grid");
    for (const cp of K.codepoints) {
      const ch = String.fromCodePoint(cp);
      if (ch.normalize("NFD").length > 1 && !viet.has(ch) && /\p{L}/u.test(ch)) lg.append(cell(ch));
    }
    const word = "Việt dẫn mại hòa liệu ỗ ợ ừ ặ ẳ ẤN ỘI Ở";
    $("#nfc").textContent = word.normalize("NFC");
    $("#nfd").textContent = word.normalize("NFD");
  }

  // ------------------------------------------------------------ glyph detail
  function showGlyph(name, button) {
    const g = K.glyphs[name];
    if (!g) return;
    $$(".cell[aria-pressed]").forEach((c) => c.setAttribute("aria-pressed", String(c === button)));
    const pad = 120;
    const top = 2040, bottom = -520;
    const w = Math.max(g.w, 600);
    const svg = $("#glyph-svg");
    svg.setAttribute("viewBox", `${-pad} ${-top} ${w + 2 * pad} ${top - bottom}`);
    const lines = [
      ["baseline", 0], ["x-height", m.xHeight], ["cap", m.capHeight], ["ascender", m.ascender], ["descender", m.descender],
    ];
    const zones = [m.xHeight + m.overshoot.lowercaseRound, m.capHeight + m.overshoot.capRound, -m.overshoot.lowercaseRound];
    const metric = lines.map(([label, y]) =>
      `<line x1="${-pad}" x2="${w + pad}" y1="${-y}" y2="${-y}"/><text x="${-pad + 10}" y="${-y - 14}">${label} ${y}</text>`).join("") +
      zones.map((y) => `<line class="zone" x1="${-pad}" x2="${w + pad}" y1="${-y}" y2="${-y}"/>`).join("");
    const pts = g.p;
    let handles = "";
    pts.forEach((p, i) => {
      if (p[2]) return;
      const prev = pts[i - 1], next = pts[i + 1];
      if (prev && prev[2]) handles += `<line class="handle" x1="${prev[0]}" y1="${-prev[1]}" x2="${p[0]}" y2="${-p[1]}"/>`;
      if (next && next[2]) handles += `<line class="handle" x1="${p[0]}" y1="${-p[1]}" x2="${next[0]}" y2="${-next[1]}"/>`;
    });
    const dots = pts.map((p) => p[2]
      ? `<rect class="on" x="${p[0] - 9}" y="${-p[1] - 9}" width="18" height="18"/>`
      : `<circle class="off" cx="${p[0]}" cy="${-p[1]}" r="9"/>`).join("");
    svg.innerHTML = `<g class="metric">${metric}</g>
      <rect class="box" x="0" y="${-top + 40}" width="${g.w}" height="${top - bottom - 80}"/>
      <g transform="scale(1,-1)"><path class="fill" d="${g.d}"/></g>${handles}${dots}`;
    let xs = pts.map((p) => p[0]);
    const lsb = xs.length ? Math.min(...xs) : 0;
    const rsb = xs.length ? g.w - Math.max(...xs) : 0;
    const uni = g.u.map((u) => `U+${u.toString(16).toUpperCase().padStart(4, "0")}`).join(", ") || "—";
    const rows = [
      ["Glyph", name], ["Unicode", uni], ["Advance", g.w], ["LSB / RSB (theo outline)", `${Math.round(lsb)} / ${Math.round(rsb)}`],
      ["Điểm (trên đường / handle)", `${pts.filter((p) => p[2]).length} / ${pts.filter((p) => !p[2]).length}`],
    ];
    if (g.note) rows.push(["Kế thừa", g.note]);
    $("#glyph-facts").innerHTML = rows.map(([k, v]) => `<tr><th>${k}</th><td>${v}</td></tr>`).join("");
  }

  // ------------------------------------------------------------ comparisons
  const REFS = { sf: ["SF Pro", "ref-sf"], inter: ["Inter", "ref-inter"], bvp: ["Be Vietnam Pro", "ref-bvp"] };
  const refsFor = (v) => (v === "none" ? [] : v === "all" ? Object.keys(REFS) : [v]);
  const COMPARE_TEXT = "Hóa đơn, khách hàng, công nợ 12.480.500 ₫ HD-2045 AVA Ty fjord quý";

  function rowsFor(text, size, weight = 400) {
    const out = [`<div class="compare-row"><span class="who">KÉT ${weight} ${size}px</span><span class="ket" style="font-size:${size}px;font-weight:${weight}" data-check>${text}</span></div>`];
    for (const key of refsFor($("#compare").value)) {
      const [label, cls] = REFS[key];
      out.push(`<div class="compare-row"><span class="who">${label} ${weight} ${size}px</span><span class="${cls}" style="font-size:${size}px;font-weight:${weight}">${text}</span></div>`);
    }
    return out.join("");
  }
  const weight = () => Number($("#weight").value);
  function renderCompare() {
    $("#weight-rows").innerHTML = [300, 400, 500, 700].map((w) => rowsFor(COMPARE_TEXT, 32, w)).join("");
    $("#size-compare").innerHTML = [11, 12, 13, 14, 16, 20, 24, 32]
      .map((s) => `<div class="compare-rows">${rowsFor(COMPARE_TEXT, s, weight())}</div>`).join("");
    $("#waterfall").innerHTML = [11, 12, 13, 14, 16, 20, 24, 32]
      .map((s) => `<div class="line"><span class="label">${s}px</span><span style="font-size:${s}px">Báo cáo quý III: doanh thu đạt 12,5 tỷ ₫, tăng 8,4% so với cùng kỳ; công nợ quá hạn còn 17 hóa đơn.</span></div>`).join("");
    refreshMissing();
  }

  // ------------------------------------------------------------ controls
  function bind() {
    const size = $("#size"), num = $("#size-num");
    const setSize = (v) => {
      v = Math.max(11, Math.min(160, Number(v) || 40));
      size.value = num.value = v;
      $$(".cell .ch").forEach((el) => (el.style.fontSize = `${Math.min(v, 64)}px`));
      $$(".sample").forEach((el) => el.style.setProperty("--size", `${v}px`));
    };
    size.addEventListener("input", () => setSize(size.value));
    num.addEventListener("change", () => setSize(num.value));
    $("#kern").addEventListener("change", (e) => (document.body.dataset.kern = e.target.checked ? "on" : "off"));
    $("#missing").addEventListener("change", (e) => (document.body.dataset.missing = e.target.checked ? "on" : "off"));
    const theme = $("#theme");
    theme.checked = matchMedia("(prefers-color-scheme: dark)").matches;
    const applyTheme = () => (document.documentElement.dataset.theme = theme.checked ? "dark" : "light");
    theme.addEventListener("change", applyTheme);
    applyTheme();
    $("#compare").addEventListener("change", renderCompare);
    $("#weight").addEventListener("change", (e) => {
      document.body.style.setProperty("--wght", e.target.value);
      renderCompare();
    });
    for (const el of $$("[contenteditable]")) el.addEventListener("blur", () => markMissing(el));
  }

  facts();
  grids();
  bind();
  renderCompare();
  showGlyph("n", $$(".cell").find((c) => c.title === "n"));
  document.fonts.ready.then(() => document.documentElement.setAttribute("data-fonts", "ready"));
})();
