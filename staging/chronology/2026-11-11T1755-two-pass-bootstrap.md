# Two-pass bootstrap (Asia/Kolkata)

Read AGENT_PROMPT, README and SOURCE_MAP; confirmed branch staging/enmeval-nov-2026.
Initial imported-file SHA256 verification passed in full. No tracked root files changed.
Port 8175 free. Host aarch64; Docker available; Rscript absent. Chose dedicated
Ubuntu 24.04 ARM64 container, two build CPUs, single-thread numerical libraries.

The scaffold sorts BIO files lexicographically, does not persist models, has an
unfiltered background, unchecked AICc selection and success exit on failures.
These are implementation work before the Aglaia gate. No full training started.

Documentation follows ../io: timestamped chronology, dated thematic narrative,
operational docs, remaining todos and proposals. Raw evidence remains ignored.
