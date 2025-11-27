# website briefing

*Source: website_briefing.pdf*

## Page 1

Mentalyc  —  Website  Briefing  (2–3  pages)  
1)  One-liner  &  Positioning  
Mentalyc  is  an  AI-powered  documentation  assistant  for  mental-health  providers  that  turns  
recorded
 
or
 
dictated
 
sessions
 
into
 
accurate,
 
compliant
 
clinical
 
notes
 
(SOAP,
 
DAP,
 
BIRP,
 
PIRP)
 
and
 
treatment
 
plans,
 
with
 
export
 
to
 
EHRs
 
via
 
FHIR.
 
It
 
reduces
 
admin
 
time,
 
strengthens
 
the
 
Golden
 
Thread
 
from
 
goals
 
→
 
progress
 
→
 
plan
 
updates,
 
and
 
meets
 
HIPAA/GDPR/Israel
 
PPL
 
requirements
 
with
 
region-aware
 
data
 
residency.
 
Audience:  solo  clinicians,  group  practices,  telehealth  networks,  behavioral  health  systems;  
IT/security
 
buyers;
 
payers/partners.
 
 
Category:
 
Clinical
 
documentation
 
&
 
assistive
 
AI
 
for
 
behavioral
 
health.
 
 
2)  Why  Mentalyc  (Outcomes,  not  features)  
●  Win  back  6–10  hours/week  per  clinician.  Faster  notes;  fewer  late-night  write-ups.  
 ●  Fewer  denials,  clearer  reimbursement.  Payer-aligned  templates;  defensible  language;  
evidence-linked
 
plans.
 
 ●  Higher  clinical  quality.  Risk  language  flagged  with  source  quotes;  measurable  progress  
tracking.
 
 ●  Enterprise  peace  of  mind.  PHI  redaction,  immutable  audit,  BAAs/DPAs,  data  residency  
controls.
 
 
Proof  points  to  highlight  on  site:  
●  Avg.  note  turnaround  time  ↓  60–80%  
 ●  Template  completeness  ≥  95%  
 ●  STT  WER  <  10%  (clean  audio);  PHI  recall  >  95%  
 ●  Clinician  satisfaction  ≥  4.0/5  by  week  two  
 

---

## Page 2

 
3)  What  It  Does  (Feature  Pillars)  
A.  Capture  &  Transcribe  
●  Capture  anywhere:  mobile  (Android/iOS),  desktop  (Windows/macOS),  or  upload  
audio/video.
 
 ●  High-quality  transcription:  cloud  STT  (Azure  Whisper,  Google  STT),  with  offline  
fallback
 
on
 
desktop
 
(Vosk/Picovoice).
 
 ●  Smart  cleanup:  punctuation,  diarization  (Clinician  /  Client),  filler  removal  without  
changing
 
meaning.
 
 
B.  PHI  Redaction  &  Privacy  
●  PHI  detection:  HIPAA’s  18  identifier  classes  via  rules  +  ML;  replace  in  working  
transcripts
 
and
 
logs.
 
 ●  Guardrails:  no  model  training  on  PHI  unless  opt-in;  content  filters;  DLP  on  logs;  
short-TTL
 
access
 
tokens.
 
 
C.  Notes  &  Plans  (The  Golden  Thread)  
●  Instant  drafts:  SOAP,  DAP,  BIRP,  PIRP  with  payer-friendly  phrasing.  
 ●  Golden  Thread:  links  today’s  content  to  diagnosis,  goals,  and  measurable  objectives;  
tracks
 
progress
 
over
 
time.
 
 ●  Risk  flags:  high-recall  detection  for  SI/HI/abuse,  with  evidence  quotes  and  suggested  
documentation
 
language.
 
 ●  Clinician  in  the  loop:  quick  review,  edit,  approve;  style  and  tone  preferences.  
 
D.  Templates  &  Customization  
●  Modality  libraries:  CBT,  EMDR,  play  therapy,  family  sessions;  editable  JSON  schemas.  
 

---

## Page 3

●  Org  policy  &  style:  required  fields,  length  guidance,  redaction  rules;  versioned  at  
org/department
 
level.
 
 ●  Multilingual  workflows:  EN/ES/HE;  translate  or  normalize  idioms  to  clinical  language.  
 
E.  Export,  Integrations  &  Analytics  
●  EHR  export:  FHIR  R4  (Composition,  DocumentReference),  PDF/DOCX,  secure  
webhooks.
 
 ●  APIs:  REST  +  FHIR  endpoints  for  partners  and  internal  tools.  
 ●  Ops  analytics:  turnaround  times,  WER,  PHI  precision/recall,  adoption  and  quality  
dashboards.
 
 
 
4)  How  It  Works  (At  a  Glance)  
1.  Record  or  upload  the  session  from  phone  or  desktop.  
 2.  Transcribe  in  the  cloud  (or  offline  on  desktop  as  needed).  
 3.  Redact  PHI  (rules  +  ML)  before  LLM  drafting  and  storage.  
 4.  Draft  note  (SOAP/DAP/BIRP)  and  link  to  goals  (Golden  Thread).  
 5.  Flag  risk  and  suggest  documentation  with  citations.  
 6.  Clinician  reviews  and  approves.  
 7.  Export  to  EHR  (FHIR)  and  store  immutable  audit  trail .  
 
Architecture  (for  IT):  cloud  functions/containers  for  STT→Redact→LLM→Checks→Export;  
tenant-scoped
 
keys;
 
object
 
storage
 
with
 
lifecycle
 
policies;
 
OpenTelemetry
 
logging;
 
WORM
 
audit.
 
 
5)  Security,  Privacy  &  Compliance  

---

## Page 4

●  HIPAA:  BAAs,  encryption  in  transit  (TLS  1.2+)  and  at  rest  (AES-256).  
 ●  GDPR:  DPAs,  SCCs/BCRs  as  applicable;  data  subject  rights  workflows.  
 ●  Israel  PPL:  regional  hosting  option  (e.g.,  me-west1)  and  residency  controls.  
 ●  Data  residency:  pin  tenants  to  US/EU/IL  regions;  no  cross-border  transfer  without  lawful  
basis
 
and
 
contracts.
 
 ●  Zero-retention  model  options:  LLM  providers  configured  for  no  training  on  your  data;  
redacted
 
logs.
 
 ●  Audit  &  access:  immutable  audit  logs;  privileged  access  monitoring;  periodic  access  
reviews.
 
 
 
6)  Who  Uses  It  (Personas  &  Use  Cases)  
●  Solo/Group  Practice  Clinicians:  cut  documentation  time,  standardize  notes,  maintain  
compliance.
 
 ●  Clinical  Directors:  enforce  templates,  reduce  denials,  improve  quality  and  supervision.  
 ●  Health  System  IT/Sec:  regional  hosting,  SSO  (OIDC),  device  policies,  APIs,  auditing.  
 ●  Telehealth  Networks:  consistent  notes  across  distributed  teams;  low-friction  
onboarding.
 
 
Common  scenarios:  individual,  family/group,  intake/discharge,  progress  notes,  risk/incident  
documentation,
 
supervision
 
summaries.
 
 
7)  Implementation  &  Onboarding  
●  Week  0–1:  Tenant  setup,  SSO,  data  residency,  consent  flows;  pilot  with  5–20  clinicians.  
 ●  Week  2–3:  Template  tuning,  prompt  preferences,  export  to  test  EHR.  
 

---

## Page 5

●  Week  4+:  Scale  to  departments;  enable  analytics  and  policy  enforcement.  
 
Minimum  tech:  modern  browser;  desktop  app  optional  for  offline;  Android/iOS  for  mobile  
capture;
 
standard
 
microphones;
 
EHR
 
with
 
FHIR
 
or
 
SFTP/PDF
 
intake.
 
 
8)  Plans  &  Packaging  (example  copy  —  pricing  TBD)  
●  Starter  (solo/2–5  seats):  core  capture/transcribe,  note  drafts,  PDF  export,  basic  
templates.
 
 ●  Clinic  (6–50):  org  templates,  Golden  Thread,  risk  flags,  FHIR/PDF/DOCX  export,  SSO,  
audit,
 
analytics.
 
 ●  Enterprise  (50+):  region-specific  hosting,  BAAs/DPAs,  advanced  policy  and  DLP,  
custom
 
SLAs,
 
dedicated
 
support,
 
partner
 
APIs.
 
 
Add  an  “Essentials  vs  Pro  vs  Enterprise”  comparison  table;  keep  pricing  “Contact  Sales”  until  
finalized.
 
 
9)  Differentiators  (site  talking  points)  
●  Purpose-built  for  behavioral  health.  Templates  and  phrasing  aligned  to  payer  and  
clinical
 
expectations.
 
 ●  Golden  Thread  built-in.  Evidence-linked  goals  and  measurable  objectives,  not  just  raw  
text
 
generation.
 
 ●  Hybrid  privacy  model.  Cloud  accuracy  where  permitted;  offline/edge  STT  where  
needed.
 
 ●  Enterprise  controls.  Residency,  BAAs/DPAs,  no-retention  LLM  modes,  immutable  
audit,
 
and
 
FHIR-native
 
export.
 
 
 
10)  Metrics  &  Social  Proof  (what  to  surface)  

---

## Page 6

●  Median  note  time  saved  (mins)  
 ●  %  notes  approved  without  edits  
 ●  Denial  rate  reduction  (when  available)  
 ●  Quotes  from  clinicians  and  clinical  directors  
 ●  Logos  (with  permission)  and  short  case  snapshots  
 
 
11)  FAQs  (short  answers)  
Is  this  HIPAA  compliant?  
 
Yes.
 
Mentalyc
 
operates
 
on
 
HIPAA-eligible
 
infrastructure
 
with
 
BAAs,
 
encryption,
 
PHI
 
redaction,
 
and
 
immutable
 
audits.
 
(Your
 
org’s
 
administrative/physical
 
safeguards
 
still
 
apply.)
 
Does  it  train  on  our  data?  
 
By
 
default,
 
no.
 
Customer
 
data
 
isn’t
 
used
 
to
 
train
 
shared
 
models.
 
Optional
 
fine-tuning
 
is
 
available
 
under
 
explicit
 
agreements.
 
Which  EHRs  are  supported?  
 
FHIR
 
R4
 
export
 
works
 
broadly;
 
we
 
also
 
support
 
PDF/DOCX
 
and
 
secure
 
webhooks.
 
What  about  accents  and  non-English?  
 
Excellent
 
English
 
STT;
 
strong
 
Spanish
 
and
 
Hebrew
 
support
 
with
 
clinical
 
phrasing
 
normalization.
 
Can  I  work  offline?  
 
Yes—desktop
 
mode
 
offers
 
offline
 
STT
 
and
 
local
 
redaction
 
with
 
later
 
sync.
 
 
12)  Page  Structure  (Information  Architecture)  
Landing  (single  page)  
1.  Hero  —  headline,  subhead,  primary  CTAs  (“Start  Pilot”,  “Talk  to  Sales”),  short  logo  strip.  
 2.  Outcomes  —  time  saved,  quality,  compliance;  3–4  KPI  tiles.  
 3.  How  it  works  —  6-step  flow  with  icons;  link  to  security  page.  
 

---

## Page 7

4.  Features  —  5  pillars  (Capture/Transcribe,  Redaction,  Notes/Plans,  Templates,  
Export/Analytics).
 
 5.  Security  &  Compliance  —  HIPAA/GDPR/PPL,  residency,  BAAs/DPAs,  audit.  
 6.  Integrations  —  FHIR,  APIs,  partner  logos  (when  available).  
 7.  Personas  —  Solo/Clinic/Enterprise  cards  with  tailored  benefits.  
 8.  Pricing  tiers  —  Starter  /  Clinic  /  Enterprise  (CTA  to  contact).  
 9.  Testimonials  —  2–3  quotes;  link  to  case  stories.  
 10.  FAQ  —  top  5  questions.  
 11.  Final  CTA  —  “Start  your  pilot”  +  contact  form.  
 
Secondary  pages:  Security  &  Compliance,  For  IT,  For  Clinicians,  Resources  (guides,  
webinars),
 
Careers.
 
 
13)  On-page  Copy  Blocks  (ready  to  paste)  
Hero  headline:  
 
Clinical
 
notes
 
that
 
write
 
themselves—accurately
 
and
 
on
 
time.
 
Hero  subhead:  
 
Mentalyc
 
turns
 
sessions
 
into
 
payer-ready
 
notes
 
and
 
treatment
 
plans,
 
with
 
risk
 
flags,
 
the
 
Golden
 
Thread,
 
and
 
export
 
to
 
your
 
EHR.
 
CTA  buttons:  
 
Start
 
a
 
Pilot
 
·
 
See
 
a
 
5-min
 
Demo
 
Outcomes  tiles  (examples):  
●  –70%  Note  time  per  session  
 ●  ≥95%  Template  completeness  
 ●  <10%  STT  WER  (clean  audio)  
 ●  0  PHI  beyond  the  redaction  layer  (target)  
 

---

## Page 8

Security  short  copy:  
 
Built
 
on
 
HIPAA-eligible
 
cloud
 
with
 
encryption,
 
PHI
 
redaction,
 
immutable
 
audits,
 
and
 
regional
 
data
 
residency
 
(US/EU/IL).
 
BAAs
 
and
 
DPAs
 
available.
 
Clinician  quote  placeholder:  
 
“Mentallyc
 
cut
 
my
 
documentation
 
time
 
in
 
half
 
without
 
sacrificing
 
clinical
 
quality.”
 
Final  CTA  band:  
 
Ready
 
to
 
reclaim
 
your
 
evenings?
 
 
Start
 
a
 
two-week
 
pilot
 
with
 
your
 
own
 
templates
 
and
 
sessions.
 
 
14)  Content  &  Asset  Checklist  (for  launch)  
●  Screenshots:  capture  screen  (mobile  &  desktop),  review/approve  note  UI,  analytics  
dashboard
 
 ●  2×  short  demo  videos  (60–90s):  “How  it  works”  &  “Security  in  60  seconds”  
 ●  PDF:  Security  &  Compliance  overview  (1–2  pages)  
 ●  Case  blurb(s)  and  2–3  anonymized  sample  notes  (before/after)  
 ●  Logos  and  approvals,  brand  guidelines,  favicon,  open-graph  images  
 

---

