(()=>{const e=document.querySelector(".cookie-box"),t=document.querySelector(".cookie-btn");t?.addEventListener("click",(()=>{localStorage.setItem("cookie","true"),e?.classList.add("hide")})),localStorage.getItem("cookie")||e?.classList.remove("hide");let s=document.querySelector(".hamburger"),a=document.querySelector(".nav-list"),c=document.querySelectorAll(".menu-close");function o(){s.classList.contains("is-active")?s.setAttribute("aria-expanded","true"):s.setAttribute("aria-expanded","false")}const l=()=>{s.classList.remove("is-active"),s.classList.remove("fixed"),s.classList.add("absolute"),a.classList.remove("opacity-1"),a.classList.remove("scale-1"),a.classList.add("opacity-0"),a.classList.add("scale-0"),a.classList.remove("max-h-dvh"),a.classList.add("max-h-0"),o()};s?.addEventListener("click",(function(){a.classList.toggle("scale-0"),a.classList.toggle("scale-1"),a.classList.toggle("opacity-0"),a.classList.toggle("opacity-1"),a.classList.toggle("max-h-0"),a.classList.toggle("max-h-dvh"),s.classList.toggle("is-active"),s.classList.toggle("absolute"),s.classList.toggle("fixed"),o()})),c?.forEach((e=>{e.addEventListener("click",l)}));const i=(e,t)=>{const s=document.querySelector(e);null!==s&&(s.style.display=t?"flex":"none")};i(".page",!1),i("#loading",!0),document.addEventListener("DOMContentLoaded",(()=>((e=0)=>new Promise((t=>setTimeout(t,e))))().then((()=>{i(".page",!0),i("#loading",!1)}))))})();