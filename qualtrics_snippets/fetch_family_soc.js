// Fetch list of six‑digit occupations for a two‑digit SOC code
// Replace QID_MAJOR with the question ID capturing the major SOC code
Qualtrics.SurveyEngine.addOnReady(async function() {
  const major = '${q://QID_MAJOR/ChoiceTextEntryValue}';
  const url = 'https://iurbinah-soc-lookup-space.hf.space/automation_family?major=' + encodeURIComponent(major);
  try {
    const resp = await fetch(url);
    if (resp.ok) {
      const list = await resp.json();
      Qualtrics.SurveyEngine.setEmbeddedData('familySOCList', JSON.stringify(list));
    } else {
      console.error('family fetch failed', resp.status);
    }
  } catch (err) {
    console.error('family fetch error', err);
  }
});
