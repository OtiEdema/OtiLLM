# Frozen JAIR v2.0 benchmark manifest status

The previously recorded manifest checksum
`55ffbb306cd647986d92638ba326756bc91f9de3c3dafcfcc6dcec17fd988fda`
is **superseded and must not be used for publication evaluation**.

During the first GPU smoke run, the FEVER mirror exposed its categorical label
as an integer ClassLabel id. The earlier validator checked counts and evidence
structure but did not require all references to be textual, so numeric FEVER
references passed validation and later caused the correctness scorer to fail.

The rebuild now:
- decodes FEVER ClassLabel ids to textual `SUPPORTS` / `REFUTES`;
- validates that every reference is a string;
- validates FEVER label/reference consistency;
- requires resolved FEVER evidence.

A new frozen manifest and SHA-256 will replace the superseded checksum after
the corrected GitHub Actions build passes all validation.
