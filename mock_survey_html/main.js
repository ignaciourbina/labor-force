// Mock data to simulate API responses
const mockMinorSoc = {
  '11': [
    { code: '11-1011', label: 'Chief Executives' },
    { code: '11-1021', label: 'General and Operations Managers' }
  ],
  '15': [
    { code: '15-1232', label: 'Software Developers' },
    { code: '15-1244', label: 'Network Architects' }
  ]
};

const mockForeignRates = {
  states: { 'CA': 27.2, 'NY': 22.5 },
  occupations: {
    '11-1011': 15.1,
    '11-1021': 16.8,
    '15-1232': 28.6,
    '15-1244': 24.3
  },
  automation: {
    '11-1011': 7,
    '11-1021': 19,
    '15-1232': 52,
    '15-1244': 42
  }
};

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
  const options = (mockMinorSoc[major] || []).map(o => `<option value="${o.code}">${o.label}</option>`).join('');
  div.innerHTML = `
    <label for="minor">Select 6 digit SOC:</label>
    <select id="minor">
      <option value="">--choose--</option>
      ${options}
    </select>
    <button id="next">Next</button>
  `;
  div.querySelector('#next').onclick = () => {
    const minor = div.querySelector('#minor').value;
    if (!minor) return alert('Please select an occupation');
    setEmbedded('soc', minor);
    // Simulated API calls
    setEmbedded('stateForeignPct', mockForeignRates.states[getEmbedded('state')]);
    setEmbedded('occForeignPct', mockForeignRates.occupations[minor]);
    setEmbedded('automationPctile', mockForeignRates.automation[minor]);
    nextPage();
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
