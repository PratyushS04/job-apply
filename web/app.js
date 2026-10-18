const state = { files: [], docs: {}, revisions: {}, dirty: new Set(), current: null, mode: 'form', invalidRaw: false };
const $ = id => document.getElementById(id);
const candidate = key => state.docs[`candidate/${key}.json`];
const el = (tag, className = '', content = '') => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (content !== '') node.textContent = String(content);
  return node;
};
const safeArray = value => Array.isArray(value) ? value : [];
const record = value => value && typeof value === 'object' && !Array.isArray(value) ? value : {};
const nice = value => String(value || '').replace(/_/g, ' ').replace(/\b\w/g, letter => letter.toUpperCase());
const text = value => value == null ? '' : String(value).trim();
const jsonCopy = value => JSON.parse(JSON.stringify(value));

async function api(path, options) {
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
  return data;
}

function toast(message) {
  const node = $('toast');
  node.textContent = message;
  node.classList.add('show');
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => node.classList.remove('show'), 3100);
}

function notice(message, kind = '') {
  const node = $('editorNotice');
  node.textContent = message;
  node.className = `editor-notice ${kind}`;
}

function markDirty() {
  if (!state.current || isReadOnly()) return;
  state.dirty.add(state.current);
  $('modeBadge').textContent = 'UNSAVED';
  refreshSaveButton();
  renderFiles();
  renderStats();
  renderPreview();
}

function isReadOnly() {
  return state.files.find(file => file.path === state.current)?.read_only || false;
}

function refreshSaveButton() {
  $('saveButton').disabled = !state.current || isReadOnly() || !state.dirty.has(state.current) || state.invalidRaw;
}

function fileLabel(path) { return path.split('/').pop().replace('.json', ''); }

function renderFiles() {
  const list = $('fileList');
  list.replaceChildren();
  const query = $('fileSearch').value.trim().toLowerCase();
  for (const group of ['candidate', 'jobs', 'state']) {
    const files = state.files.filter(file => file.path.startsWith(`${group}/`) && file.path.toLowerCase().includes(query));
    if (!files.length) continue;
    const section = el('div', 'file-group');
    section.append(el('div', 'group-label', group));
    for (const file of files) {
      const button = el('button', `file-link ${file.path === state.current ? 'active' : ''}`);
      button.type = 'button';
      button.title = file.path;
      button.append(el('span', 'file-icon', group === 'jobs' ? 'J' : group === 'state' ? 'S' : 'C'));
      button.append(el('span', '', `${nice(fileLabel(file.path))}${state.dirty.has(file.path) ? ' •' : ''}`));
      if (file.read_only) button.append(el('span', 'lock', '◈'));
      button.addEventListener('click', () => selectFile(file.path));
      section.append(button);
    }
    list.append(section);
  }
  $('fileCount').textContent = state.files.length;
}

function selectFile(path) {
  state.current = path;
  state.invalidRaw = false;
  const file = state.files.find(item => item.path === path);
  $('crumb').textContent = path;
  $('editorTitle').textContent = nice(fileLabel(path));
  $('editorSubtitle').textContent = path;
  $('modeBadge').textContent = file.read_only ? 'READ ONLY' : state.dirty.has(path) ? 'UNSAVED' : 'EDITABLE';
  $('modeBadge').classList.toggle('locked', file.read_only);
  notice(file.read_only ? 'Education is locked. It is shown here for reference and copied unchanged into every resume preview.' : 'Edit fields below. The preview updates as you type; save when ready.');
  $('rawText').value = JSON.stringify(state.docs[path], null, 2);
  $('rawText').disabled = file.read_only;
  renderForm();
  refreshSaveButton();
  renderFiles();
}

function getAt(root, path) { return path.reduce((object, key) => object[key], root); }
function replaceAt(path, value) {
  if (!path.length) state.docs[state.current] = value;
  else getAt(state.docs[state.current], path.slice(0, -1))[path.at(-1)] = value;
  markDirty();
}

function removeAt(path) {
  const parent = getAt(state.docs[state.current], path.slice(0, -1));
  const key = path.at(-1);
  if (Array.isArray(parent)) parent.splice(key, 1);
  else delete parent[key];
  markDirty();
  renderForm();
}

function blankLike(value) {
  if (Array.isArray(value)) return [];
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([key, child]) => [key, blankLike(child)]));
  if (typeof value === 'boolean') return false;
  if (typeof value === 'number') return 0;
  return '';
}

function emptyArrayEntry(path) {
  if (path.length === 0 && state.current === 'candidate/projects.json') {
    return { name: '', category: 'personal_project', description: '', technologies: [], url: '', highlights: [], start_date: '', end_date: '' };
  }
  if (path.length === 0 && state.current === 'candidate/experience.json') {
    return { company: '', title: '', start_date: '', end_date: '', current: false, location: '', description: '', technologies: [], achievements: [] };
  }
  if (path.length === 0 && state.current === 'candidate/achievements.json') {
    return { title: '', type: 'other', date: '', issuer: '', description: '' };
  }
  return '';
}

function addAt(path, collection) {
  if (Array.isArray(collection)) {
    const preset = emptyArrayEntry(path);
    collection.push(preset !== '' ? preset : collection.length ? blankLike(collection[0]) : '');
  } else {
    const key = prompt('New JSON field name');
    if (!key) return;
    if (Object.prototype.hasOwnProperty.call(collection, key)) { toast('That field already exists.'); return; }
    collection[key] = '';
  }
  markDirty();
  renderForm();
}

function primitiveField(label, value, path, canRemove) {
  const wrap = el('div', 'form-field');
  const caption = el('label', 'field-label', label);
  wrap.append(caption);
  const line = el('div', 'field-line');
  let control;
  if (typeof value === 'boolean') {
    control = el('input', ''); control.type = 'checkbox'; control.checked = value;
    control.addEventListener('change', () => replaceAt(path, control.checked));
  } else if (typeof value === 'string' && (value.length > 90 || /description|summary|highlight|achievement|reasoning|note|wording|source/i.test(label))) {
    control = el('textarea', 'field-input'); control.value = value; control.rows = 3;
    control.addEventListener('input', () => replaceAt(path, control.value));
  } else {
    control = el('input', 'field-input');
    control.type = typeof value === 'number' ? 'number' : 'text';
    control.value = value == null ? '' : String(value);
    control.addEventListener('input', () => {
      const next = typeof value === 'number' ? Number(control.value) : value === null && control.value === '' ? null : control.value;
      replaceAt(path, next);
    });
  }
  control.disabled = isReadOnly();
  caption.htmlFor = `field-${path.map(String).join('-')}`;
  control.id = caption.htmlFor;
  line.append(control);
  if (!isReadOnly() && canRemove) {
    const remove = el('button', 'remove-button', '×');
    remove.type = 'button'; remove.title = `Remove ${label}`;
    remove.addEventListener('click', () => removeAt(path));
    line.append(remove);
  }
  wrap.append(line);
  return wrap;
}

function summaryFor(value, label, index) {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    return text(value.name || value.company || value.title || value.institution || value.id) || `${nice(label)} ${index + 1}`;
  }
  return `${nice(label)} ${index + 1}`;
}

function renderValue(label, value, path, depth = 0, index = 0) {
  if (value === null || typeof value !== 'object') return primitiveField(label, value, path, depth > 0);
  const details = el('details', 'nested');
  details.open = depth === 0 || (depth === 1 && index === 0);
  const summary = el('summary', '', Array.isArray(value) ? `${nice(label)} (${value.length})` : summaryFor(value, label, index));
  summary.append(el('span', 'summary-type', Array.isArray(value) ? 'LIST' : 'OBJECT'));
  details.append(summary);
  const body = el('div', 'nested-body');
  const entries = Array.isArray(value) ? value.map((child, key) => [key, child]) : Object.entries(value);
  if (!entries.length) body.append(el('div', 'empty-note', 'Nothing here yet. Add an item to start.'));
  entries.forEach(([key, child], position) => {
    const childPath = [...path, key];
    if (child && typeof child === 'object' && !Array.isArray(child)) {
      const card = renderValue(Array.isArray(value) ? summaryFor(child, label, position) : key, child, childPath, depth + 1, position);
      if (!isReadOnly()) {
        const remove = el('button', 'small-button', 'Remove entry');
        remove.type = 'button';
        remove.addEventListener('click', event => { event.preventDefault(); event.stopPropagation(); removeAt(childPath); });
        card.querySelector('.nested-body').append(remove);
      }
      body.append(card);
    } else {
      body.append(renderValue(Array.isArray(value) ? `Item ${position + 1}` : key, child, childPath, depth + 1, position));
    }
  });
  if (!isReadOnly()) {
    const actions = el('div', 'group-actions');
    const add = el('button', 'small-button', Array.isArray(value) ? '+ Add item' : '+ Add field');
    add.type = 'button'; add.addEventListener('click', () => addAt(path, value));
    actions.append(add);
    body.append(actions);
  }
  details.append(body);
  return details;
}

function renderForm() {
  const root = $('formEditor'); root.replaceChildren();
  const data = state.docs[state.current];
  if (data === undefined) return;
  if (Array.isArray(data)) {
    data.forEach((item, index) => {
      const node = renderValue(summaryFor(item, fileLabel(state.current), index), item, [index], 1, index);
      if (!isReadOnly() && item && typeof item === 'object') {
        const remove = el('button', 'small-button', 'Remove entry');
        remove.type = 'button';
        remove.addEventListener('click', event => { event.preventDefault(); event.stopPropagation(); removeAt([index]); });
        node.querySelector('.nested-body').append(remove);
      }
      root.append(node);
    });
    if (!isReadOnly()) {
      const add = el('button', 'small-button', '+ Add entry');
      add.type = 'button'; add.addEventListener('click', () => addAt([], data)); root.append(add);
    }
  } else if (data && typeof data === 'object') {
    Object.entries(data).forEach(([key, value], index) => root.append(renderValue(key, value, [key], 0, index)));
    if (!isReadOnly()) {
      const add = el('button', 'small-button', '+ Add field');
      add.type = 'button'; add.addEventListener('click', () => addAt([], data)); root.append(add);
    }
  } else root.append(primitiveField('Value', data, [], false));
}

function setMode(mode) {
  state.mode = mode;
  if (mode === 'form' && state.invalidRaw) {
    state.invalidRaw = false;
    notice('Showing the last valid draft in field view.');
    refreshSaveButton();
  }
  $('formTab').classList.toggle('active', mode === 'form');
  $('rawTab').classList.toggle('active', mode === 'raw');
  $('formTab').setAttribute('aria-selected', String(mode === 'form'));
  $('rawTab').setAttribute('aria-selected', String(mode === 'raw'));
  $('formEditor').classList.toggle('hidden', mode !== 'form');
  $('rawEditor').classList.toggle('hidden', mode !== 'raw');
  if (mode === 'raw' && state.current) $('rawText').value = JSON.stringify(state.docs[state.current], null, 2);
  if (mode === 'form') renderForm();
}

async function saveCurrent() {
  const path = state.current;
  if (!path || isReadOnly() || state.invalidRaw) return;
  $('saveButton').disabled = true;
  try {
    const saved = await api(`/api/file?path=${encodeURIComponent(path)}`, {
      method: 'PUT', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data: state.docs[path], revision: state.revisions[path] })
    });
    state.docs[path] = saved.data;
    state.revisions[path] = saved.revision;
    state.dirty.delete(path);
    if (state.current === path) {
      $('modeBadge').textContent = 'EDITABLE';
      $('rawText').value = JSON.stringify(saved.data, null, 2);
      notice('Saved to the workspace. A copy of the previous JSON is in .dashboard/backups.', 'success');
      renderForm();
    }
    renderFiles(); renderPreview(); refreshSaveButton(); toast('Changes saved');
  } catch (error) {
    notice(error.message, 'error'); refreshSaveButton(); toast('Save failed');
  }
}

function downloadCurrent() {
  if (!state.current) return;
  const blob = new Blob([JSON.stringify(state.docs[state.current], null, 2) + '\n'], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = el('a'); link.href = url; link.download = state.current.replace('/', '-'); link.click();
  URL.revokeObjectURL(url);
}

function appendSection(paper, title) {
  const section = el('section', 'resume-section');
  section.append(el('h4', '', title)); paper.append(section); return section;
}

function appendBullets(target, values) {
  const bullets = safeArray(values).filter(item => text(item));
  if (!bullets.length) return;
  const list = el('ul');
  bullets.forEach(value => list.append(el('li', '', value)));
  target.append(list);
}

function formatDate(value) {
  const str = text(value);
  if (!str) return '';
  if (/^\d{4}-\d{2}$/.test(str)) {
    const [year, month] = str.split('-').map(Number);
    return `${new Date(year, month - 1).toLocaleString('en-US', { month: 'short' })} ${year}`;
  }
  return str;
}

function dateRange(item) {
  const start = formatDate(item.start_date);
  const end = item.current ? 'Present' : formatDate(item.end_date);
  return [start, end].filter(Boolean).join(' – ');
}

function orderForJob(items, job, kind) {
  if (!$('jobSelect').value) return items;
  const evidence = safeArray(record(job.match)[kind === 'project' ? 'relevant_projects' : 'relevant_experience']).map(value => text(value).toLowerCase());
  const requirements = record(job.requirements);
  const keywords = [...safeArray(requirements.required_skills), ...safeArray(requirements.preferred_skills)].map(value => text(value).toLowerCase()).filter(Boolean);
  return items.map((item, index) => {
    const entry = record(item);
    const name = text(kind === 'project' ? entry.name : entry.company).toLowerCase();
    const contents = [entry.name, entry.company, entry.title, entry.description, ...safeArray(entry.technologies), ...safeArray(entry.highlights), ...safeArray(entry.achievements)].map(text).join(' ').toLowerCase();
    const evidenceScore = name && evidence.some(line => line.includes(name)) ? 8 : 0;
    const keywordScore = keywords.filter(keyword => contents.includes(keyword)).length;
    return { item, index, score: evidenceScore + keywordScore };
  }).sort((a, b) => b.score - a.score || a.index - b.index).map(row => row.item);
}

function renderPreview() {
  const paper = $('resumePaper'); paper.replaceChildren();
  const profile = record(candidate('profile'));
  const education = safeArray(candidate('education'));
  const experiences = safeArray(candidate('experience'));
  const allProjects = safeArray(candidate('projects'));
  const achievements = safeArray(candidate('achievements'));
  const skills = record(candidate('skills'));
  const job = record(state.docs[$('jobSelect').value]);
  $('contextStrip').lastElementChild.textContent = $('jobSelect').value ? `${text(job.title) || 'Role'} · ${text(job.company) || 'Company'} · relevant entries first · stored match ${record(job.match).score ?? '—'}/100` : 'General profile sample';
  const head = el('header', 'resume-header');
  head.append(el('h3', '', text(profile.name) || 'Your Name'));
  const contact = el('div', 'resume-contact');
  const location = profile.location && typeof profile.location === 'object' ? Object.values(profile.location).filter(text).join(', ') : text(profile.location);
  contact.textContent = [location, profile.phone, profile.email, profile.linkedin ? 'LinkedIn' : '', profile.github ? 'GitHub' : ''].filter(text).join('  ·  ') || 'Location  ·  Phone  ·  Email';
  head.append(contact); paper.append(head);
  if (text(profile.summary)) appendSection(paper, 'Professional Summary').append(el('p', 'resume-summary', profile.summary));
  const experience = appendSection(paper, 'Experience');
  if (!experiences.length) experience.append(el('div', 'resume-empty', 'Experience entries will appear here.'));
  orderForJob(experiences, job, 'experience').forEach(rawItem => {
    const item = record(rawItem);
    const entry = el('div', 'resume-entry');
    const row = el('div', 'resume-entry-head'); row.append(el('strong', '', text(item.title) || 'Role')); row.append(el('span', '', dateRange(item))); entry.append(row);
    entry.append(el('div', 'resume-entry-meta', [item.company, item.location].filter(text).join(' · ')));
    appendBullets(entry, item.achievements); experience.append(entry);
  });
  const skillSection = appendSection(paper, 'Technical Skills');
  const technical = skills.technical && typeof skills.technical === 'object' ? skills.technical : {};
  const categories = Object.entries(technical).filter(([, values]) => safeArray(values).length);
  if (!categories.length) skillSection.append(el('div', 'resume-empty', 'Skills will appear here.'));
  categories.forEach(([key, values]) => {
    const requirements = record(job.requirements);
    const keywords = [...safeArray(requirements.required_skills), ...safeArray(requirements.preferred_skills)].map(value => text(value).toLowerCase());
    const ordered = $('jobSelect').value ? [...values].sort((a, b) => Number(keywords.includes(text(b).toLowerCase())) - Number(keywords.includes(text(a).toLowerCase()))) : values;
    const row = el('p', 'resume-skill'); row.append(el('strong', '', `${nice(key)}: `)); row.append(document.createTextNode(ordered.join(', '))); skillSection.append(row);
  });
  const filter = $('projectView').value;
  const projects = allProjects.filter(item => filter === 'all' || record(item).category === filter);
  const projectSection = appendSection(paper, 'Projects');
  if (!projects.length) projectSection.append(el('div', 'resume-empty', 'Add a project to see it here. The sample remains usable with zero projects.'));
  orderForJob(projects, job, 'project').forEach(rawItem => {
    const item = record(rawItem);
    const entry = el('div', 'resume-entry');
    const row = el('div', 'resume-entry-head'); row.append(el('strong', '', text(item.name) || 'Untitled project')); row.append(el('span', '', dateRange(item))); entry.append(row);
    const stack = safeArray(item.technologies).filter(text).join(' · ');
    entry.append(el('div', 'resume-entry-meta', [nice(item.category || 'project'), stack, item.status].filter(text).join(' | ')));
    appendBullets(entry, item.highlights);
    if (!safeArray(item.highlights).length && text(item.description)) entry.append(el('p', 'resume-summary', item.description));
    projectSection.append(entry);
  });
  if (achievements.length) {
    const section = appendSection(paper, 'Certifications & Achievements');
    const list = el('ul');
    achievements.forEach(rawItem => {
      const item = record(rawItem);
      list.append(el('li', '', [item.title, item.issuer, item.date].filter(text).join(' · ')));
    });
    section.append(list);
  }
  const school = appendSection(paper, 'Education');
  if (!education.length) school.append(el('div', 'resume-empty', 'Education remains locked in this editor.'));
  education.forEach(rawItem => {
    const item = record(rawItem);
    const entry = el('div', 'resume-entry'); const row = el('div', 'resume-entry-head');
    row.append(el('strong', '', [item.degree, item.field ? `in ${item.field}` : ''].filter(text).join(' ')));
    row.append(el('span', '', dateRange(item))); entry.append(row);
    entry.append(el('div', 'resume-entry-meta', [item.institution, item.gpa ? `CGPA: ${item.gpa}` : ''].filter(text).join(' · ')));
    school.append(entry);
  });
}

function renderStats() {
  $('experienceCount').textContent = safeArray(candidate('experience')).length;
  $('projectCount').textContent = safeArray(candidate('projects')).length;
  $('jobCount').textContent = state.files.filter(file => file.path.startsWith('jobs/')).length;
  $('proposalCount').textContent = safeArray(state.docs['state/content_proposals.json']?.proposals).filter(item => record(item).approval_status === 'pending').length;
}

async function boot() {
  $('today').textContent = new Intl.DateTimeFormat('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }).format(new Date());
  $('fileSearch').addEventListener('input', renderFiles);
  $('formTab').addEventListener('click', () => setMode('form'));
  $('rawTab').addEventListener('click', () => setMode('raw'));
  $('saveButton').addEventListener('click', saveCurrent);
  $('downloadButton').addEventListener('click', downloadCurrent);
  $('printButton').addEventListener('click', () => window.print());
  $('jobSelect').addEventListener('change', renderPreview);
  $('projectView').addEventListener('change', renderPreview);
  $('rawText').addEventListener('input', () => {
    try {
      state.docs[state.current] = JSON.parse($('rawText').value);
      state.invalidRaw = false; notice('Valid JSON. Preview updated; save when ready.'); markDirty();
    } catch (error) {
      state.invalidRaw = true; notice(`JSON needs fixing: ${error.message}`, 'error'); refreshSaveButton();
    }
  });
  try {
    state.files = (await api('/api/files')).files;
    await Promise.all(state.files.map(async file => {
      const result = await api(`/api/file?path=${encodeURIComponent(file.path)}`);
      state.docs[file.path] = result.data; state.revisions[file.path] = result.revision;
    }));
    state.files.filter(file => file.path.startsWith('jobs/')).forEach(file => {
      const job = record(state.docs[file.path]);
      const option = el('option', '', `${text(job.company) || job.id} · ${text(job.title) || 'Untitled role'}`);
      option.value = file.path; $('jobSelect').append(option);
    });
    renderStats(); renderFiles(); renderPreview();
    selectFile(state.files.some(file => file.path === 'candidate/projects.json') ? 'candidate/projects.json' : state.files[0]?.path);
  } catch (error) {
    notice(`Could not load workspace: ${error.message}`, 'error'); toast('Workspace unavailable');
  }
}

boot();
