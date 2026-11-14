K. pneumoniae manuscript release candidate — 14 November 2026

PURPOSE AND VERSION
This candidate preserves the current frozen metadata-analysis package and its
original preceding supplement. It identifies the supplied 12 November PDF and
Word manuscript versions by SHA-256, includes the exact latest Figure 1 image,
and records the checks completed on 14 November. The two manuscript files are
review versions and are identified here by hashes; their complete bytes are not
included in this candidate. The source repository is:
https://github.com/aaalshehre2024/klebsiella-amr-genomics

The separate 77-file original-source snapshot is tied to commit:
ce5c15154cb4eb96a149c0aec0c3ee12f69931ca
The release tag and external RELEASE_RECEIPT.json identify the exact commit
that builds this candidate. That commit is recorded outside the candidate to
avoid a self-referential archive hash.

CONTENTS
Kp_Updated_Results_Evidence_2026-11-08.zip — original current analysis archive.
Kp_Antibiotics_Supplementary_Data.zip — original historical supplement, also
present unchanged within the current archive as its preceding input package.
scientific_verification.json — fresh rerun and independent-check evidence.
reproduction_report.json — complete output-comparison report from the rerun.
manuscript_identity.json — version hashes, latest Figure 1 source cross-check,
and editorial/reproduction limits.
latest_figure/ — exact JPEG extracted from the latest DOCX, with provenance.
release_scope.json — explicit scientific and publication status.
INPUT_MANIFEST.json — ordered repository parts and original archive hash.
build_and_verify.py — deterministic builder and independent integrity verifier.
SHA256SUMS.txt — complete checksums for every other file in this candidate.

OBSERVED VERIFICATION
All 132 current-package checksums and 139 historical-supplement checksums pass.
Fresh execution reproduced 38 CSV tables byte-for-byte, four JSON summaries by
parsed equality, and four figure-source CSV tables byte-for-byte. All six
pipeline stages exited successfully. The packaged independent audit passed
218 quantitative checks against its bundled 8 November Results text, with no
detected feature/native-context conflicts. The rerun supports 17 exports,
20,341 unique versioned PDT records, 16,026 exact assembly links, and 3,114
records satisfying the defined target/virulence-marker co-detection rule.

WHAT THESE CHECKS COVER
This is a rerun of frozen metadata, linkage, and marker-analysis scripts. It
does not rerun genome assembly, Kleborate or AMRFinderPlus from raw sequences.
The 218 checks apply to the bundled Results text, not to every sentence in the
later manuscript. The preceding historical supplement passed integrity checks
and supplied inputs; its standalone historical analysis was not independently
rerun. The separate 77-file source snapshot retains its original NOT_RUN
scientific status and one known nested-ZIP warning. Its integrity pass must
not be interpreted as a scientific reproduction pass.

LATEST FIGURE 1 AND MANUSCRIPT LIMITS
The exact displayed four-panel Figure 1 was recovered unchanged from
word/media/image2.jpeg in the latest Word file. Its central panel counts and
the two triple-positive ST16 assembly links were checked against the frozen
tables and focal export. The dedicated script that recreates this four-panel
layout was not present in the inspected packages. Earlier figures are retained
inside their original archives and are not relabeled as the latest figure.
The supplied PDF retains highlighting and a review comment; the Word file
retains editorial/historical material. This is a release candidate with stated
limits and is not certification of a publication-clean final manuscript.

VERIFY A DOWNLOADED CANDIDATE
Use the retained SHA-256 in the GitHub release notes or independent build
record. Run from an extracted copy containing build_and_verify.py:

python3 build_and_verify.py verify --archive /path/to/downloaded-candidate.zip \
  --expected-sha256 THE_RECORDED_64_CHARACTER_SHA256 \
  --expected-file /path/to/retained-build.zip \
  --report /path/to/DOWNLOAD_VERIFICATION.json

The two ZIP paths must be separate files. If no retained build is available,
omit --expected-file; SHA-256, complete payload coverage, ZIP CRC, and all inner
archive checksums are still verified. Integrity verification is distinct from
scientific reproduction. Read each original archive's README.txt and
reproduce.py --help before rerunning its analysis into a separate output path.

BUILD FROM THE EXACT RELEASE COMMIT
From the repository root:

python3 release_data/2026-11-14_rc1/build_and_verify.py build \
  --repo-root . --output /path/to/new-build-directory

The builder checks every part, reconstructs the original evidence ZIP, extracts
the unchanged original supplement, and verifies complete checksum coverage.
It does not modify the frozen inputs and does not itself rerun the science.

DRAFT RELEASE STATUS
The publisher creates a draft prerelease, downloads its assets again, checks
the downloaded master ZIP against the retained build, and independently
verifies the downloaded source snapshot. Actual results and the exact release
commit are recorded in external download-verification reports and the release
receipt. No publication-ready claim follows merely from a successful upload.
