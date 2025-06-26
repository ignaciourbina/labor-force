// Fetch automation percentile for selected six‑digit SOC code
// Replace QID_SOC with the question ID containing the 6‑digit SOC value
Qualtrics.SurveyEngine.addOnReady(async function() {
  const soc = '${q://QID_SOC/ChoiceTextEntryValue}';
  const url = 'https://iurbinah-soc-lookup-space.hf.space/automation_percentile?soc=' + encodeURIComponent(soc);
  try {
    const resp = await fetch(url);
    if (resp.ok) {
      const data = await resp.json();
      Qualtrics.SurveyEngine.setEmbeddedData('automationPctile', data.automation_pctile);
    } else {
      console.error('automation fetch failed', resp.status);
    }
  } catch (err) {
    console.error('automation fetch error', err);
  }
});
