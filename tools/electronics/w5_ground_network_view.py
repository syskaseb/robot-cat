"""Small projected layout aid; NEVER a collision or fit proof.

Routes are control polylines, not discretized CAD curves. Contact crosses
come from exact CAD intersections in the received checks/progress receipt.
Use this to choose a coherent space allocation before another CAD run.
"""
from pathlib import Path
import json
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]


def main():
    folder = ROOT / 'hardware/electronics/full-cat/w5-ground-network-r1'
    intent = json.loads((folder / 'intent.json').read_text(encoding='utf-8'))
    proof = folder / 'checks.json'
    complete = proof.exists()
    if not complete:
        proof = folder / 'progress.json'
    receipt = json.loads(proof.read_text(encoding='utf-8'))
    fig, axes = plt.subplots(1, 3, figsize=(18, 7))
    planes = [(0, 1, 'X', 'Y'), (0, 2, 'X', 'Z'), (1, 2, 'Y', 'Z')]
    for row in intent['routes']:
        groups = [row['middle']]
        for prefix in (row['a'], row['b']):
            if prefix is not None:
                points = []
                for e in prefix['edges']:
                    points.extend([e['start'], *([e['mid']] if 'mid' in e else []), e['end']])
                groups.append(points)
        colour = '#444444' if row['moving_route'] else {
            'W001':'#b22222', 'W003':'#fc8708', 'W060':'#2678b2', 'XA05':'#7a30b0',
            'W061':'#32964b'}.get(row['wire'], '#259dad')
        for ax, (u, v, _, _) in zip(axes, planes):
            for points in groups:
                ax.plot([p[u] for p in points], [p[v] for p in points], color=colour,
                        linewidth=1.1, alpha=.75)
            p = row['a']['point_mm']
            if not row['moving_route']:
                ax.annotate(row['wire'], (p[u], p[v]), fontsize=7,
                            xytext=(3, 3), textcoords='offset points', color=colour)
    for hit in receipt['hits']:
        if hit['category'] == 'old_ground_mount_requires_rebuild':
            continue
        b = hit['bounds_mm']
        p = [(b[i]+b[i+3])/2 for i in range(3)]
        colour = '#dd0011' if hit['category'] != 'printed_owner_requires_native_resolution' else '#b99a06'
        for ax, (u, v, _, _) in zip(axes, planes):
            ax.scatter(p[u], p[v], marker='x', s=18, linewidths=.7, c=colour, zorder=5)
    for ax, (u, v, x, y) in zip(axes, planes):
        ax.set(xlabel=x+' [mm]', ylabel=y+' [mm]')
        ax.set_aspect('equal', adjustable='datalim'); ax.grid(alpha=.2)
    count = receipt.get('route_count', receipt.get('completed_checked_routes', 0))
    fig.suptitle('Ground-network R1: control polylines, NOT geometry / fit proof\n'
                 f'{"Final" if complete else "Partial"} check: {count}/21 routes; '
                 f'{len(receipt["hits"])} contacts. Red: wire/bought; ochre: PETG. Old mounts omitted from marks.')
    fig.tight_layout(rect=(0,0,1,.91))
    output = folder / 'layout-review.png'
    fig.savefig(output, dpi=140); plt.close(fig)
    print(output, flush=True)


if __name__ == '__main__': main()
