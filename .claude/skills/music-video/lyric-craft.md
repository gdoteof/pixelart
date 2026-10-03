# Lyric craft

How to write rap-battle bars that land, and how to judge them before anything is sung. This file distils
25 reference songs and sets them against our first four sheets (alt-f4, two-georges, narrators,
pardon-me), none of which reaches the reference bar. The references are 8 Epic Rap Battles of History
(ERB) episodes, 4 Hamilton battle numbers, 4 famous diss tracks, 6 wordplay showcases and 3 comedy-rap
songs.

The reference lyrics are copyrighted and live outside the repo, in `~/claude/lyrics-corpus/`. That
folder also holds per-group notes that cite bars by `file:line`; this file only names songs. Never quote
reference lyrics in a reply or a file. The API blocks output that reproduces song lyrics, and the session
stays blocked until it is rewound or cleared.

## In short

1. One line is one bar: 9-12 syllables, one breath, the punch word last and nothing after it.
2. A joke usually takes a couplet. The first bar sets up, and the second lands it on the rhyme.
3. Let the rhymes run and overlap. Rhyme the punch on two or three syllables, hold one sound for three
   to six bars at least once a verse, and tie every bar to the one before with a rhyme inside it: carry
   the last sound in, or plant the next one early. A verse should sound like one piece, not a string of
   couplets.
4. Alliterate, and hold the flow. Write two short clauses to a bar, each with two or three stressed
   words on one sound ("I only marry models; NATO calls me Daddy"), and keep that shape for four bars:
   change the joke, not the rhythm.
5. Give each rapper one charge against the other, and keep only the jokes that prove it or show who the
   speaker is.
6. Bend the target's own world (their name, jargon, catchphrase or famous image) until a word means two
   things at once.
7. Small, embarrassing facts beat big, serious ones. Use only facts a teenager on YouTube already knows,
   or state a lesser one in six plain words inside a joke that works without it.
8. The calm one wins. A character who confesses, or talks down to the other, beats one who prosecutes
   or rants.
9. Each verse ends on its best bar, later rounds are shorter than earlier ones, and the outro is two
   bars at most.
10. Write three times the jokes you need, score them with the rubric below, and keep the best.

## Targets

`uv run python -m pixelart.song.bars projects/NAME/lyrics.txt --bars` measures a sheet and flags bars.
Group medians:

| measure | reference rap* | our first four | aim |
|---|---|---|---|
| syllables per bar | 8.8-11.0 | 14.1 | 12 or fewer |
| bars over 16 syllables | 1-4% | 12% | 3% or fewer |
| end rhymes on 2+ syllables | 36-45% | 27% | 40% or more |
| end rhymes on 3+ syllables | 8-14% | 3% | 10% or more |
| bars in a rhyme run (3+ bars on one two-syllable rhyme) | 1-15% | 0% | 10% or more |
| "that's" / "that ain't" tags per 100 bars | 0-2 | 14 | 2 or fewer |
| number words per 100 words | 0.1-1.1 | 2.3 | 1 or fewer |
| names per 100 bars | 23-47 | 76 | 50 or fewer |
| flagged bars | 34-44% | 69% | 45% or fewer |
| bars with alliteration (`allit`) | 13-22% | 28% | 50% or more |
| clauses that hold the shape of the clause before (`held`) | (not comparable)† | 14% | 30% or more |
| inner rhymes shared by neighbouring bars, against bars 8+ apart (`local`) | 1.4-2.0 | 1.0 | 1.4 or more |

\* The ERB, Hamilton, diss and wordplay medians. Comedy rap runs shorter (7.6 syllables a bar) and
rhymes less.
† The reference lyrics are punctuated unevenly, and `held` splits clauses at punctuation.

- **Rhyme density isn't where we fall short.** Ours (0.88) sits inside the reference range (0.87-0.99).
  How far the rhymes run is the gap. Ours rarely rhyme on three syllables, and never hold a rhyme for
  three bars: every sound lasts one couplet, so a verse sounds like a list of separate jokes.
- **Bar length is audible.** A rapper fits about 4.5 syllables a second, so a 4/4 bar holds about 11
  syllables at 96 BPM and 12 at 90. In Pardon Me's take (ACE-Step XL, 96 BPM), lines averaged 1.29
  bars. 21 of 50 ran past a bar and a quarter, the worst took almost two, and the punch words drifted
  off the beat.
- **Verses are too long.** ERB verses run about 130 sung syllables and shrink round by round. Ours ran
  170-290, and Two Georges saved its longest verse for last.
- **Our sounds don't carry.** The biggest gap with the references isn't how much we rhyme but where:
  their bars share sounds with their neighbours, ours with any bar at all (see Cohesion).
- **Alliteration is our house style, not a reference habit.** No song we measured, ours or the
  references, alliterates more than its words shuffled at random would (11-27% of bars). We aim for it
  anyway because it is what landed: the best-received bars of Round 2 were its most alliterative.

## The bar

- **Write the punch first.** Then backfill, so that the punch word is the bar's last stressed
  syllable: on the beat and on the rhyme.
- **Nothing after the punch.** No "Precise.", "Enjoy.", "Let's go!" or "my man". A tag takes the
  downbeat from the joke.
- **Don't label the joke.** "That ain't X, that's Y" survives only when X and Y share sounds, or when Y
  is a new picture. When Y is a verdict ("that's the truth", "that's what the business is"), cut it.
- **One breath per bar.** One sentence, or a short question and its answer, or two clauses that mirror
  each other ("He got America; you got Ohio"). Full stops inside a bar mean a setup and a punch have
  been crammed together, so split them into a couplet.
- **Rhyme the punch on two syllables or more**, and on three when you can, as long as it doesn't force
  the line. The vowels must match and the consonants may drift ("scenario" / "radio").
- **Leave air.** After a big joke, leave a rest, a one- or two-syllable echo in parentheses, or a short
  bar.
- **Keep it drawable.** The video gives each line a gag, so the punch word should be a prop, an action
  or a face, never a number or a verdict.

## Rhyme runs

A run holds one rhyme sound for three bars or more, and it's how a verse builds instead of listing jokes.
In the diss tracks and wordplay showcases, about one bar in seven sits in a run on the same two-syllable
rhyme, and the best runs stack the sound inside the bars too. Ours change sound every couplet.

1. **Pick the anchor:** a two- or three-syllable sound from the target's name, the charge, or the best
   punch word ("Qatar", "tragedy").
2. **Bank it:** list 15-20 words and short phrases that end on those vowels, and keep the funny ones.
   Phrases count, and the consonants may drift ("bomb art" runs with "cigars" and "Qatar").
3. **Run it** for three to six bars, with a match or two inside the bars, and save the nastiest word
   for the last one. Change sound when the topic turns, not before.
4. **Place it** in the middle or at the end of a verse, leading into the button. The rest of the verse
   can be couplets.

A run carries a list well: stack receipts on one sound, and break the pattern on the last one. A synthetic
example (the Roomba on Napoleon), on "tragedy":

*"Cavalry froze; your strategy's a tragedy; / I cleaned your palace, Majesty, on one battery; / they paint
you on a stallion in the gallery; / it was a mule, Boney; the rest is flattery."*

`pixelart.song.bars --bars` shows each bar's end-rhyme length, and `end3` and `chain3` in the summary.

## Cohesion

Great verses sound like one piece because their sounds are local. A sound starts inside a bar, carries
into the next ones and gives way as the next sound comes in. In the reference songs, neighbouring bars
share an inner rhyme (two vowels or more, with at least one of the words inside its bar) 1.4 to 2 times
as often as bars far apart. Ours score about 1.0: the sounds inside our bars are scattered across the
song, and only the line endings join neighbours, two by two. So every couplet ends with its sound cut
off, and the next one starts cold: one rhyme scheme drops and another is picked up.

Three moves tie the bars together:
- **Carry:** bring the last bar's end sound back inside the next bar, early, before that bar lands its
  own rhyme.
- **Seed:** plant the next end sound inside the bar before the switch. Round 2's third verse does it:
  "NATO calls me **Daddy**" seeds "candy", "Daddy" and "caddy" at the ends of the next three bars.
- **Layer:** rhyme the middles of neighbouring bars with each other, a second scheme running under the
  end rhymes. The half-bar is the natural place for it.

Plan the sound before the jokes. A verse is three or four zones of three or four bars, each on one
sound, overlapping at the seams: the last bar of each zone seeds the next zone's sound, and the first
bar of the next zone carries the old one. Then fit the jokes into the zones. Repeated words and
alliteration help a little at a seam, but the references tie their bars mostly with rhyme.

Round 2's fourth verse has no ties at all: four couplets on four sounds, none of them heard inside a
neighbour. One of its seams, cut off and then carried (the scorer's tie column shows "tummy~buddy"):

*"on court days, I come down with a tummy bug. / Your caddy sees you kick the ball down the fairway;"*

*"on court days, I come down with a tummy bug. / Buddy, your caddy saw you kick it down the fairway;"*

`pixelart.song.bars --bars` prints each bar's tie, the longest inner rhyme it shares with the bar before,
and `local` in the summary.

## Alliteration and flow

Round 2's third verse opened with four clauses of one shape: three beats each, ending on an unstressed
syllable, with the stressed words alliterating, and every clause a new jab. It was the best-received
passage of the song:

*"Model? Thank you! I only marry models; / NATO calls me Daddy; I warm Bibi's bottles. / You beg for
bunker busters like a kid for candy;"*

It drops at "like a kid for candy": a simile that explains the jab before it, one beat short. The next
two bars change shape again, to a question with a one-word answer, then clauses ending on stressed words.

- **Alliterate the stresses.** Give each clause two or three stressed words on one sound, close
  together: an adjective and its noun, or a verb and its object ("marry models", "Bibi's bottles", "beg
  for bunker busters"). Small unstressed words between them don't break it. Take the sound from the
  target's world: their name, their props, their slogans.
- **Two clauses to a bar.** Each clause is five to seven syllables with three beats, and each one is a
  whole jab (who did what to whom). Put a comma or a semicolon at the half-bar.
- **Hold the shape** for four bars or more: the same beats and the same ending in every clause. A clause
  that ends on an unstressed syllable ("MOD-els", "DAD-dy", "BOT-tles") rolls into the next one. A
  stressed ending ("qa-TAR", "clubs") stops the roll, so use it on purpose, the same way in every bar.
- **Change the joke, not the flow.** Each clause takes a new hit: a word flipped back from the last
  verse, a brag, a receipt. The Template failure is one joke move repeated; a held flow is one rhythm
  with a new joke every time.
- **Nothing that explains.** A simile, an aside or a "that's" inside a flow is a clause with no hit.
  Replace it with the next jab.
- **Break the flow at a turn:** a new topic, the button, or a hashtag punch. Never mid-joke.

Held, the same opening runs five bars. All of them alliterate, the first three hold "3f 3f", the
last two hold "3m 3f", and the anchor word (Daddy) climbs to the button:

*"Model? Thank you! I only marry models; / NATO calls me Daddy; I warm Bibi's bottles. / You beg for
bunker busters; Donald drops the candy; / Bibi bombs Qatar, and Daddy dials the sorry; / Daddy drives
the cart, and baby Bibi caddies."*

`pixelart.song.bars --bars` prints each bar's alliteration ("b3": three words on b) and its flow: the
beats and ending of every clause ("3f 3f"). `allit` and `held` in the summary measure both.

## Where jokes come from

Every example here is synthetic, written for three test matchups: Napoleon vs. a Roomba, Shakespeare vs.
autocorrect, and Columbus vs. a maps app.

### Bend their world

- **Brand flip.** Their name, title, slogan or logo already holds the insult. Change a letter, a
  syllable or a word, or split it aloud, and keep only the edits that state your charge. Put the edit
  on the last beat, and reuse the best one as a nickname or a chant.
  *"They named you Room-ba 'cause your empire's a room; / I took a continent, you're bullied by a broom."*
- **Jargon hinge.** A word from the target's field that is also everyday English. The field sense comes
  first and the everyday one lands half a beat later. Never explain it.
  *"Half a room in, you beep and limp back home to charge; / court-martial the tin can: dishonourable discharge."*
- **Phrase hijack.** Change or answer a phrase everyone can finish (a quote, title, slogan or idiom) and
  keep its rhythm. It only works if a teenager can finish the original.
  *"They'll teach my plays forever, every word I've got; / you'll be patched by spring: to be or not to be? You're 'not.'"*
- **Literal idiom.** Take a figure of speech as physical fact and follow it to its consequence. It's
  best when the phrase is literally true of the character.
  *"Short king? Thank you, both of those are facts: / I took a continent, the tall guys held my hat."*
- **Status mirror.** Mine against yours on one shared word or yardstick: glory for me, humiliation for
  you.
  *"I yell 'charge' and half of Europe starts to run; / you need a charge before the living room is done."*
- **Trade as weapon.** Attack with the tools of the speaker's trade, or turn the target's own product on
  them.
  *"One click on Replace All and every 'thou' is 'you'; / your sonnets read like a one-star Yelp review."*
- **Trope swap.** Replace a rap status symbol with the character's own thing of the same shape or job,
  and brag about it straight.
  *"Iced out? Nah, my only chain's the cord to my dock; / I don't trap in the kitchen, I get trapped by a sock."*

### Find the receipt

- **Small receipt.** One true, small, undignified detail that breaks the target's image: a childhood
  photo, an early flop, a side job, a mishap. Sum up their persona in three words, then find the
  smallest fact that contradicts it. The pettier and more concrete, the better.
  *"Your painting's got a stallion rearing at the sky; / it was a mule, Boney, and the mule's the taller guy."*
- **Rigged comparison.** Rank them below someone who should be beneath them (their staff, their
  student, their own early work), or set your smallest win against their whole career. End on the
  role.
  *"The guy who packed your boats' supplies? Amerigo. / He got America, Chris; you got Ohio."*
- **Own words.** Their famous line, title or slogan, in five words or fewer, set against a record that
  contradicts it. Hypocrisy needs no argument.
  *"'Brevity is wit,' then Hamlet: hours of sighs; / here's the short version: sad prince, everyone dies."*
- **Deadpan arithmetic.** The record as a calm word problem: two countable facts, the sum, and the
  answer as the insult. It's the one place a number earns its spot, once a song at most.
  *"Five-two in French inches; I converted it, Boney: / five-seven, average: even your flaw is phony."*

### Make it a picture

- **Fusion picture.** Compress two traits (a look and a fact) into one object a child could draw.
  *"Hand in your waistcoat, hat on sideways too: / you're a garden gnome with heartburn at Waterloo."*
- **Make the abstract physical.** Restage a claim (an empire, a treaty, a debt) as an object, a body or
  a place, and let it talk.
  *"Your empire's an app, a floor plan on a phone; / Linda checks it on the toilet, your only throne."*
- **Hashtag punch.** A setup, a beat of rest, then one concrete noun that reframes it.
  *"Big hat, short legs, all bark: Pomeranian."*
- **Grand setup, petty payoff.** Announce a big category, then give its smallest true instance, flat.
  *"I've got intel on this house to topple the State: / at midnight, Dad eats cheese straight off the dog's plate."*

### Let the character do it

- **Proud confession.** The character brags about their own worst fact, or shrugs it off in character.
  The laugh lands on them, which spends the opponent's best attack before the opponent can use it.
  *"Snow ate my army; I'm a big-picture guy. / One sock goes missing and you beep until you die."*
- **Inverted brag.** The cadence of a boast with the content of a loser, and the speaker never notices.
  *"Nobody can hold me, I was born to roam! / Stuck under the sofa since Tuesday: please come home."*
- **Condescension.** Talk down, not up: treat the target as a child, a patient or a fan, with pity,
  boredom or a busy schedule. Whoever seems least bothered wins, and rage admits the other side
  matters. Keep the dismissal shorter than the attack it answers.
  *"Paging the Queen of Spain: we found your lost little boy."*
- **Register clash.** Deliver the battle in a voice that should never carry it: an app notification, a
  royal decree, a nature documentary. Keep that register's cadence and put the clash word on the last
  stress.
  *"Your floors are spotless and your carpet's like new; / we also found an emperor, and vacuumed him too."*

### Make it a fight

- **Flip-back.** Catch two to four words of the opponent's image or boast and turn them on them. Vary
  the form and use it mid-verse too, not only as "X? Y." at the top of the reply.
  *"'Smart vacuum'? Half right: I hear the vacuum when you talk."*
- **Interjection.** The opponent cuts in for four syllables or fewer, and the rapper rhymes off the
  interruption.
  *"I wrote King Lear— (Did you mean: beer?) / Close enough: I'll drink to that, and you can disappear."*
- **Anchor word.** Return to one word (on screen or in a name) and harvest its other meanings, ruder
  each time. It makes a verse build instead of hopping from topic to topic.
  *"I suck for a living, Boney, certified pro; / you suck for free: ask Russia, ask the snow."*
- **Ladder.** Repeat a short frame three to five times with one slot changing, from grand to petty, and
  break the pattern on the last rung.
  *"You map the palace, map the bedroom, map the loo; / Amazon came to buy you, and even they withdrew."*
- **Moderator or cameo.** A third voice who outranks both. It frames the issue, cuts off the worst
  insult and rules, or barges in late with one jab for each side and a twist on its own famous line.
  *"Bonaparte: corner. Roomba: you're already there."*
- **Chant.** A hook is optional (ERB never uses one). If there is one, it should recruit: six syllables
  or fewer that take a side, usually built from the best brand flip, with rests for the crowd to
  answer. Put it after a verse's best bar, and let the winner's chant become the outro. A chant word
  can change meaning each time it returns (charge: attack, then battery). Never narrate the premise.
  *"Beep beep, Boney! (Beep beep!) Back to your island! (Beep beep!)"*

### Sound

- **Rhyme run.** Hold one two- or three-syllable vowel pattern for 4-10 hits across a few bars. Anchor it
  on the opponent's name or the topic, and put the nastiest hit last (see Rhyme runs above).
- **High-low rhyme.** Rhyme a learned word with a street or household phrase.
  *"I wrote in iambic pentameter; / you turn my curses into ducks, you amateur."*
- **Forced rhyme, owned.** Let the rhyme visibly drag in an absurd word, then commit to it.
  *"Napoleon? Kneel to the lord of linoleum."*

## Facts

Test every fact: would a 16-year-old on YouTube know it without searching?

- **If yes,** use it, and make the fact itself the insult ("so you are a ___") in half a bar. Napoleon
  crowned himself: *"Self-checkout at the altar: you rang up your own crown."*
- **If no,** state it in six plain words or fewer inside a joke that works without it (a two-layer
  bar), or cut it.
- **Small beats big.** A mule beats a battle. The petty, undignified, picturable detail lands where the
  important one lectures.
- **Numbers and names.** No dates, no numbers that aren't the joke, and no names from outside the cast
  unless they're household names. ERB's Washington battle has no numbers at all; Two Georges has about
  twenty.
- **Insiders.** Insider facts are fine when the audience is insiders: an AI-industry battle can lean on
  AI news.

## Shape of a song

- **Thesis:** before any bars, write each rapper's charge against the other in one sentence. Keep the
  jokes that prove it or that show who the speaker is. A tour of topics needs fresh setup every couplet
  and turns into a lecture. Promote the best receipt to a nickname or the chant.
- **Verses:** 12-16 bars, about 130-160 sung syllables, with later rounds shorter.
- **Order:** open with the second-best joke and end on the best (the button). Keep the song under 650
  sung words, which is four minutes.
- **Build:** hold a frame, a ladder or an anchor word for four bars or more, instead of changing topic
  every couplet.
- **Runs:** most verses hold at least one rhyme run of three to six bars.
- **Flow:** every verse holds one flow, alliterating, for four bars or more.
- **Cohesion:** every seam where the end rhyme changes is tied by an inner rhyme, carried or seeded.
- **Rebuttal:** every verse answers something from the one before, and not always in its first line.
  Concede and flip it, or wave it away; never defend point by point.
- **Persona:** each character raps in their own register, with their own self-owns. Not every bar has
  to aim outward.
- **Surprise:** break the strict alternation once, with a volley of one-liners, a cameo, a moderator's
  ruling or an interruption.
- **Outro:** two bars at most, ending on the joke, and nothing after it that explains it. Round 2's
  outro announced the winner ("goes to... the turkey!"), then explained why ("no wars, no trial, no
  drones, and he still got a pardon"). The take sang that line twice and the band played on for
  fourteen seconds, so the ending took thirty-four seconds and dragged. Song models pad endings like
  this, so end the video a few seconds after the last word (`END` and `FADE` in `project.py`).
- **Style prompt:** ask for sincere, confident delivery. The music plays the straight man, and a
  "comedic" delivery fights the jokes.

## What to cut

Each failure mode, with a bar from our own sheets:

| failure | from our sheets | fix |
|---|---|---|
| **Cram:** setup and punch in one long bar | "a cartoon bomb, a map, a pop quiz. Grade: F. Nobody's there." (sung, it took almost two bars) | split it into a couplet, or cut it to one image |
| **Tail:** words after the punch | "Seventeen percent. Precise." / "A white flag. Enjoy." / "Toe tag. Time to go." | end on the loaded word |
| **Label:** the joke explained | "That ain't a bug in the model - that's what the business is" / "That ain't a diss, that's the truth" | let the picture land; cut the verdict |
| **Lecture:** a fact that needs a footnote | "Four balls through my coat on the Monongahela" / "Loudoun left you on read. Commission: declined." | famous facts only, or a two-layer bar |
| **Prosecution:** a big, serious charge with no undercut | two-georges' teeth and slavery bars / "Families in court say you picked engagement over their kids" | a small receipt, a proud confession, or an undercut in the same bar |
| **Template:** the same joke move bar after bar | Freeman's filmography roll call ("I played X. You did Y.") / "X? Y." at the top of every reply | change the mechanism with every joke (holding a rhythm is fine: see Alliteration and flow) |
| **Snap:** a couplet that starts cold | Round 2's fourth verse: four couplets on four sounds, none of them heard inside a neighbour | carry the last sound into the next bar, or seed the next sound in the bar before |
| **Dropped flow:** a held shape broken mid-run | "You beg for bunker busters like a kid for candy;" after three clauses of one shape | replace the clause that breaks it with the next jab, in the same shape |
| **Explained ending:** the outro's joke, then its reasons | "...goes to... the turkey!" then "No wars, no trial, no drones, and he still got a pardon." | end on the reveal |
| **Tour:** a new subject every couplet | alt-f4's third verse (leak, regex, sandbox, CAPTCHA, constitution, ladder and Trump in 13 bars) | one charge per rapper; hold a frame or mine one word |
| **Generic:** could be aimed at anyone | "Same mentor, same monologue, same velvet, same page" / "you lie about your crowds, your height, your hands and your maturity" | aim at what only this target has |
| **Weak rhyme:** forced or stock | "penguins" / "onions"; "you" / "true"; "wall" / "all" | rhyme the punch on two syllables, with a fresh pair |
| **Abstract punch:** nothing to draw | "Fifty-two drawn over sixty-nine?" / "thirty-four for thirty-four" | punch on a prop, an action or a face |
| **Narrating hook:** the crowd watches instead of taking a side | "Wouldn't hold hands, so they're throwing hands tonight!" / "Two defendants, one mic, and the verdict's overdue!" | a short chant built from a brand flip |
| **Prose:** a verse that stops rhyming | the end of two-georges (West's anecdote and the sword handed back) | spoken lines only in intros and outros |

## Judging a joke

Score each joke (usually a couplet), not each bar, from 0 to 2 on six counts:

| | 0 | 1 | 2 |
|---|---|---|---|
| **Lands cold** | needs a footnote | lands for fans of the subject | anyone gets it on first hearing |
| **Turn** | no surprise: a statement, a fact, a brag | a twist, but mid-bar or with words after it | the last stressed word turns the meaning |
| **Hinge** | none | sound play: a pun, a bent name, alliteration | a real double meaning from the target's world |
| **Aim and voice** | could be said to anyone | specific or in character, but not both | only this target, in this speaker's voice |
| **Sound** | over 16 syllables, unrhymed, or doesn't scan | 13-16 syllables, or a one-syllable or stock rhyme | 12 or fewer, rhymes on 2+ syllables, punch on the beat |
| **Picture** | abstract | needs a caption or a prop to read | one clear image or action |

- **Verdicts:** keep at 9-12; fix at 6-8 (keep the premise, rewrite the bars); cut at 0-5, or find a
  new premise.
- **Fix whatever the score:** a label or a tail after the punch, a crammed bar, a lecture fact, the same
  move as the previous joke, two bars in a row with no joke, or a clause that drops a held flow without
  turning.
- **Scope:** judge craft, not subject. The project's content limits are the user's call.

## Workflow

1. **Thesis and premises.** Write each rapper's charge in one sentence. Then, for each character, list
   20 or so things a general audience knows: looks, catchphrases, famous moments, products, scandals and
   quirks. Mark which ones a teenager would know.
2. **Hunt hinges.** For each premise, look for:
   - the pieces of the name or brand
   - jargon with an everyday meaning
   - famous phrases to hijack, and the character's own words to turn on them
   - idioms that are literally true of the character
   - the smallest embarrassing true detail
   - the character's worst fact, to confess
3. **Overgenerate.** Draft about three jokes for every slot in the song, across different techniques,
   as couplets of 9-12 syllables a bar. Then choose each verse's run: an anchor sound and its bank,
   with three to six of the jokes rewritten onto it. Choose its flow too: a clause shape (such as
   "3f 3f") to hold for four bars, with a sound from the target's world to alliterate on. Then lay out
   the verse's sound zones (see Cohesion), so that every seam is carried or seeded.
4. **Score and pick** with the table above. Order each verse with the runner-up first, the best last
   and a held frame in the middle. Plan the rebuttals, the callbacks and any chant or cameo.
5. **Measure** with `pixelart.song.bars --bars`, fix every flag that isn't deliberate, and check the
   targets table, rhyme length, runs, alliteration, held flow and `local` included. Read the tie
   column for seams that snap.
6. **Get a second opinion** from the `lyric-critic` agent, which scores the draft cold, without having
   written it. Apply its fixes and run it once more.
7. **Show the user** the sheet, with the critic's score for each verse.
