# Qualtrics JavaScript Snippets

These simple snippets call the public API hosted on Hugging Face Space and save the results to embedded data fields. Replace the placeholder question IDs with the actual IDs from your Qualtrics survey.

## Files

- `fetch_family_soc.js` – given a two‑digit SOC code, fetch the list of matching six‑digit occupations and store it in `familySOCList`.
- `fetch_automation_pctile.js` – look up the automation percentile for the chosen six‑digit SOC and save it to `automationPctile`.
- `fetch_state_foreign_pct.js` – get the foreign‑born labor force share for the respondent's state and save it to `stateForeignPct`.
- `fetch_occ_foreign_pct.js` – fetch the foreign‑born share for the selected occupation and save it to `occForeignPct`.

## Setup in Qualtrics

1. **Create Embedded Data**
   - In the Survey Flow, add an *Embedded Data* block before the relevant questions.
   - Define the following fields: `familySOCList`, `automationPctile`, `stateForeignPct`, `occForeignPct`.

2. **Major SOC Question**
   - Add a text entry or drop‑down question for the respondent to provide their two‑digit SOC code.
   - Edit the question's JavaScript and paste the contents of `fetch_family_soc.js`.
   - Replace `QID_MAJOR` in the snippet with this question's ID.

3. **Six‑Digit SOC Question**
   - Create a question where respondents select the final six‑digit SOC code. Populate the choices using the embedded field `familySOCList` if desired.
   - After this question, insert the JavaScript from `fetch_automation_pctile.js` **and** `fetch_occ_foreign_pct.js`.
   - Replace `QID_SOC` in those snippets with the six‑digit SOC question ID.

4. **State Question**
   - Add a question that records the respondent's state abbreviation.
   - Paste the snippet from `fetch_state_foreign_pct.js` and replace `QID_STATE` with the state's question ID.

5. **Testing**
   - Preview the survey and check the embedded data values in the session. They should populate after the corresponding pages load.
   - Use the console (F12) to look for any error messages if the fields remain empty.

These snippets intentionally omit UI enhancements. They simply fetch data in the background so you can display or process the results later in your survey.
