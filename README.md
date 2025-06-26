# Labor Force Data Integration

This project implements a Qualtrics-based workflow to fetch labor force statistics from a custom API based on survey responses.

## Process Overview

1. **Collect survey data** – Respondents provide their two-digit Standard Occupational Classification (SOC) code and select their state of residence.
2. **Retrieve detailed occupations** – Using custom JavaScript in Qualtrics, the survey sends the two-digit SOC code to an API endpoint, which returns the list of six-digit SOC codes in that major SOC group. The respondent selects the appropriate occupation from this list.
3. **Fetch labor force data** – The survey makes additional API calls to retrieve the percentage of immigrants in the labor force for the selected occupation and for the respondent's state.
4. **Store in Embedded Data** – The retrieved data are saved to Qualtrics embedded data fields so they can be used later in the survey.

This pipeline allows the survey to display personalized labor force statistics to each respondent based on their occupation and location.
