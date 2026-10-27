## Headline: program-checked accuracy (facts right / all facts)

| Command | Syntax file | Right | a listed | b real | c value | d kind | e equals | f repeat | g files | h rules |
|---|---|---|---|---|---|---|---|---|---|---|
| `cut` | reference | **61/72 (85%)** | 17/17 | 17/18 | 17/17 | 4/5 | 0/0 | 3/3 | 3/4 | 0/8 |
| `cut` | gpt-4o (shipped) | **63/76 (83%)** | 17/17 | 17/17 | 17/17 | 5/5 | 1/5 | 3/3 | 3/4 | 0/8 |
| `cut` | agent 2026-10-20_135253 | **68/76 (89%)** | 17/17 | 17/17 | 17/17 | 5/5 | 1/5 | 3/3 | 4/4 | 4/8 |
| `sort` | reference | **172/220 (78%)** | 52/53 | 54/54 | 54/54 | 7/11 | 1/4 | 0/0 | 3/4 | 1/40 |
| `sort` | gpt-4o (shipped) | **157/204 (77%)** | 48/53 | 49/49 | 49/49 | 6/8 | 1/1 | 0/0 | 3/4 | 1/40 |
| `sort` | agent 2026-10-20_160340 | **181/230 (79%)** | 53/53 | 53/53 | 52/53 | 10/12 | 6/12 | 2/2 | 4/4 | 1/41 |
| `rm` | reference | **59/60 (98%)** | 17/17 | 17/17 | 17/17 | 2/2 | 1/2 | 0/0 | 4/4 | 1/1 |
| `rm` | gpt-4o (shipped) | **59/60 (98%)** | 17/17 | 17/17 | 17/17 | 2/2 | 1/2 | 0/0 | 4/4 | 1/1 |
| `rm` | agent 2026-10-20_121932 | **58/60 (97%)** | 17/17 | 17/17 | 17/17 | 2/2 | 1/2 | 0/0 | 3/4 | 1/1 |
| `binwalk` | agent 2026-10-20_133813 | **326/337 (97%)** | 102/102 | 102/102 | 102/102 | 11/21 | 0/0 | 5/5 | 3/4 | 1/1 |

## Fit with v1's current programs (mixes the file's quality with v1's conventions)

| Command | Syntax file | Real-world lines read correctly | Lines v1's matcher counts as read | Generated lines doing real work |
|---|---|---|---|---|
| `cut` | reference | 5,856/5,856 (100%) (GNU's rules) | 5,890/5,909 (100%) | 15/29 (52%) |
| `cut` | gpt-4o (shipped) | 5,856/5,856 (100%) (GNU's rules) | 3,219/5,909 (54%) | 0/30 (0%) |
| `cut` | agent 2026-10-20_135253 | 5,856/5,856 (100%) (GNU's rules) | 5,044/5,909 (85%) | 0/240 (0%) |
| `sort` | reference | 5,010/5,010 (100%) (GNU's rules) | 5,011/5,011 (100%) | 41/56 (73%) |
| `sort` | gpt-4o (shipped) | 4,179/5,010 (83%) (GNU's rules) | 5,011/5,011 (100%) | 38/47 (81%) |
| `sort` | agent 2026-10-20_160340 | 5,010/5,010 (100%) (GNU's rules) | 4,857/5,011 (97%) | 33/56 (59%) |
| `rm` | reference | 24,195/24,195 (100%) (GNU's rules) | 24,094/24,260 (99%) | 26/32 (81%) |
| `rm` | gpt-4o (shipped) | 24,195/24,195 (100%) (GNU's rules) | 24,094/24,260 (99%) | 26/32 (81%) |
| `rm` | agent 2026-10-20_121932 | 24,195/24,195 (100%) (GNU's rules) | 24,094/24,260 (99%) | 3/21 (14%) |
| `binwalk` | agent 2026-10-20_133813 | no corpus lines | n/a | not traced: 65,659 lines; without `-s`: 72/72 (100%) |

## Paper-comparable: agreement with Caruca's reference (blind spots: task 018, section 4.4)

| Command | Syntax file | Reference options matched | Extra options | Exact by v1's cmp_specs |
|---|---|---|---|---|
| `cut` | gpt-4o (shipped) | 11/12 | 0 | no |
| `cut` | agent 2026-10-20_135253 | 11/12 | 0 | no |
| `sort` | gpt-4o (shipped) | 28/31 | 0 | no |
| `sort` | agent 2026-10-20_160340 | 31/31 | 2 | no |
| `rm` | gpt-4o (shipped) | 12/12 | 0 | yes |
| `rm` | agent 2026-10-20_121932 | 12/12 | 0 | no |

## Performance of the file's making

| Command | Syntax file | Time | Cost (list price) | Turns | Tool calls | Output tokens |
|---|---|---|---|---|---|---|
| `cut` | reference | written and corrected by hand (the paper: 80 person-hours for the whole answer key) | | | | |
| `cut` | gpt-4o (shipped) | shipped with v1; when, with which settings and at what cost it was made is not recorded | | | | |
| `cut` | agent 2026-10-20_135253 | 104 s | $1.25 | 18 | 17 | 9,117 |
| `sort` | reference | written and corrected by hand (the paper: 80 person-hours for the whole answer key) | | | | |
| `sort` | gpt-4o (shipped) | shipped with v1; when, with which settings and at what cost it was made is not recorded | | | | |
| `sort` | agent 2026-10-20_160340 | 304 s | $2.46 | 24 | 23 | 23,977 |
| `rm` | reference | written and corrected by hand (the paper: 80 person-hours for the whole answer key) | | | | |
| `rm` | gpt-4o (shipped) | shipped with v1; when, with which settings and at what cost it was made is not recorded | | | | |
| `rm` | agent 2026-10-20_121932 | 60 s | $0.80 | 6 | 5 | 4,623 |
| `binwalk` | agent 2026-10-20_133813 | 193 s | $2.12 | 19 | 18 | 15,769 |
