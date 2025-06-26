// Fetch foreign-born labor force share for selected occupation
// Replace QID_SOC with the question ID containing the 6‑digit SOC value
Qualtrics.SurveyEngine.addOnReady(async function() {
  const soc = '${q://QID_SOC/ChoiceTextEntryValue}';
  const url = 'https://iurbinah-soc-lookup-space.hf.space/occ_foreign_rate?soc=' + encodeURIComponent(soc);
  try {
    const resp = await fetch(url);
    if (resp.ok) {
      const data = await resp.json();
      Qualtrics.SurveyEngine.setEmbeddedData('occForeignPct', data.foreign_pct);
    } else {
      console.error('occupation foreign fetch failed', resp.status);
    }
  } catch (err) {
    console.error('occupation foreign fetch error', err);
  }
});
