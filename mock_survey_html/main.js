// Base URL of the deployed API
const API_BASE = 'https://iurbinah-soc-lookup-space.hf.space';

// Utility functions to query the API
async function fetchMinorSOC(major) {
  const url = `${API_BASE}/automation_family?major=${encodeURIComponent(major)}`;
  const resp = await fetch(url);
  if (!resp.ok) throw new Error('minor SOC fetch failed');
  return resp.json();
}

async function fetchStateForeign(state) {
  const url = `${API_BASE}/foreign_rate?state=${encodeURIComponent(state)}`;
  const resp = await fetch(url);
  if (!resp.ok) throw new Error('state foreign fetch failed');
  return resp.json();
}

async function fetchOccForeign(soc) {
  const url = `${API_BASE}/occ_foreign_rate?soc=${encodeURIComponent(soc)}`;
  const resp = await fetch(url);
  if (!resp.ok) throw new Error('occupation foreign fetch failed');
  return resp.json();
}

async function fetchAutomationPctile(soc) {
  const url = `${API_BASE}/automation_percentile?soc=${encodeURIComponent(soc)}`;
  const resp = await fetch(url);
  if (!resp.ok) throw new Error('automation percentile fetch failed');
  return resp.json();
}

// Simple embedded data store
const dataStore = {};

function setEmbedded(name, value) {
  dataStore[name] = value;
}

function getEmbedded(name) {
  return dataStore[name];
}

const surveyDiv = document.getElementById('survey');
let pageIndex = 0;

const pages = [
  renderStatePage,
  renderMajorSocPage,
  renderMinorSocPage,
  renderResultsPage
];

function renderStatePage() {
  const div = document.createElement('div');
  div.className = 'page active';
  div.innerHTML = `
    <label for="state">Select your state:</label>
    <select id="state">
      <option value="">--choose--</option>
      <option value="CA">California</option>
      <option value="NY">New York</option>
    </select>
    <button id="next">Next</button>
  `;
  div.querySelector('#next').onclick = () => {
    const state = div.querySelector('#state').value;
    if (!state) return alert('Please select a state');
    setEmbedded('state', state);
    nextPage();
  };
  return div;
}

function renderMajorSocPage() {
  const div = document.createElement('div');
  div.className = 'page active';
  div.innerHTML = `
    <label for="major">Select 2 digit SOC:</label>
    <select id="major">
      <option value="">--choose--</option>
      <option value="11">Management (11)</option>
      <option value="15">Computer (15)</option>
    </select>
    <button id="next">Next</button>
  `;
  div.querySelector('#next').onclick = () => {
    const major = div.querySelector('#major').value;
    if (!major) return alert('Please select a SOC major');
    setEmbedded('majorSOC', major);
    nextPage();
  };
  return div;
}

function renderMinorSocPage() {
  const div = document.createElement('div');
  div.className = 'page active';
  const major = getEmbedded('majorSOC');
  div.innerHTML = `
    <label for="minor">Select 6 digit SOC:</label>
    <select id="minor">
      <option value="">Loading...</option>
    </select>
    <button id="next">Next</button>
  `;

  const select = div.querySelector('#minor');
  fetchMinorSOC(major)
    .then(list => {
      const opts = list.map(o => `<option value="${o.soc}">${o.occupation}</option>`).join('');
      select.innerHTML = `<option value="">--choose--</option>` + opts;
    })
    .catch(err => {
      console.error(err);
      select.innerHTML = `<option value="">(failed to load)</option>`;
    });

  div.querySelector('#next').onclick = async () => {
    const minor = select.value;
    if (!minor) return alert('Please select an occupation');
    setEmbedded('soc', minor);
    try {
      const [sData, oData, aData] = await Promise.all([
        fetchStateForeign(getEmbedded('state')),
        fetchOccForeign(minor),
        fetchAutomationPctile(minor)
      ]);
      setEmbedded('stateForeignPct', sData.foreign_pct);
      setEmbedded('occForeignPct', oData.foreign_pct);
      setEmbedded('automationPctile', aData.automation_pctile);
      nextPage();
    } catch (err) {
      console.error(err);
      alert('Error contacting the API, see console for details.');
    }
  };
  return div;
}

function renderResultsPage() {
  const div = document.createElement('div');
  div.className = 'page active';
  const sPct = getEmbedded('stateForeignPct');
  const oPct = getEmbedded('occForeignPct');
  const auto = getEmbedded('automationPctile');
  div.innerHTML = `
    <p>Foreign-born share in your state: <strong>${sPct}%</strong></p>
    <p>Foreign-born share in this occupation: <strong>${oPct}%</strong></p>
    <p>Automation risk percentile: <strong>${auto}</strong></p>
    <button id="restart">Restart</button>
  `;
  div.querySelector('#restart').onclick = () => {
    pageIndex = 0;
    startSurvey();
  };
  return div;
}

function nextPage() {
  pageIndex++;
  startSurvey();
}

function startSurvey() {
  surveyDiv.innerHTML = '';
  const page = pages[pageIndex]();
  surveyDiv.appendChild(page);
}

startSurvey();
