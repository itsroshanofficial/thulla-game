# Manual testing checklist

## Offline
- [ ] Deal with 1, 3 and 7 bots; hand sizes look right; Ace of Spades player starts
- [ ] Only legal cards are clickable; off-suit cards disabled while you hold the suit
- [ ] Thulla shows 🔥 animation, pile pickup message, correct player leads next
- [ ] Game ends with exactly one "Thulla"; Play again works

## Voice
- [ ] Press “Test / unlock sound” → hear a line
- [ ] Mute all → no sound; Unmute → sound returns
- [ ] Volume slider changes loudness; language filter respected (e.g. only Punjabi)
- [ ] Reactions are not spammed (≥ ~4 s apart, thulla ≥ 1.5 s)
- [ ] Two browsers: muting in one does NOT mute the other

## Accounts
- [ ] Register (dup username rejected, mismatched passwords rejected)
- [ ] Wrong password ×5 → lockout message; correct after ~5 min
- [ ] Forgot password: right answer → new password works, old does not; token can't be reused
- [ ] Wrong recovery answer ×5 → cooldown; unknown username shows a question but fails generically

## Online (server running, same THULLA_SECRET)
- [ ] Create room, join from 2nd browser with code; add bot; start
- [ ] Each browser only sees its own hand (view page source / network tab: no other hands)
- [ ] Out-of-turn / illegal click returns an error and changes nothing
- [ ] Close a tab for >45 s: a bot plays that seat; reopening + joining same code restores the seat
- [ ] Test on a phone browser (layout, tap targets, sound after first tap)
