(()=>{
  const root=document.documentElement;
  const key='goreecloud-labs-theme';
  const choices=[...document.querySelectorAll('[data-theme-choice]')];
  const apply=choice=>{
    const value=['system','light','dark'].includes(choice)?choice:'system';
    root.dataset.theme=value;
    localStorage.setItem(key,value);
    choices.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.themeChoice===value)));
  };
  apply(localStorage.getItem(key)||'system');
  choices.forEach(button=>button.addEventListener('click',()=>apply(button.dataset.themeChoice)));

  const filters=[...document.querySelectorAll('[data-filter]')];
  const lanes=[...document.querySelectorAll('[data-lane]')];
  const filter=value=>{
    filters.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.filter===value)));
    lanes.forEach(lane=>{lane.hidden=value!=='all'&&lane.dataset.lane!==value;});
  };
  filters.forEach(button=>button.addEventListener('click',()=>filter(button.dataset.filter||'all')));
})();
