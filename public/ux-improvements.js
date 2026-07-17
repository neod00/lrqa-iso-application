(function () {
  const STEP_LABELS = ['회사 정보', '담당자·표준', '범위·인증', '인력 현황', '인증 전환', '표준별 정보', '검토·제출'];
  let pages = [];
  let currentStep = 0;
  let saveTimer;

  function setAttributes() {
    const languageSelect = document.getElementById('languageSelect');
    if (languageSelect) languageSelect.setAttribute('aria-label', '언어 선택');

    const autocompleteMap = {
      companyNameKo: 'organization',
      tradeName: 'organization',
      headOfficeAddress: 'street-address',
      city: 'address-level2',
      province: 'address-level1',
      postalCode: 'postal-code',
      country: 'country-name',
      mainPhone: 'tel',
      mainEmail: 'email',
      website: 'url',
      contactName: 'name',
      contactEmail: 'email',
      contactPhone: 'tel',
      mobilePhone: 'tel'
    };

    Object.entries(autocompleteMap).forEach(([name, value]) => {
      const field = document.querySelector(`[name="${name}"]`);
      if (field) field.setAttribute('autocomplete', value);
    });

    ['siteCount', 'totalEmployees', 'permanentEmployees', 'temporaryEmployees', 'contractorEmployees', 'casualEmployees', 'postalCode'].forEach((name) => {
      const field = document.querySelector(`[name="${name}"]`);
      if (field) field.setAttribute('inputmode', 'numeric');
    });

    ['mainPhone', 'contactPhone', 'mobilePhone'].forEach((name) => {
      const field = document.querySelector(`[name="${name}"]`);
      if (field) field.setAttribute('inputmode', 'tel');
    });

    document.querySelectorAll('.form-row').forEach((row, rowIndex) => {
      const prompt = row.querySelector(':scope > .form-label, :scope > span:first-child');
      const controls = Array.from(row.querySelectorAll('input, textarea, select'));
      if (!prompt || !controls.length) return;

      if (!prompt.id) prompt.id = `field-label-${rowIndex + 1}`;
      if (controls.length > 1) {
        row.setAttribute('role', 'group');
        row.setAttribute('aria-labelledby', prompt.id);
      }

      controls.forEach((control) => {
        if (control.getAttribute('aria-label') || control.getAttribute('aria-labelledby') || control.placeholder) return;
        let directChild = control;
        while (directChild.parentElement && directChild.parentElement !== row) directChild = directChild.parentElement;
        let labelNode = directChild.previousElementSibling;
        while (labelNode && labelNode.tagName !== 'SPAN') labelNode = labelNode.previousElementSibling;
        if (labelNode) {
          if (!labelNode.id) labelNode.id = `field-label-${rowIndex + 1}-${controls.indexOf(control) + 1}`;
          control.setAttribute('aria-labelledby', labelNode.id);
        } else {
          control.setAttribute('aria-labelledby', prompt.id);
        }
      });
    });

    document.querySelectorAll('.table input').forEach((field) => {
      if (!field.getAttribute('aria-label') && field.placeholder) field.setAttribute('aria-label', field.placeholder);
      if (/직원|인원|수$/.test(field.placeholder || '')) field.setAttribute('inputmode', 'numeric');
    });

    document.querySelectorAll('.checkbox-group').forEach((group) => {
      const field = group.querySelector('input');
      const optionText = group.querySelector(':scope > span:last-child')?.textContent.trim();
      const row = group.closest('.form-row');
      let promptNode = group.previousElementSibling;
      while (promptNode && promptNode.tagName !== 'SPAN') promptNode = promptNode.previousElementSibling;
      const rowPrompt = promptNode?.textContent.trim() || row?.querySelector(':scope > span:first-child')?.textContent.trim();
      if (field) {
        field.removeAttribute('aria-labelledby');
        field.setAttribute('aria-label', [rowPrompt, optionText].filter(Boolean).join(' - ') || optionText || '선택');
      }
    });

    const chatbotInput = document.getElementById('chatbotInput');
    if (chatbotInput) chatbotInput.setAttribute('aria-label', 'ISO 질문 입력');
    const chatbotSend = document.querySelector('.chatbot-send-btn');
    if (chatbotSend) chatbotSend.setAttribute('aria-label', '질문 보내기');
  }

  function createFirstPage(container, firstBreak) {
    const header = container.querySelector(':scope > .header');
    const firstPage = document.createElement('section');
    firstPage.className = 'wizard-page';
    firstPage.dataset.step = '1';
    container.insertBefore(firstPage, header);

    let node = firstPage.nextElementSibling;
    while (node && node !== firstBreak) {
      const next = node.nextElementSibling;
      firstPage.appendChild(node);
      node = next;
    }
    return firstPage;
  }

  function buildWizard() {
    const container = document.querySelector('.container');
    if (!container || container.dataset.wizardReady === 'true') return;

    const controlButtons = container.querySelector(':scope > .control-buttons');
    const pageBreaks = Array.from(container.querySelectorAll(':scope > .page-break'));
    if (!controlButtons || !pageBreaks.length) return;

    const firstPage = createFirstPage(container, pageBreaks[0]);
    pageBreaks.forEach((page, index) => {
      page.classList.add('wizard-page');
      page.dataset.step = String(index + 2);
    });
    pages = [firstPage, ...pageBreaks];

    const contactSection = container.querySelector(':scope > .contact-section');
    const finalFooter = contactSection && contactSection.nextElementSibling && contactSection.nextElementSibling.classList.contains('footer')
      ? contactSection.nextElementSibling
      : null;
    if (contactSection) pages[pages.length - 1].appendChild(contactSection);
    if (finalFooter) {
      finalFooter.removeAttribute('data-i18n');
      const marker = finalFooter.querySelector('[data-i18n]');
      if (marker) marker.removeAttribute('data-i18n');
      pages[pages.length - 1].appendChild(finalFooter);
    }

    const progress = document.createElement('div');
    progress.className = 'wizard-progress';
    progress.innerHTML = `
      <div class="wizard-progress-row">
        <div class="wizard-progress-title" id="wizardProgressTitle">1 / ${pages.length} · ${STEP_LABELS[0]}</div>
        <div class="wizard-save-status" id="wizardSaveStatus" aria-live="polite">자동 저장</div>
      </div>
      <div class="wizard-track" aria-hidden="true"><div class="wizard-track-fill" id="wizardTrackFill"></div></div>
      <div class="wizard-steps" aria-label="신청서 진행 단계">
        ${pages.map((_, index) => `<div class="wizard-step" data-step-indicator="${index}">${index + 1}. ${STEP_LABELS[index] || `단계 ${index + 1}`}</div>`).join('')}
      </div>`;
    container.insertBefore(progress, firstPage);

    const form = document.createElement('form');
    form.id = 'isoApplicationForm';
    form.noValidate = true;
    form.addEventListener('submit', (event) => event.preventDefault());
    container.insertBefore(form, firstPage);
    pages.forEach((page) => form.appendChild(page));

    const nav = document.createElement('div');
    nav.className = 'wizard-nav';
    nav.innerHTML = `
      <button type="button" class="wizard-prev" id="wizardPrev">이전</button>
      <button type="button" class="wizard-next" id="wizardNext">다음</button>`;
    form.appendChild(nav);

    document.getElementById('wizardPrev').addEventListener('click', () => showStep(currentStep - 1));
    document.getElementById('wizardNext').addEventListener('click', () => {
      if (validateCurrentStep()) showStep(currentStep + 1);
    });

    const savedStep = Number(sessionStorage.getItem('iso_application_step'));
    currentStep = Number.isFinite(savedStep) ? Math.min(Math.max(savedStep, 0), pages.length - 1) : 0;
    container.dataset.wizardReady = 'true';
    showStep(currentStep, false);
  }

  function validateCurrentStep() {
    const page = pages[currentStep];
    if (!page) return true;
    const missing = Array.from(page.querySelectorAll('[required]')).filter((field) => !String(field.value || '').trim());
    if (!missing.length) return true;

    missing.forEach((field) => field.classList.add('error-field'));
    const first = missing[0];
    first.focus({ preventScroll: true });
    first.scrollIntoView({ behavior: 'smooth', block: 'center' });
    const label = first.getAttribute('aria-labelledby');
    const labelText = label ? document.getElementById(label)?.textContent.trim() : first.placeholder;
    if (typeof showMessage === 'function') {
      showMessage('error', '입력 오류', `${labelText || '필수 항목'}을(를) 입력해 주세요.`);
    }
    return false;
  }

  function showStep(nextStep, shouldScroll = true) {
    if (!pages.length) return;
    currentStep = Math.min(Math.max(nextStep, 0), pages.length - 1);
    pages.forEach((page, index) => {
      page.hidden = index !== currentStep;
      page.setAttribute('aria-hidden', index === currentStep ? 'false' : 'true');
    });

    const title = document.getElementById('wizardProgressTitle');
    const fill = document.getElementById('wizardTrackFill');
    const prev = document.getElementById('wizardPrev');
    const next = document.getElementById('wizardNext');
    if (title) title.textContent = `${currentStep + 1} / ${pages.length} · ${STEP_LABELS[currentStep] || `단계 ${currentStep + 1}`}`;
    if (fill) fill.style.width = `${((currentStep + 1) / pages.length) * 100}%`;
    if (prev) prev.hidden = currentStep === 0;
    if (next) next.hidden = currentStep === pages.length - 1;

    document.querySelectorAll('[data-step-indicator]').forEach((indicator, index) => {
      indicator.classList.toggle('is-active', index === currentStep);
      indicator.classList.toggle('is-complete', index < currentStep);
      if (index === currentStep) indicator.setAttribute('aria-current', 'step');
      else indicator.removeAttribute('aria-current');
    });

    sessionStorage.setItem('iso_application_step', String(currentStep));
    persistDraft();
    if (shouldScroll) document.querySelector('.wizard-progress')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function persistDraft() {
    try {
      if (typeof collectFormData === 'function') {
        sessionStorage.setItem('iso_application_form', JSON.stringify(collectFormData()));
      }
      const status = document.getElementById('wizardSaveStatus');
      if (status) status.textContent = '저장됨';
    } catch (error) {
      const status = document.getElementById('wizardSaveStatus');
      if (status) status.textContent = '저장 확인 필요';
    }
  }

  function scheduleSaveStatus() {
    const status = document.getElementById('wizardSaveStatus');
    if (status) status.textContent = '저장 중…';
    clearTimeout(saveTimer);
    saveTimer = setTimeout(persistDraft, 650);
  }

  function setConditionalGroup(radioName, dependentElements) {
    const radios = Array.from(document.querySelectorAll(`input[name="${radioName}"]`));
    if (!radios.length) return;
    const update = () => {
      const value = radios.find((radio) => radio.checked)?.value;
      dependentElements.forEach((element) => {
        if (!element) return;
        element.classList.add('conditional-details');
        element.hidden = value !== 'yes';
        element.querySelectorAll('input, textarea, select').forEach((field) => {
          field.disabled = value !== 'yes';
        });
      });
    };
    radios.forEach((radio) => radio.addEventListener('change', update));
    update();
  }

  function setupConditionalFields() {
    const existingRadio = document.querySelector('input[name="existingCertification"]');
    if (existingRadio) {
      const section = existingRadio.closest('.section');
      const question = existingRadio.closest('.form-row');
      const dependents = [];
      let node = question?.nextElementSibling;
      while (node) {
        dependents.push(node);
        node = node.nextElementSibling;
      }
      setConditionalGroup('existingCertification', dependents);
    }

    const transferRadio = document.querySelector('input[name="transferToLrqa"]');
    if (transferRadio) {
      const question = transferRadio.closest('.form-row');
      const section = transferRadio.closest('.section');
      const dependents = [];
      let node = question?.nextElementSibling;
      while (node && node.parentElement === section) {
        dependents.push(node);
        node = node.nextElementSibling;
      }
      setConditionalGroup('transferToLrqa', dependents);
    }

    const outsourcingDetail = document.querySelector('textarea[name="workDescription"]')?.closest('.form-row');
    setConditionalGroup('outsourcing', [outsourcingDetail]);

    const repeatRadio = document.querySelector('input[name="repeatGroup"]');
    if (repeatRadio) {
      const question = repeatRadio.closest('.form-row');
      const description = question?.nextElementSibling;
      const table = description?.nextElementSibling;
      setConditionalGroup('repeatGroup', [description, table]);
    }

    const standards = Array.from(document.querySelectorAll('input[name="isoStandards"]'));
    const iso14001Section = document.querySelector('textarea[name="iso14001Business"]')?.closest('.section');
    const iso45001Section = document.querySelector('textarea[name="iso45001Business"]')?.closest('.section');
    const standardPage = iso14001Section?.closest('.wizard-page') || iso45001Section?.closest('.wizard-page');
    const note = document.createElement('div');
    note.className = 'wizard-empty-note';
    note.textContent = '선택한 표준에 필요한 추가 질문이 없습니다. 다음 단계로 이동해 주세요.';
    if (standardPage) standardPage.insertBefore(note, standardPage.firstChild);

    const integratedRow = document.querySelector('input[name="multiStandardSystem"]')?.closest('.form-row');
    const updateStandards = () => {
      const selected = standards.filter((field) => field.checked).map((field) => field.value);
      if (iso14001Section) {
        iso14001Section.classList.add('standard-conditional');
        iso14001Section.hidden = !selected.includes('iso14001');
      }
      if (iso45001Section) {
        iso45001Section.classList.add('standard-conditional');
        iso45001Section.hidden = !selected.includes('iso45001');
      }
      if (note) note.hidden = selected.includes('iso14001') || selected.includes('iso45001');
      if (integratedRow) integratedRow.hidden = selected.length < 2;
    };
    standards.forEach((field) => field.addEventListener('change', updateStandards));
    updateStandards();
  }

  function restoreMultiSelectState() {
    try {
      let raw = sessionStorage.getItem('iso_application_form');
      let data = raw ? JSON.parse(raw) : null;
      if (!data) {
        const backupRaw = localStorage.getItem('iso_application_form_backup');
        const backup = backupRaw ? JSON.parse(backupRaw) : null;
        data = backup?.data || null;
      }
      if (!data) return;

      document.querySelectorAll('input[type="checkbox"][name]').forEach((field) => {
        const savedValue = data[field.name];
        const values = Array.isArray(savedValue)
          ? savedValue
          : String(savedValue || '').split(',').map((value) => value.trim()).filter(Boolean);
        field.checked = values.includes(field.value);
      });
    } catch (error) {
      console.warn('선택 항목 복원 중 오류:', error);
    }
  }

  function createCompletionView() {
    const container = document.querySelector('.container');
    const form = document.getElementById('isoApplicationForm');
    if (!container || !form) return null;

    let completion = document.getElementById('applicationCompletion');
    if (completion) return completion;

    completion = document.createElement('section');
    completion.id = 'applicationCompletion';
    completion.className = 'application-completion';
    completion.hidden = true;
    completion.setAttribute('aria-live', 'polite');
    completion.innerHTML = `
      <div class="completion-heading">
        <div class="completion-check" aria-hidden="true">✓</div>
        <p class="completion-eyebrow">신청서 접수 완료</p>
        <h1>신청해 주셔서 감사합니다.</h1>
        <p><strong data-completion-company>고객사</strong>의 인증 심사 신청서가 정상적으로 접수되었습니다.</p>
      </div>

      <div class="completion-contact">
        <span>입력하신 이메일</span>
        <strong data-completion-email>-</strong>
        <p>담당자가 신청 내용을 검토한 후 빠른 시일 내에 연락드리겠습니다.</p>
      </div>

      <div class="completion-summary" aria-label="접수 내용 요약">
        <div><span>회사명</span><strong data-summary-company>-</strong></div>
        <div><span>담당자</span><strong data-summary-contact>-</strong></div>
        <div><span>신청 표준</span><strong data-summary-standards>-</strong></div>
        <div><span>접수 일시</span><strong data-summary-date>-</strong></div>
      </div>

      <div class="completion-process">
        <h2>이후 진행 절차</h2>
        <ol>
          <li><span>1</span><div><strong>신청서 접수</strong><p>제출하신 내용이 접수되었습니다.</p></div></li>
          <li><span>2</span><div><strong>내용 검토</strong><p>LRQA 담당자가 인증 범위와 심사 조건을 확인합니다.</p></div></li>
          <li><span>3</span><div><strong>담당자 연락</strong><p>견적 및 다음 절차를 안내해 드립니다.</p></div></li>
        </ol>
      </div>

      <div class="completion-resources">
        <h2>다음 단계에 도움이 되는 자료</h2>
        <div class="completion-resource-grid">
          <button type="button" class="completion-resource" data-completion-gap>
            <strong>갭분석 요청</strong>
            <span>현재 인증 준비 수준을 확인합니다.</span>
          </button>
          <a class="completion-resource" data-completion-news href="https://www.lrqa.com/ko-kr/latest-news/" target="_blank" rel="noopener">
            <strong>LRQA 최신 뉴스</strong>
            <span>인증 및 경영시스템 소식을 확인합니다.</span>
          </a>
          <a class="completion-resource" href="https://script.google.com/macros/s/AKfycby3nyuGeBzA5U_dzTE9zS7wfFgfGVFV73wLOWYdC8BtqeNNsdICawoWgfbs4ULEnO7MWg/exec" target="_blank" rel="noopener">
            <strong>키워드 뉴스레터</strong>
            <span>관심 분야의 주요 업데이트를 받아봅니다.</span>
          </a>
        </div>
      </div>

      <div class="completion-actions">
        <button type="button" class="completion-new-application" data-completion-new>새 신청서 작성</button>
      </div>`;

    form.insertAdjacentElement('afterend', completion);

    completion.querySelector('[data-completion-gap]')?.addEventListener('click', () => {
      if (typeof window.showGapAnalysisInfo === 'function') window.showGapAnalysisInfo();
    });

    completion.querySelector('[data-completion-new]')?.addEventListener('click', () => {
      document.querySelectorAll('#isoApplicationForm input, #isoApplicationForm textarea').forEach((field) => {
        if (field.type === 'checkbox' || field.type === 'radio') field.checked = false;
        else field.value = '';
      });
      document.querySelectorAll('#isoApplicationForm select').forEach((field) => {
        field.selectedIndex = 0;
      });
      sessionStorage.removeItem('iso_application_form');
      sessionStorage.removeItem('iso_application_step');
      localStorage.removeItem('iso_application_form_backup');
      location.reload();
    });

    return completion;
  }

  function formatCompletionStandards(formData) {
    const labels = {
      iso9001: 'ISO 9001',
      iso14001: 'ISO 14001',
      iso45001: 'ISO 45001'
    };
    const values = Array.isArray(formData.isoStandards)
      ? formData.isoStandards
      : String(formData.isoStandards || '').split(',').map((value) => value.trim()).filter(Boolean);
    const standards = values.map((value) => labels[value] || value);
    if (formData.otherStandard) standards.push(formData.otherStandard);
    return standards.join(', ') || '선택 정보 없음';
  }

  window.showApplicationCompletion = function (formData = {}) {
    const completion = createCompletionView();
    const form = document.getElementById('isoApplicationForm');
    const progress = document.querySelector('.wizard-progress');
    if (!completion || !form) return;

    const company = formData.companyNameKo || formData.companyNameEn || '고객사';
    const contact = formData.contactName || '-';
    const email = formData.contactEmail || '-';
    const standards = formatCompletionStandards(formData);
    const submittedAt = new Intl.DateTimeFormat('ko-KR', {
      dateStyle: 'long',
      timeStyle: 'short'
    }).format(new Date());

    completion.querySelector('[data-completion-company]').textContent = company;
    completion.querySelector('[data-completion-email]').textContent = email;
    completion.querySelector('[data-summary-company]').textContent = company;
    completion.querySelector('[data-summary-contact]').textContent = contact;
    completion.querySelector('[data-summary-standards]').textContent = standards;
    completion.querySelector('[data-summary-date]').textContent = submittedAt;

    const news = completion.querySelector('[data-completion-news]');
    if (news) news.href = document.documentElement.lang === 'ko'
      ? 'https://www.lrqa.com/ko-kr/latest-news/'
      : 'https://www.lrqa.com/en/latest-news/';

    document.body.classList.add('application-complete');
    form.hidden = true;
    if (progress) progress.hidden = true;
    completion.hidden = false;
    document.getElementById('messageOverlay')?.classList.remove('show');
    completion.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };
  function refineSubmitArea() {
    const submitButton = document.querySelector('.submit-btn');
    const submitPanel = submitButton?.closest('div[style*="text-align: center"]');
    if (!submitPanel) return;
    submitPanel.classList.add('submit-panel');
    Array.from(submitPanel.children).slice(2).forEach((element) => element.classList.add('post-submit-promotion'));

    if (typeof window.submitForm === 'function') {
      const legacySubmit = window.submitForm;
      window.submitForm = async function () {
        const firstMissing = Array.from(document.querySelectorAll('[required]')).find((field) => !String(field.value || '').trim());
        const consent = document.querySelector('input[name="dataProcessConsent"]:checked');
        const target = firstMissing || (!consent ? document.querySelector('input[name="dataProcessConsent"]') : null);
        if (target) {
          const targetPage = target.closest('.wizard-page');
          const targetIndex = pages.indexOf(targetPage);
          if (targetIndex >= 0) showStep(targetIndex);
        }
        return legacySubmit();
      };
    }
  }

  function minimizeChatbot() {
    try {
      if (typeof isChatbotMinimized !== 'undefined' && !isChatbotMinimized && typeof toggleChatbot === 'function') {
        toggleChatbot();
      }
    } catch (error) {
      const container = document.getElementById('chatbotContainer');
      if (container) container.style.display = 'none';
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    restoreMultiSelectState();
    buildWizard();
    setAttributes();
    setupConditionalFields();
    refineSubmitArea();
    minimizeChatbot();

    document.addEventListener('input', scheduleSaveStatus, true);
    document.addEventListener('change', scheduleSaveStatus, true);
    document.addEventListener('input', (event) => event.target.classList?.remove('error-field'), true);
  });
})();