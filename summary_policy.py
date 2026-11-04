"""Honest hub summaries from dated sibling snapshots; no source/network access."""
REVIEWED_REFERENCES={'gathin23/cleanyourtv','harry0703/moneyprinterturbo','designfuchen/word-atlas'}

def curate(summary):
    out=dict(summary)
    top=out.get('top') or {}
    if str(top.get('name','')).casefold() in REVIEWED_REFERENCES:
        out['top']=None
        out['review_note']='A previously featured entry is now an unranked reference under inclusion review; consult the index.'
    if out.get('key')=='model':
        out['blurb']='Hugging Face models with upstream trending, download and like signals.'
    if out.get('key')=='mcp':
        out['blurb']='Model Context Protocol registry entries, with source coverage and transport details.'
        out['coverage_note']='Check source coverage on the index; this count is not proof of a complete registry.'
    return out

def summarize(snapshot,index):
    out={**index,'count':None,'top':None,'categories':[],'generated_at':snapshot.get('generated_at')}
    entries=next((snapshot[key] for key in ('items','repos','models','servers') if isinstance(snapshot.get(key),list)),[])
    eligible=[r for r in entries if str(r.get('full_name') or r.get('name') or '').casefold() not in REVIEWED_REFERENCES]
    if len(eligible)!=len(entries):
        out['review_note']='Reviewed reference entries are excluded from this ranking; consult the individual index.'
    entries=eligible
    out['count']=len(entries)
    categories=snapshot.get('categories') or []
    if isinstance(categories,dict):categories=list(categories)
    out['categories']=[c.get('name') if isinstance(c,dict) else c for c in categories][:4]
    if entries:
        first=entries[0]
        out['top']={'name':first.get('full_name') or first.get('name') or first.get('repo') or first.get('id'),
                    'momentum':first.get('momentum') if 'momentum' in first else first.get('score')}
    return curate(out)
