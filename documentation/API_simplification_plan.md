# API Simplification Plan

This note outlines a few ideas to streamline the current API while maintaining compatibility with the existing Qualtrics workflow.

## 1. Consolidate Lookup Endpoints

The survey uses multiple endpoints to fetch foreign-born labor force shares, automation percentiles and SOC code lists. Combining these into a single endpoint would cut down on round trips. For example:

```http
GET /lookup?soc=<6-digit>&state=<abbr>&major=<2-digit>
```

The response could bundle all needed fields:

```json
{
  "automation_pctile": 52,
  "state_foreign_pct": 27.2,
  "occ_foreign_pct": 28.6,
  "family_soc": [{"code": "15-1232", "label": "Software Developers"}, ...]
}
```

## 2. Reduce Data Volume

For the 6-digit SOC list retrieval, the API currently returns full occupation descriptions. Trimming the payload to only include the label and code reduces client-side processing. Descriptions or synonyms could be requested separately only when needed.

## 3. Consistent Field Names

Use short and predictable JSON keys (`state_foreign_pct`, `automation_pctile` etc.) so Qualtrics JavaScript has minimal transformation logic. This also makes debugging easier.

## 4. Versioning and Defaults

Introduce an API version prefix (`/v1/`) and provide sensible default values if optional parameters are omitted. This allows new features without breaking the Qualtrics integration.

## 5. Qualtrics-Friendly Errors

Return concise error messages in a consistent structure. Qualtrics JavaScript can then surface a user-friendly alert when something goes wrong:

```json
{ "error": "unknown_state" }
```

Keeping the API small and well-documented ensures that the Qualtrics survey remains simple to maintain while still delivering all necessary data to respondents.
