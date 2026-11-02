# Submission readiness — decision gates

Engineering/audit preparation is not scientific approval.

| Requirement | Current state | Evidence to close |
|---|---|---|
| All 34 upload events hashed and duplicate reuploads identified | COMPLETE | upload_registry.csv and manifest |
| Selected output tables and overlaps audited | COMPLETE | Combined audit and working tables |
| Reproducible audit code and local tests | COMPLETE | 13 synthetic tests, TEST_REPORT.txt |
| GitHub-hosted test execution | CHECK ACTIONS | Workflow result for exact commit; do not infer from local tests |
| Corrupt M_K5 result archive | BLOCKED | Newly tested readable archive/full tables |
| 57 named technical unresolved inputs | BLOCKED | Safe-path reruns or individually justified outcomes |
| 610 full main/hAMR and 548 hAMR | BLOCKED | Recover outputs or lock narrower eligibility |
| M_K1 three unidentified omissions / M_K2 upstream ZIP | REVIEW | Named input manifest and archive decision |
| Snapshot .7 versus .12 reconciliation | BLOCKED | Final version rule; no double counting |
| Extended collection identities and tree mapping | BLOCKED | Frozen metadata and accession–PDT–PDS–tree crosswalk |
| Assembly aliases / GCA-GCF correspondence | REVIEW | Verified source correspondence and counting rule |
| Kleborate/dependency/database environment | REVIEW | Original version exports, database fingerprints and dates |
| Marker interpretation and convergence definitions | NOT FINAL | Version-specific rules, explicit uncertain/partial-hit handling |
| Statistical/figure pipeline and sensitivity analyses | NOT RUN HERE | Executed scripts and reviewed table/figure sources |
| Code/data license and contributor approval | AUTHOR DECISION | Approved terms and author metadata |
| DOI and immutable manuscript release | NOT CREATED | Versioned final deposit after scientific approval |
| Data Availability and AI-use disclosures | DRAFT REQUIRED | Accurate repository/data access and assistance statements |

MDPI requires a Data Availability Statement and encourages sharing the minimal data/code supporting the central findings. Do not use “No new data were created or analyzed” for this secondary analysis. Document the assistance actually used and retain author responsibility for code, references and interpretation. See https://www.mdpi.com/ethics . Journal-specific submission forms and instructions must be checked at submission.
