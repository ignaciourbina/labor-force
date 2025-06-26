// Fetch foreign-born labor force share for respondent's state
// Replace QID_STATE with the question ID capturing the state abbreviation
Qualtrics.SurveyEngine.addOnReady(async function() {
  const state = '${q://QID_STATE/ChoiceTextEntryValue}';
  const url = 'https://iurbinah-soc-lookup-space.hf.space/foreign_rate?state=' + encodeURIComponent(state);
  try {
    const resp = await fetch(url);
    if (resp.ok) {
      const data = await resp.json();
      Qualtrics.SurveyEngine.setEmbeddedData('stateForeignPct', data.foreign_pct);
    } else {
      console.error('state foreign fetch failed', resp.status);
    }
  } catch (err) {
    console.error('state foreign fetch error', err);
  }
});
