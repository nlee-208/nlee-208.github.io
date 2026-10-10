const root = document.documentElement;
const toggle = document.querySelector('.theme-toggle');
let savedTheme;
try { savedTheme = localStorage.getItem('noah-research-theme'); } catch {}
function setTheme(theme) {
  root.dataset.theme = theme;
  toggle.setAttribute('aria-pressed', String(theme === 'dark'));
  toggle.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
}
setTheme(savedTheme || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));
toggle.addEventListener('click', () => {
  const theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
  setTheme(theme);
  try { localStorage.setItem('noah-research-theme', theme); } catch {}
});
const archive = document.querySelector('#all-publications');
const filters = document.querySelector('.topic-filters');
const topicButtons = [...filters.querySelectorAll('button')];
const publications = [...document.querySelectorAll('#archive-list > a')];
const filterStatus = document.querySelector('#filter-status');

function filterPublications(topic) {
  let count = 0;
  for (const paper of publications) {
    const matches = topic === 'all' || paper.dataset.topics.split(' ').includes(topic);
    paper.hidden = !matches;
    if (matches) count++;
  }
  for (const button of topicButtons) {
    button.setAttribute('aria-pressed', String(button.dataset.topic === topic));
  }
  const label = topicButtons.find(button => button.dataset.topic === topic).textContent;
  filterStatus.textContent = topic === 'all'
    ? `Showing all ${count} papers.`
    : `${count} ${count === 1 ? 'paper' : 'papers'} in ${label.toLowerCase()}.`;
}

for (const button of topicButtons) {
  button.addEventListener('click', () => filterPublications(button.dataset.topic));
}
filters.hidden = false;
document.querySelector('#view-all').addEventListener('click', () => {
  filterPublications('all');
  archive.open = true;
});

document.querySelector('#browse-topics').addEventListener('click', () => {
  archive.open = true;
  topicButtons[0].focus({ preventScroll: true });
});

const figureDialog = document.querySelector('#figure-dialog');
const figureImage = document.querySelector('#figure-full');
const figureTitle = document.querySelector('#figure-title');
const figureCaption = document.querySelector('#figure-caption');
const figurePaper = document.querySelector('#figure-paper');
let figureTrigger;

for (const link of document.querySelectorAll('[data-figure]')) {
  link.addEventListener('click', event => {
    // The image link remains usable without native dialog support or JavaScript.
    if (typeof figureDialog.showModal !== 'function') return;
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    figureTrigger = link;
    const thumbnail = link.querySelector('img');
    figureImage.src = thumbnail.src;
    figureImage.alt = thumbnail.alt;
    figureTitle.textContent = link.dataset.title;
    figureCaption.textContent = thumbnail.alt;
    figurePaper.href = link.dataset.paper;
    figureDialog.showModal();
    document.body.classList.add('figure-open');
  });
}

document.querySelector('#close-figure').addEventListener('click', () => figureDialog.close());
figureDialog.addEventListener('click', event => {
  if (event.target !== figureDialog) return;
  const bounds = figureDialog.getBoundingClientRect();
  if (event.clientX < bounds.left || event.clientX > bounds.right ||
      event.clientY < bounds.top || event.clientY > bounds.bottom) {
    figureDialog.close();
  }
});
// Escape is handled by the native dialog; closing also restores scroll and focus.
figureDialog.addEventListener('close', () => {
  document.body.classList.remove('figure-open');
  if (figureTrigger) figureTrigger.focus({ preventScroll: true });
});
