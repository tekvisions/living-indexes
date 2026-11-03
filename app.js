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

  function countUp(el, target) { el.textContent=target.toLocaleString(); }

  function card(ix) {
    ix=Object.assign({},ix);
    if(ix.top&&["gathin23/cleanyourtv","harry0703/moneyprinterturbo","designfuchen/word-atlas"].indexOf(String(ix.top.name).toLowerCase())!==-1){ix.top=null;ix.review_note="A previously featured entry is now an unranked reference under inclusion review; consult the index.";}
    if(ix.key==="mcp")ix.blurb="Model Context Protocol registry entries; check source coverage on the index.";
    var cats = (ix.categories || []).map(function (c) { return '<span class="cat">' + esc(c) + "</span>"; }).join("");
    var top = ix.top && ix.top.name ? '<div class="top">top: <b>' + esc(ix.top.name) + "</b>" + (ix.top.momentum ? " · " + ix.top.momentum : "") + "</div>" : "";
    return (
      '<a class="card" href="' + esc(ix.url) + '" target="_blank" rel="noopener" style="--accent:' + esc(ix.accent) + '">' +
        '<div class="tag">' + esc(ix.tag) + "</div>" +
        '<div class="name serif">' + esc(ix.name) + "</div>" +
        '<div class="blurb">' + esc(ix.blurb) + "</div>" +
        '<div class="stat-row"><div class="count serif">' + (ix.count == null ? "—" : ix.count.toLocaleString()) +
          '<span class="u">indexed</span></div></div>' +
        '<p class="summary-date">Source snapshot: ' + esc(ix.generated_at ? ix.generated_at.slice(0,10) : "unknown") + '</p>' + (ix.review_note ? '<p class="summary-note">'+esc(ix.review_note)+'</p>' : '') + (ix.coverage_note ? '<p class="summary-note">'+esc(ix.coverage_note)+'</p>' : '') + top + '<div class="cats">' + cats + "</div>" +
        '<div class="go">Explore the index →</div>' +
      "</a>"
    );
  }

  fetch("/catalog.json?v=" + Date.now()).then(function (r) { return r.json(); }).then(function (d) {
    countUp($("#total"), d.total_indexed || 0);
    $("#grid").innerHTML = (d.indexes || []).map(card).join("");
    var cards = document.querySelectorAll(".card");
    requestAnimationFrame(function () {
      cards.forEach(function (c, i) { setTimeout(function () { c.classList.add("in"); }, i * 90); });
    });
    if (d.generated_at) $("#updated").textContent = "Synced " + new Date(d.generated_at).toUTCString().replace("GMT", "UTC");
  }).then(function(){if(window.dispatchEvent&&window.Event)window.dispatchEvent(new window.Event("catalog:ready"));}).catch(function () {
    if(window.dispatchEvent&&window.Event)window.dispatchEvent(new window.Event("catalog:error")); $("#updated").textContent = "Live refresh unavailable. Showing the published snapshot below."; });
})();
