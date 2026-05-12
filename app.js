const countryByTld={cn:"中国",hk:"中国",tw:"中国",jp:"日本",kr:"韩国",ru:"俄罗斯",uk:"英国",de:"德国",fr:"法国",in:"印度",au:"澳大利亚",ca:"加拿大",sg:"新加坡",nl:"荷兰",se:"瑞典",br:"巴西",it:"意大利",es:"西班牙"};
const labelEN={"全部":"All","搜索":"Search","AI":"AI","社交":"Social","电商":"E-commerce","跨境电商":"Cross-border","开发者":"Developer","新闻":"News","教育":"Education","中国":"China","视频":"Video","工具":"Tools","素材":"Images"};
function guessCountry(domain){const tld=String(domain).split('.').pop().toLowerCase();return countryByTld[tld]||'美国'}
function logoUrl(domain){return 'https://www.google.com/s2/favicons?domain='+encodeURIComponent(domain)+'&sz=128'}
function escapeHtml(str){return String(str??'').replace(/[&<>"']/g,s=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[s]))}
function getLang(){return document.documentElement.lang.startsWith('en')?'en':'zh'}
function t(zh){return getLang()==='en'?(labelEN[zh]||zh):zh}
function changeText(site){
  const c=Number(site.change||0);
  if(site.prev_rank===null||site.prev_rank===undefined) return {txt:getLang()==='en'?'NEW':'新', cls:'new'};
  if(c>0) return {txt:'↑'+c, cls:'up'};
  if(c<0) return {txt:'↓'+Math.abs(c), cls:'down'};
  return {txt:'—', cls:''};
}
let allSites=[];let activeFilter=window.PAGE_FILTER||'';let query='';
function matchFilter(site){if(!activeFilter) return true;return (site.categories||[]).includes(activeFilter)||site.country===activeFilter}
function matchQuery(site){if(!query) return true;const q=query.toLowerCase();return [site.name,site.domain,site.country,site.desc,(site.categories||[]).join(' ')].some(x=>String(x||'').toLowerCase().includes(q))}
function render(){
 const grid=document.getElementById('grid'); if(!grid) return; grid.innerHTML='';
 const arr=allSites.filter(s=>matchFilter(s)&&matchQuery(s)).slice(0,116);
 arr.forEach((site,index)=>{const rank=site.rank||index+1;const domain=site.domain||site.url||'';const country=site.country||guessCountry(domain);const desc=site.desc||((getLang()==='en')?'High-authority global website':'全球高权重网站');const name=site.name||domain;const a=document.createElement('a');a.className='item';a.href='https://'+domain.replace(/^https?:\/\//,'');a.target='_blank';a.rel='noopener noreferrer';a.dataset.country=country;let rankClass='rank';if(rank<=3)rankClass+=' top3';else if(rank<=10)rankClass+=' top10';const ch=changeText(site);a.innerHTML=`<div class="rankbox"><span class="${rankClass}">${rank}</span><span class="change ${ch.cls}">${ch.txt}</span></div><img class="logo" src="${logoUrl(domain)}" alt="" loading="lazy" onerror="this.style.display='none'"><div class="info"><div class="name-row"><div class="name">${escapeHtml(name)}</div><span class="badge">${escapeHtml(getLang()==='en'?(labelEN[country]||country):country)}</span></div><div class="desc">${escapeHtml(desc)}</div><div class="domain">${escapeHtml(domain)}</div></div>`;grid.appendChild(a)});
 if(!grid.children.length) grid.innerHTML='<div style="grid-column:1/-1;color:#667085;text-align:center;padding:30px">'+(getLang()==='en'?'No results':'暂无数据')+'</div>';
 const stats=document.getElementById('stats'); if(stats) stats.textContent=(getLang()==='en'?`Showing ${arr.length} sites`:`当前显示 ${arr.length} 个网站`)+(activeFilter?` · ${t(activeFilter)}`:'')+(query?` · ${query}`:'');
}
function initControls(){
 const search=document.getElementById('siteSearch'); if(search){search.addEventListener('input',e=>{query=e.target.value.trim();render()})}
 document.querySelectorAll('.filter-btn').forEach(btn=>{btn.addEventListener('click',()=>{activeFilter=btn.dataset.filter||'';document.querySelectorAll('.filter-btn').forEach(b=>b.classList.toggle('active',b===btn));render()})});
 document.querySelectorAll('.filter-btn').forEach(btn=>{if((btn.dataset.filter||'')===activeFilter) btn.classList.add('active')});
}
function init(){initControls();fetch(window.SITES_PATH||'./sites.json',{cache:'no-store'}).then(r=>r.json()).then(data=>{allSites=data;render()}).catch(()=>{allSites=window.FALLBACK_SITES||[];render()})}
document.addEventListener('DOMContentLoaded',init);
