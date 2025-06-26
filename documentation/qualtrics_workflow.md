# Qualtrics Integration Steps

This guide outlines the workflow for using the API with Qualtrics. The
JavaScript snippets referenced below are located in
`API_database_laborforce/qualtricsEngine_js_snippets/`.

## 1. Capture the Major SOC Code
1. Create a text entry question where respondents type or select the
   two‑digit major SOC group.
2. Add **Snippet 1** (`fetch_family_soc_codes.txt`) to this question.
   It grabs the major code via piping (`\${q://QID123/ChoiceTextEntryValue}`)
   and fetches all six‑digit occupations for that group. The returned
   array is stored in the embedded field `familySOCList` for later use.

## 2. Display Detailed Occupations
1. On the next page, create a text entry question to select the final
   six‑digit SOC code.
2. Use JavaScript to read `familySOCList` and provide an autocomplete
   or drop‑down list. See `fetch_6_digit_soc_from_API.txt` for a fully
   worked example of this behaviour.
3. Store the chosen code in an embedded field (e.g. `chosenSOC`).

## 3. Save Automation Percentile
1. After the occupation question, insert **Snippet 2**
   (`fetch_automation_percentile.txt`). Replace `QID456` with the ID of
   the six‑digit SOC question.
2. The script queries `/automation_percentile` and saves the returned
   value to `automationPctile`.

## 4. Save State Foreign Share
1. Capture the respondent's state (two‑letter abbreviation) in a
   separate question.
2. Add **Snippet 3** (`fetch_state_foreign_pct.txt`) to that page. It
   calls `/foreign_rate` and writes the percentage to `stateForeignPct`.

## 5. Save Occupation Foreign Share
1. Insert **Snippet 4** (`fetch_occ_foreign_pct.txt`) after the
   six‑digit SOC has been recorded.
2. It looks up the occupation in `/occ_foreign_rate` and stores the
   `foreign_pct` in `occForeignPct`.

## 6. Survey Flow
1. In the Survey Flow, define the embedded data fields used above:
   `familySOCList`, `chosenSOC`, `automationPctile`, `stateForeignPct`,
   and `occForeignPct`.
2. Place the JavaScript snippets on the appropriate questions as noted
   and test the survey to ensure the fields populate correctly.
