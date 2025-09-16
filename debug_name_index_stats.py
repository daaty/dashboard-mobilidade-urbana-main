import json, re
from collections import defaultdict, Counter
from sqlalchemy.future import select
from app.database.db import SessionLocal
from app.models.rides_data import RidesData

# Heurística simples para 'nome de pessoa'
def looks_like_person_name(x):
    if not x: return False
    s = str(x).strip()
    # avoid numeric ids and short tokens
    if len(s) < 4: return False
    if re.fullmatch(r"\d+", s): return False
    # require at least one space (first + last name) or capitalized word
    if ' ' in s and re.search(r"[A-Za-zÀ-ú]", s):
        return True
    # fallback: capitalized single word longer than 5
    if re.match(r"^[A-ZÀ-Ý][a-zà-ÿ]{4,}$", s):
        return True
    return False

async def gather():
    async with SessionLocal() as session:
        result = await session.execute(select(RidesData))
        rides = result.scalars().all()

    stats = defaultdict(Counter)
    samples = defaultdict(list)
    for r in rides[-1000:]:
        ride_data = r.ride_data
        if isinstance(ride_data, str):
            try:
                ride_data = json.loads(ride_data)
            except Exception:
                continue
        table = ride_data.get('tableName','').strip()
        new_records = ride_data.get('newRecords', [])
        for rec in new_records:
            for idx, val in enumerate(rec[:20]):
                if looks_like_person_name(val):
                    stats[table][idx] += 1
                    if len(samples[table])<5:
                        samples[table].append((idx, val))
    # print summary
    for table, counter in stats.items():
        if not counter: continue
        top = counter.most_common()
        print('\nTable:', table)
        print('Top indices with person-like values:')
        for idx, cnt in top[:6]:
            print(f'  idx {idx}: {cnt} hits')
        print('Examples:')
        for idx, val in samples.get(table,[]):
            print(f'  idx {idx} -> {val}')

import asyncio
asyncio.run(gather())
