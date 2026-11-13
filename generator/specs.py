import re, json
SRC = 'Idea from Julien Bek, Sequoia: “Services: The New Software” (5 Mar 2026). Our own words.'

def chunks(prompt, n=3):
    sents = re.split(r'(?<=[.!?])\s+', prompt.strip())
    total = len(prompt)
    out, cur = [], ''
    for s in sents:
        if cur and len(cur) + len(s) > total / n * 1.05 and len(out) < n - 1:
            out.append(cur.strip()); cur = ''
        cur += s + ' '
    out.append(cur.strip())
    return out

SPECS = {
 # ---------- 012: standard format, descriptive hook (pacing + first-frame test) ----------
 '012': dict(vno='VAULT NO. 012', mode='std', vault='012',
   hook='Messy event notes in. A minute-by-minute plan out.',
   proof=dict(app='RunSheet', rows=[['14:00','Florist setup'],['15:30','Guests arrive'],['16:00','⚠ Clash: band + photographer']], result='One plan for every vendor'),
   prob_head='Event plans live in too many places.',
   points=['Timings sit across emails, chats and vendor contracts.','Building the run sheet by hand takes hours.','One missed handover can ruin the day.'],
   idea='An AI run sheet builder for event planners.', idea_sub='Messy notes in. Minute-by-minute plan out.',
   stack=['Bolt','Supabase','Claude API','Stripe'], tool='Bolt',
   steps=[['Paste the details'],['AI builds the sheet'],['Share with the team']],
   step_rows=[['Paste details','Venue, timings, vendors'],['AI builds the sheet','Owners + clash warnings'],['Share with the team','Live link + PDF']],
   who='Freelance event and wedding planners and small venues.',
   tiers=[['Single event','$39/event'],['10-pack','$249/pack']]),
 # ---------- 001 A/B ----------
 '001a': dict(vno='VAULT NO. 001', mode='std', vault='001', test='A: beskrivende hook',
   hook='Photo in. Professional quote out.',
   proof=dict(app='QuoteSnap', rows=[['Fit new sockets','Materials + hours'],['Make good plaster','Included'],['Total','Ready to send']], result='A branded quote, one tap'),
   prob_head='Great at the job. Slow at the paperwork.',
   points=['Quotes get written at night, after a full day on site.','Slow replies mean the customer books someone else.','Messy quotes make a skilled pro look small.'],
   idea='An AI quote builder for tradespeople.', idea_sub='Photo in. Professional quote out.',
   stack=['Lovable','Supabase','Claude API','Stripe','Resend'], tool='Lovable',
   step_rows=[['Snap and talk','Photos + a voice note'],['AI drafts the quote','From your own price list'],['Review and send','Customer accepts in one click']],
   who='Small trade firms: electricians, plumbers, painters, carpenters.',
   tiers=[['Solo','$29/mo'],['Team','$79/mo']]),
 '001b': dict(vno='VAULT NO. 001', mode='std', vault='001', test='B: dristig påstand',
   hook='Stop writing quotes at night. Let the photos do it.',
   proof=dict(app='QuoteSnap', rows=[['Fit new sockets','Materials + hours'],['Make good plaster','Included'],['Total','Ready to send']], result='A branded quote, one tap'),
   prob_head='Great at the job. Slow at the paperwork.',
   points=['Quotes get written at night, after a full day on site.','Slow replies mean the customer books someone else.','Messy quotes make a skilled pro look small.'],
   idea='An AI quote builder for tradespeople.', idea_sub='Photo in. Professional quote out.',
   stack=['Lovable','Supabase','Claude API','Stripe','Resend'], tool='Lovable',
   step_rows=[['Snap and talk','Photos + a voice note'],['AI drafts the quote','From your own price list'],['Review and send','Customer accepts in one click']],
   who='Small trade firms: electricians, plumbers, painters, carpenters.',
   tiers=[['Solo','$29/mo'],['Team','$79/mo']]),
 # ---------- Sell the job, not the tool ----------
 'sj005': dict(vno='SELL THE JOB · 1/3', mode='job', vault='005',
   hook="Freelancers don't want an invoice tool. They want to get paid.",
   proof=dict(app='PaidOnTime', rows=[['Studio Nord','Reminder 1 sent'],['Studio Nord','Reminder 2 scheduled'],['Studio Nord','Paid ✓']], result='Paid. Chase stopped.'),
   versus=['An invoice tool.','Getting paid.'],
   prob_head='Sell the job, not the tool.',
   points=['Freelancers put off awkward payment reminders.','Late payments quietly break their cash flow.','The tool is a cost. Getting paid is the job.'],
   idea='Priced by the job: an invoice paid.', idea_sub='Same build. A different pitch.',
   stack=['Lovable','Supabase','Claude API','Resend','Stripe'], tool='Lovable',
   prompt='Build a web app called PaidOnTime for freelancers. Users add an invoice with client, email, amount, due date and tone. Send the details to the Claude API to write four reminders that move from friendly to firm, and schedule them with Resend. Every email carries a Stripe payment link, and the sequence stops when the invoice is paid. Show open, late and paid invoices on one dashboard. Charge a small fee per invoice that gets paid, with a free tier for the first invoices.',
   step_rows=[['Add the invoice','Client, amount, due date'],['AI chases politely','Friendly, then firm'],['Client pays','Pay link in every email']],
   who='Freelance designers, developers, writers and consultants.',
   tiers=[['Per paid invoice','$3/paid'],['Studio plan','$29/mo']], source=True),
 'sj006': dict(vno='SELL THE JOB · 2/3', mode='job', vault='006',
   hook="Landlords don't want a repair desk. They want repairs handled.",
   proof=dict(app='FixDesk', rows=[['Leaking tap, flat B','Urgent'],['Work order','Sent to plumber'],['Status','Fixed ✓']], result='Fixed. No late-night texts.'),
   versus=['A repair request desk.','Repairs handled.'],
   prob_head='Sell the job, not the tool.',
   points=['Repair requests come in by text, call and email.','Urgent and cosmetic issues look the same at first.','The tool is a cost. A fixed leak is the job.'],
   idea='Priced by the job: a repair closed.', idea_sub='Same build. A different pitch.',
   stack=['Lovable','Supabase','Claude API','Stripe'], tool='Lovable',
   prompt='Build a web app called FixDesk for small landlords. Each property gets a public repair form where tenants upload photos and describe the problem. Send each request to the Claude API to return a category, an urgency level and follow-up questions for the tenant. Turn a request into a work order email to a saved contractor with photos, address and access notes in one click. Track every job from reported to fixed. Charge a small fee per repair that gets closed.',
   step_rows=[['Tenant reports it','Photos + a short note'],['AI sorts it','Category and urgency'],['Contractor gets it','A clear work order']],
   who='Private landlords and small property managers.',
   tiers=[['Per repair closed','$4/repair'],['Portfolio plan','$49/mo']], source=True),
 'sj008': dict(vno='SELL THE JOB · 3/3', mode='job', vault='008',
   hook="Hotels don't want a guest inbox. They want guests answered.",
   proof=dict(app='GuestDesk', rows=[['Parking?','Reply drafted · EN'],['Frühstück?','Reply drafted · DE'],['Status','Sent ✓']], result='Every guest answered.'),
   versus=['A guest inbox.','Guests answered.'],
   prob_head='Sell the job, not the tool.',
   points=['Small hotels answer the same questions every day.','Guests write in their own language and expect fast replies.','The tool is a cost. A happy guest is the job.'],
   idea='Priced by the job: a guest answered.', idea_sub='Same build. A different pitch.',
   stack=['Lovable','Supabase','Claude API','Make','Stripe'], tool='Lovable',
   prompt='Build a web app called GuestDesk for small hotels. Owners fill in a knowledge base with rooms, house rules, directions, breakfast times and local tips. Guest emails are forwarded in through Make. For each email, send the message and the knowledge base to the Claude API to detect the language and draft a reply in that language and the owner\'s tone. Let the owner approve with one click and flag questions it could not answer. Charge a small fee per guest message answered.',
   step_rows=[['Teach it the house','Rooms, rules, tips'],['Guest writes in','Any language'],['Approve and send','Reply in their language']],
   who='Owners of small hotels, B&Bs and guesthouses.',
   tiers=[['Per guest answered','$0.50/reply'],['Hotel plan','$69/mo']], source=True),
}

def build(spec, idea):
    """Return REEL dict with beats (36 s)."""
    prompt = spec.get('prompt') or idea['build_prompt']
    ch = chunks(prompt, 3)
    tool = spec['tool']
    rows = spec['step_rows']
    B = []
    def add(s, e, k, **kw): B.append(dict(s=s, e=e, k=k, **kw))
    if spec['mode'] == 'std':
        add(0, 2.8, 'hook', text=spec['hook'])
        add(2.8, 4.6, 'line', eyebrow='The problem', text=spec['prob_head'])
        for i, (a, b) in enumerate([(4.6, 6.2), (6.2, 7.8), (7.8, 9.4)]):
            add(a, b, 'line', eyebrow='0%d' % (i + 1), text=spec['points'][i])
        add(9.4, 11.6, 'line', eyebrow='The idea', text=spec['idea'], sub=spec['idea_sub'])
        add(11.6, 13.0, 'stack', items=spec['stack'])
        t0 = 13.0
        for i in range(3):
            add(t0 + i * 2.4, t0 + (i + 1) * 2.4, 'prompt', text=ch[i], label='Paste into %s · %d/3' % (tool, i + 1))
        add(20.2, 21.7, 'phone', eyebrow='Step 1', rows=rows, upto=1, showRes=False)
        add(21.7, 23.2, 'phone', eyebrow='Step 2', rows=rows, upto=2, showRes=False)
        add(23.2, 24.7, 'phone', eyebrow='Step 3', rows=rows, upto=3, showRes=False)
        add(24.7, 26.2, 'phone', eyebrow='Result', rows=rows, upto=3, showRes=True)
        add(26.2, 29.0, 'cover', text=spec['hook'])
        add(29.0, 30.4, 'line', eyebrow='Who pays', text=spec['who'])
        add(30.4, 33.0, 'price', tiers=spec['tiers'])
        add(33.0, 36.0, 'cta')
    else:  # job
        add(0, 2.8, 'hook', text=spec['hook'])
        add(2.8, 4.8, 'versus', a=spec['versus'][0], b=spec['versus'][1])
        add(4.8, 6.4, 'line', eyebrow='The shift', text=spec['prob_head'])
        for i, (a, b) in enumerate([(6.4, 8.0), (8.0, 9.6), (9.6, 11.2)]):
            add(a, b, 'line', eyebrow='0%d' % (i + 1), text=spec['points'][i])
        add(11.2, 13.2, 'line', eyebrow='The pitch', text=spec['idea'], sub=spec['idea_sub'])
        add(13.2, 14.6, 'stack', items=spec['stack'])
        t0 = 14.6
        for i in range(3):
            add(t0 + i * 2.4, t0 + (i + 1) * 2.4, 'prompt', text=ch[i], label='Paste into %s · %d/3' % (tool, i + 1))
        add(21.8, 23.2, 'phone', eyebrow='Step 1', rows=rows, upto=1, showRes=False)
        add(23.2, 24.6, 'phone', eyebrow='Step 2', rows=rows, upto=2, showRes=False)
        add(24.6, 26.0, 'phone', eyebrow='Step 3', rows=rows, upto=3, showRes=True)
        add(26.0, 29.0, 'cover', text=spec['hook'])
        add(29.0, 30.4, 'line', eyebrow='Who pays', text=spec['who'])
        add(30.4, 33.0, 'price', eyebrow='Paid by the job', tiers=spec['tiers'])
        add(33.0, 36.0, 'cta', source=SRC, main='Save this reel<br>for the build prompt.')
    # sanity: cover frame (26.6 s) must be a cover/hook beat
    cov = [b for b in B if b['s'] <= 26.6 < b['e']][0]
    assert cov['k'] == 'cover', cov
    # step labels fix: for 'phone' beats rows are lists; proof rows reuse step rows in the phone
    return dict(vno=spec['vno'], proof=dict(app=spec['proof']['app'], rows=spec['proof']['rows'], result=spec['proof']['result']), beats=B)
