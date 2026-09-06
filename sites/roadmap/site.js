(()=>{
  const root=document.documentElement;
  const key='goreecloud-roadmap-appearance';
  const button=document.querySelector('[data-theme-toggle]');
  let appearance='system';
  try{appearance=localStorage.getItem(key)||'system';}catch(_){}

  const apply=()=>{
    if(appearance==='dark')root.dataset.glzAppearance='dark';
    else if(appearance==='light')root.dataset.glzAppearance='light';
    else root.removeAttribute('data-glz-appearance');
    if(button){
      const label=appearance==='system'?'System':appearance[0].toUpperCase()+appearance.slice(1);
      button.textContent=`Appearance: ${label}`;
      button.setAttribute('aria-label',`Appearance: ${label}. Change appearance.`);
    }
  };

  apply();
  button?.addEventListener('click',()=>{
    appearance=appearance==='system'?'light':appearance==='light'?'dark':'system';
    apply();
    try{localStorage.setItem(key,appearance);}catch(_){}
  });
})();
