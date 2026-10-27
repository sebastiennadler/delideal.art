/* delideal.art — script commun : thème clair/sombre (clé "delideal-theme"),
   menu hamburger, hauteur réelle de la navbar -> --site-nav-offset,
   lien courant marqué aria-current. Fonctionne aussi en local (pas de fetch). */
(function(){
  var root=document.documentElement, KEY="delideal-theme";
  try{ var s=localStorage.getItem(KEY); if(s==="dark"||s==="light") root.setAttribute("data-theme",s);
       else if(!root.getAttribute("data-theme")) root.setAttribute("data-theme","light"); }
  catch(e){ if(!root.getAttribute("data-theme")) root.setAttribute("data-theme","light"); }

  function current(){ return root.getAttribute("data-theme")==="dark"?"dark":"light"; }
  function paintToggle(btn){
    var dark=current()==="dark"; var icon=btn.querySelector(".theme-icon")||btn;
    icon.textContent = dark ? "☾" : "☀︎";
    btn.setAttribute("aria-label", dark ? "Fond sombre (cliquer pour passer en clair)" : "Fond clair (cliquer pour passer en sombre)");
    btn.title = dark ? "Fond sombre" : "Fond clair";
  }
  function setNavOffset(){ var nav=document.querySelector("nav.navbar"); if(!nav) return;
    root.style.setProperty("--site-nav-offset", (nav.getBoundingClientRect().height+12)+"px"); }

  document.addEventListener("DOMContentLoaded",function(){
    var btn=document.getElementById("theme-toggle");
    if(btn){ paintToggle(btn); btn.addEventListener("click",function(){
      var n=current()==="dark"?"light":"dark"; root.setAttribute("data-theme",n);
      try{localStorage.setItem(KEY,n);}catch(e){} paintToggle(btn); }); }
    var burger=document.getElementById("menu-toggle"), links=document.getElementById("primary-nav");
    if(burger&&links){ burger.addEventListener("click",function(){
      var open=links.classList.toggle("open"); burger.setAttribute("aria-expanded", open?"true":"false");
      burger.setAttribute("aria-label", open?"Fermer le menu":"Ouvrir le menu"); }); }
    var here=location.pathname.split("/").pop()||"index.html";
    document.querySelectorAll(".nav-links a").forEach(function(a){
      var t=a.getAttribute("href").split("/").pop()||"index.html";
      if(t===here) a.setAttribute("aria-current","page"); });
    setNavOffset(); window.addEventListener("resize",setNavOffset);
  });
})();
