/* The Living Indexes — hub client. Render the 4 index cards with live counts from data.json. */
(function () {
  "use strict";
  var $ = function (s) { return document.querySelector(s); };
  function esc(s) { return (s == null ? "" : String(s)).replace(/[&<>"']/g, function (m) {
    return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[m]; }); }

  var saved = null;
  try { saved = localStorage.getItem("li-theme"); } catch (e) {}
  if (saved) document.documentElement.setAttribute("data-theme", saved);
  $("#theme").addEventListener("click", function () {
    var cur = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", cur);
    try { localStorage.setItem("li-theme", cur); } catch (e) {}
  });

  function countUp(el, target) {
    var dur = 1100, t0 = null;
    function step(t) { if (!t0) t0 = t; var p = Math.min((t - t0) / dur, 1);
      el.textContent = Math.round((1 - Math.pow(1 - p, 3)) * target).toLocaleString();
      if (p < 1) requestAnimationFrame(step); }
    requestAnimationFrame(step);
  }

  function card(ix) {
    var cats = (ix.categories || []).map(function (c) { return '<span class="cat">' + esc(c) + "</span>"; }).join("");
    var top = ix.top && ix.top.name ? '<div class="top">top: <b>' + esc(ix.top.name) + "</b> · " + ix.top.momentum + "</div>" : "";
    return (
      '<a class="card" href="' + esc(ix.url) + '" target="_blank" rel="noopener" style="--accent:' + esc(ix.accent) + '">' +
        '<div class="tag">' + esc(ix.tag) + "</div>" +
        '<div class="name serif">' + esc(ix.name) + "</div>" +
        '<div class="blurb">' + esc(ix.blurb) + "</div>" +
        '<div class="stat-row"><div class="count serif">' + (ix.count == null ? "—" : ix.count.toLocaleString()) +
          '<span class="u">indexed</span></div></div>' +
        top + '<div class="cats">' + cats + "</div>" +
        '<div class="go">Explore the index →</div>' +
      "</a>"
    );
  }

  fetch("/data.json?v=" + Date.now()).then(function (r) { return r.json(); }).then(function (d) {
    countUp($("#total"), d.total_indexed || 0);
    $("#grid").innerHTML = (d.indexes || []).map(card).join("");
    var cards = document.querySelectorAll(".card");
    requestAnimationFrame(function () {
      cards.forEach(function (c, i) { setTimeout(function () { c.classList.add("in"); }, i * 90); });
    });
    if (d.generated_at) $("#updated").textContent = "Synced " + new Date(d.generated_at).toUTCString().replace("GMT", "UTC");
  }).catch(function () { $("#grid").innerHTML = '<div style="color:var(--faint);padding:40px">Could not load the fleet. Refresh to retry.</div>'; });
})();
