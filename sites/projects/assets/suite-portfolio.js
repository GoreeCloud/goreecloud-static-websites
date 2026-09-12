const suitePortfolioGroups=Object.freeze({
  'Productivity & organization':['GoreeCloud Notes','GoreeCloud Memos','GoreeCloud Tasks','GoreeCloud Calendar','GoreeCloud Contacts','GoreeCloud Documents'],
  'Storage, media & library':['GoreeCloud Drive','GoreeCloud File Manager','GoreeCloud Sync','GoreeCloud Photos','GoreeCloud Gallery','GoreeCloud Music','GoreeCloud Video','GoreeCloud Bookmarks','GoreeCloud Reader'],
  'Communication & discovery':['GoreeCloud Mail','GoreeCloud Messenger','GoreeCloud Search','GoreeCloud Browser','GoreeCloud Feed','GoreeCloud Location','GoreeCloud Maps','GoreeCloud Social'],
  'Devices & interface':['GoreeCloud Keyboard','GoreeCloud Launcher','GoreeCloud Terminal'],
  'Platform & operations':['GoreeCloud Manager','GoreeCloud App Store','GoreeCloud Identity','GoreeCloud Vault','GoreeCloud Backup','GoreeCloud Network','GoreeCloud DNS','GoreeCloud Gateway','GoreeCloud Notify','GoreeCloud Monitor','GoreeCloud Changelogs'],
  'Developer & intelligence':['GoreeCloud AI','GoreeCloud Index','GoreeCloud Code'],
  'Home, health & personal systems':['GoreeCloud Health','GoreeCloud Home','GoreeCloud Home Security'],
  'Infrastructure & edge products':['GoreeCloud Router OS'],
  'Public experience':['GoreeCloud Website']
});

const suitePortfolioNames=new Set(Object.values(suitePortfolioGroups).flat());
const suiteGroupByName=new Map();
for(const [group,names] of Object.entries(suitePortfolioGroups))for(const name of names)suiteGroupByName.set(name,group);

if(suitePortfolioNames.size!==45)throw new Error(`Suite portfolio contract expected 45 products, found ${suitePortfolioNames.size}`);
if(Object.keys(suitePortfolioGroups).length!==9)throw new Error('Suite portfolio contract expected 9 functional groups');

const currentSuiteAdditions=[
  {name:'GoreeCloud Index',repo:'goreecloud-index',category:'Developer & Intelligence',model:'Native',kind:'Application',status:'Development · native Android foundation',role:'Canonical universal search and indexing product for authorized device and GoreeCloud resources. Internet results remain delegated to GoreeCloud Search; production and Stable acceptance are not established.',visibility:'Public'},
  {name:'GoreeCloud Vault',repo:'goreecloud-vault',category:'Personal Data & Security',model:'Native product direction',kind:'Application',status:'Active development',role:'Canonical GoreeCloud credential, password, passkey, secret, recovery-information, secure-note, and encrypted-vault product family. GoreeCloud Vault Server is its backend identity; production and Stable acceptance are not established.',visibility:'Public'},
  {name:'GoreeCloud Health',repo:'goreecloud-health',category:'Home, Health & Personal',model:'Native',kind:'Application',status:'Development · foundation',role:'Personal health and wellness application for web and Android. Current source uses synthetic-only health records and fail-closed privacy boundaries; real health-data ingestion and production acceptance are not established.',visibility:'Public'},
  {name:'GoreeCloud Reader',repo:'goreecloud-reader',category:'Communication & Media',model:'Native',kind:'Application',status:'Development · 0.0.2 foundation',role:'Private reading and listening library for books, manga, comics, ebooks, PDFs, and audiobooks with specialized reader and player experiences. The complete product workflow and production acceptance remain pending.',visibility:'Public'},
  {name:'GoreeCloud Social',repo:'goreecloud-social',category:'Communication & Media',model:'Native',kind:'Application',status:'Development · 0.1.0-dev.6',role:'First-party social publishing, profiles, relationships, groups, communities, media, reactions, discovery, and moderation application with explicit audience, privacy, and authority boundaries.',visibility:'Public'},
  {name:'GoreeCloud Home',repo:'goreecloud-home',category:'Home, Health & Personal',model:'Native',kind:'Application',status:'Development · 0.1.0-dev.5',role:'Local-first smart-home control and automation application with a protocol-neutral device/capability model and durable local state. Physical protocol and production platform acceptance remain pending.',visibility:'Public'},
  {name:'GoreeCloud Home Security',repo:'goreecloud-home-security',category:'Home, Health & Personal',model:'Native',kind:'Application',status:'Development',role:'Local-first camera security, NVR, event-detection, review, and alerting application. Current development evidence does not establish a production NVR, Stable release, or production security acceptance.',visibility:'Public'},
  {name:'GoreeCloud Router OS',repo:'goreecloud-router-os',category:'Internet & Networking',model:'Native product on mature Linux networking foundations',kind:'Product',status:'Proposed · Milestone 0 source proof',role:'First-party router, firewall, network-edge, and local-network management platform. Milestone 0 source proofs do not complete Reference Build 0.1 or establish production qualification.',visibility:'Public'}
];

for(const addition of currentSuiteAdditions){
  if(!entries.some(entry=>entry.name===addition.name))entries.push(addition);
}

for(const entry of entries){
  entry.suiteMember=suitePortfolioNames.has(entry.name);
  entry.suiteGroup=entry.suiteMember?suiteGroupByName.get(entry.name):null;
}

const suiteProducts=[...entries].filter(entry=>entry.suiteMember);
if(suiteProducts.length!==45){
  const present=new Set(suiteProducts.map(entry=>entry.name));
  const missing=[...suitePortfolioNames].filter(name=>!present.has(name));
  throw new Error(`Projects Suite portfolio expected 45 cards; missing: ${missing.join(', ')}`);
}

const integralPlatformSystems=new Set(['GoreeCloud Manager','GoreeCloud Identity','Glaze UI','Wardveil Security','GoreeCloud Privacy Shield','Everkeep','GoreeCloud Mesh']);
appCount.textContent=String(suitePortfolioNames.size);
if(appCount.nextElementSibling)appCount.nextElementSibling.textContent='Suite products';
foundationCount.textContent=String(integralPlatformSystems.size);
if(foundationCount.nextElementSibling)foundationCount.nextElementSibling.textContent='Integral platform systems';

const projectsBaseMatchesFilter=matchesFilter;
matchesFilter=function(entry){
  if(filter==='Suite products')return entry.suiteMember===true;
  return projectsBaseMatchesFilter(entry);
};

const suiteFilterButton=document.createElement('button');
suiteFilterButton.className='filter';
suiteFilterButton.type='button';
suiteFilterButton.textContent='Suite products';
suiteFilterButton.dataset.filter='Suite products';
suiteFilterButton.setAttribute('aria-pressed','false');
suiteFilterButton.addEventListener('click',()=>{
  filter='Suite products';
  document.querySelectorAll('.filter').forEach(item=>item.setAttribute('aria-pressed',String(item===suiteFilterButton)));
  render();
});
filters.insertBefore(suiteFilterButton,filters.children[1]||null);

const projectsBaseCard=card;
card=function(entry){
  const article=projectsBaseCard(entry);
  article.dataset.suiteMember=String(entry.suiteMember===true);
  if(entry.suiteMember){
    const meta=article.querySelector('.card-meta');
    const suiteBadge=document.createElement('span');
    suiteBadge.className='badge suite-membership';
    suiteBadge.textContent=entry.suiteGroup?`Suite · ${entry.suiteGroup}`:'Suite product';
    meta?.prepend(suiteBadge);
  }else{
    const kind=article.querySelector('.kind');
    if(kind&&entry.kind==='Application')kind.textContent='Additional project';
  }
  return article;
};

render();
