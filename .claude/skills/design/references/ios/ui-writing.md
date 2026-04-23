---
name: ui-writing
description: Apple-sourced UI writing reference (voice, capitalization, component-level copy, localization)
platform: ios
---

# Words that work: an Apple-sourced reference for UI writing

A practical guide to Apple's official guidance on UI voice, capitalization, component-level copy, inclusion, localization, and locale-aware formatting — distilled from the Apple Style Guide, Human Interface Guidelines, WWDC sessions (notably WWDC22 "Writing for interfaces"), and Apple developer documentation. Direct quotes from Apple sources are in quotation marks; everything else paraphrases Apple's published rules.

---

## 1. Apple's voice

Apple's UI voice is **clear, concise, friendly, and direct**. The Human Interface Guidelines open the Writing page with a plain claim: *"The words you choose within your app are an essential part of its user experience."* That sentence sets the expectation that copy is a designed material, not an afterthought.

At WWDC22 session 10037 ("Writing for interfaces"), Kaely Coon and Jennifer Bush framed good UI writing around four ideas that spell **PACE**:

- **Purpose** — every screen and string has one job. *"As you develop the screens in your app, think about the most important thing someone needs to know at that moment. That's the purpose of your screen."*
- **Anticipation** — copy is a conversation. *"It helps to think of the words in your app as part of a conversation… develop your app's voice first, and then you can vary its tone."*
- **Context** — the moment matters. *"When someone uses your app, are they likely to be at home in a quiet space, or traveling at a busy airport?"*
- **Empathy** — write for everyone. *"Idioms and humor can be misunderstood or not translate, and some phrases have meanings that exclude people."*

### UI voice versus marketing copy

Marketing copy is aspirational; it sells a feeling. UI copy is functional; it serves the task. Apple's HIG says it plainly: *"Prioritize clarity and avoid the temptation to be too cute or clever with your labels. For example, just saying 'Next' often works better than 'Let's do this!'"* Marketing surfaces (the Apple.com product pages, App Store editorial) carry superlatives and narrative; system UI strips them away. The iPhone Temperature warning screen is the canonical example — headline "Temperature," one sentence of consequence, one button labeled "Emergency." No charm, no apology, no delay.

### Tone — one voice, many registers

Apple distinguishes **voice** (constant, recognizable) from **tone** (variable, situational). Coon: *"Apple has one consistent voice that you'll recognize no matter which of our devices you're using, but our tone changes depending on the situation."* Activity in Fitness celebrates ("You set a personal record for your longest daily Move streak: 35 days!"); Fall Detection on Apple Watch stays calm ("It looks like you've taken a hard fall. / I'm okay."); Sleep Focus whispers ("Sleep Well"); a billing alert is matter-of-fact ("There's a billing problem with your subscription.").

Two tone rules Apple calls out directly:

- **Skip the filler.** *"'Oops!' or 'uh-oh' can sound patronizing, and 'please' and 'sorry' can sound insincere. Use them sparingly."*
- **Exclamation points are rare.** Apple warns they "can look silly when they're frequent."

### A gallery of real Apple UI copy

| Surface | Copy | What it models |
|---|---|---|
| iPhone Temperature alert | "iPhone needs to cool down before you can use it." → **Emergency** | Headline + one sentence + exact-action button |
| Apple Watch Fall Detection | "It looks like you've taken a hard fall." / **I'm okay** | Calm tone in a high-stakes moment |
| Messages onboarding | "Share Your Name and Photo with Friends" / **Choose Name and Photo** | Headline and button verb mirror each other |
| Clock (weekend alarm) | "Would you like to apply this change to all weekends in this schedule?" / **Change Next Alarm Only** | Anticipates the most common intent |
| Maps commute | "8 minutes to Home · Take Audubon Ave, traffic is light." | Answers the next question before it's asked |
| Remove-device alert | "Remove iPhone?" / **Remove** / **Cancel** | Title is the question; buttons are the answers |
| Podcasts empty state | "No Saved Episodes — Save episodes you want to listen to later, and they'll show up here." | Inviting, instructive, no apology |
| Billing error | "There's a billing problem with your subscription." / **Add Payment Method** / **Not Now** | States problem + specific recovery |

### Universal rules Apple applies to voice

Address the person as **"you,"** and keep **"we"** for the app or company. Read drafts out loud — *"It can really help make sure your writing sounds conversational, like how you'd talk to a friend."* Keep a running list of the terms your product uses and stick to it; Coon: *"Make a list of commonly used terms. This can help shape the voice that you can also use for your website, emails, and other communication."*

---

## 2. Capitalization

Apple uses two styles in UI and docs, per the Apple Style Guide entry on **capitalization**:

> *"Title-style caps: This Line Provides an Example of Title-Style Caps.*
> *Sentence-style caps: This line provides an example of sentence-style caps."*

**Title-style rule.** *"Capitalize every word except articles (a, an, the), coordinating conjunctions (and, or, but, for), and prepositions of four or fewer letters"* — and *"always capitalize the first and last word, even if it is an article, a conjunction, or a preposition of four or fewer letters."*

**Sentence-style rule.** First word capitalized; the rest lowercase unless they're proper nouns or proper adjectives.

### HIG's position: pick a style per app

From the HIG Writing page: *"Decide whether you want to use title case or sentence case for alerts, page titles, headlines, button labels, and links… Title case is more formal, while sentence case is more casual. Choose a style that fits your app."* In other words: be consistent; don't mix within a component type.

### Where Apple itself uses which

| UI element | iOS / iPadOS | macOS |
|---|---|---|
| App name, feature names (Face ID, AirDrop, Dynamic Island, Focus, Stage Manager) | **Always capitalized** (proper nouns) | **Always capitalized** |
| Menu bar titles & menu items | — | **Title case** ("File," "Save As…") |
| Push/primary buttons in dialogs | **Title case** is common ("Save," "Add Account," "Done") | **Title case** |
| Destructive button | **Title case** ("Delete," "Remove") | **Title case** |
| Navigation bar titles | Mixed; short titles often title case ("New Message") | n/a |
| Section headers in Settings | **Sentence case** ("Sounds & Haptics," "Show on Lock Screen") | **Sentence case** |
| Alert title & message body | **Sentence case** | **Sentence case** |
| List rows, labels, toggles | **Sentence case** | **Sentence case** |
| Notifications | **Sentence case** | **Sentence case** |
| Figure and table captions | **Sentence case** (ASG: *"Use sentence-style capitalization for figure captions and table captions."*) | Same |
| Accessibility feature names | Proper-noun capitalization (VoiceOver, AssistiveTouch, Live Listen, Zoom) | Same |
| All caps for emphasis | **Don't** (ASG: *"Don't use all caps for emphasis."*) | Don't |

### Proper-noun cases that trip people up

Keep the lowercase "i" in iPhone, iPad, iCloud, iOS, iPadOS, iMessage, iTunes — even at the start of a sentence. (Rewrite to avoid a sentence-initial position if possible.) "Wi-Fi" is hyphenated with both caps. "Mac" is a proper noun; the plural is "Mac computers." "App Store," "App Library," "Home Screen," "Lock Screen," "Control Center," "Notification Center," "Dynamic Island," and "Focus" are all proper feature names — always capitalized.

---

## 3. Button labels

Apple's first rule for buttons is the verb. HIG Buttons: *"An action-specific title shows that a button is interactive and says what happens when you tap it."* The guidance from HIG Alerts is just as direct: *"Use verbs and verb phrases that relate directly to the alert title and message — for example, View All, Reply, or Ignore. Use OK for simple acceptance. Avoid using Yes or No."*

**Core principles:**

- **Verb-first.** "Save Draft," "Add Item," "Delete Message," "Place Order."
- **Specific, not generic.** Prefer the exact verb over "OK," "Submit," "Yes," "No" whenever a verb would be clearer.
- **Destructive buttons say what they destroy.** "Delete," "Remove," "Discard Changes," "Erase iPhone." Pair with a safe "Cancel" and use the system's destructive style so the button gets the red/emphasized treatment.
- **Keep it short.** HIG: *"Overly long text can crowd your interface and may get truncated on smaller screens."*
- **Button verbs mirror the title.** WWDC22: *"It's always best to be specific about the action the buttons are going to take… if you only read the button labels, you would still understand what you were choosing."*

**Default vs. Cancel placement.** On **iOS/iPadOS**, Cancel sits on the left and the action the person is most likely to tap (default or destructive) sits on the right. On **macOS**, the default button — the one Return activates — sits at the right end of a button row, with Cancel to its left. Never make a destructive button the default on macOS.

### Done vs. Save vs. OK

| Label | Use when | Don't use when |
|---|---|---|
| **Done** | Changes are already applied live; the button dismisses the modal or exits edit mode | Changes still need to be committed |
| **Save** | An explicit commit is needed (new document, form submission) | Nothing to persist |
| **OK** | Acknowledging an informational alert; no specific verb applies | A clearer verb exists — prefer "Got It," "Continue," or the real action |
| **Cancel** | Dismissing without applying changes | The feature itself is called "cancel" (use "Keep Subscription" / "Cancel Subscription" instead) |

### Before and after

❌ **OK** / **Cancel** on "Delete photo?"
✅ **Delete** / **Cancel**

❌ **Yes** / **No** on "Log out?"
✅ **Sign Out** / **Cancel**

❌ **Submit** at the end of a form
✅ **Send Message**, **Place Order**, or **Save Changes**

❌ **Confirm** on a purchase sheet
✅ **Buy**, **Subscribe**, or **Pay $9.99**

❌ **Proceed** on a destructive step
✅ **Erase iPhone** (styled destructive)

❌ "Let's do this!"
✅ **Next** or **Continue**

---

## 4. Alert copy

An alert has a **title**, an optional **message**, one or more **buttons**, and (occasionally) a **text field**. Its visual appearance is static; your words are the whole design.

Apple's top rule is to **use alerts sparingly**. HIG: *"Alerts disrupt the user experience and should only be used in important situations like confirming purchases and destructive actions (such as deletions), or notifying people about problems."* If the information is non-critical, use inline messaging, a banner, or a sheet — anything less interruptive trains people to read alerts rather than dismiss them reflexively.

### When to use what

| Use an **alert** for | Use **inline validation** for | Use a **sheet/modal** for |
|---|---|---|
| Destructive confirmations, urgent system state, blocking errors, purchase confirmations | Field-level errors, transient form issues, non-blocking warnings | Complex decisions with multiple inputs, multi-step flows, rich content |

### Writing the title, message, and buttons

- **Title:** short, descriptive, multi-word. A brief sentence or a question works well. Avoid single-word titles like "Warning!" or "Error."
- **Message:** only add one if the title alone doesn't land. Use complete sentences; end with a period; aim for one or two lines.
- **Drop the "Are you sure?"** — it adds words without information. State what will happen.
- **Button verbs match the title.** If the title asks "Delete this message?," the buttons are "Delete" and "Cancel," not "Yes" and "No."
- **Test in both orientations** to make sure text doesn't require scrolling.

### Before and after

❌ Title: "Warning!" · Message: "Are you sure you want to do this?" · Buttons: OK / Cancel
✅ Title: "Delete 'Beach Trip' album?" · Message: "This permanently removes 87 photos from all your devices." · Buttons: **Delete** (destructive) / **Cancel**

❌ "Error 42: Operation could not be completed." / OK
✅ "Can't send message" · "You're not connected to the internet. Your message will send when you're back online." / **OK**

❌ "Confirm" · "Are you sure you want to sign out of all devices?" / Yes / No
✅ "Sign out of all devices?" · "You'll need to sign in again on each device." / **Sign Out** / **Cancel**

❌ "Permission Required" · "Please enable notifications to continue." / OK
✅ "Turn on notifications to get match alerts" / **Open Settings** / **Not Now**

---

## 5. Error messages

Errors are where copy either rescues the user or abandons them. Apple's model is simple: **say what happened, in plain language, and tell the person what to do next.**

**Principles:**

- **Plain language; no jargon.** A raw error code ("Error -50," "HTTP 500") leaves the person stuck. If a code is useful for support, include it *after* the explanation, not as the explanation.
- **Structure = what went wrong + why (if helpful) + what to do now.**
- **Don't blame the user.** Neutral framing ("That password didn't match") beats accusatory framing ("You entered the wrong password").
- **Be specific.** "Something went wrong" is rarely useful; name the field, the action, or the resource.
- **Offer recovery.** Provide a next step — retry, edit, open Settings, contact support — whenever possible.
- **Match tone to stakes.** Don't be cutesy about payment failures or data loss.
- **Place the error near its source.** Inline beats a modal summary at the top.
- **Don't rely on color alone.** Red plus icon plus copy — never just red.

### Before and after

❌ "Error 401: Unauthorized."
✅ "Your session expired. Sign in again to continue."

❌ "Invalid input."
✅ "Password must be at least 8 characters and include a number."

❌ "Something went wrong. Try again later."
✅ "We couldn't load your library. Check your connection, then tap Retry."

❌ "You entered an invalid email address."
✅ "That email doesn't look right. Check the spelling, or try another address."

❌ "Failed to save."
✅ "Changes weren't saved because you're offline. We'll save automatically when you reconnect."

❌ "Card declined."
✅ "Your card was declined by the bank. Try a different card or contact your bank."

---

## 6. Empty state copy

An empty state should be **inviting, not apologetic**. It should explain the value of the feature and show exactly how to start.

**Principles:**

- **Describe what belongs here** ("Your saved articles will appear here").
- **Show the value** — why use this feature at all?
- **Provide a clear next action** — a primary button with a specific verb.
- **Keep it short.** One headline plus one line of body is often enough.
- **Skip the apology.** "Nothing here," "Sorry, no photos," and "You haven't…" all start the relationship poorly.
- **Match tone to stakes.** A playful tone works in a journal; it's wrong for a medical record.

### Before and after

❌ "No items." (no action)
✅ **"Save recipes you love"** — "Tap the ♥ on any recipe to find it here later." / **Browse Recipes**

❌ "You haven't added any friends yet."
✅ **"Train with friends"** — "Add a friend to share runs and cheer each other on." / **Find Friends**

❌ "0 results. Nothing to show."
✅ **"No matches for 'tacos'"** — "Try a different ingredient or cuisine." / **Clear Search**

❌ "Your inbox is empty." (sad icon)
✅ **"You're all caught up."** — "New messages will appear here."

❌ "Sorry, you have no photos."
✅ **"No photos yet"** — "Photos you take or import will appear here."

---

## 7. Permission purpose strings

Purpose strings appear in the system permission alert that iOS/iPadOS/macOS shows when an app first asks for sensitive data. Apple's App Review team rejects vague ones. From Apple's Tech Talk "Write clear purpose strings," reviewers look for two qualities:

1. **Specifically how** the app will use the data.
2. **An example** of how the data will be used.

The Tech Talk's illustrative rewrite:

❌ "To use location."
✅ "Your location is used to determine the recommended route to your destination and provide turn-by-turn directions."

**Writing rules:**

- **Be specific** about reason and user benefit.
- **Skip legalese.** This is a product sentence, not a privacy policy.
- **One or two sentences** is ideal; too much text is its own problem.
- **Use sentence case** and speak in the second person ("your location," "your photos").
- **Mention on-device processing** when true — it reassures users and shortens support tickets.
- **Don't pre-prompt** with a custom screen that mimics the system alert; use the system alert directly.
- **If you don't use an API**, don't reference it — Apple rejects apps that reference privacy APIs they don't use without a purpose string.

### The keys you'll actually ship

| Capability | Info.plist key |
|---|---|
| Camera | `NSCameraUsageDescription` |
| Microphone | `NSMicrophoneUsageDescription` |
| Photo Library (read) | `NSPhotoLibraryUsageDescription` |
| Photo Library (add only) | `NSPhotoLibraryAddUsageDescription` |
| Location while in use | `NSLocationWhenInUseUsageDescription` |
| Location always | `NSLocationAlwaysAndWhenInUseUsageDescription` |
| Contacts | `NSContactsUsageDescription` |
| Calendars | `NSCalendarsFullAccessUsageDescription` / `NSCalendarsWriteOnlyAccessUsageDescription` |
| Reminders | `NSRemindersFullAccessUsageDescription` |
| Motion & Fitness | `NSMotionUsageDescription` |
| Bluetooth | `NSBluetoothAlwaysUsageDescription` |
| Local Network | `NSLocalNetworkUsageDescription` |
| Face ID | `NSFaceIDUsageDescription` |
| HealthKit (read/write) | `NSHealthShareUsageDescription` / `NSHealthUpdateUsageDescription` |
| Speech Recognition | `NSSpeechRecognitionUsageDescription` |
| Apple Music / Media Library | `NSAppleMusicUsageDescription` |
| HomeKit | `NSHomeKitUsageDescription` |
| Siri | `NSSiriUsageDescription` |
| App Tracking Transparency | `NSUserTrackingUsageDescription` |

### Before and after

❌ `NSCameraUsageDescription`: "Camera access."
✅ "Lets you take photos of receipts so the app can categorize your expenses automatically."

❌ `NSLocationWhenInUseUsageDescription`: "We need your location."
✅ "Your location is used to show nearby coffee shops and give walking directions."

❌ `NSContactsUsageDescription`: "App would like to access your Contacts." *(Apple's own "bad" example)*
✅ "Find friends who already use HikerApp by matching phone numbers. Contacts are processed on your device and are never uploaded."

❌ `NSPhotoLibraryUsageDescription`: "Photo Library access helps us give you a better experience."
✅ "Attach photos from your library to journal entries. Only the photos you pick are added — we never scan your library."

❌ `NSMicrophoneUsageDescription`: "Microphone access required."
✅ "Record voice memos that are transcribed and attached to the meeting note you're writing."

❌ `NSUserTrackingUsageDescription`: "Your data will be used to provide a better experience." *(Apple-cited rejection)*
✅ "Your data will be used to deliver personalized ads. You'll still see ads if you decline, but they may be less relevant."

❌ `NSFaceIDUsageDescription`: "Face ID."
✅ "Use Face ID to unlock the app instead of typing your passcode each time."

---

## 8. Onboarding copy

HIG Onboarding: *"Onboarding can help people get a quick start using your app or game. Ideally, people can understand your app or game simply by experiencing it, but if onboarding is necessary, design a flow that's fast, fun, and optional."*

**Principles:**

- **Benefits, not features.** Say what the person can do, not how the system works.
- **Short headlines, short body, one action per screen.** Progressive disclosure — introduce essentials first, reveal more only when relevant.
- **Skippable.** A **Skip** or **Get Started** exit on every screen respects people who already know what to do.
- **Ask for permissions contextually**, when a feature that needs them is first used. Don't bulk-request up front.
- **Teach through interaction.** People remember what they did; they skim what they read.
- **Don't rehash the App Store page.** They already installed — start helping.

### Before and after

❌ Headline: "Welcome to our amazing app!" · Body: "This app has many great features to make your life easier. Swipe to learn more." / **Next**
✅ Headline: **"Plan a trip in minutes"** · Body: "Tell us where you're going — we'll build a day-by-day itinerary." / **Plan My First Trip** / **Skip**

❌ "Enable notifications, location, camera, and contacts to continue."
✅ Show the app immediately. Ask for location only when the user taps "Find restaurants near me."

❌ Headline: "Our revolutionary AI-powered fitness engine" · Body: "Using proprietary algorithms, we analyze over 200 biomarkers…"
✅ Headline: **"Workouts that adapt to you"** · Body: "Each week gets a little harder, based on how your last one went." / **Start Week 1**

❌ A six-screen carousel of feature tours before any content loads.
✅ Two screens max, plus a skippable inline tip that appears the first time a user reaches each feature.

❌ "You must create an account to use this app." (wall on first launch)
✅ Let the user browse or try once. Prompt for sign-in at the moment it's needed: "Sign in to save this recipe."

---

## 9. Terminology consistency

**One term per concept, per app.** HIG: *"Use the same terminology to mean the same thing. Make sure spelling, capitalization, punctuation, labels, and use of abbreviations are all consistent."* If favorites live in "My Favorites," don't call them "Saved Items" elsewhere. If the button to advance through a flow is "Continue," use it throughout, and mark the end of the flow with a different word ("Done").

Align with Apple's system terminology, particularly for interactions users expect to behave a certain way across apps.

### Apple-preferred terms

| Preferred | Avoid | Notes |
|---|---|---|
| **Apple Account** | Apple ID (legacy) | Renamed by Apple in 2024: *"An Apple Account gives you access to all Apple services."* |
| **Sign in to** (v.), **sign-in** (n./adj.) | Log in, login, log on | ASG: *"People sign in to their Apple Account; they don't sign in with their account to devices."* |
| **Settings** (iOS/iPadOS/watchOS/tvOS/visionOS) · **System Settings** (macOS Ventura+) | Preferences, System Preferences | macOS renamed "System Preferences" to "System Settings" in Ventura (2022); ASG updated accordingly |
| **Share** | Send (as a generic UI verb) | "Share" is the ecosystem-wide sharing flow |
| **app** | application (in user-facing copy) | Lowercase "app" unless sentence-initial or part of a proper name (App Store) |
| **email** | e-mail | One word, no hyphen |
| **internet** | Internet | Lowercase since 2019 |
| **Wi-Fi** | wifi, WiFi, Wi-fi | Hyphenated, both caps |
| **iPhone, iPad, iCloud, iOS, iMessage** | IPhone, Iphone | Lowercase "i" even at sentence start — rewrite if possible |
| **Apple Watch** | iWatch | Two words, proper noun |
| **AirDrop, AirPlay** (not verbs) | "AirDrop this" | *"Use AirDrop to send photos"* — the feature is a noun |
| **tap** (touchscreens) | click, press, hit, push | Touch input only |
| **click** (pointer) | tap, press | Mouse/trackpad |
| **press** (physical buttons/keys) | click, hit, push, tap, type | Digital Crown, side button, keyboard keys, Action button |
| **touch and hold** | long press, press and hold | Apple's iOS term |
| **choose** (from a menu) | select | *"Choose File > New"*; use *select* for items before acting on them |
| **Delete** | Remove, Trash (as verbs) | Use when data is permanently removed |
| **Remove** | Delete | Use when data persists elsewhere (removing a device from an account) |
| **Trash** (noun, macOS) | — | The container; drag items to it |
| **turn on / turn off** | enable, disable, activate | *"Avoid activate/deactivate; use turn on, turn off."* |
| **Done / Save / Cancel** | OK / Yes / No (when a verb is clearer) | Specific over generic |
| **deny list / allow list** | blacklist / whitelist | Apple Style Guide entries |
| **primary / secondary**, **host / client** | master / slave | Per Apple's 2020 terminology update |
| **main** (git branch) | master | Xcode 12 default |
| **logic board** | motherboard, main board | ASG entry |
| **Apple Pencil** (no article in general refs) | "the Apple Pencil" | *"Apple Pencil works with iPad."* |

### Platform-appropriate interaction verbs

Use the verb that matches the user's input modality. On cross-platform surfaces, Apple sometimes uses "Tap or click" — or writes around it with a generic verb like "choose."

---

## 10. Inclusive language

Apple's HIG Inclusion page takes a position up front: *"Inclusive apps and games put people first by prioritizing respectful communication and presenting content and functionality in ways that everyone can access and understand."* A second line sets the bar: *"Although no app should contain offensive material or experiences, an inoffensive app isn't necessarily an inclusive app."*

### Welcoming language — Apple's direct rules

- **Address people as "you."** *"Referring to people indirectly as *users* or *the user* can make your app feel distant and unwelcoming."*
- **Reserve "we" for the app or company.** Otherwise it *"can suggest a personal relationship with people that might be interpreted as insulting or condescending."*
- **Define specialized terms** or replace them.
- **Plain language over colloquialism.** Apple flags two phrases by name: *"The phrases *peanut gallery* and *grandfathered in* both arose from oppressive contexts and continue to exclude people."*
- **Humor is hard to translate.** *"Humor is highly subjective and — similar to colloquial expressions — difficult to translate from one culture to another."*

### Gendered defaults

From the HIG Inclusion page: *"A recipe-sharing app that uses copy like 'You can let a subscriber post his or her recipes to your shared folder' could avoid unnecessary gender references by using an alternative like 'Subscribers can post recipes to your shared folder.'"* Apple's rationale is welcome and localization in one move — gendered languages need less fix-up.

Where gender must be collected, Apple says to *"provide inclusive options, such as *nonbinary*, *self-identify*, and *decline to state*."* If you need to depict a generic person, Apple advises a non-gendered image.

Common substitutions (widely adopted across industry style guides; Apple endorses the principle):

| Avoid | Prefer |
|---|---|
| his or her | their; rewrite with a plural noun |
| guys (to a group) | everyone, folks, team |
| manpower | workforce, staff, personnel |
| mankind | humankind, humanity, people |
| chairman | chair, chairperson |
| salesman | sales representative |

### Ableist language

Apple's stated rule is a principle, not a word list: *"Avoid images and language that exclude people with disabilities… avoid language that uses a disability to express a negative quality."* The specific term list below comes from industry style guides (Google's developer style guide, Microsoft's) that Apple's principle endorses in spirit.

| Avoid | Prefer |
|---|---|
| crazy / insane | unexpected, surprising, intense |
| dummy | placeholder, sample |
| sanity check | quick check, confidence check |
| cripple / crippling | severely limit |
| blind to / blind eye | unaware of, overlooking |
| lame | uninspired, underwhelming |

### Racially charged technical terms — Apple is explicit

Apple posted "Updates to Coding Terminology" in July 2020 and updated the Apple Style Guide accordingly. The official substitutions:

| Avoid | Prefer |
|---|---|
| blacklist / whitelist | **deny list / allow list** (context-specific alternatives also acceptable) |
| master / slave | **primary / secondary**; host / client |
| master (git branch) | **main** |
| slave (device/process) | Don't use |
| motherboard / main board | **logic board** |
| Black (lowercase, ethnicity) | **Black** (capitalized) |

Note: Apple's official pairs are "deny list / allow list" (two words); the one-word forms "blocklist / allowlist" are common industry usage and convey the same intent.

### Person-first versus identity-first

Apple's published position: *"Take a people-first approach when writing about people with disabilities. For example, you could describe an individual's accomplishments and goals before mentioning a disability they may have. If you're writing about a specific person or community, find out how they self-identify."* The individual or community's expressed preference supersedes the default.

### Assumptions to avoid

Apple critiques assumed family structure ("a woman, a man, and their biological children"), assumed affluence in imagery, stereotyped occupations ("only male doctors or female nurses"), and culturally narrow security questions (favorite college subject, first car). It recommends "more universal human experiences" — favorite hobby, first friend's name.

### Writing about accessibility

Treat each disability as a spectrum. Include temporary and situational disability ("short-term hearing loss due to an infection… being unable to hear while on a noisy train"). Use Apple's canonical feature names, capitalized: **VoiceOver, AssistiveTouch, Live Listen, Switch Control, Speak Screen, Zoom, Hover Text, Type to Siri, Dynamic Type**. Make VoiceOver labels meaningful — a label of "Button, gear shape two" fails the user.

---

## 11. Localization considerations

Apple's single biggest instruction for localization is a writing instruction: **compose complete sentences, then let the system handle the grammar.** The tooling exists — String Catalogs, CLDR plurals, Automatic Grammar Agreement, the locale-aware formatters — but it only works if the copy is authored to flex.

### Writing rules that make copy localize well

- **Plain, direct language.** No idioms, puns, slang, or culture-bound references.
- **Full sentences, not fragments.** Fragments glued together at runtime break in languages with grammatical gender or case.
- **Reorderable variables.** Use positional format specifiers (`%1$@`, `%2$@`) so translators can swap order.
- **No gendered default pronouns.** "Their" or a plural noun beats "his or her."
- **No cultural shorthand.** Rainbows, fall colors, Thanksgiving, baseball — all flag risk.
- **Allow for expansion.** German, Russian, and Finnish strings commonly run much longer than English. A rule of thumb widely used in the iOS community is **~30% expansion** for German; Apple's own position is directional ("prepare for significant expansion") and testable via Xcode's **Double Length Pseudolanguage** scheme option. Treat 30% as a planning floor, not a guarantee.
- **Respect text direction.** Layouts must mirror for Arabic and Hebrew; use leading/trailing constraints and SF Symbols' `.forward` / `.backward` variants.

### Avoid mid-sentence variable interpolation when you can

WWDC21 session 10109: *"In order to localize text like this correctly, we end up with a combinatorial explosion. A different localized string is needed for each combination of food, size, and count."* The solutions Apple recommends:

1. **Per-condition full sentences** rather than concatenation.
2. **Plural variants** per CLDR category (zero, one, two, few, many, other).
3. **Automatic Grammar Agreement** for gender/number inflection: `"^[Welcome](inflect: true)"`.
4. **Separate code branches** for non-numeric plurality when a number isn't in the string.

### String Catalogs (Xcode 15+)

Apple's current recommended format, replacing `.strings` and `.stringsdict` over time. Features:

- Auto-extract strings from `Text(...)` and `String(localized:)` on build.
- Per-string state: New, Stale, Needs Review, Translated.
- **Vary by Plural** with CLDR categories prepopulated per language (e.g., One/Other for English; One/Few/Many/Other for Russian).
- **Vary by Device** (e.g., "Tap" on iOS versus "Click" on macOS).
- **Vary by Language** for any per-locale wording difference.
- **First-class comments**, including Xcode's auto-generated ones (Xcode 15+).
- Export/import as **XLIFF** inside Localization Catalogs.

Always write a comment:

```swift
Text("Edit", comment: "Button label that switches a note into editor mode.")
String(localized: "North America", comment: "The name of a continent.")
```

### Plural and gender agreement

CLDR plural categories: **zero, one, two, few, many, other**. When you "Vary by Plural" in a String Catalog, Xcode fills in the valid forms for each language. Important Apple caveat: String Catalog plural variants are for **number-based** plurals with the number in the string. If the string says "You have edits" without a numeral, switch in code (`if count == 1`) — some languages pluralize differently for non-numeric quantity.

For grammatical gender (French, Spanish, German, Italian, Portuguese, Hindi, Russian, Arabic), use **Automatic Grammar Agreement** (WWDC21 session 10109, expanded at WWDC23 session 10153). Wrap the inflectable word in the `inflect` Markdown attribute:

```
"^[Welcome](inflect: true)" = "Bienvenido";
```

At runtime, Foundation's `InflectionRule.automatic` and the user's `Morphology` settings resolve the word to "Bienvenido" or "Bienvenida."

### RTL support

HIG: *"Support right-to-left languages like Arabic and Hebrew by reversing your interface as needed to match the reading direction of the related scripts."* The practical rules:

- Auto Layout with **leading/trailing**, never left/right.
- **Natural text alignment** (`.natural`), not `.left`.
- SF Symbols' **`.forward`** and **`.backward`** variants, which mirror automatically — not `.right` / `.left`.
- Numbers, phone numbers, and country codes remain **left-to-right** inside RTL text runs.
- Test with Xcode's **Right to Left Pseudolanguage**.

---

## 12. Numbers, dates, and units

Locale-aware formatting isn't optional — it's the only way to produce strings that are correct across regions. Language and region are separate settings; a user with English language and German region reads English text but German dates, numbers, and currency separators.

### Principles Apple states repeatedly

- **Never hardcode display formats.** Numeric separators, date order, and currency symbols are locale-driven. `1,234.56` in the US is `1.234,56` in Italy and `1 234,56` in France.
- **Never concatenate formatted strings.** Compose a single localized sentence with placeholders and let the formatter insert the locale-aware substring.
- **Respect the user's calendar.** `Calendar.current` may be Gregorian, Hebrew, Japanese, Buddhist, or Islamic. Don't construct `Calendar(identifier: .gregorian)` for display.
- **Respect the user's region** for date order, 12/24-hour clock, first day of the week, and separators.
- **Respect the measurement system.** Metric, US, and UK differ. `Measurement.FormatStyle` converts appropriately.
- **Use `FormatStyle` (iOS 15+)** in Swift; fall back to `Formatter` subclasses for older targets or Objective-C. Cache legacy formatters — they're expensive to instantiate.

### Dates

```swift
// Presets
Date.now.formatted(date: .abbreviated, time: .shortened)
// en_US: "Apr 20, 2026, 5:00 PM"   de_DE: "20. Apr. 2026, 17:00"

Date.now.formatted(date: .complete, time: .omitted)
// "Monday, April 20, 2026"

// Composed components (order is locale-driven, not call-order)
Date.now.formatted(.dateTime.year().month().day())
// en_US: "Apr 20, 2026"   de_DE: "20. Apr. 2026"

// Override locale/calendar
let style = Date.FormatStyle(date: .long, time: .standard)
    .locale(Locale(identifier: "ja_JP"))
    .calendar(Calendar(identifier: .japanese))
Date.now.formatted(style)

// Machine-readable output — NOT the user locale
Date.now.formatted(.iso8601)
```

Never use `DateFormatter.dateFormat = "MM/dd/yyyy"` for user-facing strings. For machine output, set `locale = Locale(identifier: "en_US_POSIX")` and use a fixed pattern.

### Numbers

```swift
1234.5.formatted()                                       // "1,234.5" (en_US)
1234.5.formatted(.number.precision(.fractionLength(2)))  // "1,234.50"
1234567.formatted(.number.notation(.compactName))        // "1M"
0.25.formatted(.percent)                                 // "25%" (Double)
```

Gotcha: `.percent` treats integer `1` as "1%" and floating-point `1.0` as "100%." Store probabilities as `Double` or `Decimal`.

### Currency

```swift
9.99.formatted(.currency(code: "USD"))    // en_US: "$9.99"  fr_FR: "9,99 $US"
Decimal(9.99).formatted(.currency(code: "EUR"))
```

Use `Decimal`, not `Double`, for money. Always pass an explicit ISO 4217 code — never concatenate a symbol.

### Measurements

```swift
let d = Measurement(value: 300, unit: UnitLength.miles)
d.formatted(.measurement(width: .wide))          // "300 miles"
d.formatted(.measurement(width: .abbreviated))   // "300 mi"

Measurement(value: 10, unit: UnitMass.kilograms).formatted()
// en_US: "22 lb"   de_DE: "10 kg"   — automatic conversion by locale

Measurement(value: 100, unit: UnitTemperature.celsius).formatted()
// en_US: "212°F"   de_DE: "100 °C"
```

The `usage:` parameter (`.person`, `.road`, `.weather`, `.food`) helps the system pick culturally expected units.

### Relative dates

```swift
// Modern (iOS 15+)
Date.now.addingTimeInterval(-3600)
        .formatted(.relative(presentation: .named))     // "1 hour ago"

// Legacy (iOS 13+)
let f = RelativeDateTimeFormatter()
f.unitsStyle = .full                                    // "3 months ago"
f.localizedString(for: past, relativeTo: .now)
```

### Lists, bytes, names, durations

```swift
["A", "B", "C"].formatted(.list(type: .and))              // "A, B, and C"
(1_000_000_000).formatted(.byteCount(style: .file))       // "1 GB"

var name = PersonNameComponents()
name.givenName = "Johnny"; name.familyName = "Appleseed"
name.formatted(.name(style: .abbreviated))                // "JA"
// Name order is locale-driven — ja_JP puts family first.

Duration.seconds(3725).formatted(.time(pattern: .hourMinuteSecond))
// "1:02:05"
```

### English style rules around numbers (Apple Style Guide)

- **a.m. / p.m.** — lowercase with periods and a space before ("8:30 a.m.").
- **24/7**, not "24x7."
- Plural abbreviations take no apostrophe: "CDs," "ISPs."
- In UI, don't hardcode "AM/PM" — 12/24-hour display comes from the user's locale.
- For recent items, prefer relative expressions: "Today," "Yesterday," weekday names within the past week, then short absolute dates — produced by `Date.RelativeFormatStyle`, not composed manually.

---

## Anti-patterns at a glance

| Anti-pattern | Why it fails |
|---|---|
| "OK / Cancel" on a destructive alert | Button label doesn't describe the action |
| "Are you sure?" titles | Adds words without information |
| "Oops!", "Uh-oh!", over-use of "Please" and "Sorry" | Apple calls these patronizing or insincere |
| Single-word alert titles ("Warning!", "Error") | Don't convey the decision |
| Raw error codes as the whole message | Leaves the user stuck |
| "You entered an invalid email" | Blames the user |
| "Something went wrong. Try again." | Not specific enough to act on |
| "Sorry, no items." empty state | Apologetic and useless |
| "App would like to access your Contacts." | Apple's own example of a purpose string that won't pass review |
| "Login to your account" | Wrong verb; Apple uses "Sign in to…" |
| "Click here to learn more" | Non-descriptive link; bad for accessibility and skimming |
| "Let's do this!" as a button label | Cute over clear |
| Concatenating strings with formatted numbers/dates | Breaks in every locale that isn't en_US |
| `DateFormatter.dateFormat = "MM/dd/yyyy"` for display | Hardcoded format defies every user's region |
| Float `Double` arithmetic on money | Precision errors |
| "His or her" pronouns | Excludes and localizes badly |
| master/slave, blacklist/whitelist | Apple moved off these in 2020 |
| Bulk permission requests at first launch | Violates Apple's "ask in context" guidance |
| Six-screen feature tour before any content | Slows the user down and duplicates the App Store listing |

---

## Localization checklist

**Authoring**

- Every user-facing string goes through `Text(...)`, `String(localized:)`, or `NSLocalizedString`.
- Every string has a `comment:` explaining placement, role, and variable meanings.
- No concatenation of translated fragments.
- Positional format specifiers (`%1$@`, `%2$@`) used where variables could reorder.
- Full sentences, not fragments.
- No idioms, puns, slang, humor that depends on culture.
- No gendered default pronouns or assumptions about family, appearance, affluence.
- Inclusive terminology per Apple Style Guide (deny list, allow list, primary/secondary, main, logic board).

**Plurals and grammar**

- Numeric-dependent strings use String Catalog "Vary by Plural" (CLDR categories).
- Non-numeric plurality (no number in the string) uses a code branch instead.
- Gendered inflection uses `^[text](inflect: true)` with `Morphology`.
- Tested with a CLDR-complex language (Russian, Arabic, or Polish).

**Formatting**

- Dates via `Date.FormatStyle` or `DateFormatter`.
- Numbers and currencies via `.formatted()` or `NumberFormatter`; money stored as `Decimal`.
- Measurements via `Measurement.FormatStyle` with a `usage:` hint.
- Lists via `ListFormatter` / `.list(type:)`.
- Names via `PersonNameComponents.FormatStyle`.
- No hardcoded calendar, week start, currency symbol, or measurement system.
- Machine-readable strings use ISO 8601 or `en_US_POSIX`, explicitly.

**Layout**

- Leading/trailing constraints only.
- Natural text alignment.
- SF Symbols `.forward` / `.backward` (not `.right` / `.left`).
- Space to expand — validate with **Double Length Pseudolanguage**.
- RTL validated with **Right to Left Pseudolanguage**.

**Verification**

- **Accented Pseudolanguage** run — no hardcoded English remains.
- **Double Length Pseudolanguage** run — no truncation or layout breaks.
- At least German, Arabic, and Japanese exercised in simulator.
- XLIFF reviewed by native-speaker translators.
- Screenshots in RTL and in the longest language used in App Store listings.

**Inclusion review**

- Imagery diverse across age, body type, ability, ethnicity.
- No assumed family structure, affluence, or ability in copy or visuals.
- Accessibility feature names correct and capitalized (VoiceOver, Dynamic Type, Switch Control).
- VoiceOver labels meaningful sentences, not raw UI descriptions.
- Person-first language when writing about disability; honor community preference.

---

## References

- Apple Style Guide (web): https://support.apple.com/guide/applestyleguide/welcome/web
- Apple Style Guide (PDF, most recent): https://help.apple.com/pdf/applestyleguide/en_US/apple-style-guide.pdf
- HIG — Writing: https://developer.apple.com/design/human-interface-guidelines/writing
- HIG — Inclusion: https://developer.apple.com/design/human-interface-guidelines/inclusion
- HIG — Accessibility: https://developer.apple.com/design/human-interface-guidelines/accessibility
- HIG — Alerts: https://developer.apple.com/design/human-interface-guidelines/alerts
- HIG — Buttons: https://developer.apple.com/design/human-interface-guidelines/buttons
- HIG — Onboarding: https://developer.apple.com/design/human-interface-guidelines/onboarding
- HIG — Feedback: https://developer.apple.com/design/human-interface-guidelines/feedback
- HIG — Loading: https://developer.apple.com/design/human-interface-guidelines/loading
- HIG — Launching: https://developer.apple.com/design/human-interface-guidelines/launching
- HIG — Privacy: https://developer.apple.com/design/human-interface-guidelines/privacy
- HIG — Requesting permission: https://developer.apple.com/design/human-interface-guidelines/requesting-permission
- HIG — Right to left: https://developer.apple.com/design/human-interface-guidelines/right-to-left
- HIG — Menus: https://developer.apple.com/design/human-interface-guidelines/menus
- Apple Developer — Updates to Coding Terminology (2020): https://developer.apple.com/news/?id=1o9zxsxl
- App Store Review Guidelines — Privacy (5.1): https://developer.apple.com/app-store/review/guidelines/#privacy
- Tech Talk — Write clear purpose strings: https://developer.apple.com/videos/play/tech-talks/110152/
- WWDC22 10037 — Writing for interfaces: https://developer.apple.com/videos/play/wwdc2022/10037/
- WWDC22 10107 — Get it right (to left): https://developer.apple.com/videos/play/wwdc2022/10107/
- WWDC21 10109 — What's new in Foundation (FormatStyle, grammar agreement): https://developer.apple.com/videos/play/wwdc2021/10109/
- WWDC21 10275 — The practice of inclusive design: https://developer.apple.com/videos/play/wwdc2021/10275/
- WWDC23 10153 — Unlock the power of grammatical agreement: https://developer.apple.com/videos/play/wwdc2023/10153/
- WWDC23 10155 — Discover String Catalogs: https://developer.apple.com/videos/play/wwdc2023/10155/
- WWDC20 10219 — Build localization-friendly layouts using Xcode: https://developer.apple.com/videos/play/wwdc2020/10219/
- Foundation — FormatStyle: https://developer.apple.com/documentation/foundation/formatstyle
- Foundation — Date.FormatStyle: https://developer.apple.com/documentation/foundation/date/formatstyle
- Foundation — Date.RelativeFormatStyle: https://developer.apple.com/documentation/foundation/date/relativeformatstyle
- Foundation — Measurement.FormatStyle: https://developer.apple.com/documentation/foundation/measurement/formatstyle
- Foundation — NumberFormatter: https://developer.apple.com/documentation/foundation/numberformatter
- Foundation — DateFormatter: https://developer.apple.com/documentation/foundation/dateformatter
- Foundation — RelativeDateTimeFormatter: https://developer.apple.com/documentation/foundation/relativedatetimeformatter
- Foundation — InflectionRule / Morphology: https://developer.apple.com/documentation/foundation/inflectionrule
- Apple Localization portal: https://developer.apple.com/localization/
- Xcode Localization docs: https://developer.apple.com/documentation/xcode/localization
- Localizing and varying text with a string catalog: https://developer.apple.com/documentation/xcode/localizing-and-varying-text-with-a-string-catalog
- Information Property List — privacy keys reference (Cocoa Keys): https://developer.apple.com/library/archive/documentation/General/Reference/InfoPlistKeyReference/Articles/CocoaKeys.html
- Internationalization & Localization Guide (archived): https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPInternational/

*Two notes on sourcing: the widely cited "~30% text expansion for German" rule of thumb is documented in many iOS community guides but not stated verbatim in Apple's current primary documentation — Apple's published guidance is directional and validated via Xcode's Double Length Pseudolanguage scheme option. Similarly, the specific ableist-word list (crazy, lame, sanity check, dummy) is from Google's and Microsoft's inclusive-writing guides; Apple publishes the principle ("avoid language that uses a disability to express a negative quality") rather than a per-word list.*