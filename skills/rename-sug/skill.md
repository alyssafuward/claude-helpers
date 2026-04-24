---
name: rename-sug
description: Suggest a short chat title based on the conversation, copy it to clipboard
---

Look back at this conversation and suggest a short, descriptive chat title (under 60 characters). It should capture the main topic or work done — be specific, not generic.

Then run this bash command to copy it to the clipboard:
```bash
echo -n "/rename <suggested title>" | pbcopy
```

Output the suggestion in this exact format (no quotes, no explanation):
```
/rename <suggested title>
```

Confirm it's on her clipboard.
