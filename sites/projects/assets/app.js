const entries=[
{name:'GoreeCloud Suite',repo:'goreecloud-suite',category:'Platform & Administration',model:'Ecosystem authority',kind:'Foundation',status:'Active',role:'Portfolio-level authority for the integrated GoreeCloud application ecosystem, shared boundaries, interoperability, and Suite-wide conventions.',visibility:'Private'},
{name:'GoreeCloud Manager',repo:'goreecloud-manager',category:'Platform & Administration',model:'Native',kind:'Application',status:'Active development',role:'Central administration, operations, service health, protection status, and management console.',visibility:'Public'},
{name:'GoreeCloud Monitor',repo:'goreecloud-monitor',category:'Platform & Administration',model:'Native',kind:'Application',status:'Active development',role:'Infrastructure and service monitoring, observability, health visibility, and operational monitoring.',visibility:'Public'},
{name:'GoreeCloud Notify',repo:'goreecloud-notify',category:'Platform & Administration',model:'Native',kind:'Application',status:'Release candidate · native client foundation merged',role:'Notifications, system alerts, operational messages, and application delivery. The first-party Linux/Debian and Android client source foundation is merged; persistent Android delivery, production cutover, and ntfy retirement remain separate acceptance gates.',visibility:'Private'},
{name:'GoreeCloud Backup',repo:'goreecloud-backup',category:'Platform & Administration',model:'Maintained fork',kind:'Application',status:'Active development',role:'Backup repositories, snapshots, restoration, recovery, and protected-data workflows beneath the Everkeep resilience model.',visibility:'Public'},
{name:'GoreeCloud Identity',repo:'goreecloud-identity',category:'Platform & Administration',model:'Identity platform system',kind:'Application',status:'Active development',role:'First-party GoreeCloud platform system responsible for identity, authentication, authorization, accounts, devices, credentials, sessions, delegated authority, and user-facing identity services. Public readiness claims remain evidence-scoped.',visibility:'Public'},
{name:'GoreeCloud GitHub Dashboard',repo:'goreecloud-github-dashboard',category:'Platform & Administration',model:'Native',kind:'Application',status:'Active development',role:'Private dashboard for repository activity, changelogs, pull requests, issues, releases, and project health.',visibility:'Private'},
{name:'GoreeCloud Network',repo:'goreecloud-network',category:'Internet & Networking',model:'Maintained fork to native',kind:'Application',status:'Active development',role:'Private networking, device enrollment, access policies, secure remote connectivity, and first-party Conduit capabilities.',visibility:'Public'},
{name:'GoreeCloud DNS',repo:'goreecloud-dns',category:'Internet & Networking',model:'Maintained fork to native',kind:'Application',status:'Active development',role:'DNS filtering, encrypted DNS, caching, policy management, and Beacon capabilities. Recursive resolution remains a separate responsibility and is not claimed by this product surface.',visibility:'Public'},
{name:'GoreeCloud Search',repo:'goreecloud-search',category:'Internet & Networking',model:'Maintained fork',kind:'Application',status:'Production service · RC #09 validation',role:'Private web search and GoreeCloud-controlled research gateway. The latest RC #09 source line includes the rebuilt Glaze UI experience plus Privacy Shield and Wardveil Security integrations while release and production evidence remain explicitly scoped.',visibility:'Public'},
{name:'GoreeCloud Browser',repo:'goreecloud-browser',category:'Internet & Networking',model:'Maintained fork',kind:'Application',status:'Active development',role:'Privacy-first Firefox-based browser integrated with GoreeCloud Search, Privacy Shield, Glaze UI, and Wardveil Security.',visibility:'Public'},
{name:'GoreeCloud Drive',repo:'goreecloud-drive',category:'Productivity & Knowledge',model:'Native',kind:'Application',status:'Milestone 1 · persistent node CRUD',role:'Private multi-user cloud storage and file management. Milestone 1 now persists file/folder metadata in PostgreSQL with trusted-principal and Space-membership authorization, fail-closed service enforcement, Drop-only privacy preservation, and strict request validation.',visibility:'Public'},
{name:'GoreeCloud Sync',repo:'goreecloud-sync',category:'Productivity & Knowledge',model:'Native',kind:'Application',status:'Active development',role:'Private multi-user synchronization and secure-transfer platform for nearby and remote file and device workflows.',visibility:'Public'},
{name:'GoreeCloud Notes',repo:'goreecloud-notes',category:'Productivity & Knowledge',model:'Native',kind:'Application',status:'Active development',role:'Full notes, knowledge management, retrieval, attachments, revision recovery, and portable data workflows.',visibility:'Public'},
{name:'GoreeCloud Memos',repo:'goreecloud-memos',category:'Productivity & Knowledge',model:'Maintained fork',kind:'Application',status:'Stable web/server 0.1.3 · client acceptance in progress',role:'Lightweight quick-note capture for focused notes, snippets, lists, reminders, and ideas; v0.1.3 is accepted for the production web/server while newer client acceptance remains separate.',visibility:'Public'},
{name:'GoreeCloud Tasks',repo:'goreecloud-tasks',category:'Productivity & Knowledge',model:'Native',kind:'Application',status:'Active development',role:'Private multi-user task and project management with Waypoint capabilities and Calendar interoperability.',visibility:'Private'},
{name:'GoreeCloud Calendar',repo:'goreecloud-calendar',category:'Productivity & Knowledge',model:'Native',kind:'Application',status:'Active development',role:'First-party calendar, events, scheduling, agenda, CalDAV interoperability, and Tasks integration.',visibility:'Public'},
{name:'GoreeCloud Contacts',repo:'goreecloud-contacts',category:'Productivity & Knowledge',model:'Native',kind:'Application',status:'Active development',role:'Contact management with CardDAV interoperability, controlled writes, and portable address-book data.',visibility:'Private'},
{name:'GoreeCloud Feed',repo:'goreecloud-rss',category:'Productivity & Knowledge',model:'Native',kind:'Application',status:'Web stable; native clients in development',role:'Private feed-reading experience with controlled aggregation and reading workflows.',visibility:'Public'},
{name:'GoreeCloud Bookmarks',repo:'goreecloud-bookmarks',category:'Productivity & Knowledge',model:'Maintained fork',kind:'Application',status:'Active development',role:'Bookmark preservation, authenticated browser capture, organization, retrieval, and web-knowledge management.',visibility:'Public'},
{name:'GoreeCloud Changelogs',repo:'goreecloud-changelogs',category:'Productivity & Knowledge',model:'Native',kind:'Application',status:'Active development',role:'Historical GoreeCloud change-ledger web application and API.',visibility:'Private'},
{name:'GoreeCloud Mail',repo:'goreecloud-mail',category:'Communication & Media',model:'Native',kind:'Application',status:'Active development',role:'First-party email client for web, Linux, Android, and future iOS with Courier capabilities and provider-independent account architecture.',visibility:'Private'},
{name:'GoreeCloud Music',repo:'goreecloud-music',category:'Communication & Media',model:'Native',kind:'Application',status:'Active development',role:'Self-hosted multi-user music service with library scanning, metadata, artwork, playback, and Resonance capabilities.',visibility:'Public'},
{name:'GoreeCloud Photos',repo:'goreecloud-photos',category:'Communication & Media',model:'Maintained fork to native',kind:'Application',status:'Active development',role:'Long-term photo and video preservation, organization, search, sharing, and Keepsake capabilities.',visibility:'Public'},
{name:'GoreeCloud Video',repo:'goreecloud-video',category:'Communication & Media',model:'Maintained fork to native',kind:'Application',status:'Milestone 1 development',role:'Private video library and playback platform with a deliberately video-only media scope, first-party client direction, metadata, family access, and controlled Jellyfin-derived compatibility.',visibility:'Public'},
{name:'GoreeCloud Gallery',repo:'goreecloud-gallery',category:'Communication & Media',model:'Maintained fork',kind:'Application',status:'Active development',role:'Offline-focused Android gallery for local photo and image browsing, organization, and viewing.',visibility:'Public'},
{name:'GoreeCloud Location',repo:'goreecloud-location',category:'Personal Data & Security',model:'Native',kind:'Application',status:'Active development',role:'Private multi-user location platform for device tracking, location history, places, trips, geofencing, maps, sharing, and native Android collection.',visibility:'Public'},
{name:'GoreeCloud Vault Server',repo:'goreecloud-vault-server',category:'Personal Data & Security',model:'Maintained fork to native',kind:'Application',status:'Active development',role:'Self-hosted password, credential, secret, secure-record, and sensitive-information server.',visibility:'Public'},
{name:'GoreeCloud Keyboard',repo:'goreecloud-keyboard',category:'Device Software',model:'Maintained fork',kind:'Application',status:'Active development',role:'System keyboard powered by Quill capabilities for typing, editing, personalization, dictionaries, clipboard, and input workflows.',visibility:'Public'},
{name:'GoreeCloud Terminal',repo:'goreecloud-terminal',category:'Device Software',model:'Maintained fork',kind:'Application',status:'50.2-rc.2 source · Stable not approved',role:'Native Linux terminal for local shells, SSH administration, and GoreeCloud workstation workflows. The current 50.2-rc.2 source line remains a release candidate; production and Stable approval remain separate evidence gates.',visibility:'Public'},
{name:'GoreeCloud Launcher',repo:'goreecloud-launcher',category:'Device Software',model:'Native',kind:'Application',status:'Active development',role:'First-party Android HOME experience with application discovery, search, persistent favorites and dock state, accessible ordering, workspace placement, and launcher lifecycle integration.',visibility:'Public'},
{name:'GoreeCloud Firefox Extensions',repo:'goreecloud-firefox-extensions',category:'Device Software',model:'First-party extension collection',kind:'Application',status:'Active development',role:'Canonical home for GoreeCloud-maintained Firefox extensions and browser integration components.',visibility:'Private'},
{name:'GoreeCloud Website',repo:'goreecloud-website',category:'Public Experience',model:'Native',kind:'Application',status:'Production',role:'Main public GoreeCloud identity plus Projects, Roadmap, Blog, and Archive public websites.',visibility:'Private'},
{name:'GoreeCloud Autobiography',repo:'goreecloud-autobiography',category:'Public Experience',model:'Native',kind:'Application',status:'Early development',role:'Public long-form project for preserving and presenting the story, history, lessons, and evolution behind GoreeCloud.',visibility:'Public'},
{name:'Glaze UI',repo:'goreecloud-glaze-ui',category:'Shared Foundations',model:'Design system · Stable 2.1.0',kind:'Foundation',status:'2.1.0 current Stable · Facet identity approved',role:'GoreeCloud Design Center and shared design-system authority for Glaze UI 2.1.0 Stable across supported GoreeCloud surfaces. The current contract keeps content solid, interaction deliberately glazed, and downstream conformance repository-local and evidence-backed.',visibility:'Public',icon:'/assets/glaze-ui-mark.svg',url:'https://design.goreecloud.com/'},
{name:'GoreeCloud Privacy Shield',repo:'goreecloud-privacy-shield',category:'Shared Foundations',model:'Privacy identity',kind:'Foundation',status:'Platform policy established · adoption active',role:'Platform-wide privacy identity, privacy-control contract, data-minimization expectations, evidence semantics, and application adapters. Public privacy claims are limited to current implementation and evidence.',visibility:'Private',icon:'/assets/privacy-shield-icon.svg',url:'https://privacy.goreecloud.com/'},
{name:'Wardveil Security',repo:'goreecloud-wardveil-security',category:'Shared Foundations',model:'Security identity',kind:'Foundation',status:'0.7 foundation · policy established',role:'Platform-wide security and protection identity, shared evidence contract, and fail-closed protection-state model for security states, warnings, posture, and protection experiences.',visibility:'Private',icon:'/assets/wardveil-security-icon.svg',url:'https://security.goreecloud.com/'},
{name:'Everkeep',repo:'goreecloud-everkeep',category:'Shared Foundations',model:'Resilience identity',kind:'Foundation',status:'Platform policy established · adoption active',role:'Platform-wide resilience, recovery, preservation, portability, continuity, succession, and digital-legacy system. Backup is one operational layer beneath the broader Everkeep continuity model.',visibility:'Private'},
{name:'GoreeCloud Waypoint',repo:'goreecloud-waypoint',category:'Shared Foundations',model:'Capability identity',kind:'Foundation',status:'Active identity',role:'First-party task and work-management capability family used by GoreeCloud Tasks and related Suite integrations.',visibility:'Public'}
];

const currentProjectDirection={
  'GoreeCloud Backup':['Native rebuild target','Backup, restoration, verification, and recovery workflows are moving to an original GoreeCloud application architecture. Transitional implementation may remain for continuity and reference until the native replacement satisfies recovery and production gates.'],
  'GoreeCloud Identity':['Identity platform · active development','First-party GoreeCloud platform system responsible for identity, authentication, authorization, accounts, devices, credentials, sessions, and delegated authority. Existing migration foundations remain bounded implementation details; public readiness claims remain evidence-scoped.','Identity platform system'],
  'GoreeCloud GitHub Dashboard':['Transitional GitHub integration','Repository visibility remains useful during migration, but GoreeCloud Code is the first-party developer and source-control platform. Forgejo is its initial replaceable infrastructure foundation, so future dashboards and AI integrations should become GoreeCloud Code-first or provider-neutral.'],
  'GoreeCloud Network':['Native rebuild active','Private networking and Conduit capabilities are moving into an original GoreeCloud application layer. Mature protocol or networking foundations may remain only within narrowly justified technical boundaries.'],
  'GoreeCloud DNS':['Native rebuild active','GoreeCloud DNS is the first-party DNS filtering and policy project. Recursive resolution remains a separate responsibility and is not claimed by this product surface.'],
  'GoreeCloud Search':['Native rebuild active','GoreeCloud Search is being rebuilt as original GoreeCloud-owned software and remains the first-party search and research gateway. Transitional foundations do not change the required native end state.'],
  'GoreeCloud Browser':['Native rebuild active · Android beta path','GoreeCloud Browser is moving toward an original GoreeCloud-owned product and application layer. Mature browser-engine foundations may remain where technically justified, but inherited product architecture is transitional rather than the approved long-term application model.'],
  'GoreeCloud Memos':['Stable web/server line · native evolution continues','GoreeCloud Memos retains its accepted web/server scope while native replacement and client work remain separately gated.'],
  'GoreeCloud Bookmarks':['Native rebuild active · fail-closed readiness boundary','The original GoreeCloud Bookmarks foundation includes owner-scoped records and fail-closed native readiness semantics. Transitional capture and application surfaces do not establish a native production cutover.'],
  'GoreeCloud Photos':['Native rebuild target · transitional media service','GoreeCloud Photos is required to become an original GoreeCloud application. Transitional implementation may remain for migration, compatibility, testing, and reference while native photo-preservation capabilities replace the upstream product layer.'],
  'GoreeCloud Video':['Native rebuild active','GoreeCloud Video is being rebuilt as original GoreeCloud software. Transitional protocol and compatibility behavior may remain while native video-library, playback, client, and family capabilities replace inherited product layers.'],
  'GoreeCloud Gallery':['Native rebuild target','GoreeCloud Gallery is required to become original GoreeCloud-owned software at the application layer. Existing upstream-derived Android gallery code is transitional while equivalent local-media capabilities are rebuilt and accepted natively.'],
  'GoreeCloud Vault Server':['Native rebuild target · transitional service','The credential server is required to move to an original GoreeCloud application architecture. Transitional compatibility material remains bounded until the native replacement satisfies security, migration, recovery, and client-compatibility gates.'],
  'GoreeCloud Keyboard':['Native rebuild active','GoreeCloud Keyboard is an original GoreeCloud application target powered by first-party Quill capabilities. Platform keyboard APIs, language resources, and mature technical dependencies remain bounded supporting foundations.'],
  'GoreeCloud Terminal':['Release-candidate source · Stable not assumed','GoreeCloud Terminal must reach an original GoreeCloud application end state while retaining only narrowly justified terminal, shell, toolkit, and operating-system foundations. Stable and production acceptance remain separate evidence gates.']
};

function addCurrentPortfolioEntries(){
  const add=entry=>{if(!entries.some(existing=>existing.name===entry.name))entries.push(entry);};
  add({name:'GoreeCloud AI',repo:'goreecloud-ai',category:'Developer & Intelligence',model:'Native',kind:'Application',status:'Active development',role:'First-party conversational AI and local-model workspace built around GoreeCloud services, knowledge, research, files, tools, RAG, orchestration, and governed integrations.',visibility:'Public'});
  add({name:'GoreeCloud Code',repo:'goreecloud-code',category:'Developer & Intelligence',model:'Native with replaceable forge foundation',kind:'Application',status:'Active development',role:'First-party developer and source-control platform for repositories, collaboration, CI/CD, packages, security, and AI-assisted development. Forgejo is the initial replaceable infrastructure foundation, not the permanent product boundary.',visibility:'Private'});
  add({name:'GoreeCloud Documents',repo:'goreecloud-documents',category:'Productivity & Knowledge',model:'Native',kind:'Application',status:'Active development',role:'First-party document-management platform for capture, OCR, search, organization, automation, collaboration, and preservation.',visibility:'Public'});
  add({name:'GoreeCloud Messenger',repo:'goreecloud-messenger',category:'Communication',model:'Native',kind:'Application',status:'Active development',role:'First-party private messaging and calling application with explicit transport, identity, group, calling, and GoreeCloud integration boundaries.',visibility:'Private'});
  add({name:'GoreeCloud Gateway',repo:'goreecloud-gateway',category:'Platform & Administration',model:'Native',kind:'Application',status:'Active development',role:'Native reverse proxy, HTTPS ingress, routing, certificate-management, and controlled service-publication platform.',visibility:'Public'});
  add({name:'GoreeCloud Quill',repo:'goreecloud-quill',category:'Shared Foundations',model:'First-party capability system',kind:'Capability',status:'Active development',role:'Typing, writing assistance, editing, privacy, personalization, dictionaries, clipboard, and intelligent-input capability family used by GoreeCloud Keyboard and related input experiences.',visibility:'Public'});
  add({name:'GoreeCloud Mesh',repo:'goreecloud-mesh',category:'Shared Foundations',model:'Coordination and governance plane',kind:'Foundation',status:'Active development',role:'Substantive platform coordination and governance plane for explicit service relationships, dependencies, capability exchange, events, and evidence. Mesh preserves the authority boundaries of Identity, Wardveil Security, Privacy Shield, Everkeep, Glaze UI, and specialized applications.',visibility:'Public'});
  add({name:'GoreeCloud File Manager',repo:'goreecloud-file-manager',category:'Productivity & Knowledge',model:'Native',kind:'Application',status:'Active development',role:'First-party GoreeCloud file-management application for local and connected storage surfaces.',visibility:'Public'});
  add({name:'GoreeCloud Maps',repo:'goreecloud-maps',category:'Personal Data & Security',model:'Native',kind:'Application',status:'Active development',role:'GoreeCloud mapping experience with privacy, navigation, GoreeCloud Location, and identity boundaries kept explicit.',visibility:'Private'});
  add({name:'GoreeCloud App Store',repo:'goreecloud-app-store',category:'Platform & Administration',model:'Native',kind:'Application',status:'Active development',role:'Official multi-user catalog and distribution experience for GoreeCloud applications and services, with access determined by account identity and entitlement.',visibility:'Public'});
}
addCurrentPortfolioEntries();

const identityEntry=entries.find(entry=>entry.name==='GoreeCloud Identity');
if(identityEntry){identityEntry.kind='Foundation';identityEntry.category='Shared Foundations';}

for(const entry of entries){
  const update=currentProjectDirection[entry.name];
  if(!update)continue;
  entry.status=update[0];
  entry.role=update[1];
  entry.model=update[2]||'Native GoreeCloud end state · transitional upstream provenance retained where applicable';
}

const grid=document.querySelector('#projects');
const search=document.querySelector('#search');
const filters=document.querySelector('#filters');
const resultCount=document.querySelector('#result-count');
const appCount=document.querySelector('#app-count');
const foundationCount=document.querySelector('#foundation-count');
const themeButtons=[...document.querySelectorAll('[data-theme-choice]')];
let filter='All';

appCount.textContent=entries.filter(entry=>entry.kind==='Application').length;
foundationCount.textContent=entries.filter(entry=>entry.kind==='Foundation').length;

const filtersList=['All','Applications','Foundations','Platform & Administration','Internet & Networking','Productivity & Knowledge','Communication & Media','Personal Data & Security','Device Software','Public Experience','Developer & Intelligence'];
for(const name of filtersList){
  const button=document.createElement('button');
  button.className='filter';
  button.type='button';
  button.textContent=name;
  button.dataset.filter=name;
  button.setAttribute('aria-pressed',String(name==='All'));
  button.addEventListener('click',()=>{
    filter=name;
    document.querySelectorAll('.filter').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));
    render();
  });
  filters.append(button);
}

function matchesFilter(entry){
  if(filter==='All')return true;
  if(filter==='Applications')return entry.kind==='Application';
  if(filter==='Foundations')return entry.kind==='Foundation';
  return entry.category===filter;
}

function render(){
  const query=search.value.trim().toLowerCase();
  const list=entries.filter(entry=>matchesFilter(entry)&&(!query||`${entry.name} ${entry.repo} ${entry.category} ${entry.model} ${entry.kind} ${entry.status} ${entry.role}`.toLowerCase().includes(query)));
  grid.replaceChildren(...list.map(card));
  resultCount.textContent=`${list.length} ${list.length===1?'entry':'entries'} shown`;
}

function card(entry){
  const article=document.createElement('article');
  article.className='card';
  article.dataset.kind=entry.kind.toLowerCase();

  const head=document.createElement('div');head.className='card-head';
  const iconWrap=document.createElement('div');iconWrap.className='project-icon';
  const icon=document.createElement('img');icon.src=entry.icon||'/assets/goreecloud-logo.svg';icon.alt='';icon.width=48;icon.height=48;iconWrap.append(icon);
  const kind=document.createElement('span');kind.className='kind';kind.textContent=entry.kind;
  head.append(iconWrap,kind);

  const meta=document.createElement('div');meta.className='card-meta';
  const category=document.createElement('span');category.className='badge';category.textContent=entry.category;
  const status=document.createElement('span');status.className='status';status.textContent=entry.status;
  meta.append(category,status);

  const title=document.createElement('h3');title.textContent=entry.name;
  const role=document.createElement('p');role.className='role';role.textContent=entry.role;
  const model=document.createElement('p');model.className='model';model.textContent=entry.model;

  const footer=document.createElement('footer');
  const visibility=document.createElement('span');visibility.className='visibility';visibility.textContent=`${entry.visibility} source`;
  footer.append(visibility);
  const destination=entry.url||(entry.visibility==='Public'?`https://github.com/GoreeCloud/${entry.repo}`:null);
  if(destination){
    const link=document.createElement('a');link.href=destination;link.target='_blank';link.rel='noopener noreferrer';link.textContent=entry.kind==='Foundation'?'View foundation':'Open repository';footer.append(link);
  }

  article.append(head,meta,title,role,model,footer);
  return article;
}

function applyTheme(choice){
  document.documentElement.dataset.theme=choice;
  themeButtons.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.themeChoice===choice)));
}
let saved='system';
try{saved=localStorage.getItem('goreecloud-projects-theme')||'system';}catch(_){ }
if(!['system','light','dark'].includes(saved))saved='system';
applyTheme(saved);
themeButtons.forEach(button=>button.addEventListener('click',()=>{const choice=button.dataset.themeChoice;applyTheme(choice);try{localStorage.setItem('goreecloud-projects-theme',choice);}catch(_){}}));

search.addEventListener('input',render);
render();
