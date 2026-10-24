document.addEventListener('DOMContentLoaded',()=>{
  document.querySelectorAll('.nav-link').forEach(a=>{if(a.getAttribute('href')===location.pathname)a.classList.add('active')});
  const btn=document.getElementById('mobileMenu'); if(btn) btn.addEventListener('click',()=>document.querySelector('.sidebar').classList.toggle('open'));
});
