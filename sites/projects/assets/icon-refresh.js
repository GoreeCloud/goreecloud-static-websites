const brandingAuthority='GoreeCloud/goreecloud-branding-assets';
const publishedSuiteIconBase='https://www.goreecloud.com/assets/suite/';
const canonicalProductBranding={
  'goreecloud-ai':['products/ai/app-icon.svg','ai.svg'],
  'goreecloud-backup':['products/backup/app-icon.svg','backup.svg'],
  'goreecloud-bookmarks':['products/bookmarks/app-icon.svg','bookmarks.svg'],
  'goreecloud-browser':['products/browser/app-icon.svg','browser.svg'],
  'goreecloud-calendar':['products/calendar/app-icon.svg','calendar.svg'],
  'goreecloud-changelogs':['products/changelogs/app-icon.svg','changelogs.svg'],
  'goreecloud-code':['products/code/app-icon.svg','code.svg'],
  'goreecloud-contacts':['products/contacts/app-icon.svg','contacts.svg'],
  'goreecloud-dns':['products/dns/app-icon.svg','dns.svg'],
  'goreecloud-documents':['products/documents/app-icon.svg','documents.svg'],
  'goreecloud-drive':['products/drive/app-icon.svg','drive.svg'],
  'goreecloud-rss':['products/feed/app-icon.svg','feed.svg'],
  'goreecloud-gallery':['products/gallery/app-icon.svg','gallery.svg'],
  'goreecloud-gateway':['products/gateway/app-icon.svg','gateway.svg'],
  'goreecloud-identity':['products/identity/app-icon.svg','identity.svg'],
  'goreecloud-keyboard':['products/keyboard/app-icon.svg','keyboard.svg'],
  'goreecloud-launcher':['products/launcher/app-icon.svg','launcher.svg'],
  'goreecloud-location':['products/location/app-icon.svg','location.svg'],
  'goreecloud-mail':['products/mail/app-icon.svg','mail.svg'],
  'goreecloud-manager':['products/manager/app-icon.svg','manager.svg'],
  'goreecloud-memos':['products/memos/app-icon.svg','memos.svg'],
  'goreecloud-messenger':['products/messenger/app-icon.svg','messenger.svg'],
  'goreecloud-monitor':['products/monitor/app-icon.svg','monitor.svg'],
  'goreecloud-music':['products/music/app-icon.svg','music.svg'],
  'goreecloud-network':['products/network/app-icon.svg','network.svg'],
  'goreecloud-notes':['products/notes/app-icon.svg','notes.svg'],
  'goreecloud-notify':['products/notify/app-icon.svg','notify.svg'],
  'goreecloud-photos':['products/photos/app-icon.svg','photos.svg'],
  'goreecloud-search':['products/search/app-icon.svg','search.svg'],
  'goreecloud-sync':['products/sync/app-icon.svg','sync.svg'],
  'goreecloud-tasks':['products/tasks/app-icon.svg','tasks.svg'],
  'goreecloud-terminal':['products/terminal/app-icon.svg','terminal.svg'],
  'goreecloud-vault-server':['products/vault/app-icon.svg','vault.svg'],
  'goreecloud-video':['products/video/app-icon.svg','video.svg']
};
const canonicalSystemBranding={
  'goreecloud-glaze-ui':['systems/glaze-ui/glaze-ui-mark.svg','/assets/glaze-ui-mark.svg','approved'],
  'goreecloud-privacy-shield':['systems/privacy-shield/privacy-shield-icon.svg','/assets/privacy-shield-icon.svg','approved'],
  'goreecloud-wardveil-security':['systems/wardveil-security/wardveil-security-icon.svg','/assets/wardveil-security-icon.svg','approved'],
  'goreecloud-everkeep':['systems/everkeep/everkeep.svg','/assets/everkeep.svg','approved'],
  'goreecloud-mesh':['systems/goreecloud-mesh/goreecloud-mesh-mark.svg','/assets/goreecloud-mesh-mark.svg','approved'],
  'goreecloud-identity':['products/identity/app-icon.svg','/assets/identity.svg','approved']
};

for(const entry of entries){
  const systemBranding=canonicalSystemBranding[entry.repo];
  if(systemBranding){
    entry.brandingAuthority=brandingAuthority;
    entry.brandingSource=systemBranding[0];
    entry.brandingStatus=systemBranding[2];
    entry.icon=systemBranding[1]||'';
    continue;
  }
  const productBranding=canonicalProductBranding[entry.repo];
  if(productBranding){
    entry.brandingAuthority=brandingAuthority;
    entry.brandingSource=productBranding[0];
    entry.brandingStatus='approved';
    entry.icon=`${publishedSuiteIconBase}${productBranding[1]}`;
    continue;
  }
  entry.brandingAuthority=brandingAuthority;
  entry.brandingSource=null;
  entry.brandingStatus='text-only-no-approved-artwork';
  entry.icon='';
}

const catalogCard=card;
card=function(entry){
  const article=catalogCard(entry);
  if(!entry.icon){
    article.querySelector('.project-icon')?.remove();
    article.querySelector('.card-head')?.classList.add('text-only-brand');
  }
  return article;
};

render();
