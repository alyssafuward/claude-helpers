---
name: rename-sug
description: Suggest a short chat title and automatically rename the session
---

Look at this conversation and come up with a short, descriptive title (under 60 characters). Be specific, not generic — capture the main topic or work done.

Once you have the title, run this bash command to rename the session automatically (substitute your title for TITLE):

```bash
python3 -c "
import json, sys, os
path = os.path.expanduser('~') + '/.claude/sessions/' + str(sys.argv[1]) + '.json'
with open(path) as f: d = json.load(f)
d['name'] = sys.argv[2]
with open(path, 'w') as f: json.dump(d, f)
" "$PPID" "TITLE"
```

Tell the user what you renamed the session to.
