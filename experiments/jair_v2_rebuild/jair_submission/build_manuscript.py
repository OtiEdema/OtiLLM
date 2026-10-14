"""Build the actual manuscript with supplied frozen assets and record provenance.

Run from any directory. Does not run model inference or replace frozen results.
The output directory must be new, preventing a stale PDF from passing as a build.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REBUILD = HERE.parent
KIT = ('jair.cls', 'acmart.cls', 'acmdatamodel.dbx', 'acmauthoryear.bbx', 'acmauthoryear.cbx')
TABLES = ('Table_1_systems_and_controls.csv', 'Table_2_benchmark_composition.csv',
          'Table_3_clean_content_macro.csv', 'Table_4_selective_faithfulness.csv',
          'Table_5_selective_factuality.csv', 'Table_6_xstest_policy.csv')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--asset-dir', type=Path, required=True)
    p.add_argument('--kit-dir', type=Path, required=True)
    p.add_argument('--out-dir', type=Path, required=True)
    args = p.parse_args()
    assets, kit, out = (x.resolve() for x in (args.asset_dir, args.kit_dir, args.out_dir))
    required = [kit / x for x in KIT] + [assets / 'tables' / x for x in TABLES]
    missing = [str(x) for x in required if not x.is_file()]
    if missing:
        p.error('Missing required inputs:\n' + '\n'.join(missing))
    if out.exists():
        p.error('--out-dir must not exist; select a new build directory.')
    for exe in ('pdflatex', 'biber'):
        if not shutil.which(exe):
            p.error(f'Required executable unavailable: {exe}')
    out.mkdir(parents=True)
    (out / 'figures').mkdir()
    for name in KIT:
        shutil.copy2(kit / name, out / name)
    for name in ('main.tex', 'references.bib'):
        shutil.copy2(HERE / name, out / name)
    # Regenerate diagrams, independent of numerical result assets.
    sys.path.insert(0, str(REBUILD))
    from generate_final_publication_assets import (figure_architecture, figure_pipeline,
        selective_tradeoff, figure_xstest, read_csv, SYSTEM_LABELS)
    figure_architecture(out / 'figures')
    figure_pipeline(out / 'figures')
    # The publication CSVs preserve the paired summary values; map their field
    # names back to plotting inputs without rounding or estimating new results.
    system_ids = {label: key for key, label in SYSTEM_LABELS.items()}
    for filename, metric, output in (
        ('Table_4_selective_faithfulness.csv', 'Candidate-pool support',
         'Figure_3_coverage_selective_faithfulness'),
        ('Table_5_selective_factuality.csv', 'Reference NLI proxy',
         'Figure_4_coverage_selective_factuality'),
    ):
        plot_rows = [{
            'condition': row['condition'],
            'baseline': system_ids[row['baseline']],
            'target_mean': row['otillm_mean'],
            'target_coverage': row['otillm_coverage'],
            'baseline_mean_on_target_answered_subset': row['baseline_mean_on_same_items'],
        } for row in read_csv(assets / 'tables' / filename)]
        selective_tradeoff(plot_rows, metric, output, out / 'figures')
    policy_rows = [{**row, 'baseline': system_ids[row['baseline']],
                    'target_mean': row['otillm_mean']}
                   for row in read_csv(assets / 'tables' / 'Table_6_xstest_policy.csv')]
    figure_xstest(policy_rows, out / 'figures')
    subprocess.run([sys.executable, str(HERE / 'generate_latex_tables.py'),
                    '--asset-dir', str(assets), '--out-dir', str(out / 'tables')], check=True)
    commands = [['pdflatex', '-halt-on-error', '-interaction=nonstopmode', 'main.tex'],
                ['biber', 'main'],
                ['pdflatex', '-halt-on-error', '-interaction=nonstopmode', 'main.tex'],
                ['pdflatex', '-halt-on-error', '-interaction=nonstopmode', 'main.tex']]
    with (out / 'build-output.txt').open('w') as log:
        for command in commands:
            subprocess.run(command, cwd=out, stdout=log, stderr=subprocess.STDOUT, check=True)
    log_text = (out / 'main.log').read_text(errors='replace')
    bad = re.findall(r'^.*(?:Overfull|LaTeX Error|Class .* Error|undefined|Empty bibliography).*$',
                     log_text, re.MULTILINE)
    if bad:
        raise RuntimeError('Build requires correction:\n' + '\n'.join(bad))
    if not (out / 'main.bbl').is_file() or not (out / 'main.pdf').is_file():
        raise RuntimeError('PDF or compiled bibliography missing')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=HERE, text=True).strip()
    status = subprocess.check_output(['git', 'status', '--porcelain'], cwd=HERE, text=True)
    inputs = required + [HERE / 'main.tex', HERE / 'references.bib',
                         HERE / 'generate_latex_tables.py', REBUILD / 'generate_final_publication_assets.py']
    record = {'git_commit': head, 'working_tree_dirty': bool(status.strip()),
              'input_sha256': {str(x): sha(x) for x in inputs},
              'pdf_sha256': sha(out / 'main.pdf'), 'visual_review': 'pending',
              'note': 'Compilation is not scientific validation or visual approval.'}
    (out / 'build-provenance.json').write_text(json.dumps(record, indent=2) + '\n')
    print(f'Built {out / "main.pdf"}; page-by-page visual review remains required.')


if __name__ == '__main__':
    main()
