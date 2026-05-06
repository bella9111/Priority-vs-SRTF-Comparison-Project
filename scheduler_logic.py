# scheduler_logic.py

def avg(lst, key):
    if not lst:
        return 0
    return sum(p[key] for p in lst) / len(lst)

def detect_starvation(ps, threshold=2):
    average = avg(ps, 'wt')
    if average == 0:
        return []
    return [p['pid'] for p in ps if p['wt'] > average * threshold]

def merge_timeline(timeline):
    merged = []
    for pid, s, e in timeline:
        if merged and merged[-1][0] == pid:
            merged[-1] = (pid, merged[-1][1], e)
        else:
            merged.append((pid, s, e))
    return merged

def simulate_priority(processes):
    # Rule: lowest pr number = highest priority
    # Tie-breaking: earlier arrival time first
    ps = [dict(p, rem=p['bt'], ft=0, wt=0, tat=0, rt=-1) for p in processes]
    time, done = 0, 0
    timeline = []
    prev, prev_start = None, 0

    while done < len(ps):
        available = [p for p in ps if p['at'] <= time and p['rem'] > 0]
        if not available:
            time += 1
            continue
        available.sort(key=lambda p: (p['pr'], p['at']))
        current = available[0]
        if current['rt'] == -1:
            current['rt'] = time - current['at']
        if prev != current['pid']:
            if prev is not None:
                timeline.append((prev, prev_start, time))
            prev = current['pid']
            prev_start = time
        current['rem'] -= 1
        time += 1
        if current['rem'] == 0:
            done += 1
            current['ft'] = time
            current['tat'] = current['ft'] - current['at']
            current['wt'] = current['tat'] - current['bt']
    if prev is not None:
        timeline.append((prev, prev_start, time))
    return ps, merge_timeline(timeline)

def simulate_srtf(processes):
    # Rule: shortest remaining burst time first
    # Tie-breaking: earlier arrival time first
    ps = [dict(p, rem=p['bt'], ft=0, wt=0, tat=0, rt=-1) for p in processes]
    time, done = 0, 0
    timeline = []
    prev, prev_start = None, 0

    while done < len(ps):
        available = [p for p in ps if p['at'] <= time and p['rem'] > 0]
        if not available:
            time += 1
            continue
        available.sort(key=lambda p: (p['rem'], p['at']))
        current = available[0]
        if current['rt'] == -1:
            current['rt'] = time - current['at']
        if prev != current['pid']:
            if prev is not None:
                timeline.append((prev, prev_start, time))
            prev = current['pid']
            prev_start = time
        current['rem'] -= 1
        time += 1
        if current['rem'] == 0:
            done += 1
            current['ft'] = time
            current['tat'] = current['ft'] - current['at']
            current['wt'] = current['tat'] - current['bt']
    if prev is not None:
        timeline.append((prev, prev_start, time))
    return ps, merge_timeline(timeline)

def generate_comparison(pri_ps, srtf_ps):
    p_awt = avg(pri_ps, 'wt')
    s_awt = avg(srtf_ps, 'wt')
    p_atat = avg(pri_ps, 'tat')
    s_atat = avg(srtf_ps, 'tat')
    p_art = avg(pri_ps, 'rt')
    s_art = avg(srtf_ps, 'rt')

    p_starved = detect_starvation(pri_ps)
    s_starved = detect_starvation(srtf_ps)

    lines = []
    lines.append("=" * 52)
    lines.append("         COMPARISON SUMMARY")
    lines.append("=" * 52)
    lines.append(f"{'Metric':<28} {'Priority':>10} {'SRTF':>10}")
    lines.append("-" * 52)
    lines.append(f"{'Avg Waiting Time':<28} {p_awt:>10.2f} {s_awt:>10.2f}  {'<< SRTF wins' if s_awt < p_awt else '<< Priority wins' if p_awt < s_awt else '  TIE'}")
    lines.append(f"{'Avg Turnaround Time':<28} {p_atat:>10.2f} {s_atat:>10.2f}  {'<< SRTF wins' if s_atat < p_atat else '<< Priority wins' if p_atat < s_atat else '  TIE'}")
    lines.append(f"{'Avg Response Time':<28} {p_art:>10.2f} {s_art:>10.2f}  {'<< SRTF wins' if s_art < p_art else '<< Priority wins' if p_art < s_art else '  TIE'}")
    lines.append("-" * 52)

    lines.append("")
    lines.append("  ANALYSIS QUESTIONS")
    lines.append("-" * 52)

    if s_awt < p_awt:
        lines.append(f"[Q1] SRTF produced lower avg waiting time ({s_awt:.2f} vs {p_awt:.2f}).")
    elif p_awt < s_awt:
        lines.append(f"[Q1] Priority produced lower avg waiting time ({p_awt:.2f} vs {s_awt:.2f}).")
    else:
        lines.append(f"[Q1] Both algorithms tied in avg waiting time ({p_awt:.2f}).")

    if s_art < p_art:
        lines.append(f"[Q2] SRTF produced lower avg response time ({s_art:.2f} vs {p_art:.2f}).")
    else:
        lines.append(f"[Q2] Priority produced lower avg response time ({p_art:.2f} vs {s_art:.2f}).")

    high_pri = [p for p in pri_ps if p['pr'] == min(x['pr'] for x in pri_ps)]
    if high_pri and high_pri[0]['rt'] < avg(pri_ps, 'rt'):
        lines.append("[Q3] Priority values DID improve treatment of urgent processes (lower RT for high-priority).")
    else:
        lines.append("[Q3] Priority values did NOT significantly improve urgent process response time.")

    short_jobs = sorted(srtf_ps, key=lambda p: p['bt'])
    if short_jobs and short_jobs[0]['wt'] < avg(srtf_ps, 'wt'):
        lines.append("[Q4] SRTF DID favor short jobs more aggressively (short jobs had below-avg WT).")
    else:
        lines.append("[Q4] SRTF did not show strong favoritism toward short jobs in this workload.")

    if s_awt < p_awt:
        lines.append("[Q5] RECOMMENDATION: SRTF is better for this workload (lower avg WT).")
    else:
        lines.append("[Q5] RECOMMENDATION: Priority Scheduling is better for this workload.")

    # Q6 Short low-priority job in Priority
    if pri_ps:
        max_pr   = max(p['pr'] for p in pri_ps)
        avg_bt_p = avg(pri_ps, 'bt')
        short_low = [p for p in pri_ps if p['bt'] <= avg_bt_p and p['pr'] == max_pr]
        if short_low:
            lines.append(f"[Q6] Short low-priority jobs waited avg {avg(short_low, 'wt'):.2f} in Priority — delayed despite short burst.")
        else:
            lines.append("[Q6] No short low-priority jobs found in this workload.")

    # Q7 Long high-priority job in SRTF
    if srtf_ps:
        min_pr   = min(p['pr'] for p in srtf_ps)
        avg_bt_s = avg(srtf_ps, 'bt')
        long_urgent = [p for p in srtf_ps if p['bt'] >= avg_bt_s and p['pr'] == min_pr]
        if long_urgent:
            lines.append(f"[Q7] Long high-priority jobs waited avg {avg(long_urgent, 'wt'):.2f} in SRTF — priority was ignored.")
        else:
            lines.append("[Q7] No long high-priority jobs found in this workload.")

    lines.append("")
    lines.append("  STARVATION ANALYSIS")
    lines.append("-" * 52)
    if p_starved:
        lines.append(f"  Priority: Starvation risk detected for: {', '.join(p_starved)}")
    else:
        lines.append("  Priority: No significant starvation detected.")
    if s_starved:
        lines.append(f"  SRTF:     Starvation risk detected for: {', '.join(s_starved)}")
    else:
        lines.append("  SRTF:     No significant starvation detected.")

    lines.append("")
    lines.append("=" * 52)
    lines.append("         FINAL CONCLUSION")
    lines.append("=" * 52)

    if s_awt <= p_awt and s_atat <= p_atat:
        winner = "SRTF"
        loser = "Priority Scheduling"
    elif p_awt <= s_awt and p_atat <= s_atat:
        winner = "Priority Scheduling"
        loser = "SRTF"
    else:
        winner = "Mixed results"
        loser = "both"

    if winner != "Mixed results":
        lines.append(f"  WINNER: {winner}")
        lines.append(f"  {winner} performed better on WT and TAT metrics.")
        lines.append(f"  {loser} had higher average delays overall.")
    else:
        lines.append("  WINNER: Mixed — each algorithm excelled on different metrics.")

    lines.append("")
    lines.append("  TRADE-OFFS OBSERVED:")
    lines.append("  - Priority ensures urgent tasks run first, but may starve")
    lines.append("    low-priority processes in heavy workloads.")
    lines.append("  - SRTF minimizes waiting time globally but ignores priority,")
    lines.append("    meaning urgent long jobs can be delayed by short ones.")
    lines.append("")
    lines.append("  FAIRNESS:")
    if p_starved and not s_starved:
        lines.append("  SRTF appeared fairer — no starvation detected.")
    elif s_starved and not p_starved:
        lines.append("  Priority appeared fairer — no starvation detected.")
    else:
        lines.append("  Both algorithms showed similar fairness for this workload.")

    lines.append("=" * 52)
    return "\n".join(lines)
