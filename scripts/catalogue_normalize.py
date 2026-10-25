"""A program can appear under several institutes. Keep one record per official ID."""
def normalize(programs):
    by_id={}
    for p in programs:
        institutes=p.get('institutes') or [p['institute']]
        if p['id'] not in by_id:
            by_id[p['id']]=dict(p, institutes=list(institutes))
        else:
            for name in institutes:
                if name not in by_id[p['id']]['institutes']:by_id[p['id']]['institutes'].append(name)
    return list(by_id.values())
