from argparse import ArgumentParser
from pathlib import Path
import subprocess
import re

if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('paths', type=str, nargs='*')
    args = argparser.parse_args()

    paths = args.paths
    if len(paths) < 2:
        raise RuntimeError(f'Must provide at least 2 paths as arguments')

    for i, path in enumerate(paths):
        input_path = Path(path)
        if not input_path.is_file():
            derived_path = Path(__file__).parent / input_path
            if not derived_path.is_file():
                potential_paths = '\n'.join(set([
                    f'* {input_path.parent.absolute()}',
                    f'* {derived_path.parent.absolute()}',
                ]))

                raise FileNotFoundError(f'{input_path.name} is not a file in any of\n{potential_paths}')
            paths[i] = derived_path
        else:
            paths[i] = input_path

    output_path = Path(f'{paths[0].stem}.html')
    output_path.unlink(missing_ok=True)

    vimdiff_cmd = f"vimdiff -c \"set diffopt=internal,filler,context:99999\" -c TOhtml -c \"w {output_path} | qa!\""

    posix_path_strs = [path.as_posix().replace(':', '') for path in paths]

    try:
        subprocess.run(
            ['bash', '-c', f'{vimdiff_cmd} {" ".join(posix_path_strs)}'],
            check=True,
            text=True,
        )
    except FileNotFoundError as e:
        raise FileNotFoundError('bash not found in system environment variables PATH') from e

    with open(output_path, 'r', encoding='utf-8') as html_file:
        html_str = html_file.read()

    html_str = html_str.replace(
        '<title>diff</title>',
        f'<title>{paths[0].stem}</title>',
    )

    html_str = html_str.replace(
        'pre { font-family: monospace; color: #000000; background-color: #ffffff; }',
        'pre { font-family: monospace; color: #BBBEBF; background-color: #121314; }',
    )

    html_str = html_str.replace(
        'body { font-family: monospace; color: #000000; background-color: #ffffff; }',
        'body { font-family: monospace; color: #BBBEBF; background-color: #121314; }',
    )

    html_str = html_str.replace(
        '.Folded { color: #0000c0; background-color: #a8a8a8; padding-bottom: 1px; }',
        '.Folded { color: #404040; background-color: #121314; padding-bottom: 1px; }',
    )

    html_str = html_str.replace(
        '.DiffDelete { color: #8080ff; background-color: #afffff; padding-bottom: 1px; }',
        '.DiffDelete { color: #373839; background-color: #121314; padding-bottom: 1px; }',
    )

    html_str = html_str.replace(
        '.DiffChange { background-color: #ffd7ff; padding-bottom: 1px; }',
        '.DiffChange { background-color: #221E19; padding-bottom: 1px; }',
    )

    html_str = html_str.replace(
        '.DiffText { background-color: #ff6060; padding-bottom: 1px; font-weight: bold; }',
        '.DiffText { background-color: #493F2D; padding-bottom: 1px; font-weight: bold; }',
    )

    html_str = html_str.replace(
        '.DiffAdd { background-color: #5fd7ff; padding-bottom: 1px; }',
        '.DiffAdd { background-color: #493F2D; padding-bottom: 1px; }',
    )

    html_str = html_str.replace(
        '.Identifier { color: #008080; }',
        '.Identifier { color: #D2A8FF; }',
    )

    html_str = html_str.replace(
        '.Statement { color: #af5f00; }',
        '.Statement { color: #C586C0; }',
    )

    html_str = html_str.replace(
        '.Special { color: #c000c0; }',
        '.Special { color: #D79539; }',
    )

    html_str = html_str.replace(
        '.Type { color: #008000; }',
        '.Type { color: #4EC9B0; }',
    )

    html_str = html_str.replace(
        '.PreProc { color: #c000c0; }',
        '.PreProc { color: #C586C0; }',
    )

    html_str = html_str.replace(
        '.Constant { color: #c00000; }',
        '.Constant { color: #A5D6FF; }',
    )

    html_str = html_str.replace(
        '.Comment { color: #0000c0; }',
        '.Comment { color: #8B949E; }',
    )

    html_str = html_str.replace(
        '.Error { color: #ffffff; background-color: #ff6060; padding-bottom: 1px; }',
        '.Error { color: #ff6060; background-color: #121314; padding-bottom: 1px; font-weight: bold; }',
    )

    html_strs = html_str.splitlines(True)
    for i, html_str in enumerate(html_strs):
        groups = re.match(r'(<span class="DiffDelete">)(-+)(</span>)', html_str)
        if groups is not None:
            html_strs[i] = re.sub(
                r'(<span class="DiffDelete">)(-+)(</span>)',
                f'<span class="DiffDelete">{groups.group(2).replace("-", "/")}</span>',
                html_str,
            )

    with open(output_path, 'w', encoding='utf-8') as html_file:
        html_file.writelines(html_strs)
