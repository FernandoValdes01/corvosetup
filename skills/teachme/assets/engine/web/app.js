(() => {
  'use strict';

  const token = new URLSearchParams(window.location.search).get('token') || '';
  const $ = (id) => document.getElementById(id);
  const ui = {
    workspace: $('workspace'), title: $('course-title'), objective: $('course-objective'), nav: $('phase-nav'),
    reader: $('reader'), crumb: $('crumb-phase'), status: $('save-status'), progressText: $('progress-text'),
    progressFill: $('progress-fill'), read: $('read-button'), previous: $('previous-button'), next: $('next-button'),
    doubtPanel: $('doubts-panel'), doubtList: $('doubt-list'), doubtForm: $('doubt-form'), doubtInput: $('doubt-input'),
    doubtCount: $('doubt-count'), doubtFeedback: $('dialog-feedback'),
    exportDialog: $('export-dialog'), exportText: $('export-text'), exportFeedback: $('export-feedback'), toast: $('toast')
  };
  let lesson, files = {}, state = { version: 1, phase: null, section: 0, completed: [], doubts: [], reader: null }, report = '';
  let phaseIndex = 0, activeFile = null, articleScroll = 0, scrollTimer, toastTimer, requestChain = Promise.resolve();
  let sessionClosing = false, sessionClosed = false, doubtTargetPhase = null;

  const text = (value) => typeof value === 'string' ? value : '';
  const escLines = (value) => text(value).split('\n');
  const currentPhase = () => lesson?.phases?.[phaseIndex] || null;
  const currentPhaseId = () => currentPhase()?.id || '';
  const setStatus = (message, kind = '') => {
    ui.status.textContent = message;
    ui.status.dataset.kind = kind;
  };
  const node = (tag, className, content) => {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (content !== undefined) el.textContent = content;
    return el;
  };
  const appendText = (parent, tag, content, className = '') => {
    const el = node(tag, className, content);
    parent.append(el);
    return el;
  };
  const labelFor = (phase) => phase?.title || 'Fase';
  const safeFile = (path) => Object.prototype.hasOwnProperty.call(files, path);

  async function api(path, options = {}) {
    const headers = new Headers(options.headers || {});
    headers.set('X-Teach-Token', token);
    if (options.body !== undefined) headers.set('Content-Type', 'application/json');
    const response = await fetch(path, { ...options, headers, cache: 'no-store' });
    if (!response.ok) {
      let detail = '';
      try { detail = (await response.json()).error || ''; } catch (_) { /* respuesta sin JSON */ }
      throw new Error(detail || `El servidor respondió ${response.status}.`);
    }
    return response;
  }

  function queueAction(action) {
    if (sessionClosed) return Promise.reject(new Error('La sesión está cerrada.'));
    const run = requestChain.then(async () => {
      setStatus('Guardando…');
      const response = await api('/api/action', { method: 'POST', body: JSON.stringify(action) });
      const result = await response.json();
      if (result.state) {
        state.completed = Array.isArray(result.state.completed) ? result.state.completed : state.completed;
        state.doubts = Array.isArray(result.state.doubts) ? result.state.doubts : state.doubts;
        report = text(result.report) || report;
        updateProgress();
        renderDoubts();
      }
      setStatus('Guardado');
      return result;
    });
    requestChain = run.catch((error) => {
      setStatus('No se guardó', 'error');
      showToast(`No se guardó: ${error.message}`);
    });
    return run;
  }

  function showToast(message) {
    ui.toast.textContent = message;
    ui.toast.classList.add('is-visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => ui.toast.classList.remove('is-visible'), 3400);
  }

  function updateProgress() {
    const phases = lesson?.phases || [];
    const completed = new Set(state.completed || []);
    const count = phases.filter((phase) => completed.has(phase.id)).length;
    ui.progressText.textContent = `${count} / ${phases.length}`;
    ui.progressFill.style.width = `${phases.length ? (count / phases.length) * 100 : 0}%`;
    ui.doubtCount.textContent = String((state.doubts || []).length);
    ui.nav.querySelectorAll('.phase-link').forEach((link, index) => {
      const phase = phases[index];
      link.classList.toggle('is-complete', completed.has(phase?.id));
      if (index === phaseIndex) link.setAttribute('aria-current', 'step');
      else link.removeAttribute('aria-current');
    });
    ui.read.textContent = completed.has(currentPhaseId()) ? 'Fase leída ✓' : 'Marcar fase leída';
    ui.previous.disabled = phaseIndex <= 0;
    ui.next.disabled = phaseIndex >= phases.length - 1;
  }

  function renderNav() {
    ui.nav.replaceChildren();
    (lesson.phases || []).forEach((phase, index) => {
      const button = node('button', 'phase-link');
      button.type = 'button';
      button.dataset.phaseIndex = String(index);
      const number = node('span', 'phase-number', String(index + 1).padStart(2, '0'));
      const name = node('span', 'phase-name', labelFor(phase));
      button.append(number, name);
      ui.nav.append(button);
    });
    updateProgress();
  }

  function addSectionHeading(target, title) {
    appendText(target, 'h2', title);
  }

  function renderCallout(target, heading, copy) {
    if (!copy) return;
    const box = node('aside', 'callout');
    appendText(box, 'strong', heading);
    appendText(box, 'p', copy);
    target.append(box);
  }

  function renderFigure(target, visual) {
    if (!visual || !visual.file) return;
    const figure = node('figure', 'story-figure');
    const img = document.createElement('img');
    img.src = `/diagramas/${encodeURIComponent(visual.file)}`;
    img.alt = text(visual.alt) || 'Diagrama de esta fase';
    img.loading = 'lazy';
    figure.append(img);
    const caption = node('figcaption');
    const strong = node('strong', '', 'Diagrama · ');
    caption.append(strong, document.createTextNode(text(visual.caption)));
    const expand = node('a', '', 'Abrir diagrama a tamaño completo');
    expand.href = img.src; expand.target = '_blank'; expand.rel = 'noopener noreferrer';
    caption.append(document.createTextNode(' '), expand);
    figure.append(caption);
    target.append(figure);
  }

  function addCodeBlock(target, path, range) {
    if (!safeFile(path)) return;
    const full = escLines(files[path]);
    const start = Array.isArray(range) && Number.isInteger(range[0]) ? Math.max(1, range[0]) : 1;
    const end = Array.isArray(range) && Number.isInteger(range[1]) ? Math.min(full.length, range[1]) : Math.min(full.length, start + 9);
    const lo = Math.min(start, end);
    const excerpt = full.slice(Math.max(0, lo - 1), end);
    const card = node('section', 'code-card');
    const head = node('div', 'code-head');
    appendText(head, 'span', path, 'file-label');
    const open = node('button', 'open-file', 'Abrir archivo completo ↵');
    open.type = 'button'; open.dataset.openFile = path; open.dataset.line = String(lo);
    head.append(open);
    const body = node('div', 'code-body');
    body.tabIndex = 0;
    body.setAttribute('aria-label', `Fragmento de ${path}, líneas ${lo} a ${end}`);
    excerpt.forEach((line, index) => {
      const lineNo = lo + index;
      const row = node('div', `code-line${lineNo >= lo && lineNo <= end ? ' is-highlight' : ''}`);
      appendText(row, 'span', String(lineNo), 'line-no');
      appendText(row, 'span', line, 'code-content');
      body.append(row);
    });
    card.append(head, body);
    target.append(card);
  }

  function renderWalkthrough(target, steps) {
    (steps || []).forEach((step, index) => {
      const row = node('div', 'step');
      appendText(row, 'span', String(index + 1).padStart(2, '0'), 'step-number');
      const content = node('div');
      appendText(content, 'h3', text(step.title) || `Paso ${index + 1}`);
      if (step.text) appendText(content, 'p', step.text);
      if (step.file) addCodeBlock(content, step.file, step.lines);
      row.append(content);
      target.append(row);
    });
  }

  function renderAlternatives(target, alternatives) {
    if (!alternatives?.length) return;
    const table = node('table', 'compare');
    const head = node('thead');
    const tr = node('tr');
    ['Alternativa', 'Qué implica'].forEach((item) => appendText(tr, 'th', item));
    head.append(tr);
    const body = node('tbody');
    alternatives.forEach((item) => {
      const row = node('tr');
      appendText(row, 'td', text(item.name));
      appendText(row, 'td', text(item.tradeoff));
      body.append(row);
    });
    table.append(head, body);
    target.append(table);
  }

  function renderSources(target) {
    if (!lesson.sources?.length) return;
    addSectionHeading(target, 'Fuentes oficiales');
    const list = node('ul', 'sources');
    lesson.sources.forEach((source) => {
      const li = node('li');
      const link = node('a', '', text(source.title) || text(source.url));
      link.href = text(source.url);
      link.target = '_blank'; link.rel = 'noopener noreferrer';
      li.append(link);
      if (source.consulted) appendText(li, 'small', ` · consultada ${source.consulted}`);
      list.append(li);
    });
    target.append(list);
  }

  function renderFallback(phase, target) {
    (phase.sections || []).forEach((section) => {
      addSectionHeading(target, text(section.title));
      appendText(target, 'p', text(section.text));
      (section.files || []).forEach((path) => addCodeBlock(target, path));
    });
  }

  function renderArticle() {
    const phase = currentPhase();
    if (!phase) return;
    activeFile = null;
    ui.crumb.textContent = labelFor(phase).toLocaleUpperCase('es-CL');
    ui.reader.replaceChildren();
    appendText(ui.reader, 'p', 'FASE DE LA GUÍA', 'lead-label');
    appendText(ui.reader, 'h1', labelFor(phase));
    const dek = phase.story?.request || phase.sections?.[0]?.text || lesson.objective || '';
    appendText(ui.reader, 'p', dek, 'dek');
    const meta = node('div', 'reading-meta');
    meta.append(node('span', '', 'Decisiones y alternativas'));
    meta.append(node('span', '', 'Lectura y código')); meta.append(node('span', '', 'Solo lectura'));
    ui.reader.append(meta);

    if (phase.story) {
      if (Array.isArray(phase.flow) && phase.flow.length) {
        appendText(ui.reader, 'p', phase.flow.join('  →  '), 'scope-note');
      }
      if (phase.story.interpretation) {
        addSectionHeading(ui.reader, '1. Del requisito a la interpretación');
        appendText(ui.reader, 'p', phase.story.interpretation);
      }
      renderFigure(ui.reader, phase.story.visual);
      if (phase.story.decision) {
        addSectionHeading(ui.reader, '2. Decisión técnica');
        appendText(ui.reader, 'p', phase.story.decision);
      }
      if (phase.story.alternatives?.length) {
        appendText(ui.reader, 'h3', 'Otras formas de resolverlo');
        renderAlternatives(ui.reader, phase.story.alternatives);
      }
      if (phase.story.walkthrough?.length) {
        addSectionHeading(ui.reader, '3. Cómo se construyó');
        renderWalkthrough(ui.reader, phase.story.walkthrough);
      }
      if (phase.story.difficulties?.length) {
        addSectionHeading(ui.reader, '4. Dificultades y resolución');
        const list = node('ul', 'difficulty-list');
        phase.story.difficulties.forEach((item) => appendText(list, 'li', item));
        ui.reader.append(list);
      }
      if (phase.story.transfer) {
        addSectionHeading(ui.reader, '5. Cómo llevarlo a otro proyecto');
        appendText(ui.reader, 'p', phase.story.transfer);
      }
    } else renderFallback(phase, ui.reader);

    const related = (phase.files || []).filter(safeFile);
    if (related.length) {
      addSectionHeading(ui.reader, 'Archivos de esta fase');
      related.forEach((path) => {
        const info = lesson.files.find((item) => item.path === path);
        appendText(ui.reader, 'p', `${path}${info?.purpose ? ` — ${info.purpose}` : ''}`, 'scope-note');
        const button = node('button', 'button button-outline button-small', 'Leer archivo completo');
        button.type = 'button'; button.dataset.openFile = path; button.dataset.line = '1';
        ui.reader.append(button);
      });
    }
    {
      const note = node('aside', 'phase-note');
      appendText(note, 'p', '¿Qué te gustaría revisar de esta fase?');
      const noteButton = node('button', 'button button-outline button-small', 'Anotar una duda');
      noteButton.type = 'button'; noteButton.dataset.notePhase = phase.id;
      note.append(noteButton); ui.reader.append(note);
    }
    if (phaseIndex === (lesson.phases.length - 1)) renderSources(ui.reader);
    ui.reader.scrollTop = 0;
    window.scrollTo({ top: 0, behavior: 'instant' });
    updateProgress();
    ui.reader.focus({ preventScroll: true });
  }

  function renderFile(path, line = 1) {
    if (!safeFile(path)) { showToast('Ese archivo no está disponible en el servidor.'); return; }
    if (!activeFile) articleScroll = window.scrollY;
    activeFile = { path, line: Math.max(1, Number(line) || 1) };
    const fileMeta = (lesson.files || []).find((item) => item.path === path) || {};
    ui.crumb.textContent = 'ARCHIVO';
    ui.reader.replaceChildren();
    const back = node('button', 'button button-quiet button-small', '← Volver a la explicación (↵)');
    back.type = 'button'; back.dataset.backArticle = 'true';
    ui.reader.append(back);
    appendText(ui.reader, 'p', 'LECTURA DE CÓDIGO · SOLO LECTURA', 'lead-label');
    appendText(ui.reader, 'h1', path);
    if (fileMeta.purpose) appendText(ui.reader, 'p', fileMeta.purpose, 'dek');
    if (fileMeta.explanation) appendText(ui.reader, 'p', fileMeta.explanation);
    if (fileMeta.used_when) renderCallout(ui.reader, 'Cuándo se usa', fileMeta.used_when);
    if (fileMeta.parameters) appendText(ui.reader, 'p', `Parámetros: ${fileMeta.parameters}`, 'scope-note');
    const source = escLines(files[path]);
    const card = node('section', 'code-card full-code');
    const head = node('div', 'code-head');
    appendText(head, 'span', `${path} · ${source.length} líneas`, 'file-label');
    card.append(head);
    const body = node('div', 'code-body');
    body.tabIndex = 0; body.id = 'full-code'; body.setAttribute('aria-label', `Contenido completo de ${path}`);
    const rawHighlights = Array.isArray(fileMeta.lines) ? fileMeta.lines : [];
    const highlights = rawHighlights.length && rawHighlights.every(Number.isInteger) ? [rawHighlights] : rawHighlights;
    source.forEach((line, index) => {
      const lineNo = index + 1;
      const marked = highlights.some((range) => Array.isArray(range) && lineNo >= range[0] && lineNo <= range[1]);
      const row = node('div', `code-line${marked ? ' is-highlight' : ''}`);
      appendText(row, 'span', String(lineNo), 'line-no');
      appendText(row, 'span', line, 'code-content');
      body.append(row);
    });
    card.append(body); ui.reader.append(card);
    requestAnimationFrame(() => {
      const target = body.querySelector(`.code-line:nth-child(${activeFile.line})`);
      target?.scrollIntoView({ block: 'center' });
      body.focus({ preventScroll: true });
      window.scrollTo({ top: 0, behavior: 'instant' });
    });
  }

  function openPhase(index) {
    if (sessionClosing || sessionClosed || index < 0 || index >= lesson.phases.length || index === phaseIndex) return;
    scheduleScrollSave(true);
    phaseIndex = index;
    state.phase = currentPhaseId();
    if (!ui.doubtInput.value.trim()) doubtTargetPhase = currentPhaseId();
    renderArticle();
    renderDoubts();
    queueAction({ action: 'visit', phase: currentPhaseId(), scroll: 0 }).catch(() => {});
  }

  function scheduleScrollSave(immediate = false) {
    clearTimeout(scrollTimer);
    const phase = currentPhaseId();
    const scroll = Math.max(0, Math.round(window.scrollY));
    if (!phase || activeFile || sessionClosing || sessionClosed) return;
    const save = () => queueAction({ action: 'visit', phase, scroll }).catch(() => {});
    if (immediate) save();
    else scrollTimer = setTimeout(save, 400);
  }

  function makeNotes() {
    const completed = new Set(state.completed || []);
    const lines = [`# ${text(lesson.title)}`, '', `Objetivo: ${text(lesson.objective)}`, '', '## Fases leídas', ''];
    lesson.phases.forEach((phase) => lines.push(`- [${completed.has(phase.id) ? 'x' : ' '}] ${phase.title}`));
    lines.push('', '## Dudas', '');
    if (!(state.doubts || []).length) lines.push('_Todavía no hay dudas anotadas._');
    (state.doubts || []).forEach((doubt, index) => lines.push(`Duda ${index + 1}: ${text(doubt.text)}`));
    return report || lines.join('\n');
  }

  function renderDoubts() {
    ui.doubtList.replaceChildren();
    const doubts = state.doubts || [];
    if (!doubts.length) ui.doubtList.append(node('p', 'empty-note', 'Aún no has anotado dudas. Puedes agregarlas aquí mientras lees.'));
    doubts.forEach((doubt, index) => {
      const item = node('article', 'doubt-item');
      appendText(item, 'strong', `Duda ${index + 1}`, 'doubt-number');
      appendText(item, 'p', text(doubt.text));
      ui.doubtList.append(item);
    });
    if (!ui.doubtInput.value.trim()) doubtTargetPhase = currentPhaseId();
    ui.doubtCount.textContent = String(doubts.length);
  }

  async function copyText(value, textarea) {
    try {
      await navigator.clipboard.writeText(value);
      return true;
    } catch (_) {
      textarea?.focus(); textarea?.select();
      try { return document.execCommand('copy'); } catch (__) { return false; }
    }
  }

  function downloadMarkdown(content, name) {
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url; anchor.download = name; anchor.hidden = true;
    document.body.append(anchor); anchor.click(); anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  function isTypingTarget(target) {
    return target instanceof HTMLElement && (target.isContentEditable || ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName));
  }

  function onKeys(event) {
    if (!lesson) return;
    if (sessionClosed || sessionClosing || event.defaultPrevented || isTypingTarget(event.target) || ui.doubtPanel.contains(event.target) || ui.exportDialog.open) return;
    if (event.key === 'Enter' && event.target.closest('button, a, [role=button]')) return;
    if (activeFile) {
      if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
        event.preventDefault();
        const paths = currentPhase()?.files?.filter(safeFile) || [];
        const at = paths.indexOf(activeFile.path);
        const nextIndex = at + (event.key === 'ArrowRight' ? 1 : -1);
        if (paths[nextIndex]) renderFile(paths[nextIndex], 1);
        return;
      }
      if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
        event.preventDefault();
        const code = $('full-code');
        code?.scrollBy({ top: event.key === 'ArrowDown' ? 90 : -90, behavior: 'smooth' });
        return;
      }
      if (event.key === 'Enter') { event.preventDefault(); restoreArticle(); return; }
      return;
    }
    if (event.key === 'ArrowLeft') { event.preventDefault(); openPhase(phaseIndex - 1); }
    else if (event.key === 'ArrowRight') { event.preventDefault(); openPhase(phaseIndex + 1); }
    else if (event.key === 'ArrowDown') { event.preventDefault(); window.scrollBy({ top: 90, behavior: 'smooth' }); }
    else if (event.key === 'ArrowUp') { event.preventDefault(); window.scrollBy({ top: -90, behavior: 'smooth' }); }
    else if (event.key === 'Enter') {
      const firstStep = currentPhase()?.story?.walkthrough?.find((step) => step.file && safeFile(step.file));
      const path = firstStep?.file || currentPhase()?.files?.find(safeFile);
      const firstLine = Array.isArray(firstStep?.lines) ? firstStep.lines[0] : 1;
      if (path) { event.preventDefault(); renderFile(path, firstLine); }
    }
  }

  function restoreArticle() {
    activeFile = null;
    renderArticle();
    window.scrollTo({ top: articleScroll, behavior: 'instant' });
    ui.reader.focus({ preventScroll: true });
  }

  function openDoubts(phaseId) {
    if (!ui.doubtInput.value.trim()) doubtTargetPhase = phaseId || currentPhaseId();
    renderDoubts();
    ui.doubtFeedback.textContent = '';
    ui.doubtPanel.classList.add('is-open');
    $('doubts-open').setAttribute('aria-expanded', 'true');
    ui.doubtInput.focus({ preventScroll: true });
  }

  async function closeSession() {
    if (sessionClosing || sessionClosed) return;
    sessionClosing = true;
    clearTimeout(scrollTimer);
    $('pause-button').disabled = true;
    $('pause-button').textContent = 'Guardando…';
    try {
      await queueAction({ action: 'visit', phase: currentPhaseId(), scroll: activeFile ? Math.max(0, Math.round(articleScroll)) : Math.max(0, Math.round(window.scrollY)) });
      await requestChain;
      const response = await api('/api/action', { method: 'POST', body: JSON.stringify({ action: 'close' }) });
      const result = await response.json();
      report = text(result.report) || makeNotes();
      if (result.state) {
        state.completed = Array.isArray(result.state.completed) ? result.state.completed : state.completed;
        state.doubts = Array.isArray(result.state.doubts) ? result.state.doubts : state.doubts;
      }
      sessionClosed = true;
      document.body.classList.add('session-closed');
      setStatus('Sesión cerrada');
      $('pause-button').textContent = 'Sesión cerrada';
      [$('doubts-open'), $('export-button'), ui.read, ui.previous, ui.next].forEach((button) => { button.disabled = true; });
      ui.nav.querySelectorAll('button').forEach((button) => { button.disabled = true; });
      ui.reader.querySelectorAll('button').forEach((button) => { button.disabled = true; });
      ui.doubtForm.querySelectorAll('input, textarea, button').forEach((control) => { control.disabled = true; });
      ui.exportText.value = report;
      ui.exportFeedback.textContent = 'Sesión cerrada. Puedes copiar o descargar este resumen sin conexión.';
      ui.exportDialog.showModal();
      $('copy-export').focus();
    } catch (error) {
      sessionClosing = false;
      $('pause-button').disabled = false;
      $('pause-button').textContent = 'Pausar y salir';
      showToast(`No se pudo cerrar la sesión: ${error.message}`);
    }
  }

  async function start() {
    try {
      const response = await api('/api/bootstrap');
      const payload = await response.json();
      lesson = payload.lesson;
      files = payload.files || {};
      document.body.classList.toggle('no-motion', payload.motion === false);
      state = payload.state || state;
      state.completed ||= []; state.doubts ||= [];
      report = text(payload.report);
      if (!lesson || !Array.isArray(lesson.phases) || lesson.phases.length === 0) throw new Error('La guía no contiene fases para mostrar.');
      ui.title.textContent = text(lesson.title) || 'Recorrido guiado';
      ui.objective.textContent = text(lesson.objective);
      renderNav();
      const savedPhase = lesson.phases.findIndex((phase) => phase.id === state.phase);
      const savedReader = lesson.phases.findIndex((phase) => phase.id === state.reader?.phase);
      phaseIndex = savedPhase >= 0 ? savedPhase : Math.max(0, savedReader);
      renderArticle();
      renderDoubts();
      ui.workspace.setAttribute('aria-busy', 'false');
      $('copy-doubts').disabled = false;
      setStatus('Avance guardado');
      const initialScroll = state.reader?.phase === currentPhaseId() && Number.isFinite(state.reader.scroll)
        ? Math.max(0, state.reader.scroll)
        : 0;
      if (initialScroll) requestAnimationFrame(() => window.scrollTo({ top: initialScroll, behavior: 'instant' }));
      queueAction({ action: 'visit', phase: currentPhaseId(), scroll: initialScroll }).catch(() => {});
    } catch (error) {
      ui.workspace.setAttribute('aria-busy', 'false');
      const panel = node('section', 'fatal');
      appendText(panel, 'p', 'NO SE PUDO ABRIR LA GUÍA', 'lead-label');
      appendText(panel, 'h2', 'El visor no pudo conectar con su contenido');
      appendText(panel, 'p', error.message);
      const retry = node('button', 'button button-primary', 'Volver a intentar');
      retry.type = 'button'; retry.addEventListener('click', () => window.location.reload());
      panel.append(retry); ui.reader.replaceChildren(panel);
      setStatus('Sin conexión', 'error');
    }
  }

  ui.nav.addEventListener('click', (event) => {
    const button = event.target.closest('[data-phase-index]');
    if (button) openPhase(Number(button.dataset.phaseIndex));
  });
  ui.reader.addEventListener('click', (event) => {
    if (sessionClosed) return;
    const open = event.target.closest('[data-open-file]');
    if (open) renderFile(open.dataset.openFile, open.dataset.line);
    if (event.target.closest('[data-back-article]')) restoreArticle();
    const note = event.target.closest('[data-note-phase]');
    if (note) openDoubts(note.dataset.notePhase);
  });
  ui.previous.addEventListener('click', () => openPhase(phaseIndex - 1));
  ui.next.addEventListener('click', () => openPhase(phaseIndex + 1));
  ui.read.addEventListener('click', async () => {
    const phase = currentPhaseId();
    if (state.completed.includes(phase)) { showToast('Esta fase ya está marcada como leída.'); return; }
    try { await queueAction({ action: 'complete', phase }); showToast('Fase marcada como leída.'); }
    catch (_) { showToast('No se pudo guardar la lectura. Inténtalo de nuevo.'); }
  });
  window.addEventListener('scroll', () => scheduleScrollSave(), { passive: true });
  window.addEventListener('keydown', onKeys);

  $('doubts-close').addEventListener('click', () => {
    ui.doubtPanel.classList.remove('is-open');
    $('doubts-open').setAttribute('aria-expanded', 'false');
    $('doubts-open').focus();
  });
  window.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && ui.doubtPanel.classList.contains('is-open') && !ui.exportDialog.open) {
      $('doubts-close').click();
    }
  });
  ui.doubtInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      if (ui.doubtInput.value.trim() && !ui.doubtInput.readOnly) ui.doubtForm.requestSubmit();
    }
  });
  ui.doubtInput.addEventListener('input', () => {
    if (!ui.doubtInput.value.trim()) doubtTargetPhase = currentPhaseId();
    renderDoubts();
  });
  $('doubts-open').setAttribute('aria-controls', 'doubts-panel');
  const notesViewport = matchMedia('(max-width: 800px)');
  const syncNotesDisclosure = () => $('doubts-open').setAttribute('aria-expanded', String(!notesViewport.matches || ui.doubtPanel.classList.contains('is-open')));
  notesViewport.addEventListener('change', syncNotesDisclosure);
  syncNotesDisclosure();
  $('doubts-open').addEventListener('click', () => { if (!sessionClosed) openDoubts(currentPhaseId()); });
  ui.doubtForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (sessionClosed || sessionClosing) return;
    const value = ui.doubtInput.value.trim();
    if (!value) return;
    const submit = ui.doubtForm.querySelector('button[type=submit]');
    if (submit.disabled) return;
    submit.disabled = true;
    try {
      await queueAction({ action: 'doubt', phase: doubtTargetPhase || currentPhaseId(), text: value });
      if (ui.doubtInput.value.trim() === value) ui.doubtInput.value = '';
      renderDoubts();
      ui.doubtList.scrollTop = ui.doubtList.scrollHeight;
      ui.doubtFeedback.textContent = 'Duda guardada.';
    } catch (_) { ui.doubtFeedback.textContent = 'No se pudo guardar. Conserva el texto y vuelve a intentarlo.'; }
    finally { submit.disabled = sessionClosed; }
  });
  $('copy-doubts').addEventListener('click', async () => {
    await requestChain;
    const content = makeNotes();
    try {
      await navigator.clipboard.writeText(content);
      ui.doubtFeedback.textContent = 'Dudas copiadas con la instrucción para el agente.';
    } catch (_) {
      ui.exportText.value = content;
      ui.doubtPanel.classList.remove('is-open');
      ui.exportFeedback.textContent = 'No se pudo copiar. El resumen está seleccionado para copiarlo manualmente.';
      ui.exportDialog.showModal();
      ui.exportText.focus(); ui.exportText.select();
    }
  });
  $('download-doubts').addEventListener('click', () => { downloadMarkdown(makeNotes(), 'dudas.md'); ui.doubtFeedback.textContent = 'Descarga preparada.'; });
  $('clear-doubts').addEventListener('click', async () => {
    if (sessionClosed || sessionClosing) return;
    const button = $('clear-doubts');
    if (button.disabled) return;
    button.disabled = true;
    ui.doubtInput.readOnly = true;
    try {
      await queueAction({ action: 'clear_doubts' });
      ui.doubtInput.value = '';
      doubtTargetPhase = currentPhaseId();
      ui.doubtFeedback.textContent = 'Dudas limpiadas.';
    } catch (_) {
      ui.doubtFeedback.textContent = 'No se pudieron limpiar las dudas. Vuelve a intentarlo.';
    } finally {
      ui.doubtInput.readOnly = false;
      button.disabled = sessionClosed;
      ui.doubtInput.focus({ preventScroll: true });
    }
  });
  $('export-button').addEventListener('click', () => {
    ui.exportText.value = makeNotes(); ui.exportFeedback.textContent = ''; ui.exportDialog.showModal();
  });
  $('copy-export').addEventListener('click', async () => {
    const ok = await copyText(ui.exportText.value, ui.exportText);
    ui.exportFeedback.textContent = ok ? 'Resumen copiado.' : 'No se pudo copiar; el texto está seleccionado para copiarlo manualmente.';
  });
  $('download-export').addEventListener('click', () => { downloadMarkdown(ui.exportText.value, 'lectura-proyecto.md'); ui.exportFeedback.textContent = 'Descarga preparada.'; });
  $('home-button').addEventListener('click', () => openPhase(0));
  $('pause-button').addEventListener('click', closeSession);

  start();
})();
